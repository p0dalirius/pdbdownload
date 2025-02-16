package main

import (
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/schollz/progressbar/v3"
)

func DownloadPDB(downloadDir, pdbname, signature string) {
	// Construct the download URL
	downloadURL := fmt.Sprintf("https://msdl.microsoft.com/download/symbols/%s/%s/%s", pdbname, strings.ToUpper(signature), pdbname)
	fmt.Printf("[>] Downloading %s\n", downloadURL)

	// Send a HEAD request to get file information
	client := &http.Client{}
	req, err := http.NewRequest("HEAD", downloadURL, nil)
	if err != nil {
		fmt.Printf("[!] Error creating request: %v\n", err)
		return
	}
	req.Header.Set("User-Agent", "Microsoft-Symbol-Server/10.0.10036.206")

	resp, err := client.Do(req)
	if err != nil {
		fmt.Printf("[!] Error sending request: %v\n", err)
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusOK {
		targetFile := filepath.Join(downloadDir, pdbname)

		// Send a GET request to download the file
		req, err := http.NewRequest("GET", resp.Request.URL.String(), nil)
		if err != nil {
			fmt.Printf("[!] Error creating download request: %v\n", err)
			return
		}
		req.Header.Set("User-Agent", "Microsoft-Symbol-Server/10.0.10036.206")

		resp, err := client.Do(req)
		if err != nil {
			fmt.Printf("[!] Error downloading file: %v\n", err)
			return
		}
		defer resp.Body.Close()

		// Write the file while updating the progress bar
		outFile, err := os.Create(targetFile)
		if err != nil {
			fmt.Printf("[!] Error creating file: %v\n", err)
			return
		}
		defer outFile.Close()

		bar := progressbar.DefaultBytes(
			resp.ContentLength,
			fmt.Sprintf("Downloading %s", pdbname),
		)

		_, err = io.Copy(io.MultiWriter(outFile, bar), resp.Body)
		if err != nil {
			fmt.Printf("[!] Error saving file: %v\n", err)
		}
	} else {
		fmt.Printf("[!] (HTTP %d) Could not find %s\n", resp.StatusCode, downloadURL)
	}
}
