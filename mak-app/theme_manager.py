# SPDX-License-Identifier: GPL-3.0-or-later
# Mak Theme Manager: Global Theme Synchronizer across Shell, GTK 2/3/4, and Flatpak

import os
import subprocess
import shutil

THEMES = {
    "dark": {
        "id": "dark",
        "name": "macOS Dark Solid (Graphite)",
        "theme_name": ">>>Mac-Dark-solid-purple",
        "color_scheme": "prefer-dark",
        "icon_theme": "MacTahoe-dark",
        "cursor_theme": "MacTahoe-dark",
        "is_dark": True,
        "is_glassy": False,
        "dock_pill_color": "rgba(42, 42, 50, 0.40)",
        "dock_border_color": "rgba(255, 255, 255, 0.28)",
        "window_border_color": "rgba(255, 255, 255, 0.18)",
        "description": "Refined solid macOS dark mode with sleek Sonoma graphite windows (#242426) and native desktop accents."
    },
    "dark-glassy": {
        "id": "dark-glassy",
        "name": "macOS Dark Glass (Sonoma Frosted Glass)",
        "theme_name": ">>>Mac-Dark-glassy-purple",
        "color_scheme": "prefer-dark",
        "icon_theme": "MacTahoe-dark",
        "cursor_theme": "MacTahoe-dark",
        "is_dark": True,
        "is_glassy": True,
        "dock_pill_color": "rgba(32, 32, 40, 0.28)",
        "dock_border_color": "rgba(255, 255, 255, 0.22)",
        "window_border_color": "rgba(255, 255, 255, 0.20)",
        "description": "Translucent frosted glass dark mode with translucent windows and vibrant backdrop blur."
    },
    "amoled": {
        "id": "amoled",
        "name": "macOS AMOLED Dark Solid (Pitch Black)",
        "theme_name": ">>>Mac-Dark-Amoled-purple",
        "color_scheme": "prefer-dark",
        "icon_theme": "MacTahoe-dark",
        "cursor_theme": "MacTahoe-dark",
        "is_dark": True,
        "is_glassy": False,
        "dock_pill_color": "rgba(24, 24, 28, 0.50)",
        "dock_border_color": "rgba(255, 255, 255, 0.18)",
        "window_border_color": "rgba(255, 255, 255, 0.16)",
        "description": "Refined obsidian dark mode, a little darker than standard graphite (#18181a) with balanced contrast and crisp native accents."
    },
    "amoled-glassy": {
        "id": "amoled-glassy",
        "name": "macOS AMOLED Glass (Obsidian Translucent)",
        "theme_name": ">>>Mac-Dark-Amoled-glassy-purple",
        "color_scheme": "prefer-dark",
        "icon_theme": "MacTahoe-dark",
        "cursor_theme": "MacTahoe-dark",
        "is_dark": True,
        "is_glassy": True,
        "dock_pill_color": "rgba(20, 20, 24, 0.35)",
        "dock_border_color": "rgba(255, 255, 255, 0.18)",
        "window_border_color": "rgba(255, 255, 255, 0.16)",
        "description": "Translucent deep obsidian glass with rich backdrop blur and native desktop accents."
    },
    "light": {
        "id": "light",
        "name": "macOS Light Solid (Crisp Apple)",
        "theme_name": ">>>Mac-Light-solid-purple",
        "color_scheme": "prefer-light",
        "icon_theme": "MacTahoe-light",
        "cursor_theme": "MacTahoe-light",
        "is_dark": False,
        "is_glassy": False,
        "dock_pill_color": "rgba(255, 255, 255, 0.42)",
        "dock_border_color": "rgba(255, 255, 255, 0.65)",
        "window_border_color": "rgba(0, 0, 0, 0.12)",
        "description": "Clean, luminous solid macOS light mode with subtle borders and crisp typography."
    },
    "light-glassy": {
        "id": "light-glassy",
        "name": "macOS Light Glass (Apple Frosted Glass)",
        "theme_name": ">>>Mac-Light-glassy-purple",
        "color_scheme": "prefer-light",
        "icon_theme": "MacTahoe-light",
        "cursor_theme": "MacTahoe-light",
        "is_dark": False,
        "is_glassy": True,
        "dock_pill_color": "rgba(255, 255, 255, 0.30)",
        "dock_border_color": "rgba(255, 255, 255, 0.55)",
        "window_border_color": "rgba(0, 0, 0, 0.14)",
        "description": "Luminous frosted glass light mode with translucent app windows and rich backdrop blur."
    }
}

GRAPHITE_PALETTE_OVERRIDE = """
/* ── Mak macOS Sonoma Graphite Frosted Palette ────────────────────────────── */
@define-color window_bg_color #242426;
@define-color window_fg_color #f5f5f7;
@define-color view_bg_color #1e1e20;
@define-color view_fg_color #f5f5f7;
@define-color headerbar_bg_color #2c2c2e;
@define-color headerbar_solid_bg #2c2c2e;
@define-color headerbar_fg_color #ffffff;
@define-color headerbar_border_color rgba(255, 255, 255, 0.12);
@define-color sidebar_bg_color #222224;
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

GRAPHITE_GLASSY_PALETTE_OVERRIDE = """
/* ── Mak macOS Sonoma Graphite Glass Frosted Translucent Palette ─────────── */
@define-color window_bg_color rgba(36, 36, 40, 0.72);
@define-color window_fg_color #f5f5f7;
@define-color view_bg_color rgba(28, 28, 32, 0.68);
@define-color view_fg_color #f5f5f7;
@define-color headerbar_bg_color rgba(44, 44, 48, 0.75);
@define-color headerbar_solid_bg #2c2c2e;
@define-color headerbar_fg_color #ffffff;
@define-color headerbar_border_color rgba(255, 255, 255, 0.12);
@define-color sidebar_bg_color rgba(30, 30, 34, 0.65);
@define-color sidebar_fg_color #f5f5f7;
@define-color secondary_sidebar_bg_color rgba(26, 26, 30, 0.60);
@define-color card_bg_color rgba(48, 48, 54, 0.68);
@define-color card_fg_color #f5f5f7;
@define-color dialog_bg_color rgba(40, 40, 46, 0.82);
@define-color dialog_fg_color #f5f5f7;
@define-color popover_bg_color rgba(40, 40, 46, 0.82);
@define-color popover_fg_color #f5f5f7;
@define-color placeholder_text_color rgba(255, 255, 255, 0.45);
"""

AMOLED_PALETTE_OVERRIDE = """
/* ── Mak macOS Deep Obsidian Dark Palette (Sleek Deep Dark, Non-Void) ────────── */
@define-color window_bg_color #18181a;
@define-color window_fg_color #f5f5f7;
@define-color view_bg_color #131315;
@define-color view_fg_color #f5f5f7;
@define-color headerbar_bg_color #1e1e21;
@define-color headerbar_solid_bg #1e1e21;
@define-color headerbar_fg_color #ffffff;
@define-color headerbar_border_color rgba(255, 255, 255, 0.10);
@define-color sidebar_bg_color #161618;
@define-color sidebar_fg_color #f5f5f7;
@define-color secondary_sidebar_bg_color #111113;
@define-color card_bg_color #1e1e22;
@define-color card_fg_color #f5f5f7;
@define-color dialog_bg_color #1a1a1d;
@define-color dialog_fg_color #f5f5f7;
@define-color popover_bg_color #1e1e22;
@define-color popover_fg_color #f5f5f7;
@define-color placeholder_text_color rgba(255, 255, 255, 0.45);
"""

AMOLED_GLASSY_PALETTE_OVERRIDE = """
/* ── Mak macOS Deep Obsidian Glass Translucent Palette ────────────────────── */
@define-color window_bg_color rgba(24, 24, 26, 0.76);
@define-color window_fg_color #f5f5f7;
@define-color view_bg_color rgba(19, 19, 21, 0.72);
@define-color view_fg_color #f5f5f7;
@define-color headerbar_bg_color rgba(30, 30, 33, 0.78);
@define-color headerbar_solid_bg #1e1e21;
@define-color headerbar_fg_color #ffffff;
@define-color headerbar_border_color rgba(255, 255, 255, 0.10);
@define-color sidebar_bg_color rgba(22, 22, 24, 0.70);
@define-color sidebar_fg_color #f5f5f7;
@define-color secondary_sidebar_bg_color rgba(17, 17, 19, 0.65);
@define-color card_bg_color rgba(30, 30, 34, 0.72);
@define-color dialog_bg_color rgba(26, 26, 29, 0.85);
@define-color dialog_fg_color #f5f5f7;
@define-color popover_bg_color rgba(26, 26, 29, 0.85);
@define-color popover_fg_color #f5f5f7;
@define-color placeholder_text_color rgba(255, 255, 255, 0.45);
"""

LIGHT_PALETTE_OVERRIDE = """
/* ── Mak macOS Crisp Apple Light Palette ─────────────────────────────────── */
@define-color window_bg_color #f5f5f7;
@define-color window_fg_color #1d1d1f;
@define-color view_bg_color #ffffff;
@define-color view_fg_color #1d1d1f;
@define-color headerbar_bg_color #ebebef;
@define-color headerbar_solid_bg #ebebef;
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

LIGHT_GLASSY_PALETTE_OVERRIDE = """
/* ── Mak macOS Crisp Apple Frosted Glass Translucent Palette ──────────────── */
@define-color window_bg_color rgba(246, 246, 248, 0.75);
@define-color window_fg_color #1d1d1f;
@define-color view_bg_color rgba(255, 255, 255, 0.72);
@define-color view_fg_color #1d1d1f;
@define-color headerbar_bg_color rgba(235, 235, 239, 0.78);
@define-color headerbar_solid_bg #ebebef;
@define-color headerbar_fg_color #1d1d1f;
@define-color headerbar_border_color rgba(0, 0, 0, 0.12);
@define-color sidebar_bg_color rgba(232, 232, 237, 0.68);
@define-color sidebar_fg_color #1d1d1f;
@define-color secondary_sidebar_bg_color rgba(226, 226, 231, 0.62);
@define-color card_bg_color rgba(255, 255, 255, 0.75);
@define-color card_fg_color #1d1d1f;
@define-color dialog_bg_color rgba(246, 246, 248, 0.85);
@define-color dialog_fg_color #1d1d1f;
@define-color popover_bg_color rgba(255, 255, 255, 0.85);
@define-color popover_fg_color #1d1d1f;
@define-color placeholder_text_color rgba(0, 0, 0, 0.45);
"""

GLASSY_CONTAINER_RULES = """
/* ── Libadwaita & GTK4 Translucent Glass App Windows ──────────────────────── */
window,
window.background,
window.background.csd,
window.background.csd > contents,
window.background.csd > contents > *,
window.background.csd > widget,
window.background.csd > widget > *,
window.background.csd > dialog-host,
window.background.csd > dialog-host > *,
window.background.csd > dialog-host > widget > widget > box > leaflet,
window.background.csd > contents > leaflet.unfolded > box > stack > widget > box > widget,
leaflet,
leaflet.unfolded,
navigation-view,
navigation-page,
split-view,
.view,
view,
tab-view,
.calculator-window,
.calculator-window view {
    background-color: @window_bg_color;
}

headerbar,
.titlebar,
window.background.csd > contents > leaflet.unfolded > box > headerbar,
window.background.csd > widget > leaflet.unfolded > box > headerbar,
window.background.csd > dialog-host > widget > widget > box > leaflet > headerbar.titlebar.tweak-titlebar-left,
window.background.csd > dialog-host > widget > widget > box > leaflet > headerbar.titlebar.tweak-titlebar-right {
    background-color: @headerbar_bg_color;
    background-image: none;
}

.sidebar,
navigation-sidebar,
.navigation-sidebar,
placessidebar,
leaflet list.navigation-sidebar,
window.background.csd > dialog-host > widget > widget > box > leaflet list.navigation-sidebar {
    background-color: @sidebar_bg_color;
    background-image: none;
}
"""

CHROMIUM_ACCENT_PALETTES = {
    "default": {
        "name": "System Default (Matches Mak Theme)",
        "color": "#3c3c43",
        "dark": "@headerbar_solid_bg",
        "light": "@headerbar_solid_bg",
    },
    "slate": {
        "name": "Slate Gray",
        "color": "#475569",
        "dark": "#2b303c",
        "light": "#e2e8f0",
    },
    "blue": {
        "name": "Ocean Blue",
        "color": "#2563eb",
        "dark": "#1a365d",
        "light": "#dbeafe",
    },
    "navy": {
        "name": "Deep Cobalt",
        "color": "#1e40af",
        "dark": "#0f172a",
        "light": "#cbd5e1",
    },
    "teal": {
        "name": "Teal Wave",
        "color": "#0d9488",
        "dark": "#0d403c",
        "light": "#ccfbf1",
    },
    "mint": {
        "name": "Mint Sage",
        "color": "#10b981",
        "dark": "#164e3f",
        "light": "#dcfce7",
    },
    "purple": {
        "name": "Mac Tahoe Purple",
        "color": "#8b5cf6",
        "dark": "#3b1e54",
        "light": "#f3e8ff",
    },
    "rose": {
        "name": "Nordic Rose",
        "color": "#f43f5e",
        "dark": "#4c1d32",
        "light": "#ffe4e6",
    },
    "peach": {
        "name": "Sunset Peach",
        "color": "#f97316",
        "dark": "#4a2417",
        "light": "#ffedd5",
    },
    "amber": {
        "name": "Warm Amber",
        "color": "#f59e0b",
        "dark": "#452d0a",
        "light": "#fef3c7",
    },
    "midnight": {
        "name": "Pitch Midnight",
        "color": "#09090b",
        "dark": "#08080a",
        "light": "#1e1e24",
    },
}

