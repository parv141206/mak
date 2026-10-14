#!/usr/bin/env python3
"""
Capture Baseline Screenshots for all 6 themes x (GTK4, GTK3) into qa/baseline/
"""

import os
import subprocess
import sys

THEMES = [
    ("dark", ">>>Mac-Dark-solid-purple", "dark"),
    ("dark-glassy", ">>>Mac-Dark-glassy-purple", "dark"),
    ("amoled", ">>>Mac-Dark-Amoled-purple", "dark"),
    ("amoled-glassy", ">>>Mac-Dark-Amoled-glassy-purple", "dark"),
    ("light", ">>>Mac-Light-solid-purple", "light"),
    ("light-glassy", ">>>Mac-Light-glassy-purple", "light"),
]

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASELINE_DIR = os.path.join(REPO_ROOT, "qa", "baseline")
os.makedirs(BASELINE_DIR, exist_ok=True)

PYTHON = "/tmp/apple_fidelity_venv/bin/python3"

print("Capturing QA Baselines for 6 themes x (GTK 4, GTK 3)...")

for theme_key, theme_folder, mode in THEMES:
    # GTK 4
    gtk4_css = os.path.join(REPO_ROOT, "themes", theme_folder, "gtk-4.0", "gtk.css")
    out_gtk4 = os.path.join(BASELINE_DIR, f"{theme_key}_gtk4.png")
    if os.path.exists(gtk4_css):
        print(f"  Rendering baseline: {theme_key} (GTK 4)...")
        cmd = [PYTHON, "qa/gallery_gtk4.py", "--css", gtk4_css, "--mode", mode, "--out", out_gtk4]
        res = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"  [ERROR] GTK 4 {theme_key}: {res.stderr}")

    # GTK 3
    gtk3_css = os.path.join(REPO_ROOT, "themes", theme_folder, "gtk-3.0", "gtk.css")
    out_gtk3 = os.path.join(BASELINE_DIR, f"{theme_key}_gtk3.png")
    if os.path.exists(gtk3_css):
        print(f"  Rendering baseline: {theme_key} (GTK 3)...")
        cmd = [PYTHON, "qa/gallery_gtk3.py", "--css", gtk3_css, "--mode", mode, "--out", out_gtk3]
        res = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"  [ERROR] GTK 3 {theme_key}: {res.stderr}")

print("Baselines successfully captured into qa/baseline/.")
