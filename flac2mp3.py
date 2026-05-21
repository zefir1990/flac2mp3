#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess
import shutil
import threading
from concurrent.futures import ThreadPoolExecutor

print_lock = threading.Lock()

def safe_print(*args, **kwargs):
    with print_lock:
        print(*args, **kwargs)

def check_ffmpeg():
    if not shutil.which("ffmpeg"):
        print("Error: 'ffmpeg' executable not found in PATH.", file=sys.stderr)
        print("Please install ffmpeg and ensure it is added to your environment variables.", file=sys.stderr)
        sys.exit(1)

def convert_single_file(index, flac_path, total, search_dir, output_tree_dir, output_flat_dir, skip_existing=False):
    relative_flac = os.path.relpath(flac_path, search_dir)
    relative_flac_no_ext = os.path.splitext(relative_flac)[0]
    
    destinations = []
    if output_tree_dir:
        dest_tree = os.path.join(output_tree_dir, relative_flac_no_ext + ".mp3")
        destinations.append(dest_tree)
    if output_flat_dir:
        basename_no_ext = os.path.splitext(os.path.basename(flac_path))[0]
        dest_flat = os.path.join(output_flat_dir, basename_no_ext + ".mp3")
        destinations.append(dest_flat)
    if not destinations:
        dest_inplace = os.path.splitext(flac_path)[0] + ".mp3"
        destinations.append(dest_inplace)

    display_paths = []
    for dest in destinations:
        if output_tree_dir and dest.startswith(output_tree_dir):
            display_paths.append(os.path.relpath(dest, output_tree_dir))
        elif output_flat_dir and dest.startswith(output_flat_dir):
            display_paths.append(os.path.relpath(dest, output_flat_dir))
        else:
            display_paths.append(os.path.relpath(dest, search_dir))

    if skip_existing and all(os.path.exists(dest) for dest in destinations):
        safe_print(f"[{index}/{total}] Skipping (exists): {relative_flac}")
        return

    safe_print(f"[{index}/{total}] Converting: {relative_flac} -> {', '.join(display_paths)}")

    for dest in destinations:
        os.makedirs(os.path.dirname(dest), exist_ok=True)

    primary_dest = destinations[0]
    command = [
        "ffmpeg",
        "-y",
        "-i", flac_path,
        "-c:a", "libmp3lame",
        "-q:a", "0",
        primary_dest
    ]

    try:
        subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True
        )
        for extra_dest in destinations[1:]:
            shutil.copy2(primary_dest, extra_dest)
    except subprocess.CalledProcessError as e:
        safe_print(f"  [ERROR] Failed to convert: {relative_flac}", file=sys.stderr)
        safe_print(f"  ffmpeg output:\n{e.stderr}", file=sys.stderr)
    except Exception as e:
        safe_print(f"  [ERROR] Unexpected error occurred: {e}", file=sys.stderr)

def convert_flac_to_mp3(search_dir, output_tree_dir=None, output_flat_dir=None, parallel_run=1, skip_existing=False):
    check_ffmpeg()

    print(f"Scanning for .flac files in: {os.path.abspath(search_dir)}")
    if output_tree_dir:
        print(f"Exporting MP3s with directory tree to: {os.path.abspath(output_tree_dir)}")
    if output_flat_dir:
        print(f"Exporting MP3s without directory tree to: {os.path.abspath(output_flat_dir)}")
    flac_files = []
    for root, _, files in os.walk(search_dir):
        for file in files:
            if file.lower().endswith('.flac'):
                flac_files.append(os.path.join(root, file))

    if not flac_files:
        print("No .flac files found to convert.")
        return

    print(f"Found {len(flac_files)} .flac file(s). Starting conversion using {parallel_run} worker(s)...\n")

    with ThreadPoolExecutor(max_workers=parallel_run) as executor:
        futures = [
            executor.submit(
                convert_single_file,
                index,
                flac_path,
                len(flac_files),
                search_dir,
                output_tree_dir,
                output_flat_dir,
                skip_existing
            )
            for index, flac_path in enumerate(flac_files, start=1)
        ]
        for future in futures:
            future.result()

    print("\nConversion process completed.")

if __name__ == "__main__":
    args_to_parse = []
    for arg in sys.argv[1:]:
        if "=" in arg and not arg.startswith("-"):
            args_to_parse.append("--" + arg)
        else:
            args_to_parse.append(arg)

    parser = argparse.ArgumentParser(description="Convert FLAC files to MP3 recursively using ffmpeg.")
    parser.add_argument(
        "search_directory",
        nargs="?",
        default=".",
        help="Directory to scan for FLAC files (default: current directory)"
    )
    parser.add_argument(
        "--output-directory-save-directories-tree",
        help="Directory to save MP3s preserving the subdirectories structure"
    )
    parser.add_argument(
        "--output-directory-without-directories-tree",
        help="Directory to save MP3s directly without subdirectories structure"
    )
    parser.add_argument(
        "--parallel-run",
        type=int,
        default=1,
        help="Number of concurrent conversions (default: 1)"
    )
    parser.add_argument(
        "--skip-output-file-if-exists",
        action="store_true",
        default=False,
        help="Skip conversion if the output MP3 file already exists"
    )

    args = parser.parse_args(args_to_parse)

    if not os.path.isdir(args.search_directory):
        print(f"Error: The directory '{args.search_directory}' does not exist.", file=sys.stderr)
        sys.exit(1)

    convert_flac_to_mp3(
        args.search_directory,
        args.output_directory_save_directories_tree,
        args.output_directory_without_directories_tree,
        args.parallel_run,
        args.skip_output_file_if_exists
    )
