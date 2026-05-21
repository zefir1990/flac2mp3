# flac2mp3

[**🇷🇺 Читать на русском**](README.ru.md)

A clean Python script to recursively convert FLAC files to high-quality MP3 format using `ffmpeg`.

## Prerequisites

- **Python 3.x**
- **ffmpeg** installed and added to your system's PATH.

## Features

- Recursive search for all `.flac` files in a given directory.
- High-quality Variable Bit Rate (VBR) MP3 encoding using `libmp3lame` (quality level `-q:a 0`).
- Clean handling of file and folder names containing spaces.
- Robust subprocess call handling.
- Multiple export modes:
  - **In-place**: Saves the `.mp3` file next to its corresponding `.flac` file.
  - **Save Directory Tree**: Re-creates the source directory structure under a target folder.
  - **Flattened**: Exports all converted MP3s directly into a single folder.
  - **Combined**: Allows running both export modes simultaneously, converting once and copying the output file to avoid redundant work.

## Usage

To run the script with default settings (recursively convert FLAC files in-place starting from the current directory):

```powershell
python flac2mp3.py
```

You can optionally specify a target directory to scan and export options:

```powershell
python flac2mp3.py [search_directory] [options]
```

# Real Life Example

Converting all flacs from D:\Downloads to D:\mp3s with 4 parallel threads, saving directories tree:

```powershell
python .\flac2mp3.py D:\Downloads\ --output-directory-save-directories-tree=D:\mp3s\ --parallel-run=4
```

### Options

- `--output-directory-save-directories-tree=<path>` (or without `--` prefix: `output-directory-save-directories-tree=<path>`)
  
  Exports MP3 files to `<path>` while recreating the subfolder structure.

- `--output-directory-without-directories-tree=<path>` (or without `--` prefix: `output-directory-without-directories-tree=<path>`)
  
  Exports all MP3 files directly into `<path>`, flattening the subdirectories.

- `--parallel-run=<number>` (or without `--` prefix: `parallel-run=<number>`)
  
  Number of concurrent audio conversions (default: `1`).

### Examples

#### 1. In-place conversion
Convert all FLAC files under the current directory, saving the MP3s next to the original files:
```powershell
python flac2mp3.py
```

#### 2. Recreate directory structure elsewhere
Convert FLAC files from `C:\Music\FLAC` and export them to `D:\Music\MP3` preserving the subfolder layout:
```powershell
python flac2mp3.py C:\Music\FLAC output-directory-save-directories-tree=D:\Music\MP3
```

#### 3. Flatten export directory
Convert FLAC files from `C:\Music\FLAC` and dump all generated MP3s into `D:\Music\FlatMP3`:
```powershell
python flac2mp3.py C:\Music\FLAC output-directory-without-directories-tree=D:\Music\FlatMP3
```

#### 4. Combine export modes
Convert FLAC files and save them to both a structured and a flat directory at the same time:
```powershell
python flac2mp3.py C:\Music\FLAC output-directory-save-directories-tree=D:\Music\MP3 output-directory-without-directories-tree=D:\Music\FlatMP3
```

#### 5. Concurrent conversions
Convert FLAC files in parallel using 4 concurrent threads:
```powershell
python flac2mp3.py parallel-run=4
```
