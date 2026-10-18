#!/usr/bin/env python3
"""
scripts/unswirl.py

Restores an image affected by an elliptical swirl distortion using inverse
geometric pixel remapping and bilinear interpolation.

Algorithm:
1. Normalize horizontal and vertical coordinates separately around the image center.
2. Convert normalized Cartesian coordinates (nx, ny) to polar coordinates (radius, theta).
3. Compute sample angle using the swirl transformation model:
     theta_sample = theta + radians(angle) * max(1 - radius, 0)^2
4. Map sampled coordinates back into discrete image coordinates.
5. Perform bilinear interpolation to sample continuous pixel intensities.
"""

import argparse
import math
from pathlib import Path
import numpy as np
from PIL import Image


def unswirl(input_path: str, output_path: str, angle: float = 1000.0) -> None:
    src_file = Path(input_path)
    if not src_file.is_file():
        raise FileNotFoundError(f"Input image not found: '{input_path}'")

    img = Image.open(src_file).convert("RGBA")
    arr = np.array(img, dtype=np.float32)
    height, width, _ = arr.shape

    # Centers and semi-axes for elliptical normalization
    cx = (width - 1) / 2.0
    cy = (height - 1) / 2.0
    rx = width / 2.0
    ry = height / 2.0

    # Grid of coordinates
    y_coords, x_coords = np.indices((height, width), dtype=np.float32)
    nx = (x_coords - cx) / rx
    ny = (y_coords - cy) / ry

    # Convert to polar coordinates
    radius = np.hypot(nx, ny)
    theta = np.arctan2(ny, nx)

    # Swirl distortion inverse mapping
    # theta_sample = theta + radians(angle) * max(1 - radius, 0)^2
    swirl_factor = np.maximum(1.0 - radius, 0.0) ** 2
    theta_sample = theta + math.radians(angle) * swirl_factor

    # Map back to continuous image coordinates
    x_sample = cx + rx * (radius * np.cos(theta_sample))
    y_sample = cy + ry * (radius * np.sin(theta_sample))

    # Bilinear interpolation
    x0 = np.floor(x_sample).astype(np.int32)
    x1 = x0 + 1
    y0 = np.floor(y_sample).astype(np.int32)
    y1 = y0 + 1

    wa = (x1 - x_sample) * (y1 - y_sample)
    wb = (x_sample - x0) * (y1 - y_sample)
    wc = (x1 - x_sample) * (y_sample - y0)
    wd = (x_sample - x0) * (y_sample - y0)

    x0_clamped = np.clip(x0, 0, width - 1)
    x1_clamped = np.clip(x1, 0, width - 1)
    y0_clamped = np.clip(y0, 0, height - 1)
    y1_clamped = np.clip(y1, 0, height - 1)

    restored = (
        wa[..., None] * arr[y0_clamped, x0_clamped]
        + wb[..., None] * arr[y0_clamped, x1_clamped]
        + wc[..., None] * arr[y1_clamped, x0_clamped]
        + wd[..., None] * arr[y1_clamped, x1_clamped]
    )

    # Mask valid bounding area
    valid_mask = (
        (x_sample >= 0) & (x_sample <= width - 1) &
        (y_sample >= 0) & (y_sample <= height - 1)
    )
    restored[~valid_mask] = 0

    out_img = Image.fromarray(np.clip(restored, 0, 255).astype(np.uint8), mode="RGBA")
    dest_file = Path(output_path)
    dest_file.parent.mkdir(parents=True, exist_ok=True)
    out_img.save(dest_file)
    print(f"[+] Successfully unswirled '{input_path}' -> '{output_path}' with angle {angle}°")


def main():
    parser = argparse.ArgumentParser(
        description="Restore an elliptically swirled image using geometric coordinate inversion."
    )
    parser.add_argument("input", help="Path to input distorted image")
    parser.add_argument("output", help="Path to save output restored image")
    parser.add_argument(
        "--angle",
        type=float,
        default=1000.0,
        help="Swirl unwinding angle in degrees (default: 1000.0)",
    )

    args = parser.parse_args()
    unswirl(args.input, args.output, args.angle)


if __name__ == "__main__":
    main()