GNOME_ACCENT_PALETTES = {
    "blue": {"bg": "#3584e4", "fg": "#ffffff"},
    "teal": {"bg": "#2190a4", "fg": "#ffffff"},
    "green": {"bg": "#3a944a", "fg": "#ffffff"},
    "yellow": {"bg": "#e5a50a", "fg": "rgba(0, 0, 0, 0.85)"},
    "orange": {"bg": "#ed5b00", "fg": "#ffffff"},
    "red": {"bg": "#e01b24", "fg": "#ffffff"},
    "pink": {"bg": "#d56199", "fg": "#ffffff"},
    "purple": {"bg": "#9141ac", "fg": "#ffffff"},
    "slate": {"bg": "#5e5c64", "fg": "#ffffff"},
}

def get_icon_theme_for_accent(accent=None, is_dark=True):
    if accent is None:
        try:
            res = subprocess.run(["gsettings", "get", "org.gnome.desktop.interface", "accent-color"],
                                 capture_output=True, text=True)
            accent = res.stdout.strip().strip("'\"")
        except Exception:
            accent = "blue"
    if accent == "purple":
        return "MacTahoe-purple-dark" if is_dark else "MacTahoe-purple-light"
    return "MacTahoe-dark" if is_dark else "MacTahoe-light"

