![](./.github/banner.png)

<p align="center">
    An utility to download PDB files associated with a Portable Executable (PE).
    <br>
    <a href="https://github.com/p0dalirius/pdbdownload/actions/workflows/commit.yaml" title="Build"><img alt="Build and Release" src="https://github.com/p0dalirius/pdbdownload/actions/workflows/commit.yaml/badge.svg"></a>
    <img alt="GitHub release (latest by date)" src="https://img.shields.io/github/v/release/p0dalirius/pdbdownload">
    <a href="https://twitter.com/intent/follow?screen_name=podalirius_" title="Follow"><img src="https://img.shields.io/twitter/follow/podalirius_?label=Podalirius&style=social"></a>
    <a href="https://www.youtube.com/c/Podalirius_?sub_confirmation=1" title="Subscribe"><img alt="YouTube Channel Subscribers" src="https://img.shields.io/youtube/channel/subscribers/UCF_x5O7CSfr82AfNVTKOv_A?style=social"></a>
    <br>
</p>

## Features

 - [x] Download PDB symbols from `msdl.microsoft.com`.
 - [x] Process a single or a batch of PortableExecutable (PE) files.

## Demonstration



## Usage

```
$./pdbdownload-linux-amd64 -h
pdbdownload v1.0 - by Remi GASCOU (Podalirius)

Usage: pdbdownload [--debug] [--symbols-dir <string>] [--pe-file <string>] [--pe-dir <string>]

  -d, --debug                Debug mode. (default: false)
  -S, --symbols-dir <string> Output dir where symbols will be downloaded. (default: "./symbols/")

  Source of PE files:
    -f, --pe-file <string> Source PE file to get symbols for. (default: "")
    -d, --pe-dir <string>  Source directory where to get PE files to get symbols for. (default: "")
```

## Building the project

To build the project, use the following Docker command in this directory:

```bash
docker run -v $(pwd):/workspace/ podalirius/build-go-project
```

Or, if you want to build it manually, you can use the following commands:

```
GOOS=linux GOARCH=amd64; mkdir -p "/workspace/bin/linux/${GOOS}/${GOARCH}/" && /usr/local/go/bin/go build -o "/workspace/bin/linux/${GOOS}/${GOARCH}/pdbdownload" -buildvcs=false
```

## Quick start commands

- To download all the PDB files associated to every PE file in the specified directory:
    ```bash
    ./pdbdownload-linux-amd64 -d ./pe_files/
    ```

- To download the PDB file associated to a single PE file:
    ```bash
    ./pdbdownload-linux-amd64 -f ./example.exe
    ```

## Contributing

Pull requests are welcome. Feel free to open an issue if you want to add other features.
