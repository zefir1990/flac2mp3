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

def convert_flac_to_mp3(search_dir):
    check_ffmpeg()

    print(f"Scanning for .flac files in: {os.path.abspath(search_dir)}")
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
        mp3_path = os.path.splitext(flac_path)[0] + ".mp3"
        
        relative_flac = os.path.relpath(flac_path, search_dir)
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
    target_directory = sys.argv[1] if len(sys.argv) > 1 else "."
    
    if not os.path.isdir(target_directory):
        print(f"Error: The directory '{target_directory}' does not exist.", file=sys.stderr)
        sys.exit(1)
        
    convert_flac_to_mp3(target_directory)