def generate_traffic_lights_override(button_size=14, button_spacing=8, chromium_accent=None, is_dark=True):
    size = max(10, min(22, int(button_size)))
    spacing = max(0, min(24, int(button_spacing)))
    margin = max(0, round(spacing / 2))
    chrome_size = max(11, min(12, int(button_size) - 2))
    backdrop_bg = "rgba(255, 255, 255, 0.22)" if is_dark else "rgba(0, 0, 0, 0.18)"

    if chromium_accent is None:
        try:
            res = subprocess.run(["gsettings", "get", "org.gnome.shell.extensions.mak", "chromium-topbar-accent"],
                                 capture_output=True, text=True)
            chromium_accent = res.stdout.strip().strip("'\"")
        except Exception:
            chromium_accent = "default"

    accent_data = CHROMIUM_ACCENT_PALETTES.get(chromium_accent, CHROMIUM_ACCENT_PALETTES["default"])
    chrom_bg = accent_data["dark"] if is_dark else accent_data["light"]

    return f"""
/* ── Mak Clean macOS Traffic Light Button Controls ({size}px, spacing {spacing}px) ── */
windowcontrols,
headerbar windowcontrols,
.titlebar windowcontrols {{
    border: none;
    background: none;
    background-color: transparent;
    box-shadow: none;
}}

windowcontrols.start,
headerbar windowcontrols.start,
.titlebar windowcontrols.start,
headerbar windowcontrols:first-child,
.titlebar windowcontrols:first-child {{
    margin-left: 12px;
    margin-right: 18px;
}}

windowcontrols.end,
headerbar windowcontrols.end,
.titlebar windowcontrols.end,
headerbar windowcontrols:last-child,
.titlebar windowcontrols:last-child {{
    margin-right: 12px;
    margin-left: 18px;
}}

/* Universal Chrome, Chromium, Brave & Electron solid titlebar background */
headerbar.header-bar.titlebar {{
    padding-left: 14px;
    padding-right: 18px;
    padding-top: 0;
    padding-bottom: 0;
    margin: 0;
    background-color: {chrom_bg};
    background-image: none;
    box-shadow: none;
    border: none;
}}

window.background.chromium headerbar,
window.background.chromium headerbar.titlebar,
window.background.brave headerbar,
window.background.brave headerbar.titlebar {{
    padding: 0;
    margin: 0;
    background-color: {chrom_bg};
    background-image: none;
    box-shadow: none;
    border: none;
}}

/* Universal anti-repetition & sizing rules across GTK3, GTK4, Libadwaita, Chromium, Chrome & Electron */
windowcontrols button,
windowcontrols button:hover,
windowcontrols button:active,
windowcontrols button:backdrop,
windowcontrols button:backdrop:hover,
windowcontrols button.close,
windowcontrols button.close:hover,
windowcontrols button.close:active,
windowcontrols button.close:backdrop,
windowcontrols button.close:backdrop:hover,
windowcontrols button.maximize,
windowcontrols button.maximize:hover,
windowcontrols button.maximize:active,
windowcontrols button.maximize:backdrop,
windowcontrols button.maximize:backdrop:hover,
windowcontrols button.minimize,
windowcontrols button.minimize:hover,
windowcontrols button.minimize:active,
windowcontrols button.minimize:backdrop,
windowcontrols button.minimize:backdrop:hover,
windowcontrols button.titlebutton,
windowcontrols button.titlebutton:hover,
windowcontrols button.titlebutton:active,
windowcontrols button.titlebutton:backdrop,
windowcontrols button.titlebutton:backdrop:hover,
windowcontrols button.titlebutton.close,
windowcontrols button.titlebutton.close:hover,
windowcontrols button.titlebutton.close:active,
windowcontrols button.titlebutton.close:backdrop,
windowcontrols button.titlebutton.close:backdrop:hover,
windowcontrols button.titlebutton.maximize,
windowcontrols button.titlebutton.maximize:hover,
windowcontrols button.titlebutton.maximize:active,
windowcontrols button.titlebutton.maximize:backdrop,
windowcontrols button.titlebutton.maximize:backdrop:hover,
windowcontrols button.titlebutton.minimize,
windowcontrols button.titlebutton.minimize:hover,
windowcontrols button.titlebutton.minimize:active,
windowcontrols button.titlebutton.minimize:backdrop,
windowcontrols button.titlebutton.minimize:backdrop:hover,
headerbar windowcontrols button,
headerbar windowcontrols button:hover,
headerbar windowcontrols button:active,
headerbar windowcontrols button:backdrop,
headerbar windowcontrols button:backdrop:hover,
headerbar windowcontrols button.close,
headerbar windowcontrols button.close:hover,
headerbar windowcontrols button.close:active,
headerbar windowcontrols button.close:backdrop,
headerbar windowcontrols button.close:backdrop:hover,
headerbar windowcontrols button.maximize,
headerbar windowcontrols button.maximize:hover,
headerbar windowcontrols button.maximize:active,
headerbar windowcontrols button.maximize:backdrop,
headerbar windowcontrols button.maximize:backdrop:hover,
headerbar windowcontrols button.minimize,
headerbar windowcontrols button.minimize:hover,
headerbar windowcontrols button.minimize:active,
headerbar windowcontrols button.minimize:backdrop,
headerbar windowcontrols button.minimize:backdrop:hover,
headerbar windowcontrols button.titlebutton,
headerbar windowcontrols button.titlebutton:hover,
headerbar windowcontrols button.titlebutton:active,
headerbar windowcontrols button.titlebutton:backdrop,
headerbar windowcontrols button.titlebutton:backdrop:hover,
headerbar windowcontrols button.titlebutton.close,
headerbar windowcontrols button.titlebutton.close:hover,
headerbar windowcontrols button.titlebutton.close:active,
headerbar windowcontrols button.titlebutton.close:backdrop,
headerbar windowcontrols button.titlebutton.close:backdrop:hover,
headerbar windowcontrols button.titlebutton.maximize,
headerbar windowcontrols button.titlebutton.maximize:hover,
headerbar windowcontrols button.titlebutton.maximize:active,
headerbar windowcontrols button.titlebutton.maximize:backdrop,
headerbar windowcontrols button.titlebutton.maximize:backdrop:hover,
headerbar windowcontrols button.titlebutton.minimize,
headerbar windowcontrols button.titlebutton.minimize:hover,
headerbar windowcontrols button.titlebutton.minimize:active,
headerbar windowcontrols button.titlebutton.minimize:backdrop,
headerbar windowcontrols button.titlebutton.minimize:backdrop:hover,
headerbar button.titlebutton,
headerbar button.titlebutton:hover,
headerbar button.titlebutton:active,
headerbar button.titlebutton:backdrop,
headerbar button.titlebutton:backdrop:hover,
headerbar button.titlebutton.close,
headerbar button.titlebutton.close:hover,
headerbar button.titlebutton.close:active,
headerbar button.titlebutton.close:backdrop,
headerbar button.titlebutton.close:backdrop:hover,
headerbar button.titlebutton.maximize,
headerbar button.titlebutton.maximize:hover,
headerbar button.titlebutton.maximize:active,
headerbar button.titlebutton.maximize:backdrop,
headerbar button.titlebutton.maximize:backdrop:hover,
headerbar button.titlebutton.minimize,
headerbar button.titlebutton.minimize:hover,
headerbar button.titlebutton.minimize:active,
headerbar button.titlebutton.minimize:backdrop,
headerbar button.titlebutton.minimize:backdrop:hover,
button.titlebutton,
button.titlebutton:hover,
button.titlebutton:active,
button.titlebutton:backdrop,
button.titlebutton:backdrop:hover,
button.titlebutton.close,
button.titlebutton.close:hover,
button.titlebutton.close:active,
button.titlebutton.close:backdrop,
button.titlebutton.close:backdrop:hover,
button.titlebutton.maximize,
button.titlebutton.maximize:hover,
button.titlebutton.maximize:active,
button.titlebutton.maximize:backdrop,
button.titlebutton.maximize:backdrop:hover,
button.titlebutton.minimize,
button.titlebutton.minimize:hover,
button.titlebutton.minimize:active,
button.titlebutton.minimize:backdrop,
button.titlebutton.minimize:backdrop:hover,
window.background.chromium button.titlebutton,
window.background.chromium button.titlebutton:hover,
window.background.chromium button.titlebutton:active,
window.background.chromium button.titlebutton:backdrop,
window.background.chromium button.titlebutton:backdrop:hover,
window.background.chromium headerbar.titlebar button.titlebutton,
window.background.chromium headerbar.titlebar button.titlebutton:hover,
window.background.chromium headerbar.titlebar button.titlebutton:active,
window.background.chromium headerbar.titlebar button.titlebutton:backdrop,
window.background.chromium headerbar.titlebar button.titlebutton:backdrop:hover,
window.background.chromium headerbar.titlebar button.titlebutton.close,
window.background.chromium headerbar.titlebar button.titlebutton.close:hover,
window.background.chromium headerbar.titlebar button.titlebutton.close:active,
window.background.chromium headerbar.titlebar button.titlebutton.close:backdrop,
window.background.chromium headerbar.titlebar button.titlebutton.close:backdrop:hover,
window.background.chromium headerbar.titlebar button.titlebutton.maximize,
window.background.chromium headerbar.titlebar button.titlebutton.maximize:hover,
window.background.chromium headerbar.titlebar button.titlebutton.maximize:active,
window.background.chromium headerbar.titlebar button.titlebutton.maximize:backdrop,
window.background.chromium headerbar.titlebar button.titlebutton.maximize:backdrop:hover,
window.background.chromium headerbar.titlebar button.titlebutton.minimize,
window.background.chromium headerbar.titlebar button.titlebutton.minimize:hover,
window.background.chromium headerbar.titlebar button.titlebutton.minimize:active,
window.background.chromium headerbar.titlebar button.titlebutton.minimize:backdrop,
window.background.chromium headerbar.titlebar button.titlebutton.minimize:backdrop:hover,
window.background.chromium headerbar.header-bar.titlebar button.titlebutton,
window.background.chromium headerbar.header-bar.titlebar button.titlebutton:hover,
window.background.chromium headerbar.header-bar.titlebar button.titlebutton:active,
window.background.chromium headerbar.header-bar.titlebar button.titlebutton:backdrop,
window.background.chromium headerbar.header-bar.titlebar button.titlebutton:backdrop:hover,
window.background.chromium headerbar.header-bar.titlebar button.close,
window.background.chromium headerbar.header-bar.titlebar button.close:hover,
window.background.chromium headerbar.header-bar.titlebar button.close:active,
window.background.chromium headerbar.header-bar.titlebar button.close:backdrop,
window.background.chromium headerbar.header-bar.titlebar button.close:backdrop:hover,
window.background.chromium headerbar.header-bar.titlebar button.close.titlebutton,
window.background.chromium headerbar.header-bar.titlebar button.close.titlebutton:hover,
window.background.chromium headerbar.header-bar.titlebar button.close.titlebutton:active,
window.background.chromium headerbar.header-bar.titlebar button.maximize,
window.background.chromium headerbar.header-bar.titlebar button.maximize:hover,
window.background.chromium headerbar.header-bar.titlebar button.maximize:active,
window.background.chromium headerbar.header-bar.titlebar button.maximize:backdrop,
window.background.chromium headerbar.header-bar.titlebar button.maximize:backdrop:hover,
window.background.chromium headerbar.header-bar.titlebar button.maximize.titlebutton,
window.background.chromium headerbar.header-bar.titlebar button.maximize.titlebutton:hover,
window.background.chromium headerbar.header-bar.titlebar button.maximize.titlebutton:active,
window.background.chromium headerbar.header-bar.titlebar button.minimize,
window.background.chromium headerbar.header-bar.titlebar button.minimize:hover,
window.background.chromium headerbar.header-bar.titlebar button.minimize:active,
window.background.chromium headerbar.header-bar.titlebar button.minimize:backdrop,
window.background.chromium headerbar.header-bar.titlebar button.minimize:backdrop:hover,
window.background.chromium headerbar.header-bar.titlebar button.minimize.titlebutton,
window.background.chromium headerbar.header-bar.titlebar button.minimize.titlebutton:hover,
window.background.chromium headerbar.header-bar.titlebar button.minimize.titlebutton:active,
window.background.csd windowcontrols button,
window.background.csd windowcontrols button:hover,
window.background.csd windowcontrols button:active,
window.background.csd windowcontrols button:backdrop,
window.background.csd windowcontrols button:backdrop:hover,
window.background.csd windowcontrols button.titlebutton,
window.background.csd windowcontrols button.titlebutton:hover,
window.background.csd windowcontrols button.titlebutton:active,
window.background.csd windowcontrols button.titlebutton:backdrop,
window.background.csd windowcontrols button.titlebutton:backdrop:hover {{
    min-width: {size}px;
    min-height: {size}px;
    padding: 0;
    margin: 0 {margin}px;
    border-radius: 9999px;
    background-color: transparent;
    background-repeat: no-repeat;
    background-position: center center;
    background-size: {size}px {size}px;
    -gtk-icon-shadow: none;
    border: none;
    box-shadow: none;
}}

/* Ensure button images/icons also do not repeat and stay centered */
headerbar windowcontrols button > image,
windowcontrols button > image,
headerbar button.titlebutton > image,
button.titlebutton > image,
windowcontrols button:hover > image,
headerbar button.titlebutton:hover > image,
headerbar windowcontrols button:hover > image {{
    padding: 0;
    margin: 0;
    background-repeat: no-repeat;
    background-position: center center;
}}

/* ── Dedicated Chrome, Chromium & Electron Traffic Lights Precision Sizing & Gaps ── */
headerbar.header-bar.titlebar windowcontrols button,
headerbar.header-bar.titlebar windowcontrols button:hover,
headerbar.header-bar.titlebar windowcontrols button:active,
headerbar.header-bar.titlebar windowcontrols button:backdrop,
headerbar.header-bar.titlebar windowcontrols button:backdrop:hover,
headerbar.header-bar.titlebar button.titlebutton,
headerbar.header-bar.titlebar button.titlebutton:hover,
headerbar.header-bar.titlebar button.titlebutton:active,
headerbar.header-bar.titlebar button.titlebutton:backdrop,
headerbar.header-bar.titlebar button.titlebutton:backdrop:hover,
window.background.csd headerbar.header-bar.titlebar windowcontrols button,
window.background.csd headerbar.header-bar.titlebar windowcontrols button:hover,
window.background.csd headerbar.header-bar.titlebar windowcontrols button.titlebutton,
window.background.csd headerbar.header-bar.titlebar windowcontrols button.titlebutton:hover,
window.background.chromium headerbar windowcontrols button,
window.background.chromium headerbar windowcontrols button:hover,
window.background.chromium headerbar windowcontrols button:active,
window.background.chromium headerbar windowcontrols button:backdrop,
window.background.chromium headerbar windowcontrols button:backdrop:hover,
window.background.chromium headerbar.header-bar.titlebar windowcontrols button,
window.background.chromium headerbar.header-bar.titlebar windowcontrols button:hover,
window.background.chromium headerbar.header-bar.titlebar windowcontrols button:active,
window.background.chromium headerbar.header-bar.titlebar windowcontrols button:backdrop,
window.background.chromium headerbar.header-bar.titlebar windowcontrols button:backdrop:hover,
window.background.chromium headerbar.header-bar.titlebar button.titlebutton,
window.background.chromium headerbar.header-bar.titlebar button.titlebutton:hover,
window.background.chromium headerbar.titlebar button.titlebutton,
window.background.chromium headerbar.titlebar button.titlebutton:hover,
window.background.chromium button.titlebutton,
window.background.chromium button.titlebutton:hover,
window.background.chromium windowcontrols button,
window.background.chromium windowcontrols button:hover {{
    min-width: {chrome_size}px;
    min-height: {chrome_size}px;
    background-size: {chrome_size}px {chrome_size}px;
    background-repeat: no-repeat;
    background-position: center center;
    border-radius: 9999px;
    border: none;
    box-shadow: none;
    padding: 0;
    color: transparent;
    -gtk-icon-source: none;
    -gtk-icon-shadow: none;
}}

/* Ensure no symbolic glyphs (like x, +, -) render on top of traffic lights in Chrome */
headerbar.header-bar.titlebar windowcontrols button image,
headerbar.header-bar.titlebar button.titlebutton image,
window.background.csd headerbar.header-bar.titlebar windowcontrols button image,
window.background.chromium headerbar windowcontrols button image,
window.background.brave headerbar windowcontrols button image {{
    -gtk-icon-source: none;
    color: transparent;
    opacity: 0;
}}

headerbar.header-bar.titlebar windowcontrols button.close,
headerbar.header-bar.titlebar windowcontrols button.titlebutton.close,
headerbar.header-bar.titlebar button.close,
headerbar.header-bar.titlebar button.titlebutton.close,
window.background.csd headerbar.header-bar.titlebar windowcontrols button.close,
window.background.csd headerbar.header-bar.titlebar windowcontrols button.titlebutton.close,
window.background.chromium headerbar windowcontrols button.close,
window.background.chromium headerbar windowcontrols button.titlebutton.close,
window.background.chromium headerbar.header-bar.titlebar windowcontrols button.close,
window.background.chromium headerbar.header-bar.titlebar button.close,
window.background.chromium headerbar.header-bar.titlebar button.titlebutton.close,
window.background.chromium headerbar.titlebar button.titlebutton.close,
window.background.chromium button.titlebutton.close,
window.background.chromium windowcontrols button.close,
window.background.brave headerbar windowcontrols button.close,
window.background.brave headerbar windowcontrols button.titlebutton.close,
window.background.brave headerbar.header-bar.titlebar windowcontrols button.close,
window.background.brave headerbar.header-bar.titlebar button.close,
window.background.brave headerbar.header-bar.titlebar button.titlebutton.close,
window.background.brave headerbar.titlebar button.titlebutton.close,
window.background.brave button.titlebutton.close,
window.background.brave windowcontrols button.close {{
    margin-left: 8px;
    margin-right: 1px;
    margin-top: 0px;
    margin-bottom: 0px;
    color: transparent;
    -gtk-icon-source: none;
}}

headerbar.header-bar.titlebar windowcontrols button.minimize,
headerbar.header-bar.titlebar windowcontrols button.titlebutton.minimize,
headerbar.header-bar.titlebar button.minimize,
headerbar.header-bar.titlebar button.titlebutton.minimize,
window.background.csd headerbar.header-bar.titlebar windowcontrols button.minimize,
window.background.csd headerbar.header-bar.titlebar windowcontrols button.titlebutton.minimize,
window.background.chromium headerbar windowcontrols button.minimize,
window.background.chromium headerbar windowcontrols button.titlebutton.minimize,
window.background.chromium headerbar.header-bar.titlebar windowcontrols button.minimize,
window.background.chromium headerbar.header-bar.titlebar button.minimize,
window.background.chromium headerbar.header-bar.titlebar button.titlebutton.minimize,
window.background.chromium headerbar.titlebar button.titlebutton.minimize,
window.background.chromium button.titlebutton.minimize,
window.background.chromium windowcontrols button.minimize,
window.background.brave headerbar windowcontrols button.minimize,
window.background.brave headerbar windowcontrols button.titlebutton.minimize,
window.background.brave headerbar.header-bar.titlebar windowcontrols button.minimize,
window.background.brave headerbar.header-bar.titlebar button.minimize,
window.background.brave headerbar.header-bar.titlebar button.titlebutton.minimize,
window.background.brave headerbar.titlebar button.titlebutton.minimize,
window.background.brave button.titlebutton.minimize,
window.background.brave windowcontrols button.minimize {{
    margin-left: 1px;
    margin-right: 1px;
    margin-top: 0px;
    margin-bottom: 0px;
    color: transparent;
    -gtk-icon-source: none;
}}

headerbar.header-bar.titlebar windowcontrols button.maximize,
headerbar.header-bar.titlebar windowcontrols button.titlebutton.maximize,
headerbar.header-bar.titlebar button.maximize,
headerbar.header-bar.titlebar button.titlebutton.maximize,
window.background.csd headerbar.header-bar.titlebar windowcontrols button.maximize,
window.background.csd headerbar.header-bar.titlebar windowcontrols button.titlebutton.maximize,
window.background.chromium headerbar windowcontrols button.maximize,
window.background.chromium headerbar windowcontrols button.titlebutton.maximize,
window.background.chromium headerbar.header-bar.titlebar windowcontrols button.maximize,
window.background.chromium headerbar.header-bar.titlebar button.maximize,
window.background.chromium headerbar.header-bar.titlebar button.titlebutton.maximize,
window.background.chromium headerbar.titlebar button.titlebutton.maximize,
window.background.chromium button.titlebutton.maximize,
window.background.chromium windowcontrols button.maximize,
window.background.brave headerbar windowcontrols button.maximize,
window.background.brave headerbar windowcontrols button.titlebutton.maximize,
window.background.brave headerbar.header-bar.titlebar windowcontrols button.maximize,
window.background.brave headerbar.header-bar.titlebar button.maximize,
window.background.brave headerbar.header-bar.titlebar button.titlebutton.maximize,
window.background.brave headerbar.titlebar button.titlebutton.maximize,
window.background.brave button.titlebutton.maximize,
window.background.brave windowcontrols button.maximize {{
    margin-left: 1px;
    margin-right: 18px;
    margin-top: 0px;
    margin-bottom: 0px;
    color: transparent;
    -gtk-icon-source: none;
}}

/* ── Authentic macOS Sonoma Traffic Light Backgrounds, Borders & Colors ── */
window.background.chromium headerbar windowcontrols button.close,
window.background.chromium headerbar.header-bar.titlebar windowcontrols button.close,
window.background.chromium headerbar.header-bar.titlebar button.close,
window.background.chromium headerbar.header-bar.titlebar button.titlebutton.close,
window.background.chromium headerbar.titlebar button.titlebutton.close,
window.background.chromium headerbar button.titlebutton.close,
window.background.chromium button.titlebutton.close,
window.background.chromium windowcontrols button.close,
window.background.brave headerbar windowcontrols button.close,
window.background.brave headerbar.header-bar.titlebar windowcontrols button.close,
window.background.brave headerbar.header-bar.titlebar button.close,
window.background.brave headerbar.header-bar.titlebar button.titlebutton.close,
window.background.brave headerbar.titlebar button.titlebutton.close,
window.background.brave button.titlebutton.close,
window.background.brave windowcontrols button.close {{
    background-color: #ff5f56;
    background-image: none;
    border: 1px solid rgba(0, 0, 0, 0.15);
}}

window.background.chromium headerbar windowcontrols button.close:hover,
window.background.chromium headerbar.header-bar.titlebar windowcontrols button.close:hover,
window.background.chromium headerbar.header-bar.titlebar button.close:hover,
window.background.chromium headerbar.header-bar.titlebar button.titlebutton.close:hover,
window.background.chromium headerbar.titlebar button.titlebutton.close:hover,
window.background.chromium headerbar button.titlebutton.close:hover,
window.background.chromium button.titlebutton.close:hover,
window.background.chromium windowcontrols button.close:hover,
window.background.brave headerbar windowcontrols button.close:hover,
window.background.brave headerbar.header-bar.titlebar windowcontrols button.close:hover,
window.background.brave headerbar.header-bar.titlebar button.close:hover,
window.background.brave headerbar.header-bar.titlebar button.titlebutton.close:hover,
window.background.brave headerbar.titlebar button.titlebutton.close:hover,
window.background.brave button.titlebutton.close:hover,
window.background.brave windowcontrols button.close:hover {{
    background-color: #e0443e;
    background-image: none;
}}

window.background.chromium headerbar windowcontrols button.close:active,
window.background.chromium headerbar.header-bar.titlebar windowcontrols button.close:active,
window.background.chromium headerbar.header-bar.titlebar button.close:active,
window.background.chromium headerbar.header-bar.titlebar button.titlebutton.close:active,
window.background.chromium headerbar.titlebar button.titlebutton.close:active,
window.background.chromium headerbar button.titlebutton.close:active,
window.background.chromium button.titlebutton.close:active,
window.background.chromium windowcontrols button.close:active,
window.background.brave headerbar windowcontrols button.close:active,
window.background.brave headerbar.header-bar.titlebar windowcontrols button.close:active,
window.background.brave headerbar.header-bar.titlebar button.close:active,
window.background.brave headerbar.header-bar.titlebar button.titlebutton.close:active,
window.background.brave headerbar.titlebar button.titlebutton.close:active,
window.background.brave button.titlebutton.close:active,
window.background.brave windowcontrols button.close:active {{
    background-color: #bf302a;
    background-image: none;
}}

window.background.chromium headerbar windowcontrols button.minimize,
window.background.chromium headerbar.header-bar.titlebar windowcontrols button.minimize,
window.background.chromium headerbar.header-bar.titlebar button.minimize,
window.background.chromium headerbar.header-bar.titlebar button.titlebutton.minimize,
window.background.chromium headerbar.titlebar button.titlebutton.minimize,
window.background.chromium headerbar button.titlebutton.minimize,
window.background.chromium button.titlebutton.minimize,
window.background.chromium windowcontrols button.minimize,
window.background.brave headerbar windowcontrols button.minimize,
window.background.brave headerbar.header-bar.titlebar windowcontrols button.minimize,
window.background.brave headerbar.header-bar.titlebar button.minimize,
window.background.brave headerbar.header-bar.titlebar button.titlebutton.minimize,
window.background.brave headerbar.titlebar button.titlebutton.minimize,
window.background.brave button.titlebutton.minimize,
window.background.brave windowcontrols button.minimize {{
    background-color: #ffbd2e;
    background-image: none;
    border: 1px solid rgba(0, 0, 0, 0.15);
}}

window.background.chromium headerbar windowcontrols button.minimize:hover,
window.background.chromium headerbar.header-bar.titlebar windowcontrols button.minimize:hover,
window.background.chromium headerbar.header-bar.titlebar button.minimize:hover,
window.background.chromium headerbar.header-bar.titlebar button.titlebutton.minimize:hover,
window.background.chromium headerbar.titlebar button.titlebutton.minimize:hover,
window.background.chromium headerbar button.titlebutton.minimize:hover,
window.background.chromium button.titlebutton.minimize:hover,
window.background.chromium windowcontrols button.minimize:hover,
window.background.brave headerbar windowcontrols button.minimize:hover,
window.background.brave headerbar.header-bar.titlebar windowcontrols button.minimize:hover,
window.background.brave headerbar.header-bar.titlebar button.minimize:hover,
window.background.brave headerbar.header-bar.titlebar button.titlebutton.minimize:hover,
window.background.brave headerbar.titlebar button.titlebutton.minimize:hover,
window.background.brave button.titlebutton.minimize:hover,
window.background.brave windowcontrols button.minimize:hover {{
    background-color: #dea123;
    background-image: none;
}}

window.background.chromium headerbar windowcontrols button.minimize:active,
window.background.chromium headerbar.header-bar.titlebar windowcontrols button.minimize:active,
window.background.chromium headerbar.header-bar.titlebar button.minimize:active,
window.background.chromium headerbar.header-bar.titlebar button.titlebutton.minimize:active,
window.background.chromium headerbar.titlebar button.titlebutton.minimize:active,
window.background.chromium headerbar button.titlebutton.minimize:active,
window.background.chromium button.titlebutton.minimize:active,
window.background.chromium windowcontrols button.minimize:active,
window.background.brave headerbar windowcontrols button.minimize:active,
window.background.brave headerbar.header-bar.titlebar windowcontrols button.minimize:active,
window.background.brave headerbar.header-bar.titlebar button.minimize:active,
window.background.brave headerbar.header-bar.titlebar button.titlebutton.minimize:active,
window.background.brave headerbar.titlebar button.titlebutton.minimize:active,
window.background.brave button.titlebutton.minimize:active,
window.background.brave windowcontrols button.minimize:active {{
    background-color: #c38c1a;
    background-image: none;
}}

window.background.chromium headerbar windowcontrols button.maximize,
window.background.chromium headerbar.header-bar.titlebar windowcontrols button.maximize,
window.background.chromium headerbar.header-bar.titlebar button.maximize,
window.background.chromium headerbar.header-bar.titlebar button.titlebutton.maximize,
window.background.chromium headerbar.titlebar button.titlebutton.maximize,
window.background.chromium headerbar button.titlebutton.maximize,
window.background.chromium button.titlebutton.maximize,
window.background.chromium windowcontrols button.maximize,
window.background.brave headerbar windowcontrols button.maximize,
window.background.brave headerbar.header-bar.titlebar windowcontrols button.maximize,
window.background.brave headerbar.header-bar.titlebar button.maximize,
window.background.brave headerbar.header-bar.titlebar button.titlebutton.maximize,
window.background.brave headerbar.titlebar button.titlebutton.maximize,
window.background.brave button.titlebutton.maximize,
window.background.brave windowcontrols button.maximize {{
    background-color: #27c93f;
    background-image: none;
    border: 1px solid rgba(0, 0, 0, 0.15);
}}

window.background.chromium headerbar windowcontrols button.maximize:hover,
window.background.chromium headerbar.header-bar.titlebar windowcontrols button.maximize:hover,
window.background.chromium headerbar.header-bar.titlebar button.maximize:hover,
window.background.chromium headerbar.header-bar.titlebar button.titlebutton.maximize:hover,
window.background.chromium headerbar.titlebar button.titlebutton.maximize:hover,
window.background.chromium headerbar button.titlebutton.maximize:hover,
window.background.chromium button.titlebutton.maximize:hover,
window.background.chromium windowcontrols button.maximize:hover,
window.background.brave headerbar windowcontrols button.maximize:hover,
window.background.brave headerbar.header-bar.titlebar windowcontrols button.maximize:hover,
window.background.brave headerbar.header-bar.titlebar button.maximize:hover,
window.background.brave headerbar.header-bar.titlebar button.titlebutton.maximize:hover,
window.background.brave headerbar.titlebar button.titlebutton.maximize:hover,
window.background.brave button.titlebutton.maximize:hover,
window.background.brave windowcontrols button.maximize:hover {{
    background-color: #1aab29;
    background-image: none;
}}

window.background.chromium headerbar windowcontrols button.maximize:active,
window.background.chromium headerbar.header-bar.titlebar windowcontrols button.maximize:active,
window.background.chromium headerbar.header-bar.titlebar button.maximize:active,
window.background.chromium headerbar.header-bar.titlebar button.titlebutton.maximize:active,
window.background.chromium headerbar.titlebar button.titlebutton.maximize:active,
window.background.chromium headerbar button.titlebutton.maximize:active,
window.background.chromium button.titlebutton.maximize:active,
window.background.chromium windowcontrols button.maximize:active,
window.background.brave headerbar windowcontrols button.maximize:active,
window.background.brave headerbar.header-bar.titlebar windowcontrols button.maximize:active,
window.background.brave headerbar.header-bar.titlebar button.maximize:active,
window.background.brave headerbar.header-bar.titlebar button.titlebutton.maximize:active,
window.background.brave headerbar.titlebar button.titlebutton.maximize:active,
window.background.brave button.titlebutton.maximize:active,
window.background.brave windowcontrols button.maximize:active {{
    background-color: #138f20;
    background-image: none;
}}

/* ── Inactive / Backdrop window traffic lights (Chromium, Chrome, Brave & Electron) ── */
window.background.chromium headerbar windowcontrols button:backdrop,
window.background.chromium headerbar.header-bar.titlebar windowcontrols button:backdrop,
window.background.chromium headerbar.header-bar.titlebar button:backdrop,
window.background.chromium headerbar.header-bar.titlebar button.titlebutton:backdrop,
window.background.chromium headerbar.titlebar button.titlebutton:backdrop,
window.background.chromium headerbar button.titlebutton:backdrop,
window.background.chromium button.titlebutton:backdrop,
window.background.chromium windowcontrols button:backdrop,
window.background.brave headerbar windowcontrols button:backdrop,
window.background.brave headerbar.header-bar.titlebar windowcontrols button:backdrop,
window.background.brave headerbar.header-bar.titlebar button:backdrop,
window.background.brave headerbar.header-bar.titlebar button.titlebutton:backdrop,
window.background.brave headerbar.titlebar button.titlebutton:backdrop,
window.background.brave button.titlebutton:backdrop,
window.background.brave windowcontrols button:backdrop {{
    background-color: {backdrop_bg};
    background-image: none;
    border: 1px solid rgba(0, 0, 0, 0.10);
    box-shadow: none;
    opacity: 0.70;
}}

/* ── Native GTK Window Controls in Inactive / Backdrop State ── */
windowcontrols button:backdrop,
headerbar windowcontrols button:backdrop,
.titlebar windowcontrols button:backdrop,
window.background.csd headerbar windowcontrols button:backdrop {{
    background-color: transparent;
    border: none;
    box-shadow: none;
    opacity: 0.55;
}}

windowcontrols button:backdrop:hover,
headerbar windowcontrols button:backdrop:hover,
.titlebar windowcontrols button:backdrop:hover {{
    opacity: 1.0;
}}

window.background.chromium windowcontrols button.close:backdrop:hover,
window.background.brave windowcontrols button.close:backdrop:hover {{
    opacity: 1.0;
    background-color: #ff5f56;
}}

window.background.chromium windowcontrols button.minimize:backdrop:hover,
window.background.brave windowcontrols button.minimize:backdrop:hover {{
    opacity: 1.0;
    background-color: #ffbd2e;
}}

window.background.chromium windowcontrols button.maximize:backdrop:hover,
window.background.brave windowcontrols button.maximize:backdrop:hover {{
    opacity: 1.0;
    background-color: #27c93f;
}}

headerbar:backdrop label.title,
headerbar:backdrop .title,
.titlebar:backdrop label.title,
.titlebar:backdrop .title {{
    opacity: 0.55;
}}

headerbar:backdrop button:not(.suggested-action):not(.destructive-action):not(.close):not(.minimize):not(.maximize):not(.titlebutton),
.titlebar:backdrop button:not(.suggested-action):not(.destructive-action):not(.close):not(.minimize):not(.maximize):not(.titlebutton) {{
    opacity: 0.65;
}}
"""

