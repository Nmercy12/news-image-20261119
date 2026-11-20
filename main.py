#!/usr/bin/env python3
"""Ship the pre-rendered entry.png to the final output directory.

Standard library only. The image file next to this program is the entire
entry; this script copies it to $MAKEFUN_OUTPUT_DIR/entry.png (default
/output) and verifies the written file.
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from typing import NoReturn

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
OUTPUT_FILENAME = "entry.png"


def fail(message: str) -> NoReturn:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    source_path = Path(__file__).resolve().parent / OUTPUT_FILENAME
    if not source_path.is_file():
        fail(f"source image not found at {source_path}")

    output_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")
    destination_path = output_dir / OUTPUT_FILENAME

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        fail(f"could not create output directory {output_dir}: {exc}")

    source_size = source_path.stat().st_size
    if source_size <= 0:
        fail(f"source image is empty: {source_path}")

    try:
        shutil.copyfile(source_path, destination_path)
    except OSError as exc:
        fail(f"could not copy {source_path} to {destination_path}: {exc}")

    destination_size = destination_path.stat().st_size
    if destination_size <= 0:
        fail(f"copied image is empty: {destination_path}")

    with destination_path.open("rb") as handle:
        header = handle.read(len(PNG_MAGIC))
    if header != PNG_MAGIC:
        fail(f"copied image is not a PNG (magic bytes: {header!r})")

    with source_path.open("rb") as src_handle, destination_path.open("rb") as dst_handle:
        while True:
            src_chunk = src_handle.read(1 << 20)
            dst_chunk = dst_handle.read(1 << 20)
            if src_chunk != dst_chunk:
                fail(
                    "copied image does not match the source byte-for-byte: "
                    f"{destination_path} != {source_path}"
                )
            if not src_chunk:
                break

    print(f"source: {source_path}")
    print(f"destination: {destination_path}")
    print(f"bytes: {destination_size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
