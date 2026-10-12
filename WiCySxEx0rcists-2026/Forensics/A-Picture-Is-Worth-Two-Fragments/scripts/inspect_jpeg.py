#!/usr/bin/env python3

import argparse
from pathlib import Path

def inspect_jpeg(file_path):
    data = Path(file_path).read_bytes()

    signatures = [
        (b'\xff\xd8\xff', 'JPEG START'),
        (b'\xff\xd9', 'JPEG END')
    ]

    print(f"File: {file_path}")
    print(f"Size: {len(data)} bytes\n")

    for marker, name in signatures:
        start = 0

        while True:
            pos = data.find(marker, start)

            if pos == -1:
                break

            print(f"{name}: offset {pos} (0x{pos:x})")
            start = pos + 1

def main():
    parser = argparse.ArgumentParser(
        description="Inspect JPEG start and end markers in a file"
    )

    parser.add_argument(
        "file",
        help="Path to the JPEG file"
    )

    args = parser.parse_args()
    inspect_jpeg(args.file)

if __name__ == "__main__":
    main()