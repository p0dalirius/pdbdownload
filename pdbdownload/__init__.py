#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name          : __init__.py
# Author             : Podalirius (@podalirius_)
# Date created       : 7 Feb 2023
# Modified           : @winapiadmin
import pefile
import requests
from rich import progress
def download_pdb(pathtopefile):
    p = pefile.PE(pathtopefile, fast_load=False)
    pedata = {d.name: d for d in p.OPTIONAL_HEADER.DATA_DIRECTORY}
    raw_debug_data = [e for e in p.parse_debug_directory(pedata["IMAGE_DIRECTORY_ENTRY_DEBUG"].VirtualAddress, pedata["IMAGE_DIRECTORY_ENTRY_DEBUG"].Size) if e.entry is not None]
    raw_debug_data = raw_debug_data[0].entry
    pdbname: str = raw_debug_data.PdbFileName.strip(b'\x00').decode("utf-8")
    signature: str = p.DIRECTORY_ENTRY_DEBUG[0].entry.Signature_String
    # If an absolute path is embedded the server uses just the filename
    pdbname = pdbname.split("\\")[-1]
    download_url = "https://msdl.microsoft.com/download/symbols/%s/%s/%s" % (pdbname, signature.upper(), pdbname)
    r = requests.head(
        download_url,
        headers={"User-Agent": "Microsoft-Symbol-Server/10.0.10036.206"},
        allow_redirects=True
    )
    if r.status_code == 200:
        return r.content
    else:
        return None
