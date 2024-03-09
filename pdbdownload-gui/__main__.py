import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import threading
import binascii
import os
import pefile
import argparse
import requests
from rich import progress
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from threading import Lock

stop_requested = False

processed_files = set()
processed_files_lock = Lock()

downloading_files = set()
downloaded_files = set()
files_lock = Lock()

def download_pdb(download_dir, pdbname, guid, pdbage, update_status, download_url):
    file_path = f"{download_dir}{os.path.sep}{pdbname}"

    # Check if the file is already downloaded or being downloaded
    #
    with files_lock:
        if file_path in downloading_files or file_path in downloaded_files:
            return
        downloading_files.add(file_path)

    if update_status:
        update_status(f"Downloading: {pdbname} (URL: {download_url})")

    download_url = f"http://msdl.microsoft.com/download/symbols/{pdbname}/{guid.upper()}{pdbage:X}/{pdbname}"
    print(f"[>] Downloading {download_url}")
    r = requests.head(
        download_url,
        headers={"User-Agent": "Microsoft-Symbol-Server/10.0.10036.206"},
        allow_redirects=True
    )
    if r.status_code == 200:
        target_file = f"{download_dir}{os.path.sep}{pdbname}"
        with progress.Progress() as p:
            progress_bar, csize = p.add_task(f"[cyan]Downloading {pdbname}",
                                             total=int(r.headers["Content-Length"])), 1024 * 16
            pdb = requests.get(r.url, headers={"User-Agent": "Microsoft-Symbol-Server/10.0.10036.206"}, stream=True)
            with open(target_file, "wb") as f:
                for chunk in pdb.iter_content(chunk_size=csize):
                    f.write(chunk)
                    p.update(progress_bar, advance=len(chunk))

        # After download completion
        #
        with files_lock:
            downloading_files.remove(file_path)
            downloaded_files.add(file_path)
    else:
        print(f"[!] (HTTP {r.status_code}) Could not find {download_url}")
        with files_lock:
            downloading_files.remove(file_path)

def get_pe_debug_infos(pathtopefile):
    p = pefile.PE(pathtopefile, fast_load=False)
    pedata = {d.name: d for d in p.OPTIONAL_HEADER.DATA_DIRECTORY}
    raw_debug_data = p.parse_debug_directory(pedata["IMAGE_DIRECTORY_ENTRY_DEBUG"].VirtualAddress,
                                             pedata["IMAGE_DIRECTORY_ENTRY_DEBUG"].Size)[0].entry
    guid = f"{raw_debug_data.Signature_Data1:08X}{raw_debug_data.Signature_Data2:04X}{raw_debug_data.Signature_Data3:04X}{binascii.hexlify(raw_debug_data.Signature_Data4).decode('utf-8').upper()}"
    return raw_debug_data.PdbFileName.strip(b'\x00').decode("utf-8"), guid, raw_debug_data.Age

def process_pe_file(pef, options):
    file_hash = hash(pef)
    with processed_files_lock:
        if file_hash in processed_files:
            return
        processed_files.add(file_hash)

    try:
        if options.verbose:
            print(f"[>] Reading PE file '{pef}'")
        pdbname, guid, pdbage = get_pe_debug_infos(pef)
        if options.verbose:
            print(f"  | PdbName '{pdbname}'")
            print(f"  | GUID    {guid}")
            print(f"  | Age     {pdbage:X}")
        download_pdb(options.symbols_dir, pdbname, guid, pdbage, options.verbose)
    except Exception as e:
        with processed_files_lock:
            processed_files.remove(file_hash)
        raise e

class SymbolDownloaderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Symbol Downloader")
        self.geometry("600x200")

        # Frame for PE File/Directory Input
        #
        frame_pe_source = tk.Frame(self)
        frame_pe_source.pack(pady=10, fill=tk.X)
        self.pe_source_label = tk.Label(frame_pe_source, text="Select PE File/Directory:")
        self.pe_source_label.pack(side=tk.LEFT, padx=5)
        self.pe_source_entry = tk.Entry(frame_pe_source)
        self.pe_source_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        self.pe_source_browse_button = tk.Button(frame_pe_source, text="Browse", command=self.browse_pe_source)
        self.pe_source_browse_button.pack(side=tk.LEFT, padx=5)

        # Frame for Download Directory Input
        #
        frame_download_dir = tk.Frame(self)
        frame_download_dir.pack(pady=10, fill=tk.X)
        self.download_dir_label = tk.Label(frame_download_dir, text="Select Download Directory:")
        self.download_dir_label.pack(side=tk.LEFT, padx=5)
        self.download_dir_entry = tk.Entry(frame_download_dir)
        self.download_dir_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        self.download_dir_browse_button = tk.Button(frame_download_dir, text="Browse", command=self.browse_download_dir)
        self.download_dir_browse_button.pack(side=tk.LEFT, padx=5)

        self.status_label = tk.Label(self, text="Status: Idle", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        # Frame for Start and Stop Buttons
        #
        frame_buttons = tk.Frame(self)
        frame_buttons.pack(pady=10)

        self.start_button = tk.Button(frame_buttons, text="Start Download", command=self.start_download)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(frame_buttons, text="Stop", command=self.stop_download)
        self.stop_button.pack(side=tk.LEFT, padx=5)

    def update_status(self, message):
        self.status_label.config(text=message)

    def browse_pe_source(self):
        def select_file():
            filename = filedialog.askopenfilename(initialdir="/", title="Select a File")
            if filename:
                self.pe_source_entry.delete(0, tk.END)
                self.pe_source_entry.insert(0, filename)
            custom_dialog.destroy()

        def select_directory():
            directory = filedialog.askdirectory(initialdir="/", title="Select a Directory")
            if directory:
                self.pe_source_entry.delete(0, tk.END)
                self.pe_source_entry.insert(0, directory)
            custom_dialog.destroy()

        custom_dialog = tk.Toplevel(self)
        custom_dialog.title("Select File or Directory")
        custom_dialog.geometry("300x100")
        tk.Label(custom_dialog, text="Choose to select a file or a directory:").pack(pady=10)
        tk.Button(custom_dialog, text="Select File", command=select_file).pack(side=tk.LEFT, padx=10)
        tk.Button(custom_dialog, text="Select Directory", command=select_directory).pack(side=tk.RIGHT, padx=10)

    def browse_download_dir(self):
        directory = filedialog.askdirectory()
        self.download_dir_entry.delete(0, tk.END)
        self.download_dir_entry.insert(0, directory)

    def start_download(self):
        pe_source = self.pe_source_entry.get()
        download_dir = self.download_dir_entry.get()

        if not pe_source or not download_dir:
            messagebox.showerror("Error", "Please select both PE source and download directory.")
            return

        threading.Thread(target=self.download_symbols, args=(pe_source, download_dir), daemon=True).start()

    def stop_download(self):
        global stop_requested
        stop_requested = True
        self.update_status("Stopping after current download...")

    def download_symbols(self, pe_source, download_dir):
        global stop_requested
        stop_requested = False

        # Check if the source is a file or directory; support more extensions than exe/dll
        #
        if os.path.isdir(pe_source):
            list_of_pe_files = []
            for root, dirs, files in os.walk(pe_source):
                for filename in files:
                    if filename.lower().endswith(".exe") or filename.lower().endswith(".dll") or filename.lower().endswith(".efi") or filename.lower().endswith(".sys") or filename.lower().endswith(".bin"):
                        name = os.path.join(root, filename)
                        list_of_pe_files.append(name)

            with ThreadPoolExecutor(max_workers=1) as executor:
                for pe_file in list_of_pe_files:
                    executor.submit(self.process_pe_file, pe_file, download_dir)
        elif os.path.isfile(pe_source):
            self.process_pe_file(pe_source, download_dir)
        else:
            messagebox.showerror("Error", "Invalid PE source path.")

    def process_pe_file(self, pef, download_dir):
        global stop_requested

        try:
            pdbname, guid, pdbage = get_pe_debug_infos(pef)
            download_url = f"http://msdl.microsoft.com/download/symbols/{pdbname}/{guid.upper()}{pdbage:X}/{pdbname}"
            self.update_status(f"Located {pdbname} ({download_url})")
            download_pdb(download_dir, pdbname, guid, pdbage, self.update_status, download_url)
            self.update_status(f"Status: Idle.")
        except Exception as e:
            #messagebox.showerror("Error", f"An error occurred: {e}")
            self.update_status("Status: Error")

        if stop_requested:
            self.update_status("Download stopped.")
            return


if __name__ == '__main__':
    app = SymbolDownloaderApp()
    app.mainloop()
