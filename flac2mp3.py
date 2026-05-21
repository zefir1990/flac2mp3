#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil

def check_ffmpeg():
    if not shutil.which("ffmpeg"):
        print("Error: 'ffmpeg' executable not found in PATH.", file=sys.stderr)
        print("Please install ffmpeg and ensure it is added to your environment variables.", file=sys.stderr)
        sys.exit(1)

def convert_flac_to_mp3(search_dir, output_tree_dir=None, output_flat_dir=None):
    check_ffmpeg()

    print(f"Scanning for .flac files in: {os.path.abspath(search_dir)}")
    if output_tree_dir:
        print(f"Exporting MP3s with directory tree to: {os.path.abspath(output_tree_dir)}")
    elif output_flat_dir:
        print(f"Exporting MP3s without directory tree to: {os.path.abspath(output_flat_dir)}")
    flac_files = []
    for root, _, files in os.walk(search_dir):
        for file in files:
            if file.lower().endswith('.flac'):
                flac_files.append(os.path.join(root, file))

    if not flac_files:
        print("No .flac files found to convert.")
        return

    print(f"Found {len(flac_files)} .flac file(s). Starting conversion...\n")

    for index, flac_path in enumerate(flac_files, start=1):
        relative_flac = os.path.relpath(flac_path, search_dir)
        relative_flac_no_ext = os.path.splitext(relative_flac)[0]
        
        if output_flat_dir:
            basename_no_ext = os.path.splitext(os.path.basename(flac_path))[0]
            mp3_path = os.path.join(output_flat_dir, basename_no_ext + ".mp3")
            os.makedirs(output_flat_dir, exist_ok=True)
            relative_mp3 = os.path.relpath(mp3_path, output_flat_dir)
        elif output_tree_dir:
            mp3_path = os.path.join(output_tree_dir, relative_flac_no_ext + ".mp3")
            os.makedirs(os.path.dirname(mp3_path), exist_ok=True)
            relative_mp3 = os.path.relpath(mp3_path, output_tree_dir)
        else:
            mp3_path = os.path.splitext(flac_path)[0] + ".mp3"
            relative_mp3 = os.path.relpath(mp3_path, search_dir)
            
        print(f"[{index}/{len(flac_files)}] Converting: {relative_flac} -> {relative_mp3}")

        command = [
            "ffmpeg",
            "-y",
            "-i", flac_path,
            "-c:a", "libmp3lame",
            "-q:a", "0",
            mp3_path
        ]

        try:
            process = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"  [ERROR] Failed to convert: {relative_flac}", file=sys.stderr)
            print(f"  ffmpeg output:\n{e.stderr}", file=sys.stderr)
        except Exception as e:
            print(f"  [ERROR] Unexpected error occurred: {e}", file=sys.stderr)

    print("\nConversion process completed.")

if __name__ == "__main__":
    search_directory = "."
    output_tree_dir = None
    output_flat_dir = None

    for arg in sys.argv[1:]:
        if arg.startswith("output-directory-save-directories-tree="):
            output_tree_dir = arg.split("output-directory-save-directories-tree=", 1)[1]
        elif arg.startswith("--output-directory-save-directories-tree="):
            output_tree_dir = arg.split("--output-directory-save-directories-tree=", 1)[1]
        elif arg.startswith("output-directory-without-directories-tree="):
            output_flat_dir = arg.split("output-directory-without-directories-tree=", 1)[1]
        elif arg.startswith("--output-directory-without-directories-tree="):
            output_flat_dir = arg.split("--output-directory-without-directories-tree=", 1)[1]
        else:
            search_directory = arg

    if output_tree_dir and output_flat_dir:
        print("Error: Cannot use both 'output-directory-save-directories-tree' and 'output-directory-without-directories-tree'.", file=sys.stderr)
        sys.exit(1)

    if not os.path.isdir(search_directory):
        print(f"Error: The directory '{search_directory}' does not exist.", file=sys.stderr)
        sys.exit(1)

    convert_flac_to_mp3(search_directory, output_tree_dir, output_flat_dir)
