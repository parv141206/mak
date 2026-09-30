#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Mak Monochrome macOS Icon Generator:
# Transforms colored squircle macOS icons (MacTahoe / WhiteSur) into uniform
# Apple Sequoia / iOS 18 tinted monochrome icon themes for both Dark and Light modes.

import os
import sys
import shutil
import subprocess
from pathlib import Path

HOME = os.path.expanduser("~")
ICONS_DIR = os.path.join(HOME, ".local", "share", "icons")

THEMES_TO_CREATE = {
    "Mac-Monochrome-Dark": {
        "name": "macOS Monochrome Dark",
        "comment": "Apple Sequoia / iOS 18 dark monochrome squircle icon theme",
        "bg_color": "#1c1c1e",
        "fg_color": "#ffffff",
        "inherits": "MacTahoe-dark,WhiteSur-dark,Adwaita,hicolor"
    },
    "Mac-Monochrome-Light": {
        "name": "macOS Monochrome Light",
        "comment": "Apple Sequoia / iOS 18 crisp light monochrome squircle icon theme",
        "bg_color": "#f2f2f7",
        "fg_color": "#1d1d1f",
        "inherits": "MacTahoe-light,WhiteSur-light,Adwaita,hicolor"
    }
}

def generate_index_theme(theme_name, info):
    return f"""[Icon Theme]
Name={info['name']}
Comment={info['comment']}
Inherits={info['inherits']}
FollowsColorScheme=true

Directories=apps/scalable,places/scalable,status/scalable

[apps/scalable]
Context=Applications
Size=64
MinSize=16
MaxSize=512
Type=Scalable

[places/scalable]
Context=Places
Size=64
MinSize=16
MaxSize=512
Type=Scalable

[status/scalable]
Context=Status
Size=16
MinSize=16
MaxSize=512
Type=Scalable
"""

def setup_monochrome_themes():
    os.makedirs(ICONS_DIR, exist_ok=True)
    for theme_dir_name, info in THEMES_TO_CREATE.items():
        theme_path = os.path.join(ICONS_DIR, theme_dir_name)
        os.makedirs(os.path.join(theme_path, "apps", "scalable"), exist_ok=True)
        os.makedirs(os.path.join(theme_path, "places", "scalable"), exist_ok=True)
        os.makedirs(os.path.join(theme_path, "status", "scalable"), exist_ok=True)

        index_file = os.path.join(theme_path, "index.theme")
        with open(index_file, "w", encoding="utf-8") as f:
            f.write(generate_index_theme(theme_dir_name, info))
        print(f"Created theme structure: {theme_path}")

if __name__ == "__main__":
    setup_monochrome_themes()
    print("Monochrome macOS icon bases generated successfully.")