TRAFFIC_LIGHTS_OVERRIDE = generate_traffic_lights_override(14, 8)

def generate_window_corners_override(is_dark=True):
    window_shadow = (
        "0 10px 28px rgba(0, 0, 0, 0.22), 0 3px 10px rgba(0, 0, 0, 0.12), 0 0 0 1px rgba(255, 255, 255, 0.08)"
        if is_dark
        else "0 10px 28px rgba(0, 0, 0, 0.10), 0 3px 10px rgba(0, 0, 0, 0.05), 0 0 0 1px rgba(0, 0, 0, 0.08)"
    )
    backdrop_shadow = (
        "0 6px 18px rgba(0, 0, 0, 0.14), 0 2px 6px rgba(0, 0, 0, 0.08), 0 0 0 1px rgba(255, 255, 255, 0.05)"
        if is_dark
        else "0 6px 18px rgba(0, 0, 0, 0.06), 0 2px 6px rgba(0, 0, 0, 0.03), 0 0 0 1px rgba(0, 0, 0, 0.06)"
    )
    border_maximized = "rgba(255, 255, 255, 0.12)" if is_dark else "rgba(0, 0, 0, 0.12)"
    border_maximized_backdrop = "rgba(255, 255, 255, 0.08)" if is_dark else "rgba(0, 0, 0, 0.08)"
    return f"""
/* ── Mak macOS Window Corner & Geometry Consistency (16px) ──────────────── */
window,
window.background,
window.csd,
window.background.csd,
window.background.solid-csd,
window.solid-csd {{
    border-radius: 16px;
}}

window.csd:not(.fullscreen):not(.tiled):not(.maximized),
window.background.csd:not(.fullscreen):not(.tiled):not(.maximized) {{
    box-shadow: {window_shadow};
}}

window.csd:not(.fullscreen):not(.tiled):not(.maximized):backdrop,
window.background.csd:not(.fullscreen):not(.tiled):not(.maximized):backdrop {{
    box-shadow: {backdrop_shadow};
}}

/* Maximized Window Borders (Preserve 1px outline border in maximized view) */
window.csd.maximized,
window.background.csd.maximized,
window.background.maximized,
window.background.solid-csd.maximized,
window.maximized.csd,
window.maximized.solid-csd,
window.maximized,
window.csd.tiled,
window.csd.tiled-top,
window.csd.tiled-bottom,
window.csd.tiled-left,
window.csd.tiled-right,
window.background.tiled,
window.tiled {{
    box-shadow: inset 0 0 0 1px {border_maximized};
    border-radius: 16px;
}}

window.csd.maximized:backdrop,
window.background.csd.maximized:backdrop,
window.background.maximized:backdrop,
window.maximized:backdrop,
window.csd.tiled:backdrop,
window.tiled:backdrop {{
    box-shadow: inset 0 0 0 1px {border_maximized_backdrop};
}}

/* Compact macOS Unified Titlebar Height (38px) */
headerbar,
headerbar.default-decoration,
.titlebar,
window.csd > headerbar,
window.background.csd > headerbar,
window.csd headerbar,
window.background headerbar {{
    min-height: 38px;
    padding-top: 2px;
    padding-bottom: 2px;
    border-top-left-radius: 16px;
    border-top-right-radius: 16px;
}}

headerbar > windowhandle > box,
headerbar windowhandle > box {{
    min-height: 38px;
}}

headerbar label.title,
.titlebar label.title,
headerbar .title,
.titlebar .title {{
    font-size: 13px;
    font-weight: 600;
}}

.tiled headerbar,
.maximized headerbar,
window.background.maximized headerbar,
window.background.maximized.csd headerbar,
window.background.csd.maximized headerbar,
window.maximized.csd headerbar,
window.maximized headerbar,
window.background.maximized .titlebar,
window.background.maximized.csd .titlebar,
window.background.csd.maximized .titlebar,
window.maximized.csd .titlebar,
window.maximized .titlebar,
window.background.tiled headerbar,
window.background.csd.tiled headerbar,
window.tiled.csd headerbar,
window.tiled headerbar,
window.background.tiled .titlebar,
window.tiled .titlebar {{
    border-top-left-radius: 16px;
    border-top-right-radius: 16px;
}}

window.background.maximized > contents,
window.background.maximized.csd > contents,
window.background.csd.maximized > contents,
window.maximized.csd > contents,
window.maximized > contents,
window.background.maximized > widget,
window.maximized > widget,
window.background.maximized > box,
window.maximized > box {{
    border-radius: 16px;
}}

window.background.chromium headerbar.header-bar.titlebar {{
    border-radius: 16px 16px 0 0;
}}

/* True Fullscreen Only */
window.fullscreen,
window.csd.fullscreen,
window.background.fullscreen,
window.background.fullscreen.csd,
window.background.csd.fullscreen,
window.fullscreen.csd {{
    border-radius: 0;
    outline: none;
    box-shadow: none;
    border: none;
}}

window.fullscreen headerbar,
window.fullscreen .titlebar,
window.background.fullscreen headerbar,
window.background.fullscreen.csd headerbar,
window.background.csd.fullscreen headerbar,
window.fullscreen.csd headerbar {{
    border-radius: 0;
}}
"""

WINDOW_CORNERS_CSS_OVERRIDE = generate_window_corners_override(True)

