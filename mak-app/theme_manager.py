# SPDX-License-Identifier: GPL-3.0-or-later
# Mak Theme Manager: Global Theme Synchronizer across Shell, GTK 2/3/4, and Flatpak

import os
import subprocess
import shutil

THEMES = {
    "dark": {
        "id": "dark",
        "name": "macOS Dark (Graphite)",
        "theme_name": ">>>Mac-Dark-solid-purple",
        "color_scheme": "prefer-dark",
        "icon_theme": "MacTahoe-purple-dark",
        "cursor_theme": "MacTahoe-dark",
        "is_dark": True,
        "dock_pill_color": "rgba(42, 42, 50, 0.40)",
        "dock_border_color": "rgba(255, 255, 255, 0.28)",
        "window_border_color": "(1.0, 1.0, 1.0, 0.18)",
        "description": "Refined macOS dark mode with sleek Sonoma graphite windows (#282828) and purple accents."
    },
    "amoled": {
        "id": "amoled",
        "name": "macOS AMOLED Dark (Deep Midnight)",
        "theme_name": ">>>Mac-Dark-Amoled-purple",
        "color_scheme": "prefer-dark",
        "icon_theme": "MacTahoe-purple-dark",
        "cursor_theme": "MacTahoe-dark",
        "is_dark": True,
        "dock_pill_color": "rgba(10, 10, 12, 0.60)",
        "dock_border_color": "rgba(255, 255, 255, 0.16)",
        "window_border_color": "(1.0, 1.0, 1.0, 0.14)",
        "description": "True pitch black OLED Midnight (#000000) with ultra-high contrast and deep obsidian surfaces."
    },
    "light": {
        "id": "light",
        "name": "macOS Light (Crisp Apple)",
        "theme_name": ">>>Mac-Light-solid-purple",
        "color_scheme": "prefer-light",
        "icon_theme": "MacTahoe-purple-light",
        "cursor_theme": "MacTahoe-light",
        "is_dark": False,
        "dock_pill_color": "rgba(255, 255, 255, 0.42)",
        "dock_border_color": "rgba(255, 255, 255, 0.65)",
        "window_border_color": "(0.0, 0.0, 0.0, 0.12)",
        "description": "Clean, luminous macOS light mode with subtle borders and smooth hover states."
    }
}

GRAPHITE_PALETTE_OVERRIDE = """
/* ── Mak macOS Sonoma Graphite Frosted Palette ────────────────────────────── */
@define-color window_bg_color #242426;
@define-color window_fg_color #f5f5f7;
@define-color view_bg_color #1e1e20;
@define-color view_fg_color #f5f5f7;
@define-color headerbar_bg_color #2c2c2e;
@define-color headerbar_fg_color #ffffff;
@define-color headerbar_border_color rgba(255, 255, 255, 0.12);
@define-color sidebar_bg_color #1e1e20;
@define-color sidebar_fg_color #f5f5f7;
@define-color secondary_sidebar_bg_color #1a1a1c;
@define-color card_bg_color #2c2c2e;
@define-color card_fg_color #f5f5f7;
@define-color dialog_bg_color #28282a;
@define-color dialog_fg_color #f5f5f7;
@define-color popover_bg_color #2c2c2e;
@define-color popover_fg_color #f5f5f7;
@define-color placeholder_text_color rgba(255, 255, 255, 0.45);
"""

AMOLED_PALETTE_OVERRIDE = """
/* ── Mak macOS AMOLED Pitch Black Obsidian Palette ────────────────────────── */
@define-color window_bg_color #000000;
@define-color window_fg_color #ffffff;
@define-color view_bg_color #000000;
@define-color view_fg_color #ffffff;
@define-color headerbar_bg_color #08080a;
@define-color headerbar_fg_color #ffffff;
@define-color headerbar_border_color rgba(255, 255, 255, 0.12);
@define-color sidebar_bg_color #000000;
@define-color sidebar_fg_color #ffffff;
@define-color secondary_sidebar_bg_color #000000;
@define-color card_bg_color #121214;
@define-color card_fg_color #ffffff;
@define-color dialog_bg_color #0a0a0c;
@define-color dialog_fg_color #ffffff;
@define-color popover_bg_color #0e0e10;
@define-color popover_fg_color #ffffff;
@define-color placeholder_text_color rgba(255, 255, 255, 0.45);
"""

