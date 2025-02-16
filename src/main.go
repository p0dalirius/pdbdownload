package main

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"

	"pdbdownload/logger"
	"pdbdownload/utils"

	"github.com/p0dalirius/goopts/parser"
)

var (
	debug bool

	peFile     string
	peDir      string
	symbolsDir string
)

func parseArgs() {
	ap := parser.ArgumentsParser{
		Banner:          "pdbdownload v1.0 - by Remi GASCOU (Podalirius)",
		ShowBannerOnRun: true,
	}

	ap.NewBoolArgument(&debug, "-d", "--debug", false, "Debug mode.")

	group_pesource, err := ap.NewRequiredMutuallyExclusiveArgumentGroup("Source of PE files")
	if err != nil {
		fmt.Printf("[error] Error creating ArgumentGroup: %s\n", err)
	} else {
		group_pesource.NewStringArgument(&peFile, "-f", "--pe-file", "", false, "Source PE file to get symbols for.")
		group_pesource.NewStringArgument(&peDir, "-d", "--pe-dir", "", false, "Source directory where to get PE files to get symbols for.")
	}

	ap.NewStringArgument(&symbolsDir, "-S", "--symbols-dir", "./symbols/", false, "Output dir where symbols will be downloaded.")

	// Parse the arguments
	ap.Parse()
}

func main() {
	parseArgs()

	startTime := time.Now()

	// Ensure the symbols directory exists
	if _, err := os.Stat(symbolsDir); os.IsNotExist(err) {
		if debug {
			fmt.Printf("[>] Creating '%s'\n", symbolsDir)
		}
		err := os.MkdirAll(symbolsDir, 0755)
		if err != nil {
			fmt.Printf("Error creating symbols directory: %v\n", err)
			os.Exit(1)
		}
	}

	if len(peDir) != 0 {
		// Resolve absolute path for the PE directory
		absPeDir, err := filepath.Abs(peDir)
		if err != nil {
			fmt.Printf("Error resolving absolute path for PE directory: %v\n", err)
			os.Exit(1)
		}
		peDir = absPeDir
		var listOfPeFiles []struct {
			path   string
			subdir string
		}

		// Search for PE files in the directory
		if debug {
			fmt.Printf("[debug] Searching for PE files in '%s' ...\n", peDir)
		}
		err = filepath.Walk(peDir, func(path string, info os.FileInfo, err error) error {
			if err != nil {
				return err
			}
			if !info.IsDir() && (strings.HasSuffix(strings.ToLower(info.Name()), ".exe") || strings.HasSuffix(strings.ToLower(info.Name()), ".dll")) {
				relPath, _ := filepath.Rel(peDir, filepath.Dir(path))
				listOfPeFiles = append(listOfPeFiles, struct {
					path   string
					subdir string
				}{path, relPath})
			}
			return nil
		})
		if err != nil {
			fmt.Printf("Error walking the PE directory: %v\n", err)
			os.Exit(1)
		}

		// Process each PE file
		for _, file := range listOfPeFiles {
			if debug {
				fmt.Printf("[>] Reading PE file '%s'\n", file.path)
			}
			pdbName, signature, err := PEGetPDBandSignature(file.path)
			if err != nil {
				fmt.Printf("Error finding PDB and Signature for PE: %v\n", err)
				os.Exit(1)
			} else {
				if len(pdbName) != 0 && len(signature) != 0 {
					if debug {
						fmt.Printf("  | PdbName  '%s'\n", pdbName)
						fmt.Printf("  | Signature %s\n", signature)
					}
					DownloadPDB(symbolsDir, pdbName, signature)
				}
			}
		}
	} else if len(peFile) != 0 {
		// Process a single PE file
		if debug {
			fmt.Printf("[>] Reading PE file '%s'\n", peFile)
		}
		pdbName, signature, err := PEGetPDBandSignature(peFile)
		if err != nil {
			fmt.Printf("Error finding PDB and Signature for PE: %v\n", err)
			os.Exit(1)
		} else {
			if len(pdbName) != 0 && len(signature) != 0 {
				if debug {
					fmt.Printf("  | PdbName  : '%s'\n", pdbName)
					fmt.Printf("  | Signature: %s\n", signature)
				}
				DownloadPDB(symbolsDir, pdbName, signature)
			}
		}
	}

	logger.Info(fmt.Sprintf("Total time elapsed: %s", utils.ElapsedTime(startTime)))
}
