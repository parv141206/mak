#!/usr/bin/env python3
"""
Generate side-by-side visual comparison between Apple reference and rendered GTK output.
"""

import os
import sys
import argparse
from PIL import Image, ImageDraw, ImageFont

def make_side_by_side(ref_path, test_path, out_path, label="Component Comparison"):
    if not os.path.exists(ref_path) or not os.path.exists(test_path):
        print(f"Error: Missing {ref_path} or {test_path}", file=sys.stderr)
        return False

    ref_img = Image.open(ref_path).convert("RGBA")
    test_img = Image.open(test_path).convert("RGBA")

    # Target height
    h = max(ref_img.size[1], test_img.size[1], 150)
    w1, h1 = ref_img.size
    w2, h2 = test_img.size

    # Scale if drastically different
    pad = 20
    header_h = 36
    total_w = w1 + w2 + pad * 3
    total_h = max(h1, h2) + header_h + pad * 2

    canvas = Image.new("RGBA", (total_w, total_h), (30, 30, 34, 255))
    draw = ImageDraw.Draw(canvas)

    # Draw titles
    draw.text((pad, 10), "Apple Figma Reference (1x)", fill=(200, 200, 205, 255))
    draw.text((pad * 2 + w1, 10), "Mak Rendered Output (Staged)", fill=(100, 200, 255, 255))

    # Paste images
    canvas.paste(ref_img, (pad, header_h + pad), ref_img)
    canvas.paste(test_img, (pad * 2 + w1, header_h + pad), test_img)

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    canvas.save(out_path)
    print(f"[Comparison] Saved side-by-side to {out_path}")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("ref", help="Apple reference image")
    parser.add_argument("test", help="Rendered test image")
    parser.add_argument("out", help="Output comparison image")
    args = parser.parse_args()
    make_side_by_side(args.ref, args.test, args.out)