def generate_popover_override(is_dark=True):
    border_color = "rgba(255, 255, 255, 0.10)" if is_dark else "rgba(0, 0, 0, 0.08)"
    hover_bg = "rgba(255, 255, 255, 0.10)" if is_dark else "rgba(0, 0, 0, 0.05)"
    selected_bg = "rgba(255, 255, 255, 0.16)" if is_dark else "rgba(0, 0, 0, 0.08)"
    text_color = "#f5f5f7" if is_dark else "#1d1d1f"
    shadow = (
        "0 8px 18px rgba(0, 0, 0, 0.20), 0 2px 6px rgba(0, 0, 0, 0.10)"
        if is_dark
        else "0 6px 16px rgba(0, 0, 0, 0.08), 0 1px 4px rgba(0, 0, 0, 0.04)"
    )

    return f"""
/* ── Clean macOS Translucent Popover & Dropdown Cards ────────────────────── */
popover,
popover.background,
popover.menu,
popover.menu.background,
popover.menu:backdrop,
popover:backdrop {{
    background: transparent;
    background-color: transparent;
    box-shadow: none;
    border: none;
    padding: 0;
}}

popover > contents,
popover.menu > contents,
popover.menu.background > contents,
popover contents {{
    background-color: @popover_bg_color;
    color: @popover_fg_color;
    border-radius: 10px;
    border: 1px solid {border_color};
    box-shadow: {shadow};
    padding: 3px;
    margin: 0;
}}

popover > arrow,
popover.menu > arrow,
popover.menu.background > arrow,
popover arrow,
popover > arrow.top,
popover > arrow.bottom,
popover > arrow.left,
popover > arrow.right {{
    background: none;
    background-color: transparent;
    background-image: none;
    border: none;
    box-shadow: none;
    outline: none;
    opacity: 0;
    min-width: 0;
    min-height: 0;
    padding: 0;
    margin: 0;
    border-image: none;
}}

popover.menu stack,
popover.menu box,
popover.menu > contents > stack,
popover.menu > contents > stack > box,
popover.menu > contents > scrolledwindow > viewport > stack > box {{
    padding: 0;
    margin: 0;
}}

popover modelbutton,
popover.menu modelbutton,
popover listview > row,
popover list > row,
row.combo popover listview > row,
row.combo popover list > row {{
    border-radius: 5px;
    min-height: 24px;
    padding: 4px 8px;
    margin: 1px 3px;
    color: {text_color};
    font-size: 13px;
    transition: background-color 80ms ease, color 80ms ease;
}}

popover modelbutton:hover,
popover modelbutton:focus,
popover.menu modelbutton:hover,
popover.menu modelbutton:focus,
popover listview > row:hover,
popover list > row:hover,
row.combo popover listview > row:hover,
row.combo popover list > row:hover {{
    background-color: @accent_bg_color;
    color: #ffffff;
}}

popover modelbutton:hover label,
popover.menu modelbutton:hover label,
popover listview > row:hover label,
popover list > row:hover label,
row.combo popover listview > row:hover label,
row.combo popover list > row:hover label,
popover modelbutton:hover image,
popover.menu modelbutton:hover image,
popover listview > row:hover image,
popover list > row:hover image,
row.combo popover listview > row:hover image,
row.combo popover list > row:hover image,
popover modelbutton:hover accelerator,
popover.menu modelbutton:hover accelerator {{
    color: #ffffff;
}}

popover modelbutton:selected,
popover.menu modelbutton:selected,
popover listview > row:selected,
popover list > row:selected,
row.combo popover listview > row:selected,
row.combo popover list > row:selected {{
    background-color: @accent_bg_color;
    color: #ffffff;
    font-weight: 500;
}}

popover modelbutton:selected label,
popover.menu modelbutton:selected label,
popover listview > row:selected label,
popover list > row:selected label,
row.combo popover listview > row:selected label,
row.combo popover list > row:selected label,
popover modelbutton:selected image,
popover.menu modelbutton:selected image,
popover listview > row:selected image,
popover list > row:selected image,
row.combo popover listview > row:selected image,
row.combo popover list > row:selected image,
popover modelbutton:selected accelerator,
popover.menu modelbutton:selected accelerator {{
    color: #ffffff;
}}

popover check,
popover radio,
popover check:checked,
popover radio:checked,
popover image {{
    color: inherit;
}}

popover separator {{
    margin: 4px 2px;
    background-color: {border_color};
}}
"""


def generate_nautilus_override(is_dark=True):
    border_color = "rgba(255, 255, 255, 0.08)" if is_dark else "rgba(0, 0, 0, 0.08)"
    text_primary = "#f5f5f7" if is_dark else "#1d1d1f"
    text_secondary = "rgba(255, 255, 255, 0.50)" if is_dark else "rgba(0, 0, 0, 0.50)"
    text_sidebar = "rgba(255, 255, 255, 0.85)" if is_dark else "rgba(0, 0, 0, 0.82)"
    icon_sidebar = "rgba(255, 255, 255, 0.70)" if is_dark else "rgba(0, 0, 0, 0.65)"
    sidebar_selected_bg = "rgba(255, 255, 255, 0.14)" if is_dark else "rgba(0, 0, 0, 0.08)"
    sidebar_hover_bg = "rgba(255, 255, 255, 0.08)" if is_dark else "rgba(0, 0, 0, 0.05)"
    alt_row_bg = "rgba(255, 255, 255, 0.02)" if is_dark else "rgba(0, 0, 0, 0.02)"
    row_hover_bg = "rgba(255, 255, 255, 0.06)" if is_dark else "rgba(0, 0, 0, 0.05)"
    path_btn_bg = "rgba(255, 255, 255, 0.08)" if is_dark else "rgba(0, 0, 0, 0.06)"
    path_btn_hover = "rgba(255, 255, 255, 0.14)" if is_dark else "rgba(0, 0, 0, 0.10)"

    return f"""
/* ── macOS Finder (Nautilus) Elegant Native Styling ──────────────────────── */
.nautilus-window {{
    background-color: @window_bg_color;
}}

/* Seamless Sidebar: completely eliminate 6px black outline & gap */
.nautilus-window .sidebar-pane,
.nautilus-window .sidebar-pane:dir(ltr),
.nautilus-window .sidebar-pane:dir(rtl),
.nautilus-window .sidebar-pane:backdrop,
.nautilus-window .sidebar-pane:backdrop:dir(ltr),
.nautilus-window .sidebar-pane:backdrop:dir(rtl),
#NautilusFileChooser .sidebar-pane,
#NautilusFileChooser .sidebar-pane:dir(ltr),
#NautilusFileChooser .sidebar-pane:dir(rtl),
#NautilusFileChooser .sidebar-pane:backdrop {{
    box-shadow: none;
    background-color: @sidebar_bg_color;
    border-right: 1px solid {border_color};
}}

.nautilus-window .sidebar-pane placessidebar,
#NautilusFileChooser .sidebar-pane placessidebar,
.nautilus-window placessidebar {{
    background: transparent;
    background-color: transparent;
}}

/* Sidebar Rows (Compact Apple Finder Sidebar) */
.nautilus-window .sidebar-pane placessidebar row,
.nautilus-window placessidebar row,
.nautilus-window .navigation-sidebar > row,
#NautilusFileChooser placessidebar row,
#NautilusFileChooser .navigation-sidebar > row {{
    border-radius: 6px;
    margin: 1px 6px;
    padding: 2px 8px;
    min-height: 22px;
    font-size: 12.5px;
    color: {text_sidebar};
    transition: background-color 80ms ease, color 80ms ease;
}}

.nautilus-window .sidebar-pane placessidebar row label,
.nautilus-window placessidebar row label,
.nautilus-window .navigation-sidebar > row label,
#NautilusFileChooser placessidebar row label,
#NautilusFileChooser .navigation-sidebar > row label {{
    color: {text_sidebar};
}}

.nautilus-window .sidebar-pane placessidebar row image,
.nautilus-window placessidebar row image,
.nautilus-window .navigation-sidebar > row image,
#NautilusFileChooser placessidebar row image,
#NautilusFileChooser .navigation-sidebar > row image {{
    min-width: 16px;
    min-height: 16px;
    margin-right: 6px;
    color: {icon_sidebar};
}}

/* Sidebar Row Hover */
.nautilus-window .sidebar-pane placessidebar row:hover,
.nautilus-window placessidebar row:hover,
.nautilus-window .navigation-sidebar > row:hover {{
    background-color: {sidebar_hover_bg};
    color: {text_primary};
}}

.nautilus-window .sidebar-pane placessidebar row:hover label,
.nautilus-window .sidebar-pane placessidebar row:hover image,
.nautilus-window placessidebar row:hover label,
.nautilus-window placessidebar row:hover image {{
    color: {text_primary};
}}

/* Selected Sidebar Row */
.nautilus-window .sidebar-pane placessidebar row:selected,
.nautilus-window placessidebar row:selected,
.nautilus-window .navigation-sidebar > row:selected,
.nautilus-window .sidebar-pane placessidebar .navigation-sidebar:not(.view) > row:selected,
#NautilusFileChooser .sidebar-pane placessidebar .navigation-sidebar:not(.view) > row:selected {{
    background-color: {sidebar_selected_bg};
    color: {text_primary};
    font-weight: 500;
    box-shadow: none;
    outline: none;
    border: none;
}}

.nautilus-window .sidebar-pane placessidebar row:selected label,
.nautilus-window .sidebar-pane placessidebar row:selected image,
.nautilus-window placessidebar row:selected label,
.nautilus-window placessidebar row:selected image,
.nautilus-window .navigation-sidebar > row:selected label,
.nautilus-window .navigation-sidebar > row:selected image {{
    color: {text_primary};
    font-weight: 500;
}}

/* Content Pane (Files View) */
.nautilus-window .content-pane,
#NautilusFileChooser .content-pane {{
    background-color: @view_bg_color;
}}

.nautilus-window .view,
.nautilus-window listview.view,
.nautilus-window columnview,
.nautilus-window .nautilus-list-view,
.nautilus-window .nautilus-grid-view {{
    background-color: @view_bg_color;
    color: @view_fg_color;
}}

/* Column Header Titles: Name, Size, Modified (Flat, clean Apple typography) */
columnview header,
columnview header > button,
columnview header button,
columnview.view > header > button,
treeview.view > header > button,
.nautilus-window columnview header,
.nautilus-window columnview header > button,
.nautilus-window columnview header button,
.nautilus-window columnview header button label {{
    color: {text_secondary};
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.3px;
    border: none;
    background: transparent;
    background-color: transparent;
    background-image: none;
    box-shadow: none;
    padding: 2px 8px;
    min-height: 22px;
}}

columnview header > button:hover,
columnview header button:hover,
columnview.view > header > button:hover,
treeview.view > header > button:hover,
.nautilus-window columnview header button:hover {{
    background: transparent;
    background-color: transparent;
    background-image: none;
    border: none;
    box-shadow: none;
    color: {text_primary};
}}

columnview header > button:active,
columnview header button:active,
columnview header button:checked,
columnview.view > header > button:active,
columnview.view > header > button:checked,
treeview.view > header > button:active,
treeview.view > header > button:checked,
.nautilus-window columnview header button:active,
.nautilus-window columnview header button:checked {{
    background: transparent;
    background-color: transparent;
    background-image: none;
    border: none;
    box-shadow: none;
    color: {text_primary};
}}

/* List View Alternating Rows & Spacing: Full width, compact macOS height */
.nautilus-window .nautilus-list-view listview.view,
#NautilusFileChooser .nautilus-list-view listview.view {{
    padding: 0;
    margin: 0;
}}

.nautilus-window .nautilus-list-view listview.view > row.activatable,
#NautilusFileChooser .nautilus-list-view listview.view > row.activatable {{
    padding: 0 4px;
    min-height: 18px;
    border-radius: 0;
    margin: 0;
    font-size: 12.5px;
}}

.nautilus-window .nautilus-list-view cell,
#NautilusFileChooser .nautilus-list-view cell {{
    min-height: 18px;
    padding: 0;
}}

.nautilus-window .nautilus-list-view listview.view > row.activatable > cell > widget#NautilusViewCell,
#NautilusFileChooser .nautilus-list-view listview.view > row.activatable > cell > widget#NautilusViewCell {{
    padding: 0 4px;
    min-height: 18px;
}}

.nautilus-window .nautilus-list-view listview.view > row.activatable:nth-child(even),
#NautilusFileChooser .nautilus-list-view listview.view > row.activatable:nth-child(even) {{
    background-color: transparent;
    background-image: none;
}}

.nautilus-window .nautilus-list-view listview.view > row.activatable:nth-child(odd):not(:selected):not(:hover),
#NautilusFileChooser .nautilus-list-view listview.view > row.activatable:nth-child(odd):not(:selected):not(:hover) {{
    background-color: {alt_row_bg};
    background-image: none;
}}

.nautilus-window .nautilus-list-view listview.view > row.activatable:hover:not(:selected),
#NautilusFileChooser .nautilus-list-view listview.view > row.activatable:hover:not(:selected) {{
    background-color: {row_hover_bg};
    background-image: none;
}}

/* Selected File Row */
.nautilus-window .nautilus-list-view listview.view > row.activatable:selected,
#NautilusFileChooser .nautilus-list-view listview.view > row.activatable:selected,
.nautilus-window .nautilus-grid-view child.activatable:selected,
#NautilusFileChooser .nautilus-grid-view child.activatable:selected {{
    background-color: @accent_bg_color;
    background-image: none;
    color: @accent_fg_color;
    border-radius: 0;
    margin: 0;
}}

.nautilus-window .nautilus-list-view listview.view > row.activatable:selected label,
.nautilus-window .nautilus-list-view listview.view > row.activatable:selected .dim-label,
.nautilus-window .nautilus-grid-view child.activatable:selected label {{
    color: #ffffff;
}}

/* Subtitle / Dim labels */
.nautilus-window .dim-label,
.nautilus-window label.subtitle,
.nautilus-window cell label:not(:first-child) {{
    color: {text_secondary};
}}

/* Star / Favorite Icon */
.nautilus-window cell button.star image {{
    color: {text_secondary};
}}

.nautilus-window cell button.star:checked image {{
    color: #f5a623;
}}

/* Pathbar Container (Transparent: prevents stretched dark box across headerbar) */
.nautilus-window .nautilus-pathbar,
#NautilusFileChooser .nautilus-pathbar {{
    background: transparent;
    background-color: transparent;
    border: none;
    box-shadow: none;
    padding: 0;
    margin: 0 4px;
}}

/* Pathbar Location Dropdown Button (Apple macOS Compact Pill) */
.nautilus-window .nautilus-pathbar button,
#NautilusFileChooser .nautilus-pathbar button {{
    border-radius: 9999px;
    background: transparent;
    background-color: rgba(255, 255, 255, 0.08);
    border: none;
    padding: 2px 10px;
    min-height: 24px;
    font-size: 13px;
    font-weight: 500;
    color: {text_primary};
    box-shadow: none;
}}

.nautilus-window .nautilus-pathbar button:hover,
#NautilusFileChooser .nautilus-pathbar button:hover {{
    background-color: rgba(255, 255, 255, 0.14);
    box-shadow: none;
}}

/* History Navigation Capsule (< | >) */
.nautilus-window headerbar > windowhandle > box > widget > box.start > stack > widget > box,
.nautilus-window headerbar > windowhandle > box > widget > box.start > box > stack > widget > box,
#NautilusFileChooser headerbar > windowhandle > box > widget > box.start > stack > widget > box,
#NautilusFileChooser headerbar > windowhandle > box > widget > box.start > box > stack > widget > box {{
    margin-left: 10px;
    padding: 2px;
    border-radius: 9999px;
    background-color: rgba(255, 255, 255, 0.08);
    border: none;
    box-shadow: none;
}}

.nautilus-window headerbar > windowhandle > box > widget > box.start > stack > widget > box > button,
.nautilus-window headerbar > windowhandle > box > widget > box.start > box > stack > widget > box > button,
#NautilusFileChooser headerbar > windowhandle > box > widget > box.start > stack > widget > box > button,
#NautilusFileChooser headerbar > windowhandle > box > widget > box.start > box > stack > widget > box > button {{
    min-height: 22px;
    min-width: 22px;
    padding: 2px 4px;
    border-radius: 9999px;
    background: transparent;
    background-color: transparent;
    border: none;
    box-shadow: none;
    color: {text_primary};
}}

.nautilus-window headerbar > windowhandle > box > widget > box.start > stack > widget > box > button:hover,
.nautilus-window headerbar > windowhandle > box > widget > box.start > box > stack > widget > box > button:hover,
#NautilusFileChooser headerbar > windowhandle > box > widget > box.start > stack > widget > box > button:hover,
#NautilusFileChooser headerbar > windowhandle > box > widget > box.start > box > stack > widget > box > button:hover {{
    background-color: rgba(255, 255, 255, 0.10);
}}

/* Dialog & Window Bottom Action Bar (Save / Cancel / New Folder / Delete) */
.dialog-action-area,
.response-area,
actionbar,
actionbar > revealer > box {{
    background-color: @headerbar_bg_color;
    border-top: 1px solid {border_color};
    padding: 8px 16px;
}}

.dialog-action-area button,
.response-area button,
actionbar button {{
    min-height: 28px;
    border-radius: 9999px;
    padding: 4px 18px;
    font-weight: 500;
}}
"""



