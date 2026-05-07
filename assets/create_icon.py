"""
Generate a simple app_icon.ico programmatically.

Requires only Python stdlib + struct/zlib (no PIL needed).
The icon is a blue PDF document shape at 256x256, 64x64, 48x48, 32x32, 16x16.

Run:
    python assets/create_icon.py
"""
from __future__ import annotations
import os
import struct
import zlib
from pathlib import Path

ICON_PATH = Path(__file__).parent / "app_icon.ico"

# ── Minimal PNG encoder ───────────────────────────────────────────────────────

def _pack_png(width: int, height: int, pixels: list[tuple[int,int,int,int]]) -> bytes:
    """Return a minimal RGBA PNG as bytes."""
    def chunk(name: bytes, data: bytes) -> bytes:
        c = name + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    raw_rows = b""
    for row in range(height):
        raw_rows += b"\x00"
        for col in range(width):
            r, g, b, a = pixels[row * width + col]
            raw_rows += bytes([r, g, b, a])
    compressed = zlib.compress(raw_rows, 9)

    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", compressed)
        + chunk(b"IEND", b"")
    )


def _make_icon_pixels(size: int) -> list[tuple[int,int,int,int]]:
    """Draw a simple PDF document icon at the given pixel size."""
    pix: list[tuple[int,int,int,int]] = []

    # Geometry
    margin = max(1, size // 8)
    doc_x1 = margin
    doc_x2 = size - margin
    doc_y1 = margin
    doc_y2 = size - margin
    fold_size = max(2, size // 6)

    # Colours
    body_fill   = (37, 99, 235, 255)   # blue-600
    fold_fill   = (147, 197, 253, 255) # blue-300
    bg          = (0, 0, 0, 0)        # transparent

    for row in range(size):
        for col in range(size):
            in_doc = (doc_x1 <= col < doc_x2 - fold_size or
                      (doc_x1 <= col < doc_x2 and row >= doc_y1 + fold_size)) and \
                     doc_y1 <= row < doc_y2

            is_fold = (doc_x2 - fold_size <= col < doc_x2 and
                       doc_y1 <= row < doc_y1 + fold_size)

            if is_fold:
                pix.append(fold_fill)
            elif in_doc:
                pix.append(body_fill)
            else:
                pix.append(bg)

    return pix


def _make_ico(sizes: list[int]) -> bytes:
    """Assemble multiple PNG images into a .ico file."""
    images = []
    for size in sizes:
        pixels = _make_icon_pixels(size)
        png = _pack_png(size, size, pixels)
        images.append((size, png))

    # ICO header
    count = len(images)
    header = struct.pack("<HHH", 0, 1, count)

    # Directory entries (each 16 bytes)
    data_offset = 6 + count * 16
    directory = b""
    for size, png in images:
        w = 0 if size >= 256 else size
        h = 0 if size >= 256 else size
        directory += struct.pack("<BBBBHHII", w, h, 0, 0, 1, 32, len(png), data_offset)
        data_offset += len(png)

    image_data = b"".join(png for _, png in images)
    return header + directory + image_data


if __name__ == "__main__":
    ICON_PATH.parent.mkdir(parents=True, exist_ok=True)
    ico_bytes = _make_ico([256, 64, 48, 32, 16])
    ICON_PATH.write_bytes(ico_bytes)
    print(f"Icon written to {ICON_PATH}  ({len(ico_bytes)} bytes)")
