#!/usr/bin/env python3
"""
Pixel Difference & Regression Checker
Compares two PNG screenshots, reports diff metrics, and outputs a visual diff map.
"""

import sys
import os
import argparse
from PIL import Image, ImageChops

def compare_images(baseline_path, current_path, diff_out=None, threshold=5):
    if not os.path.exists(baseline_path):
        print(f"[Diff] Error: Baseline {baseline_path} does not exist", file=sys.stderr)
        return {"error": "Missing baseline", "diff_pixels": -1}
    if not os.path.exists(current_path):
        print(f"[Diff] Error: Current {current_path} does not exist", file=sys.stderr)
        return {"error": "Missing current", "diff_pixels": -1}

    img1 = Image.open(baseline_path).convert("RGBA")
    img2 = Image.open(current_path).convert("RGBA")

    # Match sizes
    w = max(img1.size[0], img2.size[0])
    h = max(img1.size[1], img2.size[1])

    canvas1 = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    canvas2 = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    canvas1.paste(img1, (0, 0))
    canvas2.paste(img2, (0, 0))

    pix1 = canvas1.load()
    pix2 = canvas2.load()

    diff_map = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    diff_pix = diff_map.load()

    diff_count = 0
    total_pixels = w * h

    for y in range(h):
        for x in range(w):
            p1 = pix1[x, y]
            p2 = pix2[x, y]
            delta = max(abs(p1[0] - p2[0]), abs(p1[1] - p2[1]), abs(p1[2] - p2[2]), abs(p1[3] - p2[3]))
            if delta > threshold:
                diff_count += 1
                diff_pix[x, y] = (255, 0, 0, 255) # Red highlight for diff
            else:
                # Faint grayscale of original
                g = (p1[0] + p1[1] + p1[2]) // 6
                diff_pix[x, y] = (g, g, g, 255)

    diff_pct = (diff_count / total_pixels) * 100.0

    if diff_out:
        os.makedirs(os.path.dirname(os.path.abspath(diff_out)), exist_ok=True)
        diff_map.save(diff_out)

    return {
        "baseline": baseline_path,
        "current": current_path,
        "w": w,
        "h": h,
        "total_pixels": total_pixels,
        "diff_pixels": diff_count,
        "diff_pct": diff_pct,
        "identical": diff_count == 0
    }

def main():
    parser = argparse.ArgumentParser(description="Compare two images for pixel regression")
    parser.add_argument("baseline", help="Baseline image path")
    parser.add_argument("current", help="Current image path")
    parser.add_argument("--diff", help="Output diff image path")
    parser.add_argument("--threshold", type=int, default=5, help="Color channel delta threshold")
    args = parser.parse_args()

    res = compare_images(args.baseline, args.current, args.diff, args.threshold)
    print(f"[Diff] Result: {res['diff_pixels']} / {res['total_pixels']} pixels changed ({res['diff_pct']:.2f}%)")
    if not res["identical"] and args.diff:
        print(f"[Diff] Diff map saved to {args.diff}")

if __name__ == "__main__":
    main()
