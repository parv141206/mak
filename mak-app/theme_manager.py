# SPDX-License-Identifier: GPL-3.0-or-later
# Mak Theme Manager: Global Theme Synchronizer across Shell, GTK 2/3/4, and Flatpak

import os
import sys
import json
import subprocess
import shutil

class TokenManager:
    """
    Unified Design Token Manager for Mak.
    Loads tokens from docs/fidelity/tokens.json with built-in fallbacks.
    Central source of truth across GTK 4, GTK 3, GTK 2, and GNOME Shell.
    """
    _tokens = None

    @classmethod
    def load(cls):
        if cls._tokens is not None:
            return cls._tokens
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        token_path = os.path.join(repo_root, "docs", "fidelity", "tokens.json")
        if os.path.exists(token_path):
            try:
                with open(token_path, "r", encoding="utf-8") as f:
                    cls._tokens = json.load(f)
                    return cls._tokens
            except Exception:
                pass
        cls._tokens = {
            "geometry": {
                "window": {"corner_radius": 14, "headerbar_standard_height": 52, "headerbar_compact_height": 38},
                "traffic_lights": {"size": 14, "spacing": 8, "margin_left": 13},
                "buttons": {"height_regular": 24, "corner_radius": 5, "capsule_corner_radius": 9999},
                "segmented": {"height": 22, "container_radius": 6, "segment_radius": 5},
                "entries": {"height_regular": 22, "corner_radius": 5, "focus_ring_width": 3},
                "menus": {"row_height": 24, "item_radius": 4},
                "popovers": {"corner_radius": 10},
                "sidebars": {"row_height": 32, "corner_radius": 5},
                "lists": {"row_height": 24, "column_header_height": 28},
                "dialogs": {"corner_radius": 20, "button_height": 26, "button_radius": 9999},
                "group_boxes": {"corner_radius": 10},
                "color_wells": {"height": 22, "corner_radius": 4},
                "notifications": {"corner_radius": 16, "padding": 14}
            },
            "colors": {
                "traffic_close": "#ff5c60",
                "traffic_minimize": "#fac800",
                "traffic_maximize": "#35c759"
            }
        }
        return cls._tokens

    @classmethod
    def get(cls, *keys, default=None):
        data = cls.load()
        for k in keys:
            if isinstance(data, dict) and k in data:
                data = data[k]
            else:
                return default
        return data

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
@define-color view_bg_color #1c1c1e;
@define-color view_fg_color #f5f5f7;
@define-color headerbar_bg_color #242426;
@define-color headerbar_solid_bg #242426;
@define-color headerbar_fg_color #ffffff;
@define-color headerbar_border_color rgba(255, 255, 255, 0.12);
@define-color sidebar_bg_color #242426;
@define-color sidebar_fg_color #f5f5f7;
@define-color secondary_sidebar_bg_color #242426;
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
@define-color window_bg_color rgba(36, 36, 38, 0.75);
@define-color window_fg_color #f5f5f7;
@define-color view_bg_color rgba(28, 28, 30, 0.68);
@define-color view_fg_color #f5f5f7;
@define-color headerbar_bg_color rgba(36, 36, 38, 0.75);
@define-color headerbar_solid_bg #242426;
@define-color headerbar_fg_color #ffffff;
@define-color headerbar_border_color rgba(255, 255, 255, 0.12);
@define-color sidebar_bg_color rgba(36, 36, 38, 0.75);
@define-color sidebar_fg_color #f5f5f7;
@define-color secondary_sidebar_bg_color rgba(36, 36, 38, 0.75);
@define-color card_bg_color rgba(44, 44, 48, 0.72);
@define-color card_fg_color #f5f5f7;
@define-color dialog_bg_color rgba(40, 40, 46, 0.82);
@define-color dialog_fg_color #f5f5f7;
@define-color popover_bg_color rgba(44, 44, 48, 0.82);
@define-color popover_fg_color #f5f5f7;
@define-color placeholder_text_color rgba(255, 255, 255, 0.45);
"""

AMOLED_PALETTE_OVERRIDE = """
/* ── Mak macOS Deep Obsidian Dark Palette (Pitch Black AMOLED) ────────────── */
@define-color window_bg_color #000000;
@define-color window_fg_color #f5f5f7;
@define-color view_bg_color #000000;
@define-color view_fg_color #f5f5f7;
@define-color headerbar_bg_color #0a0a0c;
@define-color headerbar_solid_bg #0a0a0c;
@define-color headerbar_fg_color #ffffff;
@define-color headerbar_border_color rgba(255, 255, 255, 0.12);
@define-color sidebar_bg_color #0a0a0c;
@define-color sidebar_fg_color #f5f5f7;
@define-color secondary_sidebar_bg_color #0a0a0c;
@define-color card_bg_color #121214;
@define-color card_fg_color #f5f5f7;
@define-color dialog_bg_color #121214;
@define-color dialog_fg_color #f5f5f7;
@define-color popover_bg_color #141416;
@define-color popover_fg_color #f5f5f7;
@define-color placeholder_text_color rgba(255, 255, 255, 0.45);
"""

AMOLED_GLASSY_PALETTE_OVERRIDE = """
/* ── Mak macOS Deep Obsidian Glass Translucent Palette ────────────────────── */
@define-color window_bg_color rgba(10, 10, 12, 0.82);
@define-color window_fg_color #f5f5f7;
@define-color view_bg_color rgba(0, 0, 0, 0.75);
@define-color view_fg_color #f5f5f7;
@define-color headerbar_bg_color rgba(10, 10, 12, 0.82);
@define-color headerbar_solid_bg #0a0a0c;
@define-color headerbar_fg_color #ffffff;
@define-color headerbar_border_color rgba(255, 255, 255, 0.12);
@define-color sidebar_bg_color rgba(10, 10, 12, 0.82);
@define-color sidebar_fg_color #f5f5f7;
@define-color secondary_sidebar_bg_color rgba(10, 10, 12, 0.82);
@define-color card_bg_color rgba(18, 18, 22, 0.75);
@define-color dialog_bg_color rgba(18, 18, 22, 0.85);
@define-color popover_bg_color rgba(18, 18, 22, 0.88);
@define-color popover_fg_color #f5f5f7;
@define-color placeholder_text_color rgba(255, 255, 255, 0.45);
"""

LIGHT_PALETTE_OVERRIDE = """
/* ── Mak macOS Crisp Apple Light Palette ─────────────────────────────────── */
@define-color window_bg_color #ececf0;
@define-color window_fg_color #1d1d1f;
@define-color view_bg_color #ffffff;
@define-color view_fg_color #1d1d1f;
@define-color headerbar_bg_color #ececf0;
@define-color headerbar_solid_bg #ececf0;
@define-color headerbar_fg_color #1d1d1f;
@define-color headerbar_border_color rgba(0, 0, 0, 0.10);
@define-color sidebar_bg_color #ececf0;
@define-color sidebar_fg_color #1d1d1f;
@define-color secondary_sidebar_bg_color #ececf0;
@define-color card_bg_color #ffffff;
@define-color card_fg_color #1d1d1f;
@define-color dialog_bg_color #ebebef;
@define-color dialog_fg_color #1d1d1f;
@define-color popover_bg_color #ffffff;
@define-color popover_fg_color #1d1d1f;
@define-color placeholder_text_color rgba(0, 0, 0, 0.45);
"""

LIGHT_GLASSY_PALETTE_OVERRIDE = """
/* ── Mak macOS Crisp Apple Frosted Glass Translucent Palette ──────────────── */
@define-color window_bg_color rgba(236, 236, 240, 0.78);
@define-color window_fg_color #1d1d1f;
@define-color view_bg_color rgba(255, 255, 255, 0.72);
@define-color view_fg_color #1d1d1f;
@define-color headerbar_bg_color rgba(236, 236, 240, 0.78);
@define-color headerbar_solid_bg #ececf0;
@define-color headerbar_fg_color #1d1d1f;
@define-color headerbar_border_color rgba(0, 0, 0, 0.10);
@define-color sidebar_bg_color rgba(236, 236, 240, 0.78);
@define-color sidebar_fg_color #1d1d1f;
@define-color secondary_sidebar_bg_color rgba(236, 236, 240, 0.78);
@define-color card_bg_color rgba(255, 255, 255, 0.78);
@define-color card_fg_color #1d1d1f;
@define-color dialog_bg_color rgba(235, 235, 239, 0.85);
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
    backdrop_bg = "rgba(255, 255, 255, 0.17)" if is_dark else "rgba(0, 0, 0, 0.13)"
    margin_left = TokenManager.get("geometry", "traffic_lights", "margin_left", default=13)

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
    margin-left: {margin_left}px;
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
window.background.csd windowcontrols button:focus,
window.background.csd windowcontrols button:checked,
window.background.csd windowcontrols button:backdrop,
window.background.csd windowcontrols button:backdrop:hover,
window.background.csd windowcontrols > button,
window.background.csd windowcontrols > button:hover,
window.background.csd windowcontrols > button:active,
window.background.csd windowcontrols > button:focus,
window.background.csd windowcontrols > button:checked,
window.background.csd windowcontrols > button:backdrop,
window.background.csd windowcontrols > button:backdrop:hover,
window.background.csd windowcontrols button.titlebutton,
window.background.csd windowcontrols button.titlebutton:hover,
window.background.csd windowcontrols button.titlebutton:active,
window.background.csd windowcontrols button.titlebutton:focus,
window.background.csd windowcontrols button.titlebutton:checked,
window.background.csd windowcontrols button.titlebutton:backdrop,
window.background.csd windowcontrols button.titlebutton:backdrop:hover,
windowcontrols > button,
windowcontrols > button:hover,
windowcontrols > button:active,
windowcontrols > button:focus,
windowcontrols > button:checked,
windowcontrols > button:backdrop,
headerbar windowcontrols > button,
headerbar windowcontrols > button:hover,
headerbar windowcontrols > button:active,
headerbar windowcontrols > button:focus,
headerbar windowcontrols > button:checked,
headerbar windowcontrols > button:backdrop,
.titlebar windowcontrols > button,
.titlebar windowcontrols > button:hover,
.titlebar windowcontrols > button:active,
.titlebar windowcontrols > button:focus,
.titlebar windowcontrols > button:checked,
headerbar button.titlebutton:focus,
headerbar button.titlebutton:checked,
button.titlebutton:focus,
button.titlebutton:checked,
button.close:focus,
button.close:checked,
button.maximize:focus,
button.maximize:checked,
button.minimize:focus,
button.minimize:checked {{
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
    outline-style: none;
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
    window_radius = TokenManager.get("geometry", "window", "corner_radius", default=14)
    header_h = TokenManager.get("geometry", "window", "headerbar_compact_height", default=38)
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
/* ── Mak macOS Window Corner & Geometry Consistency ({window_radius}px) ──────────────── */
window,
window.background,
window.csd,
window.background.csd,
window.background.solid-csd,
window.solid-csd {{
    border-radius: {window_radius}px;
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
    border-radius: {window_radius}px;
}}

window.csd.maximized:backdrop,
window.background.csd.maximized:backdrop,
window.background.maximized:backdrop,
window.maximized:backdrop,
window.csd.tiled:backdrop,
window.tiled:backdrop {{
    box-shadow: inset 0 0 0 1px {border_maximized_backdrop};
}}

/* Compact macOS Unified Titlebar Height (38px) - Flush & Clean */
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
    border-radius: 0;
    border-top-left-radius: 0;
    border-top-right-radius: 0;
}}

/* Standalone top-level floating CSD headerbars inherit window curvature */
window.csd:not(.maximized):not(.tiled) > headerbar:first-child,
window.solid-csd:not(.maximized):not(.tiled) > headerbar:first-child {{
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
    border-radius: 0;
    border-top-left-radius: 0;
    border-top-right-radius: 0;
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
    border-radius: 0;
}}

