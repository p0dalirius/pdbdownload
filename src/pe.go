package main

import (
	"fmt"

	"github.com/saferwall/pe"
)

func PEGetVersion(filePath string) (fileVersion, productVersion string, err error) {
	// Open the PE file
	peFile, err := pe.New(filePath, &pe.Options{})
	if err != nil {
		return "", "", fmt.Errorf("failed to open PE file: %w", err)
	}
	defer peFile.Close()

	// Parse the PE file
	err = peFile.Parse()
	if err != nil {
		return "", "", fmt.Errorf("failed to parse PE file: %w", err)
	}

	// Access the resource version info
	versionInfo, err := peFile.ParseVersionResources()
	if err != nil {
		return "", "", fmt.Errorf("failed to retrieve version info: %w", err)
	}

	// Extract file version and product version
	fileVersion = versionInfo["FileVersion"]
	productVersion = versionInfo["ProductVersion"]

	return fileVersion, productVersion, nil
}

func PEGetPDBandSignature(filePath string) (pdbName string, signature string, err error) {
	// Open the PE file
	peFile, err := pe.New(filePath, &pe.Options{})
	if err != nil {
		return pdbName, signature, fmt.Errorf("failed to open PE file: %w", err)
	}
	defer peFile.Close()

	// Parse the PE file
	err = peFile.Parse()
	if err != nil {
		return pdbName, signature, fmt.Errorf("failed to parse PE file: %w", err)
	}

	if len(peFile.Debugs) != 0 {
		// Todo: Handle other types:
		// Src: https://github.com/saferwall/pe/blob/ed7fd35b849f1faeddb50e9f792773560acd4042/cmd/dump.go#L608-L695

		switch v := peFile.Debugs[0].Info.(type) {
		case pe.CVInfoPDB70:
			pdbName = v.PDBFileName
			signatureData := v.Signature
			signature = fmt.Sprintf(
				"%08x%04x%04x%012x",
				signatureData.Data1,
				signatureData.Data2,
				signatureData.Data3,
				signatureData.Data4,
			)
			// I don't understand why, but guid is 33 chars, that is the signature, ending with 1
			signature = signature + "1"
		case pe.CVInfoPDB20:
			pdbName = ""
			signature = ""
		case pe.POGO:
			pdbName = ""
			signature = ""
		}
	}

	return pdbName, signature, nil
}