def generate_widgets_override(is_dark=True, is_glassy=False, is_amoled=False):
    if not is_dark:
        btn_bg = "rgba(0, 0, 0, 0.05)"
        btn_hover = "rgba(0, 0, 0, 0.09)"
        btn_active = "rgba(0, 0, 0, 0.14)"
        btn_border = "0.5px solid rgba(0, 0, 0, 0.08)"
        btn_fg = "#1d1d1f"
        btn_shadow = "0 0.5px 1px rgba(0, 0, 0, 0.08)"
        dim_label = "rgba(0, 0, 0, 0.50)"
        entry_bg = "#ffffff"
        entry_border = "1px solid rgba(0, 0, 0, 0.12)"
        entry_border_hover = "rgba(0, 0, 0, 0.22)"
        hover_subtle = "rgba(0, 0, 0, 0.06)"
        active_subtle = "rgba(0, 0, 0, 0.12)"
        switch_off_bg = "rgba(0, 0, 0, 0.15)"
        scale_trough_bg = "rgba(0, 0, 0, 0.12)"
        pill_bg = "rgba(0, 0, 0, 0.06)"
        pill_hover = "rgba(0, 0, 0, 0.08)"
        pill_active = "rgba(0, 0, 0, 0.12)"
        pill_checked = "#ffffff"
        pill_checked_fg = "#1d1d1f"
        search_bg = "rgba(0, 0, 0, 0.05)"
        dropdown_bg = "rgba(0, 0, 0, 0.05)"
        dropdown_border = "0.5px solid rgba(0, 0, 0, 0.08)"
        destr_bg = "rgba(255, 59, 48, 0.12)"
        destr_fg = "#d70015"
        destr_hover = "rgba(255, 59, 48, 0.20)"
        destr_active = "rgba(255, 59, 48, 0.30)"
        dialog_ring = "rgba(0, 0, 0, 0.12)"
    else:
        btn_bg = "rgba(255, 255, 255, 0.10)"
        btn_hover = "rgba(255, 255, 255, 0.16)"
        btn_active = "rgba(255, 255, 255, 0.24)"
        btn_border = "none"
        btn_fg = "#ffffff"
        btn_shadow = "0 0.5px 1px rgba(0, 0, 0, 0.15)"
        dim_label = "rgba(255, 255, 255, 0.50)"
        entry_bg = "rgba(255, 255, 255, 0.06)"
        entry_border = "1px solid rgba(255, 255, 255, 0.08)"
        entry_border_hover = "rgba(255, 255, 255, 0.18)"
        hover_subtle = "rgba(255, 255, 255, 0.10)"
        active_subtle = "rgba(255, 255, 255, 0.18)"
        switch_off_bg = "rgba(255, 255, 255, 0.18)"
        scale_trough_bg = "rgba(255, 255, 255, 0.14)"
        pill_bg = "rgba(255, 255, 255, 0.08)"
        pill_hover = "rgba(255, 255, 255, 0.10)"
        pill_active = "rgba(255, 255, 255, 0.16)"
        pill_checked = "rgba(255, 255, 255, 0.18)"
        pill_checked_fg = "#ffffff"
        search_bg = "rgba(255, 255, 255, 0.08)"
        dropdown_bg = "rgba(255, 255, 255, 0.08)"
        dropdown_border = "none"
        destr_bg = "rgba(255, 69, 58, 0.18)"
        destr_fg = "#ff453a"
        destr_hover = "rgba(255, 69, 58, 0.28)"
        destr_active = "rgba(255, 69, 58, 0.38)"
        dialog_ring = "rgba(255, 255, 255, 0.12)"

    return f"""
/* ── Mak macOS Sonoma Refined Interactive Widgets & States ────────────────── */

/* 1. Universal In-Window Push Buttons (Dialogs, content pages, settings) */
button:not(.titlebutton):not(.close):not(.minimize):not(.maximize):not(.flat):not(.suggested-action):not(.destructive-action):not(.link):not(.image-button):not(.circular):not(.style-item):not(.card):not(checkbutton):not(.color-palette-item):not(.color-button) {{
    background-color: {btn_bg};
    background-image: none;
    border: {btn_border};
    color: {btn_fg};
    border-radius: 9999px;
    padding: 2px 12px;
    min-height: 24px;
    font-size: 13px;
    font-weight: 400;
    box-shadow: {btn_shadow};
    transition: background-color 80ms ease, color 80ms ease;
}}

button:not(.titlebutton):not(.close):not(.minimize):not(.maximize):not(.flat):not(.suggested-action):not(.destructive-action):not(.link):not(.image-button):not(.circular):not(.style-item):not(.card):not(checkbutton):not(.color-palette-item):not(.color-button):hover {{
    background-color: {btn_hover};
    color: {btn_fg};
}}

button:not(.titlebutton):not(.close):not(.minimize):not(.maximize):not(.flat):not(.suggested-action):not(.destructive-action):not(.link):not(.image-button):not(.circular):not(.style-item):not(.card):not(checkbutton):not(.color-palette-item):not(.color-button):active {{
    background-color: {btn_active};
}}

button:not(.titlebutton):not(.close):not(.minimize):not(.maximize):not(.flat):not(.suggested-action):not(.destructive-action):not(.link):not(.image-button):not(.circular):not(.style-item):not(.card):not(checkbutton):not(.color-palette-item):not(.color-button):checked {{
    background-color: @accent_bg_color;
    color: @accent_fg_color;
}}

button:not(.titlebutton):not(.close):not(.minimize):not(.maximize):not(.circular):disabled {{
    opacity: 0.35;
    box-shadow: none;
}}

/* Cards, Preference Row Buttons & Style Items (Preserve rounded rectangular geometry) */
.card,
button.card,
.card.activatable,
checkbutton.selection-mode,
.style-item,
.style-item button,
flowboxchild.card,
flowboxchild.style-item,
row.activatable {{
    border-radius: 12px;
}}

checkbutton.selection-mode:checked,
.style-item:checked,
button.card:checked {{
    border-radius: 12px;
    outline: 2px solid @accent_bg_color;
    outline-offset: 2px;
    box-shadow: none;
}}

button.circular {{
    border-radius: 9999px;
    padding: 0;
    min-width: 22px;
    min-height: 22px;
    box-shadow: none;
}}

/* Compact SpinButtons */
spinbutton {{
    min-height: 24px;
    padding: 0;
    border-radius: 9999px;
}}

spinbutton > button,
spinbutton button {{
    min-width: 22px;
    min-height: 22px;
    padding: 0;
    border-radius: 9999px;
    border: none;
    box-shadow: none;
}}

/* 2. macOS Headerbar & Titlebar Icon Buttons (Flat, borderless at rest, subtle rounded pill on hover) */
headerbar button:not(.suggested-action):not(.destructive-action):not(.titlebutton):not(.close):not(.minimize):not(.maximize),
.titlebar button:not(.suggested-action):not(.destructive-action):not(.titlebutton):not(.close):not(.minimize):not(.maximize),
window headerbar button:not(.suggested-action):not(.destructive-action):not(.titlebutton):not(.close):not(.minimize):not(.maximize),
window.csd headerbar button:not(.suggested-action):not(.destructive-action):not(.titlebutton):not(.close):not(.minimize):not(.maximize),
headerbar menubutton > button,
.titlebar menubutton > button,
headerbar menubutton.flat > button,
tab button,
.sidebar button,
popover button:not(.suggested-action):not(.destructive-action),
.kgx-window headerbar button:not(.suggested-action):not(.destructive-action),
window.kgx headerbar button:not(.suggested-action):not(.destructive-action) {{
    background: transparent;
    background-color: transparent;
    background-image: none;
    border: none;
    box-shadow: none;
    border-radius: 9999px;
    color: {btn_fg};
    min-height: 24px;
    min-width: 24px;
    padding: 2px 6px;
    margin: 0 1px;
    transition: background-color 80ms ease, color 80ms ease;
}}

headerbar button:not(.suggested-action):not(.destructive-action):not(.titlebutton):not(.close):not(.minimize):not(.maximize):hover,
.titlebar button:not(.suggested-action):not(.destructive-action):not(.titlebutton):not(.close):not(.minimize):not(.maximize):hover,
window headerbar button:not(.suggested-action):not(.destructive-action):not(.titlebutton):not(.close):not(.minimize):not(.maximize):hover,
window.csd headerbar button:not(.suggested-action):not(.destructive-action):not(.titlebutton):not(.close):not(.minimize):not(.maximize):hover,
headerbar menubutton > button:hover,
.titlebar menubutton > button:hover,
headerbar menubutton.flat > button:hover,
tab button:hover,
.sidebar button:hover,
popover button:not(.suggested-action):not(.destructive-action):hover,
.kgx-window headerbar button:not(.suggested-action):not(.destructive-action):hover,
window.kgx headerbar button:not(.suggested-action):not(.destructive-action):hover {{
    background: transparent;
    background-color: {hover_subtle};
    background-image: none;
    border: none;
    box-shadow: none;
}}

headerbar button:not(.suggested-action):not(.destructive-action):not(.titlebutton):not(.close):not(.minimize):not(.maximize):active,
.titlebar button:not(.suggested-action):not(.destructive-action):not(.titlebutton):not(.close):not(.minimize):not(.maximize):active,
window headerbar button:not(.suggested-action):not(.destructive-action):not(.titlebutton):not(.close):not(.minimize):not(.maximize):active,
window.csd headerbar button:not(.suggested-action):not(.destructive-action):not(.titlebutton):not(.close):not(.minimize):not(.maximize):active,
headerbar menubutton > button:active,
.titlebar menubutton > button:active,
headerbar menubutton.flat > button:active,
tab button:active,
.sidebar button:active,
popover button:not(.suggested-action):not(.destructive-action):active,
.kgx-window headerbar button:not(.suggested-action):not(.destructive-action):active,
window.kgx headerbar button:not(.suggested-action):not(.destructive-action):active {{
    background: transparent;
    background-color: {active_subtle};
    background-image: none;
    border: none;
    box-shadow: none;
}}

headerbar button:not(.suggested-action):not(.destructive-action):not(.titlebutton):not(.close):not(.minimize):not(.maximize):checked,
.titlebar button:not(.suggested-action):not(.destructive-action):not(.titlebutton):not(.close):not(.minimize):not(.maximize):checked,
headerbar menubutton > button:checked,
.titlebar menubutton > button:checked,
headerbar menubutton.flat > button:checked,
tab button:checked {{
    background: transparent;
    background-color: {active_subtle};
    background-image: none;
    border: none;
    color: @accent_bg_color;
    box-shadow: none;
}}

/* 3. Headerbar Segmented Controls, Split Buttons & Linked Controls */
headerbar splitbutton,
.titlebar splitbutton,
headerbar .linked,
.titlebar .linked,
headerbar box.linked,
.titlebar box.linked,
headerbar stackswitcher,
.titlebar stackswitcher,
headerbar viewswitcher,
.titlebar viewswitcher,
.kgx-window headerbar splitbutton,
window.kgx headerbar splitbutton,
.kgx-window headerbar .linked,
window.kgx headerbar .linked {{
    background-color: {pill_bg};
    background-image: none;
    border: none;
    box-shadow: none;
    border-radius: 9999px;
    margin: 0 3px;
    padding: 2px;
}}

headerbar splitbutton > button,
headerbar splitbutton > menubutton > button,
headerbar .linked > button,
headerbar .linked > menubutton > button,
headerbar box.linked > button,
headerbar box.linked > menubutton > button,
headerbar stackswitcher > button,
headerbar viewswitcher > button,
.kgx-window headerbar splitbutton > button,
.kgx-window headerbar splitbutton > menubutton > button,
window.kgx headerbar splitbutton > button,
window.kgx headerbar splitbutton > menubutton > button {{
    min-height: 22px;
    min-width: 22px;
    padding: 2px 8px;
    border-radius: 9999px;
    background: transparent;
    background-color: transparent;
    background-image: none;
    border: none;
    box-shadow: none;
    color: {btn_fg};
    transition: background-color 80ms ease;
}}

headerbar splitbutton > button:hover,
headerbar splitbutton > menubutton > button:hover,
headerbar .linked > button:hover,
headerbar .linked > menubutton > button:hover,
headerbar box.linked > button:hover,
headerbar box.linked > menubutton > button:hover,
headerbar stackswitcher > button:hover,
headerbar viewswitcher > button:hover,
.kgx-window headerbar splitbutton > button:hover,
.kgx-window headerbar splitbutton > menubutton > button:hover,
window.kgx headerbar splitbutton > button:hover,
window.kgx headerbar splitbutton > menubutton > button:hover {{
    background-color: {pill_hover};
    background-image: none;
    border: none;
    box-shadow: none;
}}

headerbar splitbutton > button:active,
headerbar splitbutton > menubutton > button:active,
headerbar .linked > button:active,
headerbar .linked > menubutton > button:active,
headerbar box.linked > button:active,
headerbar box.linked > menubutton > button:active,
.kgx-window headerbar splitbutton > button:active,
.kgx-window headerbar splitbutton > menubutton > button:active,
window.kgx headerbar splitbutton > button:active,
window.kgx headerbar splitbutton > menubutton > button:active {{
    background-color: {pill_active};
    background-image: none;
    border: none;
    box-shadow: none;
}}

/* Segmented Control Active / Selected Segment (Apple Elevated Plate) */
headerbar .linked > button:checked,
headerbar box.linked > button:checked,
headerbar stackswitcher > button:checked,
headerbar viewswitcher > button:checked {{
    background-color: {pill_checked};
    background-image: none;
    border: none;
    color: {pill_checked_fg};
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.20);
    border-radius: 9999px;
}}

/* 5. Flat Buttons */
button.flat:not(.titlebutton):not(.close):not(.minimize):not(.maximize):not(.card):not(.style-item) {{
    background-color: transparent;
    background-image: none;
    border: none;
    box-shadow: none;
    border-radius: 9999px;
    transition: background-color 80ms ease, color 80ms ease;
}}

button.flat:not(.titlebutton):not(.close):not(.minimize):not(.maximize):not(.card):not(.style-item):hover {{
    background-color: {hover_subtle};
}}

button.flat:not(.titlebutton):not(.close):not(.minimize):not(.maximize):not(.card):not(.style-item):active {{
    background-color: {active_subtle};
}}

button.flat:not(.titlebutton):not(.close):not(.minimize):not(.maximize):not(.card):not(.style-item):checked {{
    background-color: {active_subtle};
    color: @accent_bg_color;
}}

/* 6. Action Buttons */
button.suggested-action {{
    background-color: @accent_bg_color;
    color: @accent_fg_color;
    border: none;
    border-radius: 9999px;
    padding: 2px 14px;
    min-height: 24px;
    font-size: 13px;
    font-weight: 500;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.20);
}}

button.suggested-action:hover {{
    background-color: alpha(@accent_bg_color, 0.88);
    background-image: none;
}}

button.suggested-action:active {{
    background-color: alpha(@accent_bg_color, 0.72);
    background-image: none;
}}

button.destructive-action {{
    background-color: {destr_bg};
    color: {destr_fg};
    border: none;
    border-radius: 9999px;
    padding: 2px 14px;
    min-height: 24px;
    font-size: 13px;
    font-weight: 500;
    transition: background-color 100ms ease;
}}

button.destructive-action:hover {{
    background-color: {destr_hover};
}}

button.destructive-action:active {{
    background-color: {destr_active};
}}

/* 7. Dropdowns & Combo Boxes (In content views / forms) */
dropdown,
combobox,
row.combo {{
    border-radius: 9999px;
}}

box.content dropdown > button,
preferencespage dropdown > button,
dialog dropdown > button,
row.combo dropdown > button,
combobox > box > button.combo,
box.content menubutton:not(.flat) > button,
preferencespage menubutton:not(.flat) > button {{
    background-color: {dropdown_bg};
    border: {dropdown_border};
    color: {btn_fg};
    border-radius: 9999px;
    padding: 3px 10px;
    min-height: 24px;
    box-shadow: {btn_shadow};
    transition: background-color 100ms ease;
}}

box.content dropdown > button:hover,
preferencespage dropdown > button:hover,
dialog dropdown > button:hover,
row.combo dropdown > button:hover,
combobox > box > button.combo:hover,
box.content menubutton:not(.flat) > button:hover,
preferencespage menubutton:not(.flat) > button:hover {{
    background-color: {btn_hover};
}}

box.content dropdown > button:active,
preferencespage dropdown > button:active,
dialog dropdown > button:active,
row.combo dropdown > button:active,
combobox > box > button.combo:active,
box.content menubutton:not(.flat) > button:active,
preferencespage menubutton:not(.flat) > button:active {{
    background-color: {btn_active};
}}

headerbar dropdown > button {{
    background-color: transparent;
    background-image: none;
    border: none;
    box-shadow: none;
}}

dropdown arrow,
combobox arrow {{
    color: {dim_label};
    min-width: 12px;
    min-height: 12px;
}}

box.content dropdown > button:focus,
preferencespage dropdown > button:focus,
dialog dropdown > button:focus,
row.combo dropdown > button:focus,
combobox > box > button.combo:focus {{
    border-color: @accent_bg_color;
    outline: 2px solid @accent_bg_color;
    outline-offset: -1px;
    box-shadow: 0 0 0 3px alpha(@accent_bg_color, 0.35);
}}

/* 8. Text Entries */
entry {{
    background-color: {entry_bg};
    border: {entry_border};
    border-radius: 6px;
    padding: 3px 8px;
    min-height: 24px;
    color: {btn_fg};
    caret-color: @accent_bg_color;
    box-shadow: none;
    transition: border-color 120ms ease, box-shadow 120ms ease;
}}

entry:hover {{
    border-color: {entry_border_hover};
}}

entry:focus,
entry:focus-within {{
    border-color: @accent_bg_color;
    outline: 2px solid @accent_bg_color;
    outline-offset: -1px;
    box-shadow: 0 0 0 3px alpha(@accent_bg_color, 0.35);
}}

entry.search,
searchbar entry,
headerbar searchbar entry {{
    border-radius: 9999px;
    border: none;
    background-color: {search_bg};
    padding: 3px 12px;
    min-height: 24px;
    box-shadow: none;
}}

entry.search:focus,
searchbar entry:focus,
headerbar searchbar entry:focus {{
    outline: 2px solid @accent_bg_color;
    outline-offset: -1px;
    box-shadow: 0 0 0 3px alpha(@accent_bg_color, 0.35);
}}

/* 9. Switches */
switch {{
    border-radius: 9999px;
    min-width: 40px;
    min-height: 22px;
    background-color: {switch_off_bg};
    border: 1px solid rgba(255, 255, 255, 0.08);
    transition: background-color 160ms ease, border-color 160ms ease;
}}

switch:checked {{
    background-color: @accent_bg_color;
    border-color: rgba(0, 0, 0, 0.15);
}}

switch > slider {{
    min-width: 18px;
    min-height: 18px;
    margin: 1px;
    border-radius: 9999px;
    background-color: #ffffff;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.28);
    border: none;
}}

/* 10. Checkboxes & Radio Buttons */
check {{
    border-radius: 4px;
    border: 1px solid {entry_border_hover};
    min-width: 16px;
    min-height: 16px;
    background-color: {entry_bg};
    color: transparent;
    transition: background-color 100ms ease, border-color 100ms ease;
}}

check:checked {{
    background-color: @accent_bg_color;
    border-color: @accent_bg_color;
    color: @accent_fg_color;
}}

radio {{
    border-radius: 9999px;
    border: 1px solid {entry_border_hover};
    min-width: 16px;
    min-height: 16px;
    background-color: {entry_bg};
    color: transparent;
    transition: background-color 100ms ease, border-color 100ms ease;
}}

radio:checked {{
    background-color: @accent_bg_color;
    border-color: @accent_bg_color;
    color: @accent_fg_color;
}}

/* 11. Sliders (GtkScale) */
scale trough {{
    background-color: {scale_trough_bg};
    border-radius: 9999px;
    min-height: 5px;
}}

scale highlight {{
    background-color: @accent_bg_color;
    border-radius: 9999px;
}}

scale slider {{
    min-width: 18px;
    min-height: 18px;
    border-radius: 9999px;
    background-color: #ffffff;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.25);
    border: 1px solid rgba(0, 0, 0, 0.12);
}}

/* 12. Interactive List Rows */
list > row.activatable:hover,
listview > row.activatable:hover,
columnview row:hover {{
    background-color: {hover_subtle};
}}

list > row.activatable:active,
listview > row.activatable:active {{
    background-color: {active_subtle};
}}

list > row.activatable:selected,
listview > row.activatable:selected {{
    background-color: @accent_bg_color;
    color: @accent_fg_color;
}}

/* 13. Stack Switchers / Segmented Controls */
stackswitcher {{
    border-radius: 9999px;
    padding: 2px;
    background-color: {pill_bg};
    border: none;
    box-shadow: none;
}}

stackswitcher > button {{
    border-radius: 9999px;
    padding: 2px 12px;
    min-height: 22px;
    background-color: transparent;
    border: none;
    box-shadow: none;
    color: {btn_fg};
}}

stackswitcher > button:hover {{
    background-color: {pill_hover};
}}

stackswitcher > button:checked {{
    background-color: {pill_checked};
    color: {pill_checked_fg};
    font-weight: 500;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.20);
    border-radius: 9999px;
}}

/* 14. Minimal macOS Scrollbars */
scrollbar trough {{
    background: transparent;
    border: none;
}}

scrollbar slider {{
    border-radius: 9999px;
    min-width: 6px;
    min-height: 6px;
    background-color: {dim_label};
    border: 2px solid transparent;
    background-clip: padding-box;
    transition: background-color 120ms ease;
}}

scrollbar slider:hover {{
    background-color: {btn_fg};
}}

/* 15. macOS Alerts, Sheets & Dialog Boxes */
window.dialog,
dialog,
messagedialog,
.messagedialog,
window.message {{
    border-radius: 18px;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.35), 0 3px 10px rgba(0, 0, 0, 0.16), 0 0 0 1px {dialog_ring};
}}

window.dialog headerbar,
dialog headerbar,
messagedialog headerbar {{
    border-top-left-radius: 18px;
    border-top-right-radius: 18px;
}}

window.dialog .dialog-action-area button,
dialog .dialog-action-area button,
messagedialog .dialog-action-area button,
window.dialog .response-area button,
dialog .response-area button,
messagedialog .response-area button {{
    min-height: 30px;
    border-radius: 9999px;
    padding: 4px 18px;
    font-weight: 500;
}}
"""