LIGHT_PALETTE_OVERRIDE = """
/* ── Mak macOS Crisp Apple Light Palette ─────────────────────────────────── */
@define-color window_bg_color #f5f5f7;
@define-color window_fg_color #1d1d1f;
@define-color view_bg_color #ffffff;
@define-color view_fg_color #1d1d1f;
@define-color headerbar_bg_color #ebebef;
@define-color headerbar_fg_color #1d1d1f;
@define-color headerbar_border_color rgba(0, 0, 0, 0.12);
@define-color sidebar_bg_color #e8e8ed;
@define-color sidebar_fg_color #1d1d1f;
@define-color secondary_sidebar_bg_color #e2e2e7;
@define-color card_bg_color #ffffff;
@define-color card_fg_color #1d1d1f;
@define-color dialog_bg_color #f5f5f7;
@define-color dialog_fg_color #1d1d1f;
@define-color popover_bg_color #ffffff;
@define-color popover_fg_color #1d1d1f;
@define-color placeholder_text_color rgba(0, 0, 0, 0.45);
"""

TRAFFIC_LIGHTS_OVERRIDE = """
/* ── Mak Clean macOS Traffic Light Button Controls ────────────────────────── */
windowcontrols,
headerbar windowcontrols {
    border: none !important;
    background: none !important;
    background-color: transparent !important;
    box-shadow: none !important;
}

windowcontrols button,
windowcontrols button:hover,
windowcontrols button:active,
windowcontrols button:checked,
windowcontrols button:focus,
headerbar button.titlebutton,
headerbar button.titlebutton:hover,
headerbar button.titlebutton:active,
headerbar button.titlebutton:focus,
headerbar windowcontrols button,
headerbar windowcontrols button:hover,
headerbar windowcontrols button:active,
headerbar windowcontrols button:focus {
    background: none !important;
    background-color: transparent !important;
    background-image: none !important;
    box-shadow: none !important;
    border: none !important;
    outline: none !important;
    outline-style: none !important;
    min-width: 14px;
    min-height: 14px;
    padding: 0;
    margin: 0 3px;
    border-radius: 9999px;
    -gtk-icon-shadow: none !important;
}
"""

HOME = os.path.expanduser("~")
THEMES_DIR = os.path.join(HOME, ".themes")
GTK4_CONFIG = os.path.join(HOME, ".config", "gtk-4.0")
GTK3_CONFIG = os.path.join(HOME, ".config", "gtk-3.0")
GTK2_RC = os.path.join(HOME, ".gtkrc-2.0")

def get_current_theme():
    try:
        res = subprocess.run(["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"],
                             capture_output=True, text=True, check=True)
        current = res.stdout.strip().strip("'\"")
        for key, val in THEMES.items():
            if val["theme_name"] == current:
                return key
        if "amoled" in current.lower():
            return "amoled"
        if "light" in current.lower():
            return "light"
        return "dark"
    except Exception:
        return "dark"

