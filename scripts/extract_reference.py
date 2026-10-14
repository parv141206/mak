#!/usr/bin/env python3
import os
import re
import json
from PIL import Image, ImageDraw, ImageFont

APPLE_DIR = "apple"
CONTACT_DIR = "docs/fidelity/contact"
INDEX_MD = "apple/INDEX.md"
SPEC_MD = "docs/fidelity/SPEC.md"
TOKENS_JSON = "docs/fidelity/tokens.json"

os.makedirs(CONTACT_DIR, exist_ok=True)
os.makedirs("docs/fidelity", exist_ok=True)

folders = sorted([f for f in os.listdir(APPLE_DIR) if os.path.isdir(os.path.join(APPLE_DIR, f))])

index_entries = []
spec_data = {}
all_tokens = {
    "_meta": {
        "source": "apple/ UI kit reference PNGs (Figma export)",
        "scale": "1x (logical CSS pixels)",
        "toolkits": ["GTK 4", "GTK 3", "GTK 2", "GNOME Shell"]
    },
    "tokens": {}
}

print(f"Processing {len(folders)} folders...")

for folder in folders:
    fpath = os.path.join(APPLE_DIR, folder)
    all_files = sorted(os.listdir(fpath))
    png_files = [f for f in all_files if f.lower().endswith(".png")]
    
    # Categorize files
    composites = []
    layers = []
    for f in png_files:
        if "__" in f or any(w in f for w in ["alert", "dialog", "window", "group_box", "button", "swatch", "popover", "sidebar", "menu"]):
            composites.append(f)
        else:
            layers.append(f)
            
    # Sample file dimensions
    dims = []
    for f in png_files[:10]:
        try:
            with Image.open(os.path.join(fpath, f)) as im:
                dims.append(f"{im.size[0]}x{im.size[1]}")
        except Exception:
            pass
    dim_summary = ", ".join(sorted(set(dims))[:4])
    
    # Check naming patterns
    patterns = set()
    has_light = False
    has_dark = False
    has_active = False
    has_state = False
    for f in png_files:
        if "light" in f.lower(): has_light = True
        if "dark" in f.lower(): has_dark = True
        if "active" in f.lower(): has_active = True
        if "state" in f.lower(): has_state = True
        parts = re.findall(r'([a-zA-Z0-9_]+)__', f)
        for p in parts: patterns.add(p)

    mode_info = []
    if has_light: mode_info.append("light")
    if has_dark: mode_info.append("dark")
    if not mode_info: mode_info.append("neutral/inherits")

    index_entries.append({
        "folder": folder,
        "count": len(png_files),
        "scale": "1x",
        "modes": ", ".join(mode_info),
        "sample_dims": dim_summary,
        "patterns": sorted(list(patterns))[:5],
        "composites_count": len(composites),
        "layers_count": len(layers)
    })

    # Generate a contact sheet of top representative images
    # Select up to 16 representative composites or files
    selected_for_sheet = composites[:16] if len(composites) >= 4 else png_files[:16]
    if selected_for_sheet:
        sheet_imgs = []
        for sf in selected_for_sheet:
            try:
                im = Image.open(os.path.join(fpath, sf)).convert("RGBA")
                # Thumbnail to max 240x160 preserving aspect ratio
                im.thumbnail((240, 160), Image.Resampling.LANCZOS)
                sheet_imgs.append((sf, im))
            except Exception:
                pass
        
        if sheet_imgs:
            cols = min(4, len(sheet_imgs))
            rows = (len(sheet_imgs) + cols - 1) // cols
            cell_w, cell_h = 260, 190
            sheet = Image.new("RGBA", (cols * cell_w, rows * cell_h), (240, 240, 245, 255))
            draw = ImageDraw.Draw(sheet)
            
            for idx, (sname, simg) in enumerate(sheet_imgs):
                r = idx // cols
                c = idx % cols
                x = c * cell_w + (cell_w - simg.size[0]) // 2
                y = r * cell_h + 20 + (cell_h - 40 - simg.size[1]) // 2
                sheet.paste(simg, (x, y), simg)
                # Label
                lbl = sname if len(sname) <= 30 else sname[:27] + "..."
                draw.text((c * cell_w + 10, r * cell_h + cell_h - 18), lbl, fill=(40, 40, 45, 255))
            
            safe_name = folder.replace(" ", "_")
            sheet_path = os.path.join(CONTACT_DIR, f"{safe_name}_contact.png")
            sheet.save(sheet_path)

print(f"Generated contact sheets for {len(folders)} folders.")

# Write apple/INDEX.md
with open(INDEX_MD, "w", encoding="utf-8") as f:
    f.write("# Apple UI Kit Reference Index\n\n")
    f.write("Extracted directly from Apple's official macOS UI kit (Figma).\n")
    f.write("Scale: **1x** (logical CSS pixels). All coordinates, heights, radii, and paddings are 1:1 with GTK CSS px values.\n\n")
    f.write("| Component Folder | File Count | Modes | PNG Scale | Typical Dimensions | Contact Sheet |\n")
    f.write("|---|---|---|---|---|---|\n")
    for e in index_entries:
        safe_name = e["folder"].replace(" ", "_")
        contact_link = f"[Contact Sheet](../docs/fidelity/contact/{safe_name}_contact.png)"
        f.write(f"| `{e['folder']}` | {e['count']} | {e['modes']} | {e['scale']} | {e['sample_dims']} | {contact_link} |\n")

print(f"Wrote {INDEX_MD}.")