def inject_theme_css(src_css_path, dst_css_path, palette, is_glassy, button_size=14, button_spacing=8, chromium_accent=None, is_dark=True):
    try:
        with open(src_css_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        content = ""

    color_keys = [
        "window_bg_color", "window_fg_color", "view_bg_color", "view_fg_color",
        "headerbar_bg_color", "headerbar_solid_bg", "headerbar_fg_color", "headerbar_border_color",
        "sidebar_bg_color", "sidebar_fg_color", "secondary_sidebar_bg_color",
        "card_bg_color", "card_fg_color", "dialog_bg_color", "dialog_fg_color",
        "popover_bg_color", "popover_fg_color", "placeholder_text_color",
        "accent_bg_color", "accent_fg_color", "accent_color",
        "theme_selected_bg_color", "selected_bg_color"
    ]
    lines = content.splitlines()
    filtered = []
    for line in lines:
        stripped = line.strip()
        if any(stripped.startswith(f"@define-color {k} ") for k in color_keys):
            continue
        if "#9A57A3" in line or "#9a57a3" in line:
            line = line.replace("#9A57A3", "@accent_bg_color").replace("#9a57a3", "@accent_bg_color")
        filtered.append(line)

    curr_acc = "blue"
    try:
        res = subprocess.run(["gsettings", "get", "org.gnome.desktop.interface", "accent-color"],
                             capture_output=True, text=True)
        curr_acc = res.stdout.strip().strip("'\"") or "blue"
    except Exception:
        curr_acc = "blue"

    acc_info = GNOME_ACCENT_PALETTES.get(curr_acc, GNOME_ACCENT_PALETTES["blue"])
    acc_bg = acc_info["bg"]
    acc_fg = acc_info["fg"]

    accent_css_override = f"""
/* ── Dynamic GNOME Desktop Accent Synchronization ─────────────────────── */
@define-color accent_color {acc_bg};
@define-color accent_bg_color {acc_bg};
@define-color accent_fg_color {acc_fg};
@define-color theme_selected_bg_color {acc_bg};
@define-color selected_bg_color {acc_bg};
"""

    is_amoled = "amoled" in dst_css_path.lower() or "amoled" in palette.lower()
    widgets_override = generate_widgets_override(is_dark=is_dark, is_glassy=is_glassy, is_amoled=is_amoled)
    traffic_override = generate_traffic_lights_override(button_size, button_spacing, chromium_accent=chromium_accent, is_dark=is_dark)
    popover_override = generate_popover_override(is_dark=is_dark)
    nautilus_override = generate_nautilus_override(is_dark=is_dark)
    window_corners_override = generate_window_corners_override(is_dark=is_dark)
    rules_to_append = [widgets_override, window_corners_override, popover_override, nautilus_override, traffic_override]
    if is_glassy:
        rules_to_append.append(GLASSY_CONTAINER_RULES)

    final_content = palette.strip() + "\n\n" + accent_css_override.strip() + "\n\n" + "\n".join(filtered) + "\n\n" + "\n\n".join(rules_to_append) + "\n"
    with open(dst_css_path, "w", encoding="utf-8") as f:
        f.write(final_content)


def update_titlebar_buttons(button_size=None, button_spacing=None, chromium_accent=None):
    """Dynamically regenerates GTK 4 and GTK 3 active CSS configurations with the new traffic light button size, spacing, and Chromium accent."""
    if button_size is None:
        try:
            res = subprocess.run(["gsettings", "get", "org.gnome.shell.extensions.mak", "titlebar-button-size"],
                                 capture_output=True, text=True)
            button_size = int(res.stdout.strip())
        except Exception:
            button_size = 14

    if button_spacing is None:
        try:
            res = subprocess.run(["gsettings", "get", "org.gnome.shell.extensions.mak", "titlebar-button-spacing"],
                                 capture_output=True, text=True)
            button_spacing = int(res_spacing.stdout.strip()) if 'res_spacing' in locals() else int(res.stdout.strip())
        except Exception:
            button_spacing = 8

    if chromium_accent is None:
        try:
            res = subprocess.run(["gsettings", "get", "org.gnome.shell.extensions.mak", "chromium-topbar-accent"],
                                 capture_output=True, text=True)
            chromium_accent = res.stdout.strip().strip("'\"")
        except Exception:
            chromium_accent = "default"

    theme_key = get_current_theme()
    theme_info = THEMES.get(theme_key, THEMES["dark"])
    theme_name = theme_info["theme_name"]
    source_dir = os.path.join(THEMES_DIR, theme_name)
    is_glassy = theme_info.get("is_glassy", False)
    is_dark = theme_info.get("is_dark", True)

    palette_map = {
        "dark": GRAPHITE_PALETTE_OVERRIDE,
        "dark-glassy": GRAPHITE_GLASSY_PALETTE_OVERRIDE,
        "amoled": AMOLED_PALETTE_OVERRIDE,
        "amoled-glassy": AMOLED_GLASSY_PALETTE_OVERRIDE,
        "light": LIGHT_PALETTE_OVERRIDE,
        "light-glassy": LIGHT_GLASSY_PALETTE_OVERRIDE,
    }
    palette_override = palette_map.get(theme_key, GRAPHITE_PALETTE_OVERRIDE)

    # GTK 4
    src_gtk4 = os.path.join(source_dir, "gtk-4.0")
    if os.path.exists(src_gtk4):
        for css_file in ["gtk.css", "gtk-dark.css"]:
            src_css = os.path.join(src_gtk4, css_file)
            dst_css = os.path.join(GTK4_CONFIG, css_file)
            if os.path.exists(src_css):
                inject_theme_css(src_css, dst_css, palette_override, is_glassy, button_size, button_spacing, chromium_accent=chromium_accent, is_dark=is_dark)

    # GTK 3
    src_gtk3 = os.path.join(source_dir, "gtk-3.0")
    if os.path.exists(src_gtk3):
        for css_file in ["gtk.css", "gtk-dark.css"]:
            src_css = os.path.join(src_gtk3, css_file)
            dst_css = os.path.join(GTK3_CONFIG, css_file)
            if os.path.exists(src_css):
                inject_theme_css(src_css, dst_css, palette_override, is_glassy, button_size, button_spacing, chromium_accent=chromium_accent, is_dark=is_dark)

    ensure_settings_ini_decoration_layout()

def update_desktop_accent(accent_name):
    """Updates the desktop accent across GNOME interface, icon theme, and regenerated GTK stylesheets."""
    if not accent_name:
        return
    theme_key = get_current_theme()
    theme_info = THEMES.get(theme_key, THEMES["dark"])
    is_dark = theme_info.get("is_dark", True)
    icon_theme = get_icon_theme_for_accent(accent_name, is_dark)
    try:
        subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "accent-color", accent_name], check=False)
        subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "icon-theme", icon_theme], check=False)
    except Exception:
        pass
    update_titlebar_buttons()