def apply_global_theme(theme_key):
    """
    Applies the chosen theme globally across:
    1. GNOME Desktop Interface (gtk-theme, color-scheme)
    2. GNOME Shell User Theme extension
    3. GTK 4 / Libadwaita config
    4. GTK 3 config
    5. GTK 2 (~/.gtkrc-2.0)
    6. Flatpak overrides
    """
    if theme_key not in THEMES:
        theme_key = "dark"

    theme_info = THEMES[theme_key]
    theme_name = theme_info["theme_name"]
    color_scheme = theme_info["color_scheme"]
    icon_theme = theme_info.get("icon_theme", "MacTahoe-purple-dark")
    cursor_theme = theme_info.get("cursor_theme", "MacTahoe-dark")
    is_dark = theme_info["is_dark"]
    source_dir = os.path.join(THEMES_DIR, theme_name)

    log = []

    # 1. GNOME Desktop Interface GSettings
    try:
        subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "gtk-theme", theme_name], check=True)
        subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "color-scheme", color_scheme], check=True)
        subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "icon-theme", icon_theme], check=True)
        subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "cursor-theme", cursor_theme], check=True)
        try:
            subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "accent-color", "purple"], check=True)
        except Exception:
            pass
        log.append(f"Set GNOME interface gtk-theme to '{theme_name}', color-scheme to '{color_scheme}', icon-theme to '{icon_theme}', and cursor to '{cursor_theme}'.")
    except Exception as e:
        log.append(f"Error setting GNOME interface: {e}")

    # 2. GNOME Shell Theme
    try:
        subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.user-theme", "name", theme_name], check=True)
        log.append(f"Set GNOME Shell theme to '{theme_name}'.")
    except Exception as e:
        log.append(f"Error setting Shell theme: {e}")

    # 3. GTK 4 / Libadwaita Configuration
    try:
        os.makedirs(GTK4_CONFIG, exist_ok=True)
        src_gtk4 = os.path.join(source_dir, "gtk-4.0")
        palette_override = GRAPHITE_PALETTE_OVERRIDE if theme_key == "dark" else (
            AMOLED_PALETTE_OVERRIDE if theme_key == "amoled" else LIGHT_PALETTE_OVERRIDE
        )

        if os.path.exists(src_gtk4):
            # Copy gtk.css and gtk-dark.css, appending clean traffic light overrides and exact palette
            for css_file in ["gtk.css", "gtk-dark.css"]:
                src_css = os.path.join(src_gtk4, css_file)
                dst_css = os.path.join(GTK4_CONFIG, css_file)
                if os.path.exists(src_css):
                    shutil.copyfile(src_css, dst_css)
                    with open(dst_css, "a", encoding="utf-8") as f:
                        f.write(palette_override)
                        f.write(TRAFFIC_LIGHTS_OVERRIDE)

            # Update symlinks for assets and windows-assets
            for asset_folder in ["assets", "windows-assets"]:
                dst_asset = os.path.join(GTK4_CONFIG, asset_folder)
                src_asset = os.path.join(src_gtk4, asset_folder)
                if os.path.islink(dst_asset) or os.path.exists(dst_asset):
                    try: os.unlink(dst_asset)
                    except: pass
                if os.path.exists(src_asset):
                    os.symlink(src_asset, dst_asset)

            # settings.ini
            gtk4_ini = os.path.join(GTK4_CONFIG, "settings.ini")
            with open(gtk4_ini, "w", encoding="utf-8") as f:
                f.write(
                    f"[Settings]\n"
                    f"gtk-application-prefer-dark-theme={1 if is_dark else 0}\n"
                    f"gtk-theme-name={theme_name}\n"
                    f"gtk-icon-theme-name={icon_theme}\n"
                    f"gtk-cursor-theme-name={cursor_theme}\n"
                )

            log.append("Synchronized GTK 4 / Libadwaita configuration and assets.")
    except Exception as e:
        log.append(f"Error syncing GTK 4: {e}")

    # 4. GTK 3 Configuration
    try:
        os.makedirs(GTK3_CONFIG, exist_ok=True)
        src_gtk3 = os.path.join(source_dir, "gtk-3.0")
        if os.path.exists(src_gtk3):
            for css_file in ["gtk.css", "gtk-dark.css"]:
                src_css = os.path.join(src_gtk3, css_file)
                dst_css = os.path.join(GTK3_CONFIG, css_file)
                if os.path.exists(src_css):
                    shutil.copyfile(src_css, dst_css)
                    with open(dst_css, "a", encoding="utf-8") as f:
                        f.write(palette_override)
                        f.write(TRAFFIC_LIGHTS_OVERRIDE)

            # Update symlinks for assets and windows-assets for GTK 3
            for asset_folder in ["assets", "windows-assets"]:
                dst_asset = os.path.join(GTK3_CONFIG, asset_folder)
                src_asset = os.path.join(src_gtk3, asset_folder)
                if os.path.islink(dst_asset) or os.path.exists(dst_asset):
                    try: os.unlink(dst_asset)
                    except: pass
                if os.path.exists(src_asset):
                    os.symlink(src_asset, dst_asset)

        # Update settings.ini for GTK 3
        gtk3_ini = os.path.join(GTK3_CONFIG, "settings.ini")
        lines = []
        if os.path.exists(gtk3_ini):
            with open(gtk3_ini, "r", encoding="utf-8") as f:
                lines = f.readlines()
        
        new_lines = []
        has_theme = False
        has_dark = False
        has_icon = False
        has_cursor = False
        for line in lines:
            if line.startswith("gtk-theme-name="):
                new_lines.append(f"gtk-theme-name={theme_name}\n")
                has_theme = True
            elif line.startswith("gtk-application-prefer-dark-theme="):
                new_lines.append(f"gtk-application-prefer-dark-theme={1 if is_dark else 0}\n")
                has_dark = True
            elif line.startswith("gtk-icon-theme-name="):
                new_lines.append(f"gtk-icon-theme-name={icon_theme}\n")
                has_icon = True
            elif line.startswith("gtk-cursor-theme-name="):
                new_lines.append(f"gtk-cursor-theme-name={cursor_theme}\n")
                has_cursor = True
            else:
                new_lines.append(line)

        if not has_theme:
            new_lines.append(f"gtk-theme-name={theme_name}\n")
        if not has_dark:
            new_lines.append(f"gtk-application-prefer-dark-theme={1 if is_dark else 0}\n")
        if not has_icon:
            new_lines.append(f"gtk-icon-theme-name={icon_theme}\n")
        if not has_cursor:
            new_lines.append(f"gtk-cursor-theme-name={cursor_theme}\n")

        with open(gtk3_ini, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        log.append("Synchronized GTK 3 settings.ini and stylesheets.")
    except Exception as e:
        log.append(f"Error syncing GTK 3: {e}")

    # 5. GTK 2 Configuration (~/.gtkrc-2.0)
    try:
        gtk2_content = ""
        if os.path.exists(GTK2_RC):
            with open(GTK2_RC, "r", encoding="utf-8") as f:
                gtk2_content = f.read()

        import re
        if re.search(r'gtk-theme-name\s*=\s*".*?"', gtk2_content):
            gtk2_content = re.sub(r'gtk-theme-name\s*=\s*".*?"', f'gtk-theme-name="{theme_name}"', gtk2_content)
        else:
            gtk2_content = f'gtk-theme-name="{theme_name}"\n' + gtk2_content

        if re.search(r'gtk-icon-theme-name\s*=\s*".*?"', gtk2_content):
            gtk2_content = re.sub(r'gtk-icon-theme-name\s*=\s*".*?"', f'gtk-icon-theme-name="{icon_theme}"', gtk2_content)
        else:
            gtk2_content += f'\ngtk-icon-theme-name="{icon_theme}"\n'

        if re.search(r'gtk-cursor-theme-name\s*=\s*".*?"', gtk2_content):
            gtk2_content = re.sub(r'gtk-cursor-theme-name\s*=\s*".*?"', f'gtk-cursor-theme-name="{cursor_theme}"', gtk2_content)
        else:
            gtk2_content += f'\ngtk-cursor-theme-name="{cursor_theme}"\n'

        with open(GTK2_RC, "w", encoding="utf-8") as f:
            f.write(gtk2_content)

        log.append("Synchronized GTK 2 configuration (~/.gtkrc-2.0).")
    except Exception as e:
        log.append(f"Error syncing GTK 2: {e}")

    # 6. Flatpak Overrides
    try:
        if shutil.which("flatpak"):
            subprocess.run([
                "flatpak", "override", "--user",
                f"--filesystem={THEMES_DIR}:ro",
                f"--filesystem={GTK4_CONFIG}:ro",
                f"--filesystem={GTK3_CONFIG}:ro",
                f"--env=GTK_THEME={theme_name}",
            ], check=True, capture_output=True)
            log.append("Applied Flatpak theme environment overrides.")
    except Exception as e:
        log.append(f"Note on Flatpak overrides: {e}")

    # 7. Aqua Dock Pro and Mak Dock Colors
    try:
        dock_pill = theme_info.get("dock_pill_color", "rgba(42, 42, 50, 0.40)")
        dock_border = theme_info.get("dock_border_color", "rgba(255, 255, 255, 0.28)")
        subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.aqua-dock-pro", "pill-color", dock_pill], check=False)
        subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.aqua-dock-pro", "border-color", dock_border], check=False)
        subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.mak", "pill-color", dock_pill], check=False)
        subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.mak", "border-color", dock_border], check=False)
        log.append(f"Updated dock pill color to '{dock_pill}' and border to '{dock_border}'.")
    except Exception as e:
        log.append(f"Error updating dock colors: {e}")

    # 8. Rounded Window Corners Border Highlight
    try:
        w_border = theme_info.get("window_border_color", "(1.0, 1.0, 1.0, 0.16)")
        new_val = f"{{'padding': <{{'left': uint32 0, 'right': 0, 'top': 0, 'bottom': 0}}>, 'keepRoundedCorners': <{{'maximized': true, 'fullscreen': true}}>, 'borderRadius': <uint32 12>, 'smoothing': <0.0>, 'borderColor': <{w_border}>, 'enabled': <true>}}"
        subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.rounded-window-corners-reborn", "global-rounded-corner-settings", new_val], check=False)
        subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.rounded-window-corners-reborn", "border-width", "1"], check=False)
        subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.rounded-window-corners-reborn", "skip-libadwaita-app", "true"], check=False)
        subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.rounded-window-corners-reborn", "skip-libhandy-app", "true"], check=False)
        log.append(f"Updated window corner settings (radius 12, smoothing 0, border {w_border}, skip-libadwaita true).")
    except Exception as e:
        log.append(f"Error updating window corners border: {e}")

    return {
        "success": True,
        "theme": theme_name,
        "log": log
    }

if __name__ == "__main__":
    import sys
    t = sys.argv[1] if len(sys.argv) > 1 else "dark"
    res = apply_global_theme(t)
    print(res)
