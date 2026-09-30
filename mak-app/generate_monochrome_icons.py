#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Mak Monochrome macOS Icon Theme Generator
# Transforms 1,390+ macOS squircle application icons and 4,980+ symlinks from MacTahoe
# into native Apple Sequoia / iOS 18 tinted monochrome icon packs:
#   - Mac-Monochrome-Dark: Charcoal/Obsidian squircle with luminous silver glyphs.
#   - Mac-Monochrome-Light: Pearl white squircle with crisp charcoal glyphs.

import os
import sys
import shutil
import time
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

HOME = os.path.expanduser("~")
ICONS_DIR = os.path.join(HOME, ".local", "share", "icons")
SOURCE_THEME = os.path.join(ICONS_DIR, "MacTahoe")

THEMES = {
    "Mac-Monochrome-Dark": {
        "name": "Mac-Monochrome-Dark",
        "display_name": "macOS Monochrome Dark",
        "comment": "macOS Sequoia & iOS 18 dark monochrome squircle icon theme",
        "inherits": "MacTahoe-purple-dark,MacTahoe-dark,WhiteSur-dark,Adwaita,hicolor",
        "mode": "dark",
        "source_base": "MacTahoe-purple-dark",
    },
    "Mac-Monochrome-Light": {
        "name": "Mac-Monochrome-Light",
        "display_name": "macOS Monochrome Light",
        "comment": "macOS Sequoia & iOS 18 crisp light monochrome squircle icon theme",
        "inherits": "MacTahoe-purple-light,MacTahoe-light,WhiteSur-light,Adwaita,hicolor",
        "mode": "light",
        "source_base": "MacTahoe-purple-light",
    }
}

INDEX_THEME_TEMPLATE = """[Icon Theme]
Name={display_name}
Comment={comment}
Inherits={inherits}
FollowsColorScheme=true

Directories=apps/scalable,places/scalable,status/scalable,actions/scalable,devices/scalable,categories/scalable

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

[actions/scalable]
Context=Actions
Size=16
MinSize=16
MaxSize=512
Type=Scalable

[devices/scalable]
Context=Devices
Size=64
MinSize=16
MaxSize=512
Type=Scalable

[categories/scalable]
Context=Categories
Size=64
MinSize=16
MaxSize=512
Type=Scalable
"""

def prepare_theme_directory(theme_key):
    info = THEMES[theme_key]
    dest_theme = os.path.join(ICONS_DIR, info["name"])
    os.makedirs(os.path.join(dest_theme, "apps", "scalable"), exist_ok=True)

    # Link companion directories from matching base theme
    base_theme = os.path.join(ICONS_DIR, info["source_base"])
    for folder in ["places", "status", "actions", "devices", "categories"]:
        src_folder = os.path.join(base_theme, folder)
        dst_folder = os.path.join(dest_theme, folder)
        if not os.path.exists(dst_folder) and not os.path.islink(dst_folder):
            if os.path.exists(src_folder):
                os.symlink(src_folder, dst_folder)

    # Write index.theme
    index_path = os.path.join(dest_theme, "index.theme")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(INDEX_THEME_TEMPLATE.format(
            display_name=info["display_name"],
            comment=info["comment"],
            inherits=info["inherits"]
        ))
    return dest_theme

def convert_single_icon(args):
    src_file, dark_dst, light_dst = args

    # 1. Dark Mode Icon: Charcoal #1c1c1e squircle with luminous #f5f5f7 glyph
    cmd_dark = [
        "magick", "-background", "none", str(src_file),
        "-channel", "RGB", "-colorspace", "Gray", "-negate",
        "+level-colors", "#1c1c1e,#f5f5f7", "+channel",
        f"PNG32:{dark_dst}"
    ]

    # 2. Light Mode Icon: Pearl #ffffff squircle with crisp charcoal #1c1c1e glyph
    cmd_light = [
        "magick", "-background", "none", str(src_file),
        "-channel", "RGB", "-colorspace", "Gray",
        "+level-colors", "#1c1c1e,#ffffff", "+channel",
        f"PNG32:{light_dst}"
    ]

    subprocess.run(cmd_dark, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(cmd_light, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def generate_all_icons():
    src_scalable = os.path.join(SOURCE_THEME, "apps", "scalable")
    if not os.path.exists(src_scalable):
        print(f"Error: Source icons directory '{src_scalable}' does not exist.")
        sys.exit(1)

    print("Initializing Monochrome Theme targets...")
    dark_dir = prepare_theme_directory("Mac-Monochrome-Dark")
    light_dir = prepare_theme_directory("Mac-Monochrome-Light")

    dark_apps = os.path.join(dark_dir, "apps", "scalable")
    light_apps = os.path.join(light_dir, "apps", "scalable")

    src_entries = os.listdir(src_scalable)
    regular_files = []
    symlinks = []

    for name in src_entries:
        full_path = os.path.join(src_scalable, name)
        if os.path.islink(full_path):
            target = os.readlink(full_path)
            symlinks.append((name, target))
        elif name.endswith(".svg"):
            regular_files.append(name)

    print(f"Found {len(regular_files)} unique application SVGs and {len(symlinks)} symlink aliases.")
    tasks = []
    for name in regular_files:
        src_path = os.path.join(src_scalable, name)
        stem = Path(name).stem
        # Generate both .png and link .svg to satisfy any application lookup
        dark_png = os.path.join(dark_apps, f"{stem}.png")
        light_png = os.path.join(light_apps, f"{stem}.png")
        tasks.append((src_path, dark_png, light_png))

    print(f"Transforming {len(tasks)} icons across 16 parallel threads into Dark and Light monochrome...")
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=16) as pool:
        list(pool.map(convert_single_icon, tasks))

    elapsed = time.time() - start_time
    print(f"Rendered {len(tasks) * 2} icons in {elapsed:.1f} seconds ({len(tasks) / elapsed:.1f} icons/sec).")

    print(f"Replicating {len(symlinks)} symlinks to ensure full coverage...")
    for link_name, target in symlinks:
        link_stem = Path(link_name).stem
        target_stem = Path(target).stem

        for app_dir in [dark_apps, light_apps]:
            dst_link_png = os.path.join(app_dir, f"{link_stem}.png")
            dst_link_svg = os.path.join(app_dir, link_name)
            target_png = f"{target_stem}.png"

            if not os.path.exists(dst_link_png) and not os.path.islink(dst_link_png):
                try: os.symlink(target_png, dst_link_png)
                except: pass

            if not os.path.exists(dst_link_svg) and not os.path.islink(dst_link_svg):
                try: os.symlink(target_png, dst_link_svg)
                except: pass

    # Also link .svg to .png for all regular files so apps requesting .svg find the .png
    for name in regular_files:
        stem = Path(name).stem
        for app_dir in [dark_apps, light_apps]:
            svg_alias = os.path.join(app_dir, name)
            if not os.path.exists(svg_alias) and not os.path.islink(svg_alias):
                try: os.symlink(f"{stem}.png", svg_alias)
                except: pass

    # Update icon caches
    print("Building icon theme caches...")
    for theme_dir in [dark_dir, light_dir]:
        subprocess.run(["gtk-update-icon-cache", "-f", "-t", theme_dir],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print("Success! 'Mac-Monochrome-Dark' and 'Mac-Monochrome-Light' are fully generated and ready.")

if __name__ == "__main__":
    generate_all_icons()