update_titlebar_button_size = update_titlebar_buttons

def ensure_settings_ini_decoration_layout():
    """Ensures gtk-decoration-layout=close,minimize,maximize: is explicitly set in GTK3 and GTK4 settings.ini."""
    for cfg_dir in [GTK3_CONFIG, GTK4_CONFIG]:
        try:
            os.makedirs(cfg_dir, exist_ok=True)
            ini_path = os.path.join(cfg_dir, "settings.ini")
            lines = []
            if os.path.exists(ini_path):
                with open(ini_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
            new_lines = []
            has_layout = False
            for line in lines:
                if line.startswith("gtk-decoration-layout="):
                    new_lines.append("gtk-decoration-layout=close,minimize,maximize:\n")
                    has_layout = True
                else:
                    new_lines.append(line)
            if not has_layout:
                if not any(l.strip() == "[Settings]" for l in new_lines):
                    new_lines.insert(0, "[Settings]\n")
                new_lines.append("gtk-decoration-layout=close,minimize,maximize:\n")
            with open(ini_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
        except Exception:
            pass


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
        is_glassy = "glassy" in current.lower()
        if "amoled" in current.lower():
            return "amoled-glassy" if is_glassy else "amoled"
        if "light" in current.lower():
            return "light-glassy" if is_glassy else "light"
        return "dark-glassy" if is_glassy else "dark"
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
    is_dark = theme_info["is_dark"]
    curr_acc = "blue"
    try:
        res = subprocess.run(["gsettings", "get", "org.gnome.desktop.interface", "accent-color"],
                             capture_output=True, text=True)
        curr_acc = res.stdout.strip().strip("'\"") or "blue"
    except Exception:
        pass
    icon_theme = get_icon_theme_for_accent(curr_acc, is_dark)
    cursor_theme = theme_info.get("cursor_theme", "MacTahoe-dark")
    source_dir = os.path.join(THEMES_DIR, theme_name)

    log = []

    # 1. GNOME Desktop Interface GSettings
    try:
        subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "gtk-theme", theme_name], check=True)
        subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "color-scheme", color_scheme], check=True)
        subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "icon-theme", icon_theme], check=True)
        subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "cursor-theme", cursor_theme], check=True)
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
        palette_map = {
            "dark": GRAPHITE_PALETTE_OVERRIDE,
            "dark-glassy": GRAPHITE_GLASSY_PALETTE_OVERRIDE,
            "amoled": AMOLED_PALETTE_OVERRIDE,
            "amoled-glassy": AMOLED_GLASSY_PALETTE_OVERRIDE,
            "light": LIGHT_PALETTE_OVERRIDE,
            "light-glassy": LIGHT_GLASSY_PALETTE_OVERRIDE,
        }
        palette_override = palette_map.get(theme_key, GRAPHITE_PALETTE_OVERRIDE)

        is_glassy = theme_info["is_glassy"]
        try:
            res = subprocess.run(["gsettings", "get", "org.gnome.shell.extensions.mak", "titlebar-button-size"],
                                 capture_output=True, text=True)
            button_size = int(res.stdout.strip())
        except Exception:
            button_size = 14

        try:
            res_sp = subprocess.run(["gsettings", "get", "org.gnome.shell.extensions.mak", "titlebar-button-spacing"],
                                    capture_output=True, text=True)
            button_spacing = int(res_sp.stdout.strip())
        except Exception:
            button_spacing = 8

        try:
            res_acc = subprocess.run(["gsettings", "get", "org.gnome.shell.extensions.mak", "chromium-topbar-accent"],
                                     capture_output=True, text=True)
            chromium_accent = res_acc.stdout.strip().strip("'\"")
        except Exception:
            chromium_accent = "default"

        if os.path.exists(src_gtk4):
            # Generate gtk.css and gtk-dark.css with exact palette at top, no duplicate defines, and clean overrides
            for css_file in ["gtk.css", "gtk-dark.css"]:
                src_css = os.path.join(src_gtk4, css_file)
                dst_css = os.path.join(GTK4_CONFIG, css_file)
                if os.path.exists(src_css):
                    inject_theme_css(src_css, dst_css, palette_override, is_glassy, button_size, button_spacing, chromium_accent=chromium_accent, is_dark=is_dark)

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
                    f"gtk-decoration-layout=close,minimize,maximize:\n"
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
                    inject_theme_css(src_css, dst_css, palette_override, is_glassy, button_size, button_spacing, chromium_accent=chromium_accent, is_dark=is_dark)

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
        has_layout = False
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
            elif line.startswith("gtk-decoration-layout="):
                new_lines.append("gtk-decoration-layout=close,minimize,maximize:\n")
                has_layout = True
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
        if not has_layout:
            new_lines.append("gtk-decoration-layout=close,minimize,maximize:\n")

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
        w_border = theme_info.get("window_border_color", "rgba(255, 255, 255, 0.16)")
        m = re.match(r"rgba?\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)(?:\s*,\s*([\d.]+))?\)", str(w_border))
        if m:
            r = round(float(m.group(1)) / 255.0, 3)
            g = round(float(m.group(2)) / 255.0, 3)
            b = round(float(m.group(3)) / 255.0, 3)
            a = round(float(m.group(4)) if m.group(4) is not None else 1.0, 3)
            tuple_str = f"({r}, {g}, {b}, {a})"
        else:
            tuple_str = "(1.0, 1.0, 1.0, 0.16)"

        new_val = f"{{'padding': <{{'left': uint32 0, 'right': 0, 'top': 0, 'bottom': 0}}>, 'keepRoundedCorners': <{{'maximized': true, 'fullscreen': true}}>, 'borderRadius': <uint32 16>, 'smoothing': <0.8>, 'borderColor': <{tuple_str}>, 'enabled': <true>}}"
        subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.rounded-window-corners-reborn", "global-rounded-corner-settings", new_val], check=False)
        subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.rounded-window-corners-reborn", "border-width", "1"], check=False)
        subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.rounded-window-corners-reborn", "skip-libadwaita-app", "true"], check=False)
        subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.rounded-window-corners-reborn", "skip-libhandy-app", "true"], check=False)
        subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.mak", "corner-border-color", w_border], check=False)
        log.append(f"Updated window corner settings (radius 16, smoothing 0.8, border {w_border}, skip-libadwaita true).")
    except Exception as e:
        log.append(f"Error updating window corners border: {e}")

    # 9. Sync Application Translucency / Blur (Blur-my-shell & Liquid Glass)
    try:
        if is_glassy:
            subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.blur-my-shell.applications", "blur", "true"], check=False)
            subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.blur-my-shell.applications", "opacity", "215"], check=False)
            subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.liquid-glass@thinkingcoding1231.gmail.com", "enable-application-glass", "true"], check=False)
            subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.liquid-glass@thinkingcoding1231.gmail.com", "application-glass-all-windows", "true"], check=False)
            subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.liquid-glass@thinkingcoding1231.gmail.com", "application-content-opacity", "0.85"], check=False)
        else:
            subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.blur-my-shell.applications", "blur", "false"], check=False)
            subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.blur-my-shell.applications", "opacity", "255"], check=False)
            subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.liquid-glass@thinkingcoding1231.gmail.com", "enable-application-glass", "false"], check=False)
            subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.liquid-glass@thinkingcoding1231.gmail.com", "application-glass-all-windows", "false"], check=False)
            subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.liquid-glass@thinkingcoding1231.gmail.com", "application-content-opacity", "1.0"], check=False)
        log.append(f"Set application blur & glass to {'enabled (translucent)' if is_glassy else 'disabled (solid opaque)'}.")
    except Exception as e:
        log.append(f"Error syncing application blur & glass: {e}")

    return {
        "success": True,
        "theme": theme_name,
        "log": log
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--accent":
        acc = sys.argv[2] if len(sys.argv) > 2 else "default"
        subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.mak", "chromium-topbar-accent", acc], check=False)
        update_titlebar_buttons(chromium_accent=acc)
        print(f"Updated Chromium topbar accent to {acc}")
    elif len(sys.argv) > 1 and sys.argv[1] == "--buttons":
        bsize = int(sys.argv[2]) if len(sys.argv) > 2 else 14
        bspacing = int(sys.argv[3]) if len(sys.argv) > 3 else 8
        subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.mak", "titlebar-button-size", str(bsize)], check=False)
        subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.mak", "titlebar-button-spacing", str(bspacing)], check=False)
        update_titlebar_buttons(button_size=bsize, button_spacing=bspacing)
        print(f"Updated titlebar buttons to size={bsize}, spacing={bspacing}")
    else:
        t = sys.argv[1] if len(sys.argv) > 1 else "dark"
        res = apply_global_theme(t)
        print(res)