window.background.chromium headerbar.header-bar.titlebar {{
    border-radius: 0;
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

def generate_popover_override(is_dark=True, is_glassy=False, is_amoled=False):
    border_color = (
        "rgba(255, 255, 255, 0.08)" if is_amoled
        else "rgba(255, 255, 255, 0.10)" if is_dark
        else "rgba(0, 0, 0, 0.08)"
    )
    hover_bg = "rgba(255, 255, 255, 0.10)" if is_dark else "rgba(0, 0, 0, 0.05)"
    selected_bg = "rgba(255, 255, 255, 0.16)" if is_dark else "rgba(0, 0, 0, 0.08)"
    text_color = "#f5f5f7" if is_dark else "#1d1d1f"
    shadow = (
        "0 8px 22px rgba(0, 0, 0, 0.45), 0 2px 6px rgba(0, 0, 0, 0.20)"
        if is_amoled
        else "0 8px 20px rgba(0, 0, 0, 0.22), 0 2px 6px rgba(0, 0, 0, 0.12)"
        if is_dark
        else "0 6px 18px rgba(0, 0, 0, 0.10), 0 1px 4px rgba(0, 0, 0, 0.05)"
    )

    return f"""
/* ── Clean macOS Menus & Translucent Popovers ────────────────────────────── */
popover,
.popover,
popover.background,
popover.menu,
.popover.menu,
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
.popover > .contents,
.popover > contents,
popover.menu > contents,
.popover.menu > contents,
popover.menu.background > contents,
popover contents,
.popover .contents {{
    background-color: @popover_bg_color;
    color: @popover_fg_color;
    border-radius: 10px;
    border: 1px solid {border_color};
    box-shadow: {shadow};
    padding: 6px;
    margin: 0;
}}

popover.menu > contents,
.popover.menu > contents,
popover.menu contents,
.popover.menu .contents {{
    border-radius: 8px;
    padding: 4px;
}}

/* GTK 3 Menu styling */
menu,
.menu,
.background.csd > menu,
.background.popup > menu,
window.popup.background.csd > menu {{
    background-color: @popover_bg_color;
    color: @popover_fg_color;
    border-radius: 8px;
    border: 1px solid {border_color};
    box-shadow: {shadow};
    padding: 4px;
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

/* Menu items & modelbuttons */
popover modelbutton,
.popover modelbutton,
popover.menu modelbutton,
.popover.menu modelbutton,
popover .modelbutton,
.popover .modelbutton,
popover.menu .modelbutton,
.popover.menu .modelbutton,
popover contents button,
.popover .contents button,
popover > contents > button,
.popover > .contents > button,
popover listview > row,
popover list > row,
row.combo popover listview > row,
row.combo popover list > row,
menu > menuitem,
.menu > menuitem,
menuitem.button.flat,
modelbutton,
modelbutton.flat,
.modelbutton {{
    background: transparent;
    background-color: transparent;
    background-image: none;
    border: none;
    box-shadow: none;
    border-radius: 4px;
    min-height: 24px;
    padding: 3px 8px;
    margin: 1px 2px;
    color: {text_color};
    font-size: 13px;
    transition: background-color 80ms ease, color 80ms ease;
}}

popover modelbutton:hover,
.popover modelbutton:hover,
popover modelbutton:active,
.popover modelbutton:active,
popover modelbutton:focus,
.popover modelbutton:focus,
popover.menu modelbutton:hover,
.popover.menu modelbutton:hover,
popover.menu modelbutton:active,
.popover.menu modelbutton:active,
popover.menu modelbutton:focus,
.popover.menu modelbutton:focus,
popover .modelbutton:hover,
.popover .modelbutton:hover,
popover .modelbutton:active,
.popover .modelbutton:active,
popover contents button:hover,
.popover .contents button:hover,
popover contents button:active,
.popover .contents button:active,
popover > contents > button:hover,
.popover > .contents > button:hover,
popover > contents > button:active,
.popover > .contents > button:active,
popover listview > row:hover,
popover listview > row:active,
popover list > row:hover,
popover list > row:active,
row.combo popover listview > row:hover,
row.combo popover listview > row:active,
row.combo popover list > row:hover,
row.combo popover list > row:active,
menu > menuitem:hover,
.menu > menuitem:hover,
menu > menuitem:active,
.menu > menuitem:active,
menu > menuitem:selected,
.menu > menuitem:selected,
menuitem.button.flat:hover,
menuitem.button.flat:active,
menuitem.button.flat:selected,
modelbutton:hover,
modelbutton:active,
modelbutton:selected,
modelbutton.flat:hover,
modelbutton.flat:active,
modelbutton.flat:selected,
.modelbutton:hover,
.modelbutton:active,
.modelbutton:selected,
.modelbutton.selected {{
    background: @accent_bg_color;
    background-color: @accent_bg_color;
    background-image: none;
    color: #ffffff;
}}

popover modelbutton:hover label,
popover modelbutton:active label,
popover.menu modelbutton:hover label,
popover.menu modelbutton:active label,
popover listview > row:hover label,
popover listview > row:active label,
popover list > row:hover label,
popover list > row:active label,
row.combo popover listview > row:hover label,
row.combo popover listview > row:active label,
row.combo popover list > row:hover label,
row.combo popover list > row:active label,
popover modelbutton:hover image,
popover modelbutton:active image,
popover.menu modelbutton:hover image,
popover.menu modelbutton:active image,
popover listview > row:hover image,
popover listview > row:active image,
popover list > row:hover image,
popover list > row:active image,
row.combo popover listview > row:hover image,
row.combo popover listview > row:active image,
row.combo popover list > row:hover image,
row.combo popover list > row:active image,
popover modelbutton:hover accelerator,
popover modelbutton:active accelerator,
popover.menu modelbutton:hover accelerator,
popover.menu modelbutton:active accelerator,
menu > menuitem:hover label,
menu > menuitem:active label,
menu > menuitem:hover > arrow,
menu > menuitem:active > arrow {{
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

popover separator,
menu > separator {{
    margin: 4px 6px;
    min-height: 1px;
    background-color: {border_color};
}}
"""


def generate_nautilus_override(is_dark=True, is_glassy=False, is_amoled=False):
    if not is_dark:
        if is_glassy:
            border_color = "rgba(0, 0, 0, 0.08)"
            sidebar_selected_bg = "rgba(0, 0, 0, 0.08)"
            sidebar_hover_bg = "rgba(0, 0, 0, 0.045)"
            sidebar_selected_hover_bg = "rgba(0, 0, 0, 0.12)"
            sidebar_selected_active_bg = "rgba(0, 0, 0, 0.16)"
            search_bg = "rgba(0, 0, 0, 0.05)"
            search_border = "rgba(0, 0, 0, 0.08)"
            path_floating_bg = "rgba(255, 255, 255, 0.82)"
            path_btn_bg = "rgba(0, 0, 0, 0.05)"
            path_btn_hover = "rgba(0, 0, 0, 0.09)"
            hover_subtle = "rgba(0, 0, 0, 0.06)"
        else:
            border_color = "rgba(0, 0, 0, 0.08)"
            sidebar_selected_bg = "rgba(0, 0, 0, 0.08)"
            sidebar_hover_bg = "rgba(0, 0, 0, 0.04)"
            sidebar_selected_hover_bg = "rgba(0, 0, 0, 0.12)"
            sidebar_selected_active_bg = "rgba(0, 0, 0, 0.16)"
            search_bg = "rgba(0, 0, 0, 0.05)"
            search_border = "rgba(0, 0, 0, 0.08)"
            path_floating_bg = "rgba(255, 255, 255, 0.92)"
            path_btn_bg = "rgba(0, 0, 0, 0.05)"
            path_btn_hover = "rgba(0, 0, 0, 0.09)"
            hover_subtle = "rgba(0, 0, 0, 0.05)"
        text_primary = "#1d1d1f"
        text_sidebar = "#1d1d1f"
        text_secondary = "rgba(0, 0, 0, 0.50)"
        text_muted = "rgba(0, 0, 0, 0.45)"
        alt_row_bg = "rgba(0, 0, 0, 0.02)"
        row_hover_bg = "rgba(0, 0, 0, 0.045)"
    else:
        if is_amoled:
            if is_glassy:
                border_color = "rgba(255, 255, 255, 0.08)"
                sidebar_selected_bg = "rgba(255, 255, 255, 0.14)"
                sidebar_hover_bg = "rgba(255, 255, 255, 0.07)"
                sidebar_selected_hover_bg = "rgba(255, 255, 255, 0.20)"
                sidebar_selected_active_bg = "rgba(255, 255, 255, 0.24)"
                search_bg = "rgba(255, 255, 255, 0.07)"
                search_border = "rgba(255, 255, 255, 0.08)"
                path_floating_bg = "rgba(24, 24, 28, 0.85)"
                path_btn_bg = "rgba(255, 255, 255, 0.08)"
                path_btn_hover = "rgba(255, 255, 255, 0.14)"
                hover_subtle = "rgba(255, 255, 255, 0.09)"
            else:
                border_color = "rgba(255, 255, 255, 0.07)"
                sidebar_selected_bg = "rgba(255, 255, 255, 0.13)"
                sidebar_hover_bg = "rgba(255, 255, 255, 0.06)"
                sidebar_selected_hover_bg = "rgba(255, 255, 255, 0.19)"
                sidebar_selected_active_bg = "rgba(255, 255, 255, 0.23)"
                search_bg = "rgba(255, 255, 255, 0.06)"
                search_border = "rgba(255, 255, 255, 0.07)"
                path_floating_bg = "rgba(24, 24, 28, 0.92)"
                path_btn_bg = "rgba(255, 255, 255, 0.07)"
                path_btn_hover = "rgba(255, 255, 255, 0.13)"
                hover_subtle = "rgba(255, 255, 255, 0.08)"
            text_muted = "rgba(255, 255, 255, 0.42)"
        else:
            if is_glassy:
                border_color = "rgba(255, 255, 255, 0.09)"
                sidebar_selected_bg = "rgba(255, 255, 255, 0.14)"
                sidebar_hover_bg = "rgba(255, 255, 255, 0.07)"
                sidebar_selected_hover_bg = "rgba(255, 255, 255, 0.19)"
                sidebar_selected_active_bg = "rgba(255, 255, 255, 0.23)"
                search_bg = "rgba(255, 255, 255, 0.08)"
                search_border = "rgba(255, 255, 255, 0.09)"
                path_floating_bg = "rgba(36, 36, 40, 0.85)"
                path_btn_bg = "rgba(255, 255, 255, 0.09)"
                path_btn_hover = "rgba(255, 255, 255, 0.15)"
                hover_subtle = "rgba(255, 255, 255, 0.09)"
            else:
                border_color = "rgba(255, 255, 255, 0.08)"
                sidebar_selected_bg = "rgba(255, 255, 255, 0.12)"
                sidebar_hover_bg = "rgba(255, 255, 255, 0.06)"
                sidebar_selected_hover_bg = "rgba(255, 255, 255, 0.18)"
                sidebar_selected_active_bg = "rgba(255, 255, 255, 0.22)"
                search_bg = "rgba(255, 255, 255, 0.07)"
                search_border = "rgba(255, 255, 255, 0.08)"
                path_floating_bg = "rgba(36, 36, 40, 0.92)"
                path_btn_bg = "rgba(255, 255, 255, 0.08)"
                path_btn_hover = "rgba(255, 255, 255, 0.14)"
                hover_subtle = "rgba(255, 255, 255, 0.08)"
            text_muted = "rgba(255, 255, 255, 0.45)"
        text_primary = "#f5f5f7"
        text_sidebar = "#f5f5f7"
        text_secondary = "rgba(255, 255, 255, 0.50)"
        alt_row_bg = "rgba(255, 255, 255, 0.02)"
        row_hover_bg = "rgba(255, 255, 255, 0.06)"

    return f"""
/* ── macOS 27 "Golden Gate" Finder & Universal System Sidebar ────────────── */

/* 1. Eliminate Adwaita Floating Overlay Shadows, Dimming & Outlines */
overlay-split-view > shadow,
overlay-split-view > shadow.left,
overlay-split-view > shadow.right,
overlay-split-view > shadow.up,
overlay-split-view > shadow.down,
overlay-split-view > dimming,
overlay-split-view > border,
navigation-split-view > shadow,
navigation-split-view > dimming,
navigation-split-view > border {{
    background: none;
    background-image: none;
    box-shadow: none;
    border: none;
    min-width: 0;
    min-height: 0;
}}

/* 2. Seamless Top-Left Sidebar Titlebar (Eliminate separator above sidebar) */
navigation-split-view > widget.sidebar-pane headerbar,
overlay-split-view > widget.sidebar-pane headerbar,
split-view > widget.sidebar-pane headerbar,
navigation-split-view .sidebar-pane headerbar,
overlay-split-view .sidebar-pane headerbar,
split-view .sidebar-pane headerbar,
.sidebar-pane headerbar,
.sidebar headerbar,
.nautilus-window .sidebar-pane headerbar,
.nautilus-window headerbar.flat,
headerbar.titlebar.tweak-titlebar-left,
headerbar.titlebar.tweak-titlebar-left:backdrop {{
    border-top-left-radius: 16px;
    border-top-right-radius: 0;
    background: @headerbar_bg_color;
    background-color: @headerbar_bg_color;
    background-image: none;
    border: none;
    border-bottom: none;
    box-shadow: none;
}}

/* 3. Anchored Sidebar Pane: Exact Same Color as Topbar */
navigation-split-view > widget.sidebar-pane,
overlay-split-view > widget.sidebar-pane,
split-view > widget.sidebar-pane,
navigation-split-view .sidebar-pane,
overlay-split-view .sidebar-pane,
split-view .sidebar-pane,
navigation-split-view > widget.sidebar-pane navigation-view-page,
navigation-split-view > widget.sidebar-pane toolbarview,
overlay-split-view > widget.sidebar-pane navigation-view-page,
overlay-split-view > widget.sidebar-pane toolbarview,
.sidebar-pane navigation-view-page,
.sidebar-pane toolbarview,
.nautilus-window .sidebar-pane,
.nautilus-window .sidebar-pane:dir(ltr),
.nautilus-window .sidebar-pane:dir(rtl),
.nautilus-window .sidebar-pane:backdrop,
#NautilusFileChooser .sidebar-pane,
#NautilusFileChooser .sidebar-pane:dir(ltr),
#NautilusFileChooser .sidebar-pane:dir(rtl),
#NautilusFileChooser .sidebar-pane:backdrop,
.sidebar-pane,
.sidebar-pane:dir(ltr),
.sidebar-pane:dir(rtl),
.content-pane .sidebar-pane,
.content-pane .sidebar-pane:dir(ltr),
.content-pane .sidebar-pane:dir(rtl),
.sidebar-pane .content-pane,
.sidebar-pane .content-pane:dir(ltr),
.sidebar-pane .content-pane:dir(rtl),
placessidebar,
stacksidebar,
navigation-sidebar,
.navigation-sidebar {{
    margin: 0;
    border-radius: 0;
    box-shadow: none;
    background-image: none;
    background: @headerbar_bg_color;
    background-color: @headerbar_bg_color;
}}

navigation-split-view > widget.sidebar-pane,
overlay-split-view > widget.sidebar-pane,
split-view > widget.sidebar-pane,
.sidebar-pane {{
    border-right: 1px solid {border_color};
    border-left: none;
    border-top: none;
    border-bottom: none;
}}

navigation-split-view > widget.sidebar-pane:dir(rtl),
overlay-split-view > widget.sidebar-pane:dir(rtl),
split-view > widget.sidebar-pane:dir(rtl),
.sidebar-pane:dir(rtl),
placessidebar:dir(rtl),
stacksidebar:dir(rtl) {{
    border-left: 1px solid {border_color};
    border-right: none;
}}

/* 4. Anchor Content Pane Flush With Divider & Zero Radius Cutout */
navigation-split-view > widget.content-pane,
overlay-split-view > widget.content-pane,
split-view > widget.content-pane,
navigation-split-view .content-pane,
overlay-split-view .content-pane,
split-view .content-pane,
navigation-split-view > widget:not(.sidebar-pane),
navigation-split-view > widget.content-pane navigation-view-page,
navigation-split-view > widget.content-pane toolbarview,
navigation-split-view > widget.content-pane toolbarview > scrolledwindow,
.nautilus-window .content-pane,
#NautilusFileChooser .content-pane,
.content-pane {{
    margin: 0;
    border-radius: 0;
    border-top-left-radius: 0;
    box-shadow: none;
    background-color: @view_bg_color;
}}

navigation-split-view > widget.content-pane headerbar,
overlay-split-view > widget.content-pane headerbar,
split-view > widget.content-pane headerbar,
navigation-split-view .content-pane headerbar,
overlay-split-view .content-pane headerbar,
split-view .content-pane headerbar,
navigation-split-view > widget:not(.sidebar-pane) headerbar,
navigation-view-page headerbar,
toolbarview headerbar,
leaflet headerbar,
flap headerbar,
.nautilus-window .content-pane headerbar,
#NautilusFileChooser .content-pane headerbar,
headerbar.titlebar.tweak-titlebar-right {{
    border-radius: 0;
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
    border-top-right-radius: 0;
    border-bottom-right-radius: 0;
    border-bottom: 1px solid {border_color};
    background: @headerbar_bg_color;
    background-color: @headerbar_bg_color;
}}

/* 5. Transparent Sidebar Background Containers */
.nautilus-window .sidebar-pane placessidebar,
#NautilusFileChooser .sidebar-pane placessidebar,
.nautilus-window placessidebar,
navigation-split-view > widget.sidebar-pane scrolledwindow,
overlay-split-view > widget.sidebar-pane scrolledwindow,
split-view > widget.sidebar-pane scrolledwindow,
.sidebar-pane scrolledwindow,
navigation-sidebar,
.navigation-sidebar,
placessidebar list,
stacksidebar list {{
    background: transparent;
    background-color: transparent;
    border: none;
    box-shadow: none;
}}

/* 4. Category & Group Headers ("Favourites", "Locations", "Tags", etc.) */
navigation-sidebar row.heading,
.navigation-sidebar row.heading,
placessidebar row.heading,
.sidebar-pane row.heading,
placessidebar row:not(.activatable),
.navigation-sidebar row:not(.activatable),
stacksidebar row:not(.activatable),
navigation-sidebar label.heading,
.navigation-sidebar label.heading,
placessidebar label.heading,
.sidebar-pane label.heading,
.sidebar label.heading,
.nautilus-window .sidebar-pane row.heading,
.nautilus-window placessidebar row.heading,
#NautilusFileChooser placessidebar row.heading {{
    background: transparent;
    background-color: transparent;
    border: none;
    box-shadow: none;
    outline: none;
    color: {text_muted};
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.4px;
    margin-top: 14px;
    margin-bottom: 2px;
    padding: 2px 12px;
    min-height: 20px;
}}

navigation-sidebar row.heading:hover,
.navigation-sidebar row.heading:hover,
placessidebar row.heading:hover,
placessidebar row:not(.activatable):hover {{
    background: transparent;
    background-color: transparent;
}}

/* 5. Inset Floating Rounded Pill Sidebar Rows (macOS 27 Signature Look - Compact & Sleek) */
navigation-sidebar,
.navigation-sidebar {{
    padding: 4px;
}}

navigation-sidebar > row + row,
.navigation-sidebar > row + row {{
    margin-top: 1px;
}}

navigation-sidebar > row,
.navigation-sidebar > row,
listview.navigation-sidebar > row,
list.navigation-sidebar > row,
placessidebar row.activatable,
placessidebar row,
placessidebar list > row,
.sidebar-pane placessidebar row,
.sidebar-pane row.activatable,
.sidebar-pane row,
stacksidebar row,
stacksidebar list > row,
.sidebar row,
sidebar row,
.nautilus-window .sidebar-pane placessidebar row,
.nautilus-window placessidebar row,
.nautilus-window .navigation-sidebar > row,
#NautilusFileChooser placessidebar row,
#NautilusFileChooser .navigation-sidebar > row {{
    border-radius: 5px;
    margin: 1px 8px;
    padding: 4px 10px;
    min-height: 32px;
    font-size: 13px;
    font-weight: 500;
    color: {text_sidebar};
    border: none;
    outline: none;
    box-shadow: none;
    background-color: transparent;
    transition: background-color 100ms ease, color 100ms ease;
}}

navigation-sidebar > row > box,
.navigation-sidebar > row > box,
listview.navigation-sidebar > row > box,
list.navigation-sidebar > row > box,
.sidebar-pane row > box {{
    min-height: 20px;
    padding: 0;
    margin: 0;
}}

navigation-sidebar > row label,
.navigation-sidebar > row label,
listview.navigation-sidebar > row label,
list.navigation-sidebar > row label,
placessidebar row label,
.sidebar-pane row label,
stacksidebar row label,
.sidebar row label,
sidebar row label {{
    font-size: 13px;
    font-weight: 500;
    padding: 0;
    margin: 0;
}}

/* 6. Sidebar SF-Symbols Vibrant Accent Glyphs */
navigation-sidebar > row image,
.navigation-sidebar > row image,
listview.navigation-sidebar > row image,
list.navigation-sidebar > row image,
placessidebar row image,
placessidebar list > row image,
.sidebar-pane row image,
stacksidebar row image,
.sidebar row image,
.nautilus-window .sidebar-pane placessidebar row image,
.nautilus-window placessidebar row image,
.nautilus-window .navigation-sidebar > row image,
#NautilusFileChooser placessidebar row image,
#NautilusFileChooser .navigation-sidebar > row image {{
    min-width: 16px;
    min-height: 16px;
    margin-right: 8px;
    color: @accent_color;
}}

/* Eject and Action Buttons in Sidebar */
navigation-sidebar row button.sidebar-button,
placessidebar row button.sidebar-button,
placessidebar row button.image-button,
.sidebar-pane row button.sidebar-button,
.nautilus-window .sidebar-pane placessidebar row button {{
    border-radius: 9999px;
    padding: 2px 4px;
    min-height: 18px;
    min-width: 18px;
    color: {text_muted};
    background: transparent;
    border: none;
    box-shadow: none;
    opacity: 0.65;
    transition: opacity 100ms ease, background-color 100ms ease, color 100ms ease;
}}

navigation-sidebar row button.sidebar-button:hover,
placessidebar row button.sidebar-button:hover,
placessidebar row button.image-button:hover,
.sidebar-pane row button.sidebar-button:hover,
.nautilus-window .sidebar-pane placessidebar row button:hover {{
    opacity: 1.0;
    color: {text_primary};
    background-color: {hover_subtle};
}}

/* 7. Sidebar Row Hover & Active State */
navigation-sidebar > row:hover:not(:selected):not(.heading),
.navigation-sidebar > row:hover:not(:selected):not(.heading),
listview.navigation-sidebar > row:hover:not(:selected):not(.heading),
list.navigation-sidebar > row:hover:not(:selected):not(.heading),
placessidebar row:hover:not(:selected):not(.heading),
placessidebar list > row:hover:not(:selected):not(.heading),
.sidebar-pane placessidebar row:hover:not(:selected):not(.heading),
.sidebar-pane row:hover:not(:selected):not(.heading),
stacksidebar row:hover:not(:selected):not(.heading),
.sidebar row:hover:not(:selected):not(.heading),
sidebar row:hover:not(:selected):not(.heading),
.nautilus-window .sidebar-pane placessidebar row:hover:not(:selected):not(.heading),
.nautilus-window placessidebar row:hover:not(:selected):not(.heading),
.nautilus-window .navigation-sidebar > row:hover:not(:selected):not(.heading),
#NautilusFileChooser placessidebar row:hover:not(:selected):not(.heading),
#NautilusFileChooser .navigation-sidebar > row:hover:not(:selected):not(.heading) {{
    background-color: {sidebar_hover_bg};
    color: {text_primary};
    border-radius: 5px;
    margin: 1px 8px;
    padding: 4px 10px;
    min-height: 32px;
    border: none;
    outline: none;
    box-shadow: none;
}}

navigation-sidebar > row:active:not(:selected):not(.heading),
.navigation-sidebar > row:active:not(:selected):not(.heading),
listview.navigation-sidebar > row:active:not(:selected):not(.heading),
list.navigation-sidebar > row:active:not(:selected):not(.heading),
placessidebar row:active:not(:selected):not(.heading),
placessidebar list > row:active:not(:selected):not(.heading),
.sidebar-pane placessidebar row:active:not(:selected):not(.heading),
.sidebar-pane row:active:not(:selected):not(.heading),
stacksidebar row:active:not(:selected):not(.heading),
.sidebar row:active:not(:selected):not(.heading),
sidebar row:active:not(:selected):not(.heading),
.nautilus-window .sidebar-pane placessidebar row:active:not(:selected):not(.heading),
.nautilus-window placessidebar row:active:not(:selected):not(.heading),
.nautilus-window .navigation-sidebar > row:active:not(:selected):not(.heading),
#NautilusFileChooser placessidebar row:active:not(:selected):not(.heading),
#NautilusFileChooser .navigation-sidebar > row:active:not(:selected):not(.heading) {{
    background-color: {sidebar_selected_bg};
    color: {text_primary};
    border-radius: 5px;
    margin: 1px 8px;
    padding: 4px 10px;
    min-height: 32px;
    border: none;
    outline: none;
    box-shadow: none;
}}

/* 8. Sidebar Row Selected State (Clean macOS Inset Floating Pill) */
.sidebar-pane .navigation-sidebar:not(.view) > row:selected,
.sidebar-pane .navigation-sidebar > row:selected,
.content-pane .sidebar-pane .navigation-sidebar:not(.view) > row:selected,
navigation-split-view > widget.sidebar-pane .navigation-sidebar > row:selected,
overlay-split-view > widget.sidebar-pane .navigation-sidebar > row:selected,
split-view > widget.sidebar-pane .navigation-sidebar > row:selected,
navigation-sidebar > row:selected,
.navigation-sidebar > row:selected,
listview.navigation-sidebar > row:selected,
list.navigation-sidebar > row:selected,
placessidebar row:selected,
placessidebar list > row:selected,
.sidebar-pane placessidebar row:selected,
.sidebar-pane row:selected,
stacksidebar row:selected,
.sidebar row:selected,
sidebar row:selected,
.nautilus-window .sidebar-pane placessidebar row:selected,
.nautilus-window placessidebar row:selected,
.nautilus-window .navigation-sidebar > row:selected,
.nautilus-window .sidebar-pane placessidebar .navigation-sidebar:not(.view) > row:selected,
#NautilusFileChooser .sidebar-pane placessidebar .navigation-sidebar:not(.view) > row:selected,
#NautilusFileChooser placessidebar row:selected,
#NautilusFileChooser .navigation-sidebar > row:selected {{
    background-color: {sidebar_selected_bg};
    color: {text_primary};
    font-weight: 600;
    border-radius: 5px;
    margin: 1px 8px;
    padding: 4px 10px;
    min-height: 32px;
    border: none;
    outline: none;
    box-shadow: none;
}}

/* 8b. Selected Row Hover & Active State (Fix disappearing text / background) */
.sidebar-pane .navigation-sidebar:not(.view) > row:selected:hover,
.sidebar-pane .navigation-sidebar > row:selected:hover,
.content-pane .sidebar-pane .navigation-sidebar:not(.view) > row:selected:hover,
navigation-split-view > widget.sidebar-pane .navigation-sidebar > row:selected:hover,
overlay-split-view > widget.sidebar-pane .navigation-sidebar > row:selected:hover,
split-view > widget.sidebar-pane .navigation-sidebar > row:selected:hover,
navigation-sidebar > row:selected:hover,
.navigation-sidebar > row:selected:hover,
listview.navigation-sidebar > row:selected:hover,
list.navigation-sidebar > row:selected:hover,
placessidebar row:selected:hover,
placessidebar list > row:selected:hover,
.sidebar-pane placessidebar row:selected:hover,
.sidebar-pane row:selected:hover,
stacksidebar row:selected:hover,
.sidebar row:selected:hover,
sidebar row:selected:hover,
.nautilus-window .sidebar-pane placessidebar row:selected:hover,
.nautilus-window placessidebar row:selected:hover,
.nautilus-window .navigation-sidebar > row:selected:hover,
.nautilus-window .sidebar-pane placessidebar .navigation-sidebar:not(.view) > row:selected:hover,
#NautilusFileChooser .sidebar-pane placessidebar .navigation-sidebar:not(.view) > row:selected:hover,
#NautilusFileChooser placessidebar row:selected:hover,
#NautilusFileChooser .navigation-sidebar > row:selected:hover {{
    background-color: {sidebar_selected_hover_bg};
    color: {text_primary};
    font-weight: 600;
    border-radius: 5px;
    margin: 1px 8px;
    padding: 4px 10px;
    min-height: 32px;
    border: none;
    outline: none;
    box-shadow: none;
}}

.sidebar-pane .navigation-sidebar:not(.view) > row:selected:active,
.sidebar-pane .navigation-sidebar > row:selected:active,
.content-pane .sidebar-pane .navigation-sidebar:not(.view) > row:selected:active,
navigation-split-view > widget.sidebar-pane .navigation-sidebar > row:selected:active,
overlay-split-view > widget.sidebar-pane .navigation-sidebar > row:selected:active,
split-view > widget.sidebar-pane .navigation-sidebar > row:selected:active,
navigation-sidebar > row:selected:active,
.navigation-sidebar > row:selected:active,
listview.navigation-sidebar > row:selected:active,
list.navigation-sidebar > row:selected:active,
placessidebar row:selected:active,
placessidebar list > row:selected:active,
.sidebar-pane placessidebar row:selected:active,
.sidebar-pane row:selected:active,
stacksidebar row:selected:active,
.sidebar row:selected:active,
sidebar row:selected:active,
.nautilus-window .sidebar-pane placessidebar row:selected:active,
.nautilus-window placessidebar row:selected:active,
.nautilus-window .navigation-sidebar > row:selected:active,
.nautilus-window .sidebar-pane placessidebar .navigation-sidebar:not(.view) > row:selected:active,
#NautilusFileChooser .sidebar-pane placessidebar .navigation-sidebar:not(.view) > row:selected:active,
#NautilusFileChooser placessidebar row:selected:active,
#NautilusFileChooser .navigation-sidebar > row:selected:active {{
    background-color: {sidebar_selected_active_bg};
    color: {text_primary};
    font-weight: 600;
    border-radius: 5px;
    margin: 1px 8px;
    padding: 4px 10px;
    min-height: 32px;
    border: none;
    outline: none;
    box-shadow: none;
}}

/* Labels and text across selected, hover, and active states */
navigation-sidebar > row label,
.navigation-sidebar > row label,
listview.navigation-sidebar > row label,
list.navigation-sidebar > row label,
placessidebar row label,
.sidebar-pane row label,
stacksidebar row label,
.sidebar row label,
sidebar row label,
navigation-sidebar > row:hover label,
.navigation-sidebar > row:hover label,
listview.navigation-sidebar > row:hover label,
list.navigation-sidebar > row:hover label,
placessidebar row:hover label,
.sidebar-pane row:hover label,
stacksidebar row:hover label,
.sidebar row:hover label,
sidebar row:hover label,
.sidebar-pane .navigation-sidebar:not(.view) > row:selected label,
.sidebar-pane .navigation-sidebar > row:selected label,
.content-pane .sidebar-pane .navigation-sidebar:not(.view) > row:selected label,
navigation-split-view > widget.sidebar-pane .navigation-sidebar > row:selected label,
overlay-split-view > widget.sidebar-pane .navigation-sidebar > row:selected label,
split-view > widget.sidebar-pane .navigation-sidebar > row:selected label,
navigation-sidebar > row:selected label,
.navigation-sidebar > row:selected label,
listview.navigation-sidebar > row:selected label,
list.navigation-sidebar > row:selected label,
placessidebar row:selected label,
placessidebar list > row:selected label,
.sidebar-pane placessidebar row:selected label,
.sidebar-pane row:selected label,
stacksidebar row:selected label,
.sidebar row:selected label,
sidebar row:selected label,
.nautilus-window .sidebar-pane placessidebar row:selected label,
.nautilus-window placessidebar row:selected label,
.nautilus-window .navigation-sidebar > row:selected label,
#NautilusFileChooser placessidebar row:selected label,
#NautilusFileChooser .navigation-sidebar > row:selected label,
.sidebar-pane .navigation-sidebar:not(.view) > row:selected:hover label,
.sidebar-pane .navigation-sidebar > row:selected:hover label,
.content-pane .sidebar-pane .navigation-sidebar:not(.view) > row:selected:hover label,
navigation-split-view > widget.sidebar-pane .navigation-sidebar > row:selected:hover label,
overlay-split-view > widget.sidebar-pane .navigation-sidebar > row:selected:hover label,
split-view > widget.sidebar-pane .navigation-sidebar > row:selected:hover label,
navigation-sidebar > row:selected:hover label,
.navigation-sidebar > row:selected:hover label,
listview.navigation-sidebar > row:selected:hover label,
list.navigation-sidebar > row:selected:hover label,
placessidebar row:selected:hover label,
placessidebar list > row:selected:hover label,
.sidebar-pane placessidebar row:selected:hover label,
.sidebar-pane row:selected:hover label,
stacksidebar row:selected:hover label,
.sidebar row:selected:hover label,
sidebar row:selected:hover label,
.nautilus-window .sidebar-pane placessidebar row:selected:hover label,
.nautilus-window placessidebar row:selected:hover label,
.nautilus-window .navigation-sidebar > row:selected:hover label,
#NautilusFileChooser placessidebar row:selected:hover label,
#NautilusFileChooser .navigation-sidebar > row:selected:hover label,
navigation-sidebar > row:selected:active label,
.navigation-sidebar > row:selected:active label,
placessidebar row:selected:active label,
.sidebar-pane row:selected:active label {{
    color: {text_primary};
}}

navigation-sidebar > row:selected label,
.navigation-sidebar > row:selected label,
placessidebar row:selected label,
.sidebar-pane row:selected label,
navigation-sidebar > row:selected:hover label,
.navigation-sidebar > row:selected:hover label,
placessidebar row:selected:hover label,
.sidebar-pane row:selected:hover label,
navigation-sidebar > row:selected:active label,
.navigation-sidebar > row:selected:active label,
placessidebar row:selected:active label,
.sidebar-pane row:selected:active label {{
    font-weight: 600;
}}

/* Icons across selected, hover, and active states */
.sidebar-pane .navigation-sidebar:not(.view) > row:selected image,
.sidebar-pane .navigation-sidebar > row:selected image,
.content-pane .sidebar-pane .navigation-sidebar:not(.view) > row:selected image,
navigation-split-view > widget.sidebar-pane .navigation-sidebar > row:selected image,
overlay-split-view > widget.sidebar-pane .navigation-sidebar > row:selected image,
split-view > widget.sidebar-pane .navigation-sidebar > row:selected image,
navigation-sidebar > row:selected image,
.navigation-sidebar > row:selected image,
listview.navigation-sidebar > row:selected image,
list.navigation-sidebar > row:selected image,
placessidebar row:selected image,
placessidebar list > row:selected image,
.sidebar-pane row:selected image,
stacksidebar row:selected image,
.sidebar row:selected image,
.nautilus-window .sidebar-pane placessidebar row:selected image,
.nautilus-window placessidebar row:selected image,
.nautilus-window .navigation-sidebar > row:selected image,
#NautilusFileChooser placessidebar row:selected image,
#NautilusFileChooser .navigation-sidebar > row:selected image,
navigation-sidebar > row:selected:hover image,
.navigation-sidebar > row:selected:hover image,
listview.navigation-sidebar > row:selected:hover image,
list.navigation-sidebar > row:selected:hover image,
placessidebar row:selected:hover image,
placessidebar list > row:selected:hover image,
.sidebar-pane row:selected:hover image,
stacksidebar row:selected:hover image,
.sidebar row:selected:hover image,
.nautilus-window .navigation-sidebar > row:selected:hover image,
navigation-sidebar > row:selected:active image,
.navigation-sidebar > row:selected:active image,
placessidebar row:selected:active image,
.sidebar-pane row:selected:active image {{
    color: @accent_color;
}}

navigation-sidebar > row:selected:backdrop,
.navigation-sidebar > row:selected:backdrop,
placessidebar row:selected:backdrop,
.sidebar-pane row:selected:backdrop,
.nautilus-window .navigation-sidebar > row:selected:backdrop {{
    opacity: 0.85;
}}

/* 9. Content Pane (Files View & General App Body) */
navigation-split-view > widget.content-pane,
overlay-split-view > widget.content-pane,
split-view > widget.content-pane,
.nautilus-window .content-pane,
#NautilusFileChooser .content-pane {{
    background-color: @view_bg_color;
}}

navigation-split-view > widget.content-pane headerbar,
overlay-split-view > widget.content-pane headerbar,
split-view > widget.content-pane headerbar,
.nautilus-window .content-pane headerbar,
headerbar.titlebar.tweak-titlebar-right {{
    background-color: @headerbar_bg_color;
    border-bottom: 1px solid {border_color};
    box-shadow: none;
}}

.nautilus-window .view,
.nautilus-window listview.view,
.nautilus-window columnview,
.nautilus-window .nautilus-list-view,
.nautilus-window .nautilus-grid-view {{
    background-color: @view_bg_color;
    color: @view_fg_color;
}}

/* 10. Column Header Titles (Apple Flat Sans Typography) */
columnview header,
columnview header > button,
columnview header button,
columnview.view > header > button,
columnview.view header button,
treeview.view > header > button,
.nautilus-window columnview header,
.nautilus-window columnview header > button,
.nautilus-window columnview header button,
.nautilus-window columnview header button label,
.nautilus-window .nautilus-list-view columnview header,
.nautilus-window .nautilus-list-view columnview header button,
.nautilus-window .nautilus-list-view header button,
.nautilus-list-view header,
.nautilus-list-view header button,
columnview title,
columnview header cell,
columnview header cell button,
columnview header cell > button {{
    color: {text_secondary};
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.3px;
    border: none;
    border-radius: 0;
    border-image: none;
    background: transparent;
    background-color: transparent;
    background-image: none;
    box-shadow: none;
    padding: 3px 10px;
    min-height: 28px;
}}

columnview header > button:hover,
columnview header button:hover,
columnview.view > header > button:hover,
columnview.view header button:hover,
treeview.view > header > button:hover,
.nautilus-window columnview header button:hover,
.nautilus-window .nautilus-list-view header button:hover,
.nautilus-list-view header button:hover {{
    background: transparent;
    background-color: transparent;
    background-image: none;
    border: none;
    border-radius: 0;
    border-image: none;
    box-shadow: none;
    color: {text_primary};
}}

columnview header > button:active,
columnview header button:active,
columnview header button:checked,
columnview.view > header > button:active,
columnview.view > header > button:checked,
columnview.view header button:active,
columnview.view header button:checked,
treeview.view > header > button:active,
treeview.view > header > button:checked,
.nautilus-window columnview header button:active,
.nautilus-window columnview header button:checked,
.nautilus-window .nautilus-list-view header button:active,
.nautilus-window .nautilus-list-view header button:checked,
.nautilus-list-view header button:active,
.nautilus-list-view header button:checked {{
    background: transparent;
    background-color: transparent;
    background-image: none;
    border: none;
    border-radius: 0;
    border-image: none;
    box-shadow: none;
    color: {text_primary};
}}

/* 11. List View Alternating Rows */
.nautilus-window .nautilus-list-view listview.view,
#NautilusFileChooser .nautilus-list-view listview.view {{
    padding: 0;
    margin: 0;
}}

.nautilus-window .nautilus-list-view listview.view > row.activatable,
#NautilusFileChooser .nautilus-list-view listview.view > row.activatable {{
    padding: 0 4px;
    min-height: 20px;
    border-radius: 0;
    margin: 0;
    font-size: 12.5px;
}}

.nautilus-window .nautilus-list-view cell,
#NautilusFileChooser .nautilus-list-view cell {{
    min-height: 20px;
    padding: 0;
}}

.nautilus-window .nautilus-list-view listview.view > row.activatable > cell > widget#NautilusViewCell,
#NautilusFileChooser .nautilus-list-view listview.view > row.activatable > cell > widget#NautilusViewCell {{
    padding: 0 4px;
    min-height: 20px;
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

.nautilus-window .nautilus-list-view listview.view > row.activatable:selected,
.nautilus-window .nautilus-list-view listview.view > row.activatable:selected:hover,
#NautilusFileChooser .nautilus-list-view listview.view > row.activatable:selected,
#NautilusFileChooser .nautilus-list-view listview.view > row.activatable:selected:hover {{
    background-color: @accent_bg_color;
    background-image: none;
    color: @accent_fg_color;
    border-radius: 0;
    margin: 0;
}}

.nautilus-window .nautilus-list-view listview.view > row.activatable:selected label,
.nautilus-window .nautilus-list-view listview.view > row.activatable:selected .dim-label,
.nautilus-window .nautilus-list-view listview.view > row.activatable:selected:hover label,
.nautilus-window .nautilus-list-view listview.view > row.activatable:selected:hover .dim-label,
#NautilusFileChooser .nautilus-list-view listview.view > row.activatable:selected label,
#NautilusFileChooser .nautilus-list-view listview.view > row.activatable:selected .dim-label,
#NautilusFileChooser .nautilus-list-view listview.view > row.activatable:selected:hover label,
#NautilusFileChooser .nautilus-list-view listview.view > row.activatable:selected:hover .dim-label {{
    color: #ffffff;
}}

/* 12. Grid View Items (Smooth Squircle Selection) */
.nautilus-window .nautilus-grid-view child.activatable {{
    border-radius: 10px;
    padding: 4px;
    transition: background-color 80ms ease;
}}

.nautilus-window .nautilus-grid-view child.activatable:hover:not(:selected) {{
    background-color: {row_hover_bg};
}}

.nautilus-window .nautilus-grid-view child.activatable:selected,
#NautilusFileChooser .nautilus-grid-view child.activatable:selected {{
    background-color: alpha(@accent_bg_color, 0.22);
    border-radius: 10px;
    color: {text_primary};
}}

.nautilus-window .nautilus-grid-view child.activatable:selected label {{
    color: {text_primary};
    font-weight: 500;
}}

/* 13. Subtitle / Dim Labels & Stars */
.nautilus-window .dim-label,
.nautilus-window label.subtitle,
.nautilus-window cell label:not(:first-child) {{
    color: {text_secondary};
}}

.nautilus-window cell button.star image {{
    color: {text_secondary};
}}

.nautilus-window cell button.star:checked image {{
    color: #f5a623;
}}

/* 14. Pathbar Transparent Buttons (Plain Text at Rest) */
.nautilus-window .nautilus-pathbar,
#NautilusFileChooser .nautilus-pathbar,
filechooser .path-bar,
filechooser pathbar,
.path-bar,
pathbar {{
    background: transparent;
    background-color: transparent;
    border: none;
    box-shadow: none;
    padding: 0;
    margin: 0 4px;
}}

.nautilus-window .nautilus-pathbar button,
#NautilusFileChooser .nautilus-pathbar button,
filechooser .path-bar button,
filechooser pathbar button,
filechooser stack button,
.path-bar button,
pathbar button,
headerbar .path-bar button,
headerbar pathbar button {{
    border-radius: 9999px;
    background: transparent;
    background-color: transparent;
    background-image: none;
    border: none;
    padding: 2px 8px;
    min-height: 24px;
    font-size: 13px;
    font-weight: 500;
    color: {text_primary};
    box-shadow: none;
    transition: background-color 80ms ease;
}}

.nautilus-window .nautilus-pathbar button:hover,
.nautilus-window .nautilus-pathbar button:active,
#NautilusFileChooser .nautilus-pathbar button:hover,
#NautilusFileChooser .nautilus-pathbar button:active,
filechooser .path-bar button:hover,
filechooser pathbar button:hover,
filechooser stack button:hover,
.path-bar button:hover,
pathbar button:hover,
headerbar .path-bar button:hover,
headerbar pathbar button:hover {{
    background-color: {hover_subtle};
    box-shadow: none;
}}

/* 15. History Navigation Capsule (< | >) (macOS Connected Seamless Style) */
.nautilus-window headerbar > windowhandle > box > widget > box.start > stack > widget > box,
.nautilus-window headerbar > windowhandle > box > widget > box.start > box > stack > widget > box,
#NautilusFileChooser headerbar > windowhandle > box > widget > box.start > stack > widget > box,
#NautilusFileChooser headerbar > windowhandle > box > widget > box.start > box > stack > widget > box {{
    margin-left: 10px;
    padding: 0;
    border-radius: 6px;
    background-color: {path_btn_bg};
    border: 1px solid {border_color};
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08);
}}

.nautilus-window headerbar > windowhandle > box > widget > box.start > stack > widget > box > button,
.nautilus-window headerbar > windowhandle > box > widget > box.start > box > stack > widget > box > button,
#NautilusFileChooser headerbar > windowhandle > box > widget > box.start > stack > widget > box > button,
#NautilusFileChooser headerbar > windowhandle > box > widget > box.start > box > stack > widget > box > button {{
    min-height: 22px;
    min-width: 22px;
    padding: 2px 8px;
    border-radius: 0;
    background: transparent;
    background-color: transparent;
    border: none;
    box-shadow: none;
    color: {text_primary};
    transition: background-color 80ms ease;
}}

.nautilus-window headerbar > windowhandle > box > widget > box.start > stack > widget > box > button:first-child,
.nautilus-window headerbar > windowhandle > box > widget > box.start > box > stack > widget > box > button:first-child,
#NautilusFileChooser headerbar > windowhandle > box > widget > box.start > stack > widget > box > button:first-child,
#NautilusFileChooser headerbar > windowhandle > box > widget > box.start > box > stack > widget > box > button:first-child {{
    border-top-left-radius: 5px;
    border-bottom-left-radius: 5px;
    border-top-right-radius: 0;
    border-bottom-right-radius: 0;
}}

.nautilus-window headerbar > windowhandle > box > widget > box.start > stack > widget > box > button:last-child,
.nautilus-window headerbar > windowhandle > box > widget > box.start > box > stack > widget > box > button:last-child,
#NautilusFileChooser headerbar > windowhandle > box > widget > box.start > stack > widget > box > button:last-child,
#NautilusFileChooser headerbar > windowhandle > box > widget > box.start > box > stack > widget > box > button:last-child {{
    border-top-right-radius: 5px;
    border-bottom-right-radius: 5px;
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
    border-left: 1px solid {border_color};
}}

.nautilus-window headerbar > windowhandle > box > widget > box.start > stack > widget > box > button:hover,
.nautilus-window headerbar > windowhandle > box > widget > box.start > box > stack > widget > box > button:hover,
#NautilusFileChooser headerbar > windowhandle > box > widget > box.start > stack > widget > box > button:hover,
#NautilusFileChooser headerbar > windowhandle > box > widget > box.start > box > stack > widget > box > button:hover {{
    background-color: {path_btn_hover};
}}

.nautilus-window headerbar > windowhandle > box > widget > box.start > stack > widget > box > button:active,
.nautilus-window headerbar > windowhandle > box > widget > box.start > box > stack > widget > box > button:active,
#NautilusFileChooser headerbar > windowhandle > box > widget > box.start > stack > widget > box > button:active,
#NautilusFileChooser headerbar > windowhandle > box > widget > box.start > box > stack > widget > box > button:active {{
    background-color: {path_btn_hover};
}}

.nautilus-window headerbar > windowhandle > box > widget > box.start > stack > widget > box > button:disabled,
.nautilus-window headerbar > windowhandle > box > widget > box.start > box > stack > widget > box > button:disabled,
#NautilusFileChooser headerbar > windowhandle > box > widget > box.start > stack > widget > box > button:disabled,
#NautilusFileChooser headerbar > windowhandle > box > widget > box.start > box > stack > widget > box > button:disabled {{
    opacity: 0.35;
    background-color: transparent;
}}

/* 16. Pill Search Entry (macOS 27 Top-Right Style) */
entry.search,
searchbar entry,
searchentry,
.nautilus-window searchbar entry,
window.background.csd > dialog-host searchbar entry {{
    border-radius: 9999px;
    border: 1px solid {search_border};
    background-color: {search_bg};
    padding: 3px 12px;
    min-height: 26px;
    color: {text_primary};
    box-shadow: none;
}}

entry.search:focus,
searchbar entry:focus,
searchentry:focus,
.nautilus-window searchbar entry:focus {{
    border-color: @accent_bg_color;
    outline: 2px solid @accent_bg_color;
    outline-offset: -1px;
    box-shadow: 0 0 0 3px alpha(@accent_bg_color, 0.35);
}}

/* 17. Floating Bottom Statusbar / Path Capsule (macOS 27 Style) */
.nautilus-window .floating-bar,
floating-bar {{
    border-radius: 9999px;
    background-color: {path_floating_bg};
    border: 1px solid {border_color};
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.15);
    padding: 4px 14px;
    color: {text_primary};
    font-size: 12px;
    margin-bottom: 8px;
}}

/* 18. Dialog & Window Bottom Action Bar (Save / Cancel / New Folder / Delete) */
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
    btn_radius = TokenManager.get("geometry", "buttons", "corner_radius", default=5)
    btn_capsule_radius = TokenManager.get("geometry", "buttons", "capsule_corner_radius", default=9999)
    btn_height = TokenManager.get("geometry", "buttons", "height_regular", default=24)
    btn_pad_x = TokenManager.get("geometry", "buttons", "padding_x_regular", default=12)
    btn_pad_y = TokenManager.get("geometry", "buttons", "padding_y_regular", default=3)
    btn_border_width = TokenManager.get("geometry", "buttons", "border_width", default=1)

    seg_height = TokenManager.get("geometry", "segmented", "height", default=22)
    seg_container_radius = TokenManager.get("geometry", "segmented", "container_radius", default=6)
    seg_radius = TokenManager.get("geometry", "segmented", "segment_radius", default=5)
    seg_pad = TokenManager.get("geometry", "segmented", "padding", default=2)

    entry_radius = TokenManager.get("geometry", "entries", "corner_radius", default=5)
    entry_height = TokenManager.get("geometry", "entries", "height_regular", default=22)
    entry_pad_x = TokenManager.get("geometry", "entries", "padding_x", default=8)
    focus_ring_w = TokenManager.get("geometry", "entries", "focus_ring_width", default=3)

    if not is_dark:
        btn_bg = TokenManager.get("colors", "light", "btn_default_bg", default="rgba(0, 0, 0, 0.08)")
        btn_hover = TokenManager.get("colors", "light", "btn_default_hover", default="rgba(0, 0, 0, 0.12)")
        btn_active = TokenManager.get("colors", "light", "btn_default_active", default="rgba(0, 0, 0, 0.18)")
        btn_border = f"{btn_border_width}px solid {TokenManager.get('colors', 'light', 'border', default='rgba(0, 0, 0, 0.12)')}"
        btn_fg = TokenManager.get("colors", "light", "text_primary", default="#1d1d1f")
        btn_shadow = "0 0.5px 1px rgba(0, 0, 0, 0.08)"
        dim_label = "rgba(0, 0, 0, 0.50)"
        entry_bg = TokenManager.get("colors", "light", "entry_bg", default="#ffffff")
        entry_border = f"{btn_border_width}px solid {TokenManager.get('colors', 'light', 'entry_border', default='rgba(0, 0, 0, 0.15)')}"
        entry_border_hover = "rgba(0, 0, 0, 0.22)"
        focus_ring = TokenManager.get("colors", "light", "focus_ring", default="rgba(0, 128, 247, 0.50)")
        hover_subtle = "rgba(0, 0, 0, 0.06)"
        active_subtle = "rgba(0, 0, 0, 0.12)"
        switch_off_bg = "rgba(0, 0, 0, 0.15)"
        scale_trough_bg = "rgba(0, 0, 0, 0.12)"
        pill_bg = "rgba(0, 0, 0, 0.06)"
        pill_hover = "rgba(0, 0, 0, 0.08)"
        pill_active = "rgba(0, 0, 0, 0.12)"
        pill_checked = "#ffffff"
        pill_checked_fg = "#1d1d1f"
        linked_bg = "rgba(0, 0, 0, 0.06)"
        linked_border = f"{btn_border_width}px solid rgba(0, 0, 0, 0.12)"
        linked_shadow = "0 1px 2px rgba(0, 0, 0, 0.06)"
        linked_divider = "1px solid rgba(0, 0, 0, 0.10)"
        linked_divider_color = "rgba(0, 0, 0, 0.10)"
        linked_hover = "rgba(0, 0, 0, 0.06)"
        linked_active = "rgba(0, 0, 0, 0.12)"
        linked_checked = "#ffffff"
        linked_checked_fg = "#1d1d1f"
        linked_checked_shadow = "0 1px 2px rgba(0, 0, 0, 0.15), 0 0 0 0.5px rgba(0, 0, 0, 0.08)"
        search_bg = "rgba(0, 0, 0, 0.05)"
        dropdown_bg = TokenManager.get("colors", "light", "btn_default_bg", default="rgba(0, 0, 0, 0.08)")
        dropdown_border = f"{btn_border_width}px solid {TokenManager.get('colors', 'light', 'border', default='rgba(0, 0, 0, 0.12)')}"
        sug_bg = TokenManager.get("colors", "light", "btn_prominent_bg", default="#0080f7")
        sug_fg = TokenManager.get("colors", "light", "btn_prominent_fg", default="#ffffff")
        sug_hover = "rgba(0, 110, 230, 0.90)"
        sug_active = "rgba(0, 94, 196, 0.90)"
        destr_bg = TokenManager.get("colors", "light", "btn_destructive_bg", default="#ff383c")
        destr_fg = TokenManager.get("colors", "light", "btn_destructive_fg", default="#ffffff")
        destr_hover = "rgba(224, 40, 44, 0.90)"
        destr_active = "rgba(196, 30, 34, 0.90)"
        dialog_ring = "rgba(0, 0, 0, 0.12)"
        list_inactive_selected = "rgba(0, 0, 0, 0.14)"
        zebra_bg = "rgba(0, 0, 0, 0.05)"
    else:
        border_col = TokenManager.get("colors", "amoled" if is_amoled else "dark", "border", default="rgba(255, 255, 255, 0.12)")
        btn_bg = TokenManager.get("colors", "dark", "btn_default_bg", default="rgba(255, 255, 255, 0.10)")
        btn_hover = TokenManager.get("colors", "dark", "btn_default_hover", default="rgba(255, 255, 255, 0.15)")
        btn_active = TokenManager.get("colors", "dark", "btn_default_active", default="rgba(255, 255, 255, 0.22)")
        btn_border = f"{btn_border_width}px solid {border_col}"
        btn_fg = TokenManager.get("colors", "dark", "text_primary", default="#f5f5f7")
        btn_shadow = "0 0.5px 1px rgba(0, 0, 0, 0.20)"
        dim_label = "rgba(255, 255, 255, 0.50)"
        entry_bg = TokenManager.get("colors", "amoled" if is_amoled else "dark", "entry_bg", default="rgba(255, 255, 255, 0.08)")
        entry_border = f"{btn_border_width}px solid {TokenManager.get('colors', 'dark', 'entry_border', default='rgba(255, 255, 255, 0.15)')}"
        entry_border_hover = "rgba(255, 255, 255, 0.18)"
        focus_ring = TokenManager.get("colors", "dark", "focus_ring", default="rgba(10, 132, 255, 0.60)")
        hover_subtle = "rgba(255, 255, 255, 0.10)"
        active_subtle = "rgba(255, 255, 255, 0.18)"
        switch_off_bg = "rgba(255, 255, 255, 0.18)"
        scale_trough_bg = "rgba(255, 255, 255, 0.14)"
        pill_bg = "rgba(255, 255, 255, 0.08)"
        pill_hover = "rgba(255, 255, 255, 0.10)"
        pill_active = "rgba(255, 255, 255, 0.16)"
        pill_checked = "rgba(255, 255, 255, 0.18)"
        pill_checked_fg = "#ffffff"
        linked_bg = "rgba(255, 255, 255, 0.08)"
        linked_border = f"{btn_border_width}px solid {border_col}"
        linked_shadow = "0 1px 3px rgba(0, 0, 0, 0.35), 0 0.5px 1px rgba(0, 0, 0, 0.20)"
        linked_divider = "1px solid rgba(255, 255, 255, 0.10)"
        linked_divider_color = "rgba(255, 255, 255, 0.10)"
        linked_hover = "rgba(255, 255, 255, 0.10)"
        linked_active = "rgba(255, 255, 255, 0.18)"
        linked_checked = "rgba(255, 255, 255, 0.20)"
        linked_checked_fg = "#ffffff"
        linked_checked_shadow = "0 1px 2px rgba(0, 0, 0, 0.35), 0 0 0 0.5px rgba(255, 255, 255, 0.12)"
        search_bg = "rgba(255, 255, 255, 0.08)"
        dropdown_bg = TokenManager.get("colors", "dark", "btn_default_bg", default="rgba(255, 255, 255, 0.10)")
        dropdown_border = f"{btn_border_width}px solid {border_col}"
        sug_bg = TokenManager.get("colors", "dark", "btn_prominent_bg", default="#0a84ff")
        sug_fg = TokenManager.get("colors", "dark", "btn_prominent_fg", default="#ffffff")
        sug_hover = "rgba(0, 113, 227, 0.90)"
        sug_active = "rgba(0, 98, 196, 0.90)"
        destr_bg = TokenManager.get("colors", "dark", "btn_destructive_bg", default="#ff453a")
        destr_fg = TokenManager.get("colors", "dark", "btn_destructive_fg", default="#ffffff")
        destr_hover = "rgba(224, 52, 42, 0.90)"
        destr_active = "rgba(194, 43, 34, 0.90)"
        dialog_ring = "rgba(255, 255, 255, 0.12)"
        list_inactive_selected = "rgba(255, 255, 255, 0.14)"
        zebra_bg = "rgba(255, 255, 255, 0.04)"

    return f"""
/* ── Mak macOS Sonoma Refined Interactive Widgets & States ────────────────── */

/* 1. Universal In-Window Push Buttons (Dialogs, content pages, settings) */
button:not(.titlebutton):not(.close):not(.minimize):not(.maximize):not(.flat):not(.suggested-action):not(.destructive-action):not(.link):not(.image-button):not(.circular):not(.style-item):not(.card):not(checkbutton):not(.color-palette-item):not(.color-button):not(.pill):not(.modelbutton) {{
    background-color: {btn_bg};
    background-image: none;
    border: {btn_border};
    color: {btn_fg};
    border-radius: {btn_radius}px;
    padding: {btn_pad_y}px {btn_pad_x}px;
    min-height: {btn_height}px;
    font-size: 13px;
    font-weight: 400;
    box-shadow: {btn_shadow};
    transition: background-color 80ms ease, color 80ms ease;
}}

button:not(.titlebutton):not(.close):not(.minimize):not(.maximize):not(.flat):not(.suggested-action):not(.destructive-action):not(.link):not(.image-button):not(.circular):not(.style-item):not(.card):not(checkbutton):not(.color-palette-item):not(.color-button):not(.modelbutton):hover {{
    background-color: {btn_hover};
    color: {btn_fg};
}}

button:not(.titlebutton):not(.close):not(.minimize):not(.maximize):not(.flat):not(.suggested-action):not(.destructive-action):not(.link):not(.image-button):not(.circular):not(.style-item):not(.card):not(checkbutton):not(.color-palette-item):not(.color-button):not(.modelbutton):active {{
    background-color: {btn_active};
}}

button:not(.titlebutton):not(.close):not(.minimize):not(.maximize):not(.flat):not(.suggested-action):not(.destructive-action):not(.link):not(.image-button):not(.circular):not(.style-item):not(.card):not(checkbutton):not(.color-palette-item):not(.color-button):not(.modelbutton):checked {{
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

/* Compact SpinButtons (Apple UI kit stepper fidelity) */
spinbutton {{
    min-height: {entry_height}px;
    padding: 0;
    border-radius: {entry_radius}px;
    background-color: {entry_bg};
    border: {entry_border};
}}

spinbutton:focus,
spinbutton:focus-within {{
    border-color: @accent_bg_color;
    outline: none;
    box-shadow: 0 0 0 {focus_ring_w}px {focus_ring};
}}

spinbutton > text,
spinbutton > entry {{
    min-height: {entry_height}px;
    padding: 2px {entry_pad_x}px;
    background: transparent;
    border: none;
    box-shadow: none;
    color: {btn_fg};
}}

spinbutton > button,
spinbutton button {{
    min-width: 18px;
    min-height: 18px;
    padding: 1px 4px;
    border-radius: 4px;
    border: none;
    box-shadow: none;
    background-color: transparent;
    color: {btn_fg};
}}

spinbutton > button:hover,
spinbutton button:hover {{
    background-color: {hover_subtle};
}}

spinbutton > button:active,
spinbutton button:active {{
    background-color: {active_subtle};
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
button.suggested-action:not(.circular):not(.pill) {{
    background-color: {sug_bg};
    color: {sug_fg};
    border: none;
    border-radius: {btn_radius}px;
    padding: {btn_pad_y}px 14px;
    min-height: {btn_height}px;
    font-size: 13px;
    font-weight: 500;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.20);
}}

button.suggested-action:hover {{
    background-color: {sug_hover};
    background-image: none;
}}

button.suggested-action:active {{
    background-color: {sug_active};
    background-image: none;
}}

button.destructive-action:not(.circular):not(.pill) {{
    background-color: {destr_bg};
    color: {destr_fg};
    border: none;
    border-radius: {btn_radius}px;
    padding: {btn_pad_y}px 14px;
    min-height: {btn_height}px;
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

/* Dialog & Alert Action Buttons (Apple UI Kit 26px Capsule Geometry) */
dialog button,
window.dialog button,
messagedialog button,
adwdialog button,
.dialog-action-area button,
.response-area button {{
    border-radius: {btn_capsule_radius}px;
    min-height: 26px;
    padding: 4px 18px;
    font-weight: 500;
}}

/* 7. Dropdowns, Combos & Pop-ups */
dropdown,
combobox,
row.combo {{
    border-radius: {btn_radius}px;
}}

dropdown > button,
combobox > box > button.combo,
combobox button,
row.combo dropdown > button,
box.content dropdown > button,
preferencespage dropdown > button,
dialog dropdown > button,
menubutton:not(.flat):not(.titlebutton) > button {{
    background-color: {dropdown_bg};
    border: {dropdown_border};
    color: {btn_fg};
    border-radius: {btn_radius}px;
    padding: 3px 10px;
    min-height: {btn_height}px;
    box-shadow: {btn_shadow};
    transition: background-color 100ms ease;
}}

dropdown > button:hover,
combobox > box > button.combo:hover,
combobox button:hover,
row.combo dropdown > button:hover,
box.content dropdown > button:hover,
preferencespage dropdown > button:hover,
dialog dropdown > button:hover,
menubutton:not(.flat):not(.titlebutton) > button:hover {{
    background-color: {btn_hover};
    color: {btn_fg};
}}

dropdown > button:active,
combobox > box > button.combo:active,
combobox button:active,
row.combo dropdown > button:active,
box.content dropdown > button:active,
preferencespage dropdown > button:active,
dialog dropdown > button:active,
menubutton:not(.flat):not(.titlebutton) > button:active {{
    background-color: {btn_active};
}}

dropdown > button:focus,
dropdown > button:focus-within,
combobox > box > button.combo:focus,
combobox button:focus,
row.combo dropdown > button:focus,
box.content dropdown > button:focus,
preferencespage dropdown > button:focus,
dialog dropdown > button:focus,
menubutton:not(.flat):not(.titlebutton) > button:focus {{
    border-color: @accent_bg_color;
    outline: none;
    box-shadow: 0 0 0 {focus_ring_w}px {focus_ring};
}}

headerbar dropdown > button,
headerbar menubutton.flat > button {{
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

/* 8. Text Entries */
entry,
passwordentry {{
    background-color: {entry_bg};
    border: {entry_border};
    border-radius: {entry_radius}px;
    padding: 2px {entry_pad_x}px;
    min-height: {entry_height}px;
    color: {btn_fg};
    caret-color: @accent_bg_color;
    box-shadow: none;
    transition: border-color 120ms ease, box-shadow 120ms ease;
}}

entry:hover,
passwordentry:hover {{
    border-color: {entry_border_hover};
}}

entry:focus,
entry:focus-within,
passwordentry:focus,
passwordentry:focus-within {{
    border-color: @accent_bg_color;
    outline: none;
    box-shadow: 0 0 0 {focus_ring_w}px {focus_ring};
}}

entry.search,
searchentry,
searchbar entry,
headerbar searchbar entry {{
    border-radius: 9999px;
    border: {entry_border};
    background-color: {search_bg};
    padding: 2px 10px;
    min-height: {entry_height}px;
    color: {btn_fg};
    box-shadow: none;
}}

entry.search:hover,
searchentry:hover,
searchbar entry:hover,
headerbar searchbar entry:hover {{
    border-color: {entry_border_hover};
}}

entry.search:focus,
entry.search:focus-within,
searchentry:focus,
searchentry:focus-within,
searchbar entry:focus,
headerbar searchbar entry:focus {{
    border-color: @accent_bg_color;
    outline: none;
    box-shadow: 0 0 0 {focus_ring_w}px {focus_ring};
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

/* 12. Interactive List Rows, Columnviews & Treeviews */
listview > row,
columnview row,
columnview.view > listview > row,
treeview.view,
treeview.view > row,
list > row {{
    min-height: 24px;
    padding: 2px 10px;
    border-radius: 4px;
    transition: background-color 80ms ease, color 80ms ease;
}}

listview.compact > row,
columnview.compact row,
treeview.compact,
treeview.view.compact {{
    min-height: 20px;
    padding: 1px 8px;
}}

list > row.activatable:hover:not(:selected),
listview > row.activatable:hover:not(:selected),
columnview row:hover:not(:selected),
columnview.view > listview > row:hover:not(:selected),
treeview.view:hover:not(:selected) {{
    background-color: {hover_subtle};
}}

list > row.activatable:active,
listview > row.activatable:active,
columnview row:active,
treeview.view:active {{
    background-color: {active_subtle};
}}

list > row.activatable:selected,
list > row.activatable:selected:hover,
listview > row.activatable:selected,
listview > row.activatable:selected:hover,
columnview row:selected,
columnview row:selected:hover,
columnview.view > listview > row:selected,
columnview.view > listview > row:selected:hover,
treeview.view:selected,
treeview.view:selected:hover {{
    background-color: @accent_bg_color;
    color: #ffffff;
}}

/* Inactive window selection (14% alpha per Apple UI kit) */
list > row.activatable:selected:backdrop,
listview > row.activatable:selected:backdrop,
columnview row:selected:backdrop,
columnview.view > listview > row:selected:backdrop,
treeview.view:selected:backdrop {{
    background-color: {list_inactive_selected};
    color: {btn_fg};
}}

/* Alternating zebra rows (5% alpha per Apple UI kit) */
list > row.alt-row:not(:selected),
listview > row.alt-row:not(:selected),
columnview row.alt-row:not(:selected),
treeview.view:nth-child(even):not(:selected),
columnview.view > listview > row:nth-child(even):not(:selected),
list > row:nth-child(even):not(:selected) {{
    background-color: {zebra_bg};
}}

list > row.activatable:selected label,
list > row.activatable:selected:hover label,
listview > row.activatable:selected label,
listview > row.activatable:selected:hover label,
columnview row:selected label,
columnview row:selected:hover label,
columnview.view > listview > row:selected label,
columnview.view > listview > row:selected:hover label,
treeview.view:selected label {{
    color: #ffffff;
}}

list > row.activatable:selected:backdrop label,
listview > row.activatable:selected:backdrop label,
columnview row:selected:backdrop label,
columnview.view > listview > row:selected:backdrop label,
treeview.view:selected:backdrop label {{
    color: {btn_fg};
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

/* 16. Headerbar Segmented Controls, Split Buttons & Linked Controls (Seamless macOS style with shadows) */
window headerbar splitbutton,
window .titlebar splitbutton,
window headerbar .linked,
window .titlebar .linked,
window headerbar box.linked,
window .titlebar box.linked,
window headerbar stackswitcher,
window .titlebar stackswitcher,
window headerbar viewswitcher,
window .titlebar viewswitcher,
window splitbutton,
window .linked,
window box.linked,
window stackswitcher,
window viewswitcher,
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
splitbutton,
.linked,
box.linked,
stackswitcher,
viewswitcher,
.kgx-window headerbar splitbutton,
window.kgx headerbar splitbutton,
.kgx-window headerbar .linked,
window.kgx headerbar .linked {{
    background-color: {linked_bg};
    background-image: none;
    border: {linked_border};
    box-shadow: {linked_shadow};
    border-radius: {seg_container_radius}px;
    margin: 0 4px;
    padding: {seg_pad}px;
}}

/* Force all inner buttons to be seamless and flush at rest - NO double button */
window headerbar splitbutton button,
window headerbar splitbutton > button,
window headerbar splitbutton > button.flat,
window headerbar splitbutton menubutton,
window headerbar splitbutton > menubutton,
window headerbar splitbutton menubutton > button,
window headerbar splitbutton > menubutton > button,
window headerbar splitbutton > menubutton > button.flat,
window headerbar .linked button,
window headerbar .linked > button,
window headerbar .linked > button.flat,
window headerbar .linked menubutton,
window headerbar .linked > menubutton,
window headerbar .linked menubutton > button,
window headerbar .linked > menubutton > button,
window headerbar .linked > menubutton > button.flat,
window headerbar box.linked button,
window headerbar box.linked > button,
window headerbar box.linked > button.flat,
window headerbar box.linked menubutton,
window headerbar box.linked > menubutton,
window headerbar box.linked menubutton > button,
window headerbar box.linked > menubutton > button,
window headerbar box.linked > menubutton > button.flat,
window headerbar stackswitcher button,
window headerbar stackswitcher > button,
window headerbar stackswitcher > button.flat,
window headerbar viewswitcher button,
window headerbar viewswitcher > button,
window headerbar viewswitcher > button.flat,
window splitbutton button,
window splitbutton > button,
window splitbutton > button.flat,
window splitbutton menubutton,
window splitbutton > menubutton,
window splitbutton menubutton > button,
window splitbutton > menubutton > button,
window splitbutton > menubutton > button.flat,
window .linked button,
window .linked > button,
window .linked > button.flat,
window .linked menubutton,
window .linked > menubutton,
window .linked menubutton > button,
window .linked > menubutton > button,
window .linked > menubutton > button.flat,
window box.linked button,
window box.linked > button,
window box.linked > button.flat,
window box.linked menubutton,
window box.linked > menubutton,
window box.linked menubutton > button,
window box.linked > menubutton > button,
window box.linked > menubutton > button.flat,
window stackswitcher button,
window stackswitcher > button,
window viewswitcher button,
window viewswitcher > button,
headerbar splitbutton button,
headerbar splitbutton > button,
headerbar splitbutton > button.flat,
headerbar splitbutton menubutton,
headerbar splitbutton > menubutton,
headerbar splitbutton menubutton > button,
headerbar splitbutton > menubutton > button,
headerbar splitbutton > menubutton > button.flat,
headerbar .linked button,
headerbar .linked > button,
headerbar .linked > button.flat,
headerbar .linked menubutton,
headerbar .linked > menubutton,
headerbar .linked menubutton > button,
headerbar .linked > menubutton > button,
headerbar .linked > menubutton > button.flat,
headerbar box.linked button,
headerbar box.linked > button,
headerbar box.linked > button.flat,
headerbar box.linked menubutton,
headerbar box.linked > menubutton,
headerbar box.linked menubutton > button,
headerbar box.linked > menubutton > button,
headerbar box.linked > menubutton > button.flat,
headerbar stackswitcher button,
headerbar stackswitcher > button,
headerbar viewswitcher button,
headerbar viewswitcher > button,
splitbutton button,
splitbutton > button,
splitbutton > button.flat,
splitbutton menubutton,
splitbutton > menubutton,
splitbutton menubutton > button,
splitbutton > menubutton > button,
splitbutton > menubutton > button.flat,
.linked button,
.linked > button,
.linked > button.flat,
.linked menubutton,
.linked > menubutton,
.linked menubutton > button,
.linked > menubutton > button,
.linked > menubutton > button.flat,
box.linked button,
box.linked > button,
box.linked > button.flat,
box.linked menubutton,
box.linked > menubutton,
box.linked menubutton > button,
box.linked > menubutton > button,
box.linked > menubutton > button.flat,
stackswitcher button,
stackswitcher > button,
viewswitcher button,
viewswitcher > button,
.kgx-window headerbar splitbutton button,
window.kgx headerbar splitbutton button {{
    min-height: 22px;
    min-width: 22px;
    padding: 2px 8px;
    border-radius: 0;
    margin: 0;
    background: transparent;
    background-color: transparent;
    background-image: none;
    border: none;
    box-shadow: none;
    outline: none;
    color: {btn_fg};
    transition: background-color 80ms ease, color 80ms ease;
}}

/* First button rounded left flush with capsule container */
window headerbar splitbutton > button:first-child,
window headerbar splitbutton > button.flat:first-child,
window headerbar splitbutton > menubutton:first-child,
window headerbar splitbutton > menubutton:first-child > button,
window headerbar splitbutton > menubutton:first-child > button.flat,
window headerbar .linked > button:first-child,
window headerbar .linked > button.flat:first-child,
window headerbar .linked > menubutton:first-child,
window headerbar .linked > menubutton:first-child > button,
window headerbar box.linked > button:first-child,
window headerbar box.linked > button.flat:first-child,
window headerbar box.linked > menubutton:first-child,
window headerbar box.linked > menubutton:first-child > button,
window headerbar stackswitcher > button:first-child,
window headerbar viewswitcher > button:first-child,
window splitbutton > button:first-child,
window splitbutton > button.flat:first-child,
window splitbutton > menubutton:first-child,
window splitbutton > menubutton:first-child > button,
window .linked > button:first-child,
window .linked > button.flat:first-child,
window box.linked > button:first-child,
window stackswitcher > button:first-child,
window viewswitcher > button:first-child,
headerbar splitbutton > button:first-child,
headerbar splitbutton > button.flat:first-child,
headerbar splitbutton > menubutton:first-child,
headerbar splitbutton > menubutton:first-child > button,
headerbar .linked > button:first-child,
headerbar .linked > button.flat:first-child,
headerbar .linked > menubutton:first-child,
headerbar .linked > menubutton:first-child > button,
headerbar box.linked > button:first-child,
headerbar box.linked > button.flat:first-child,
headerbar box.linked > menubutton:first-child,
headerbar box.linked > menubutton:first-child > button,
headerbar stackswitcher > button:first-child,
headerbar viewswitcher > button:first-child,
splitbutton > button:first-child,
splitbutton > button.flat:first-child,
splitbutton > menubutton:first-child,
splitbutton > menubutton:first-child > button,
.linked > button:first-child,
.linked > button.flat:first-child,
box.linked > button:first-child,
stackswitcher > button:first-child,
viewswitcher > button:first-child,
headerbar splitbutton > button:dir(ltr),
splitbutton > button:dir(ltr),
headerbar splitbutton > menubutton > button:dir(rtl),
splitbutton > menubutton > button:dir(rtl) {{
    border-top-left-radius: {seg_radius}px;
    border-bottom-left-radius: {seg_radius}px;
    border-top-right-radius: 0;
    border-bottom-right-radius: 0;
}}

/* Last button rounded right flush with capsule container */
window headerbar splitbutton > button:last-child,
window headerbar splitbutton > button.flat:last-child,
window headerbar splitbutton > menubutton:last-child,
window headerbar splitbutton > menubutton:last-child > button,
window headerbar splitbutton > menubutton:last-child > button.flat,
window headerbar .linked > button:last-child,
window headerbar .linked > button.flat:last-child,
window headerbar .linked > menubutton:last-child,
window headerbar .linked > menubutton:last-child > button,
window headerbar box.linked > button:last-child,
window headerbar box.linked > button.flat:last-child,
window headerbar box.linked > menubutton:last-child,
window headerbar box.linked > menubutton:last-child > button,
window headerbar stackswitcher > button:last-child,
window headerbar viewswitcher > button:last-child,
window splitbutton > button:last-child,
window splitbutton > button.flat:last-child,
window splitbutton > menubutton:last-child,
window splitbutton > menubutton:last-child > button,
window .linked > button:last-child,
window .linked > button.flat:last-child,
window box.linked > button:last-child,
window stackswitcher > button:last-child,
window viewswitcher > button:last-child,
headerbar splitbutton > button:last-child,
headerbar splitbutton > button.flat:last-child,
headerbar splitbutton > menubutton:last-child,
headerbar splitbutton > menubutton:last-child > button,
headerbar .linked > button:last-child,
headerbar .linked > button.flat:last-child,
headerbar .linked > menubutton:last-child,
headerbar .linked > menubutton:last-child > button,
headerbar box.linked > button:last-child,
headerbar box.linked > button.flat:last-child,
headerbar box.linked > menubutton:last-child,
headerbar box.linked > menubutton:last-child > button,
headerbar stackswitcher > button:last-child,
headerbar viewswitcher > button:last-child,
splitbutton > button:last-child,
splitbutton > button.flat:last-child,
splitbutton > menubutton:last-child,
splitbutton > menubutton:last-child > button,
.linked > button:last-child,
.linked > button.flat:last-child,
box.linked > button:last-child,
stackswitcher > button:last-child,
viewswitcher > button:last-child,
headerbar splitbutton > menubutton > button:dir(ltr),
splitbutton > menubutton > button:dir(ltr),
headerbar splitbutton > button:dir(rtl),
splitbutton > button:dir(rtl) {{
    border-top-right-radius: {seg_radius}px;
    border-bottom-right-radius: {seg_radius}px;
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
}}

/* Only child */
window headerbar splitbutton > button:only-child,
window headerbar splitbutton > menubutton:only-child > button,
window headerbar .linked > button:only-child,
window headerbar box.linked > button:only-child,
window splitbutton > button:only-child,
window .linked > button:only-child,
headerbar splitbutton > button:only-child,
headerbar .linked > button:only-child,
headerbar box.linked > button:only-child,
splitbutton > button:only-child,
.linked > button:only-child,
box.linked > button:only-child {{
    border-radius: {btn_radius}px;
}}

/* Clean hairline divider between adjacent buttons */
window headerbar splitbutton > button + button,
window headerbar splitbutton > button + menubutton > button,
window headerbar splitbutton > menubutton + button,
window headerbar .linked > button + button,
window headerbar .linked > button + menubutton > button,
window headerbar .linked > menubutton + button,
window headerbar box.linked > button + button,
window headerbar box.linked > button + menubutton > button,
window headerbar box.linked > menubutton + button,
window headerbar stackswitcher > button + button,
window headerbar viewswitcher > button + button,
window splitbutton > button + button,
window splitbutton > button + menubutton > button,
window splitbutton > menubutton + button,
window .linked > button + button,
window .linked > button + menubutton > button,
window .linked > menubutton + button,
window box.linked > button + button,
window box.linked > button + menubutton > button,
window box.linked > menubutton + button,
headerbar splitbutton > button + button,
headerbar splitbutton > button + menubutton > button,
headerbar splitbutton > menubutton + button,
headerbar .linked > button + button,
headerbar .linked > button + menubutton > button,
headerbar .linked > menubutton + button,
headerbar box.linked > button + button,
headerbar box.linked > button + menubutton > button,
headerbar box.linked > menubutton + button,
headerbar stackswitcher > button + button,
headerbar viewswitcher > button + button,
splitbutton > button + button,
splitbutton > button + menubutton > button,
splitbutton > menubutton + button,
.linked > button + button,
.linked > button + menubutton > button,
.linked > menubutton + button,
box.linked > button + button,
box.linked > button + menubutton > button,
box.linked > menubutton + button,
stackswitcher > button + button,
viewswitcher > button + button {{
    border-left: {linked_divider};
}}

/* Splitbutton separator widget */
window headerbar splitbutton > separator,
window splitbutton > separator,
headerbar splitbutton > separator,
splitbutton > separator {{
    min-width: 1px;
    min-height: 1px;
    background-color: {linked_divider_color};
    margin: 3px 0;
    padding: 0;
    border: none;
}}

/* Hover state on segment button */
window headerbar splitbutton > button:hover,
window headerbar splitbutton > button.flat:hover,
window headerbar splitbutton > menubutton > button:hover,
window headerbar splitbutton > menubutton > button.flat:hover,
window headerbar .linked > button:hover,
window headerbar .linked > button.flat:hover,
window headerbar .linked > menubutton > button:hover,
window headerbar box.linked > button:hover,
window headerbar box.linked > button.flat:hover,
window headerbar box.linked > menubutton > button:hover,
window headerbar stackswitcher > button:hover,
window headerbar viewswitcher > button:hover,
window splitbutton > button:hover,
window splitbutton > button.flat:hover,
window splitbutton > menubutton > button:hover,
window .linked > button:hover,
window .linked > button.flat:hover,
window box.linked > button:hover,
headerbar splitbutton > button:hover,
headerbar splitbutton > menubutton > button:hover,
headerbar .linked > button:hover,
headerbar .linked > menubutton > button:hover,
headerbar box.linked > button:hover,
headerbar box.linked > menubutton > button:hover,
headerbar stackswitcher > button:hover,
headerbar viewswitcher > button:hover,
splitbutton > button:hover,
splitbutton > menubutton > button:hover,
.linked > button:hover,
.linked > menubutton > button:hover,
box.linked > button:hover,
box.linked > menubutton > button:hover,
stackswitcher > button:hover,
viewswitcher > button:hover {{
    background-color: {linked_hover};
    color: {btn_fg};
    box-shadow: none;
}}

/* Active state on segment button */
window headerbar splitbutton > button:active,
window headerbar splitbutton > button.flat:active,
window headerbar splitbutton > menubutton > button:active,
window headerbar .linked > button:active,
window headerbar .linked > button.flat:active,
window headerbar .linked > menubutton > button:active,
window headerbar box.linked > button:active,
window headerbar box.linked > button.flat:active,
window headerbar box.linked > menubutton > button:active,
window splitbutton > button:active,
window splitbutton > button.flat:active,
window splitbutton > menubutton > button:active,
window .linked > button:active,
window .linked > button.flat:active,
headerbar splitbutton > button:active,
headerbar splitbutton > menubutton > button:active,
headerbar .linked > button:active,
headerbar .linked > menubutton > button:active,
headerbar box.linked > button:active,
headerbar box.linked > menubutton > button:active,
splitbutton > button:active,
splitbutton > menubutton > button:active,
.linked > button:active,
.linked > menubutton > button:active,
box.linked > button:active,
box.linked > menubutton > button:active,
stackswitcher > button:active,
viewswitcher > button:active {{
    background-color: {linked_active};
    color: {btn_fg};
    box-shadow: none;
}}

/* Selected / Checked Segment (Elevated macOS Segment Plate) */
window headerbar .linked > button:checked,
window headerbar .linked > button.flat:checked,
window headerbar box.linked > button:checked,
window headerbar box.linked > button.flat:checked,
window headerbar stackswitcher > button:checked,
window headerbar viewswitcher > button:checked,
window splitbutton > button:checked,
window splitbutton > button.flat:checked,
window splitbutton > menubutton > button:checked,
window .linked > button:checked,
window .linked > button.flat:checked,
window box.linked > button:checked,
headerbar .linked > button:checked,
headerbar box.linked > button:checked,
headerbar stackswitcher > button:checked,
headerbar viewswitcher > button:checked,
splitbutton > button:checked,
splitbutton > menubutton > button:checked,
.linked > button:checked,
box.linked > button:checked,
stackswitcher > button:checked,
viewswitcher > button:checked {{
    background-color: {linked_checked};
    color: {linked_checked_fg};
    box-shadow: {linked_checked_shadow};
    border-radius: 5px;
    font-weight: 500;
}}
"""


def inject_theme_css(src_css_path, dst_css_path, palette, is_glassy, button_size=14, button_spacing=8, chromium_accent=None, is_dark=True, sync_repo=False):
    base_path = src_css_path + ".base"
    read_path = base_path if os.path.exists(base_path) else src_css_path
    try:
        with open(read_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        content = ""

    # Correctly identify and preserve the upstream GTK base body
    # Base body starts right after the initial palette / accent definitions
    marker = "@define-color selected_bg_color"
    if marker in content:
        pos = content.find(marker)
        eol = content.find("\n", pos)
        base_start = eol + 1
    elif "@define-color blue_1" in content:
        base_start = content.find("@define-color blue_1")
    else:
        base_start = 0

    # Find where Mak overrides start
    override_markers = [
        "/* ── Mak macOS Sonoma Refined Interactive Widgets",
        "/* ── Universal Mak Widgets & Control Metrics Override",
        "/* === Mak Suite Refinements",
        "/* ── Mak Clean macOS Traffic Light Button Controls",
        "/* ── Mak macOS Window Corner"
    ]
    base_end = len(content)
    for om in override_markers:
        pos = content.find(om)
        if pos != -1 and pos < base_end:
            base_end = pos

    base_body = content[base_start:base_end].strip()

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
    popover_override = generate_popover_override(is_dark=is_dark, is_glassy=is_glassy, is_amoled=is_amoled)
    nautilus_override = generate_nautilus_override(is_dark=is_dark, is_glassy=is_glassy, is_amoled=is_amoled)
    window_corners_override = generate_window_corners_override(is_dark=is_dark)
    rules_to_append = [widgets_override, window_corners_override, popover_override, nautilus_override, traffic_override]
    if is_glassy:
        rules_to_append.append(GLASSY_CONTAINER_RULES)

    final_content = palette.strip() + "\n\n" + accent_css_override.strip() + "\n\n" + base_body + "\n\n" + "\n\n".join(rules_to_append) + "\n"
    os.makedirs(os.path.dirname(dst_css_path), exist_ok=True)
    with open(dst_css_path, "w", encoding="utf-8") as f:
        f.write(final_content)

    if sync_repo:
        try:
            repo_themes_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "themes")
            parts = os.path.normpath(src_css_path).split(os.sep)
            if len(parts) >= 3:
                t_name = parts[-3]
                gtk_ver = parts[-2]
                f_name = parts[-1]
                repo_file = os.path.join(repo_themes_dir, t_name, gtk_ver, f_name)
                if os.path.exists(os.path.dirname(repo_file)):
                    with open(repo_file, "w", encoding="utf-8") as f:
                        f.write(final_content)
        except Exception:
            pass


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

def inject_shell_theme_contrast(theme_name, is_dark, is_amoled=False):
    css_path = os.path.join(THEMES_DIR, theme_name, "gnome-shell", "gnome-shell.css")
    if not os.path.exists(css_path):
        return
    try:
        with open(css_path, "r", encoding="utf-8") as f:
            content = f.read()

        marker = "/* ── Mak Shell Contrast & Liquid Glass Refraction Tuning ── */"
        if marker in content:
            content = content.split(marker)[0].rstrip()

        if not is_dark:
            bg_color = "rgba(255, 255, 255, 0.82)"
            banner_bg = "rgba(255, 255, 255, 0.86)"
            border_color = "rgba(0, 0, 0, 0.08)"
            fg_color = "#1d1d1f"
            hover_bg = "rgba(0, 0, 0, 0.08)"
            shadow = "0 8px 24px rgba(0, 0, 0, 0.12)"
        else:
            bg_color = "rgba(22, 22, 26, 0.85)" if is_amoled else "rgba(36, 36, 40, 0.82)"
            banner_bg = "rgba(22, 22, 26, 0.88)" if is_amoled else "rgba(36, 36, 40, 0.86)"
            border_color = "rgba(255, 255, 255, 0.08)"
            fg_color = "#f5f5f7"
            hover_bg = "rgba(255, 255, 255, 0.12)"
            shadow = "0 8px 24px rgba(0, 0, 0, 0.22)"

        block = f"""\n\n{marker}
.popup-menu-content {{
    background-color: {bg_color};
    color: {fg_color};
    border: 1px solid {border_color};
    box-shadow: {shadow};
    border-radius: 12px;
}}

.popup-menu-item {{
    color: {fg_color};
    font-weight: 500;
}}

.popup-menu-item StLabel {{
    color: {fg_color};
}}

.popup-menu-item:hover,
.popup-menu-item:active {{
    background-color: {hover_bg};
    color: {fg_color};
}}

.popup-menu-item:selected {{
    background-color: #007aff;
    color: #ffffff;
}}

.popup-menu-item:selected StLabel {{
    color: #ffffff;
}}

.notification-banner {{
    background-color: {banner_bg};
    color: {fg_color};
    border: 1px solid {border_color};
    box-shadow: {shadow};
}}

.notification-banner StLabel {{
    color: {fg_color};
}}
"""
        with open(css_path, "w", encoding="utf-8") as f:
            f.write(content + block)
    except Exception as e:
        print(f"Error injecting shell theme contrast: {e}")

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

    try:
        sync_all_theme_directories()
    except Exception:
        pass

    theme_info = THEMES[theme_key]
    theme_name = theme_info["theme_name"]
    color_scheme = theme_info["color_scheme"]
    is_dark = theme_info["is_dark"]
    is_amoled = "amoled" in theme_key.lower()
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
        inject_shell_theme_contrast(theme_name, is_dark=is_dark, is_amoled=is_amoled)
        subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.user-theme", "name", theme_name], check=True)
        log.append(f"Set GNOME Shell theme to '{theme_name}' and injected contrast styling.")
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

        # Intelligent slight theme tint for menus, notifications & popups (white for light, obsidian for dark)
        if not is_dark:
            subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.blur-my-shell.popup", "style-popup", "1"], check=False)
            subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.blur-my-shell.popup", "preserve-shell-theme", "true"], check=False)
            subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.blur-my-shell.popup", "brightness", "0.95"], check=False)
            subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.blur-my-shell.panel", "style-panel", "1"], check=False)
        else:
            subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.blur-my-shell.popup", "style-popup", "2"], check=False)
            subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.blur-my-shell.popup", "preserve-shell-theme", "true"], check=False)
            subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.blur-my-shell.popup", "brightness", "0.65"], check=False)
            subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.blur-my-shell.panel", "style-panel", "2"], check=False)

        log.append(f"Set application blur & glass to {'enabled (translucent)' if is_glassy else 'disabled (solid opaque)'} with {'light' if not is_dark else 'dark'} popup styling.")
    except Exception as e:
        log.append(f"Error syncing application blur & glass: {e}")

    # 10. Gracefully reload / restart Nautilus daemon so running file manager instances pick up new styles immediately
    try:
        subprocess.run(["nautilus", "-q"], check=False)
        log.append("Reloaded Nautilus daemon (nautilus -q).")
    except Exception as e:
        log.append(f"Note on reloading Nautilus: {e}")

    return {
        "success": True,
        "theme": theme_name,
        "log": log
    }


def sync_all_theme_directories():
    """Synchronizes all 6 curated macOS theme variations in ~/.themes and repo themes/ with full macOS 27 styling."""
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

    palette_map = {
        "dark": GRAPHITE_PALETTE_OVERRIDE,
        "dark-glassy": GRAPHITE_GLASSY_PALETTE_OVERRIDE,
        "amoled": AMOLED_PALETTE_OVERRIDE,
        "amoled-glassy": AMOLED_GLASSY_PALETTE_OVERRIDE,
        "light": LIGHT_PALETTE_OVERRIDE,
        "light-glassy": LIGHT_GLASSY_PALETTE_OVERRIDE,
    }

    for key, info in THEMES.items():
        theme_name = info["theme_name"]
        is_glassy = info["is_glassy"]
        is_dark = info["is_dark"]
        palette = palette_map.get(key, GRAPHITE_PALETTE_OVERRIDE)
        source_dir = os.path.join(THEMES_DIR, theme_name)
        if not os.path.exists(source_dir):
            continue
        for gver in ["gtk-4.0", "gtk-3.0"]:
            gdir = os.path.join(source_dir, gver)
            if not os.path.exists(gdir):
                continue
            for css_file in ["gtk.css", "gtk-dark.css"]:
                src_css = os.path.join(gdir, css_file)
                base_css = src_css + ".base"
                if os.path.exists(base_css) or os.path.exists(src_css):
                    inject_theme_css(src_css, src_css, palette, is_glassy, button_size, button_spacing, chromium_accent=chromium_accent, is_dark=is_dark)

def stage_all_themes(stage_dir=None):
    """
    Safely compiles and stages all 6 macOS themes into a dedicated staging directory
    (e.g. build/stage/themes) without modifying live system directories or restarting Nautilus.
    """
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if stage_dir is None:
        stage_dir = os.path.join(repo_root, "build", "stage", "themes")
    os.makedirs(stage_dir, exist_ok=True)

    repo_themes = os.path.join(repo_root, "themes")
    palette_map = {
        "dark": GRAPHITE_PALETTE_OVERRIDE,
        "dark-glassy": GRAPHITE_GLASSY_PALETTE_OVERRIDE,
        "amoled": AMOLED_PALETTE_OVERRIDE,
        "amoled-glassy": AMOLED_GLASSY_PALETTE_OVERRIDE,
        "light": LIGHT_PALETTE_OVERRIDE,
        "light-glassy": LIGHT_GLASSY_PALETTE_OVERRIDE,
    }

    button_size = TokenManager.get("geometry", "traffic_lights", "size", default=14)
    button_spacing = TokenManager.get("geometry", "traffic_lights", "spacing", default=8)

    for key, info in THEMES.items():
        tname = info["theme_name"]
        src_tdir = os.path.join(repo_themes, tname)
        dst_tdir = os.path.join(stage_dir, tname)
        if not os.path.exists(src_tdir):
            continue

        for gver in ["gtk-4.0", "gtk-3.0", "gtk-2.0", "gnome-shell", "cinnamon", "metacity-1", "xfwm4", "unity", "plank", "labwc"]:
            s_gver = os.path.join(src_tdir, gver)
            d_gver = os.path.join(dst_tdir, gver)
            if os.path.exists(s_gver):
                os.makedirs(d_gver, exist_ok=True)
                for item in os.listdir(s_gver):
                    s_item = os.path.join(s_gver, item)
                    d_item = os.path.join(d_gver, item)
                    if os.path.isdir(s_item) and not os.path.exists(d_item):
                        shutil.copytree(s_item, d_item, symlinks=True)
                    elif os.path.isfile(s_item) and not item.endswith(".css"):
                        shutil.copy2(s_item, d_item)

        idx_theme = os.path.join(src_tdir, "index.theme")
        if os.path.exists(idx_theme):
            shutil.copy2(idx_theme, os.path.join(dst_tdir, "index.theme"))

        is_glassy = info["is_glassy"]
        is_dark = info["is_dark"]
        palette = palette_map.get(key, GRAPHITE_PALETTE_OVERRIDE)

        for gver in ["gtk-4.0", "gtk-3.0"]:
            s_gver = os.path.join(src_tdir, gver)
            d_gver = os.path.join(dst_tdir, gver)
            for css_file in ["gtk.css", "gtk-dark.css"]:
                src_css = os.path.join(s_gver, css_file)
                dst_css = os.path.join(d_gver, css_file)
                base_css = src_css + ".base"
                read_src = base_css if os.path.exists(base_css) else src_css
                if os.path.exists(read_src):
                    inject_theme_css(read_src, dst_css, palette, is_glassy, button_size, button_spacing, chromium_accent="default", is_dark=is_dark)

    print(f"[ThemeManager] Staged all 6 themes successfully to: {stage_dir}")
    return stage_dir

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--stage":
        sdir = sys.argv[2] if len(sys.argv) > 2 else None
        stage_all_themes(sdir)
    elif len(sys.argv) > 1 and sys.argv[1] == "--accent":
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

