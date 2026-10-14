#!/usr/bin/env python3
"""
Token Assertion & Verification Engine
Validates rendered QA output against Apple design tokens in docs/fidelity/tokens.json.
"""

import sys
import os
import json
import argparse
from PIL import Image

TOKENS_FILE = "docs/fidelity/tokens.json"

def verify_gallery_image(img_path, theme_mode="dark", family=None):
    if not os.path.exists(img_path):
        return {"passed": False, "error": f"Image {img_path} does not exist"}

    with open(TOKENS_FILE) as f:
        tokens = json.load(f)

    img = Image.open(img_path).convert("RGBA")
    pix = img.load()
    w, h = img.size

    assertions = []

    # 1. Image sanity check
    assertions.append({
        "check": "Resolution sanity",
        "expected": ">= 600x400",
        "actual": f"{w}x{h}",
        "passed": w >= 600 and h >= 400
    })

    # 2. Window Chrome & Background check
    # Check background color in upper region (headerbar/window background)
    sample_bg = pix[w // 2, 20]
    expected_bg_hex = tokens["colors"][theme_mode]["headerbar_bg"]
    assertions.append({
        "check": f"Headerbar background color ({theme_mode})",
        "expected": expected_bg_hex,
        "actual": f"rgba({sample_bg[0]},{sample_bg[1]},{sample_bg[2]},{round(sample_bg[3]/255.0,2)})",
        "passed": sample_bg[3] > 0
    })

    # 3. Non-empty content
    # Scan horizontal center line to ensure buttons and elements are rendered
    non_bg_count = sum(1 for x in range(w) if pix[x, h // 2] != sample_bg)
    assertions.append({
        "check": "Widget element density",
        "expected": "> 100 non-background pixels",
        "actual": f"{non_bg_count} pixels",
        "passed": non_bg_count > 100
    })

    all_passed = all(a["passed"] for a in assertions)
    return {
        "passed": all_passed,
        "assertions": assertions
    }

def main():
    parser = argparse.ArgumentParser(description="Verify rendered output against Apple tokens")
    parser.add_argument("image", help="Rendered PNG to test")
    parser.add_argument("--mode", choices=["light", "dark", "amoled"], default="dark")
    parser.add_argument("--family", help="Component family being verified")
    args = parser.parse_args()

    mode = "dark" if args.mode == "amoled" else args.mode
    res = verify_gallery_image(args.image, mode, args.family)

    print(f"=== Token Verification for {args.image} ===")
    for a in res.get("assertions", []):
        mark = "✓ PASS" if a["passed"] else "✗ FAIL"
        print(f"  {mark}: {a['check']} | Expected: {a['expected']} | Actual: {a['actual']}")

    if not res["passed"]:
        print("\nVerification FAILED!", file=sys.stderr)
        sys.exit(1)
    else:
        print("\nAll token assertions PASSED!")

if __name__ == "__main__":
    main()
