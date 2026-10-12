
#!/usr/bin/env python3

import argparse
from pathlib import Path


def inspect_jpeg(file_path):
    path = Path(file_path)

    if not path.is_file():
        print(f"Error: File '{file_path}' not found.")
        return

    try:
        data = path.read_bytes()
    except OSError as e:
        print(f"Error reading '{file_path}': {e}")
        return

    signatures = [
        (b'\xff\xd8\xff', 'JPEG START'),
        (b'\xff\xd9', 'JPEG END')
    ]

    print(f"File: {path.name}")
    print(f"Size: {len(data)} bytes\n")

    results = []

    for marker, name in signatures:
        start = 0

        while True:
            pos = data.find(marker, start)

            if pos == -1:
                break

            results.append((pos, name))
            start = pos + 1

    if not results:
        print("No JPEG signatures found.")
        return

    for pos, name in sorted(results):
        print(f"{name}: offset {pos} (0x{pos:x})")


def main():
    parser = argparse.ArgumentParser(
        description="Detect JPEG start and end markers in a file."
    )

    parser.add_argument(
        "file",
        help="Path to the JPEG file to inspect"
    )

    args = parser.parse_args()
    inspect_jpeg(args.file)


if __name__ == "__main__":
    main()
