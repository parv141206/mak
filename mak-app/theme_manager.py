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
        "icon_theme": "MacTahoe-purple-dark",
        "cursor_theme": "MacTahoe-dark",
        "is_dark": True,
        "is_glassy": False,
        "dock_pill_color": "rgba(42, 42, 50, 0.40)",
        "dock_border_color": "rgba(255, 255, 255, 0.28)",
        "window_border_color": "(1.0, 1.0, 1.0, 0.18)",
        "description": "Refined solid macOS dark mode with sleek Sonoma graphite windows (#242426) and purple accents."
    },
    "dark-glassy": {
        "id": "dark-glassy",
        "name": "macOS Dark Glass (Sonoma Frosted Glass)",
        "theme_name": ">>>Mac-Dark-glassy-purple",
        "color_scheme": "prefer-dark",
        "icon_theme": "MacTahoe-purple-dark",
        "cursor_theme": "MacTahoe-dark",
        "is_dark": True,
        "is_glassy": True,
        "dock_pill_color": "rgba(32, 32, 40, 0.28)",
        "dock_border_color": "rgba(255, 255, 255, 0.22)",
        "window_border_color": "(1.0, 1.0, 1.0, 0.20)",
        "description": "Translucent frosted glass dark mode with translucent windows and vibrant backdrop blur."
    },
    "amoled": {
        "id": "amoled",
        "name": "macOS AMOLED Dark Solid (Pitch Black)",
        "theme_name": ">>>Mac-Dark-Amoled-purple",
        "color_scheme": "prefer-dark",
        "icon_theme": "MacTahoe-purple-dark",
        "cursor_theme": "MacTahoe-dark",
        "is_dark": True,
        "is_glassy": False,
        "dock_pill_color": "rgba(10, 10, 12, 0.60)",
        "dock_border_color": "rgba(255, 255, 255, 0.16)",
        "window_border_color": "(1.0, 1.0, 1.0, 0.14)",
        "description": "True pitch black solid OLED Midnight (#000000) with ultra-high contrast and obsidian surfaces."
    },
    "amoled-glassy": {
        "id": "amoled-glassy",
        "name": "macOS AMOLED Glass (Obsidian Translucent)",
        "theme_name": ">>>Mac-Dark-Amoled-glassy-purple",
        "color_scheme": "prefer-dark",
        "icon_theme": "MacTahoe-purple-dark",
        "cursor_theme": "MacTahoe-dark",
        "is_dark": True,
        "is_glassy": True,
        "dock_pill_color": "rgba(0, 0, 0, 0.35)",
        "dock_border_color": "rgba(255, 255, 255, 0.16)",
        "window_border_color": "(1.0, 1.0, 1.0, 0.16)",
        "description": "Translucent pitch black obsidian glass with deep backdrop blur and purple highlights."
    },
    "light": {
        "id": "light",
        "name": "macOS Light Solid (Crisp Apple)",
        "theme_name": ">>>Mac-Light-solid-purple",
        "color_scheme": "prefer-light",
        "icon_theme": "MacTahoe-purple-light",
        "cursor_theme": "MacTahoe-light",
        "is_dark": False,
        "is_glassy": False,
        "dock_pill_color": "rgba(255, 255, 255, 0.42)",
        "dock_border_color": "rgba(255, 255, 255, 0.65)",
        "window_border_color": "(0.0, 0.0, 0.0, 0.12)",
        "description": "Clean, luminous solid macOS light mode with subtle borders and crisp typography."
    },
    "light-glassy": {
        "id": "light-glassy",
        "name": "macOS Light Glass (Apple Frosted Glass)",
        "theme_name": ">>>Mac-Light-glassy-purple",
        "color_scheme": "prefer-light",
        "icon_theme": "MacTahoe-purple-light",
        "cursor_theme": "MacTahoe-light",
        "is_dark": False,
        "is_glassy": True,
        "dock_pill_color": "rgba(255, 255, 255, 0.30)",
        "dock_border_color": "rgba(255, 255, 255, 0.55)",
        "window_border_color": "(0.0, 0.0, 0.0, 0.14)",
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

GRAPHITE_GLASSY_PALETTE_OVERRIDE = """
/* ── Mak macOS Sonoma Graphite Glass Frosted Translucent Palette ─────────── */
@define-color window_bg_color rgba(36, 36, 40, 0.72);
@define-color window_fg_color #f5f5f7;
@define-color view_bg_color rgba(28, 28, 32, 0.68);
@define-color view_fg_color #f5f5f7;
@define-color headerbar_bg_color rgba(44, 44, 48, 0.75);
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

AMOLED_GLASSY_PALETTE_OVERRIDE = """
/* ── Mak macOS AMOLED Obsidian Glass Translucent Palette ─────────────────── */
@define-color window_bg_color rgba(0, 0, 0, 0.75);
@define-color window_fg_color #ffffff;
@define-color view_bg_color rgba(0, 0, 0, 0.70);
@define-color view_fg_color #ffffff;
@define-color headerbar_bg_color rgba(12, 12, 14, 0.80);
@define-color headerbar_fg_color #ffffff;
@define-color headerbar_border_color rgba(255, 255, 255, 0.12);
@define-color sidebar_bg_color rgba(0, 0, 0, 0.68);
@define-color sidebar_fg_color #ffffff;
@define-color secondary_sidebar_bg_color rgba(0, 0, 0, 0.62);
@define-color card_bg_color rgba(18, 18, 22, 0.70);
@define-color card_fg_color #ffffff;
@define-color dialog_bg_color rgba(12, 12, 14, 0.85);
@define-color dialog_fg_color #ffffff;
@define-color popover_bg_color rgba(14, 14, 16, 0.85);
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

LIGHT_GLASSY_PALETTE_OVERRIDE = """
/* ── Mak macOS Crisp Apple Frosted Glass Translucent Palette ──────────────── */
@define-color window_bg_color rgba(246, 246, 248, 0.75);
@define-color window_fg_color #1d1d1f;
@define-color view_bg_color rgba(255, 255, 255, 0.72);
@define-color view_fg_color #1d1d1f;
@define-color headerbar_bg_color rgba(235, 235, 239, 0.78);
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
.background,
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
.nautilus-window,
.nautilus-window view,
.nautilus-window .view,
.nautilus-window scrolledwindow,
.nautilus-window columnview,
.nautilus-window listview,
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

def generate_traffic_lights_override(button_size=14, button_spacing=8):
    size = max(10, min(22, int(button_size)))
    spacing = max(0, min(24, int(button_spacing)))
    margin = max(0, round(spacing / 2))
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

/* Universal Chrome, Chromium & GTK transparent titlebar controls background */
window.background.chromium headerbar,
window.background.chromium headerbar.titlebar,
window.background.chromium headerbar.header-bar.titlebar {{
    padding: 0;
    margin: 0;
    background-color: transparent;
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
window.background.chromium headerbar.header-bar.titlebar windowcontrols button,
window.background.chromium headerbar.header-bar.titlebar windowcontrols button:hover,
window.background.chromium headerbar.header-bar.titlebar windowcontrols button:active,
window.background.chromium headerbar.header-bar.titlebar windowcontrols button.close,
window.background.chromium headerbar.header-bar.titlebar windowcontrols button.close:hover,
window.background.chromium headerbar.header-bar.titlebar windowcontrols button.maximize,
window.background.chromium headerbar.header-bar.titlebar windowcontrols button.maximize:hover,
window.background.chromium headerbar.header-bar.titlebar windowcontrols button.minimize,
window.background.chromium headerbar.header-bar.titlebar windowcontrols button.minimize:hover,
window.background.csd headerbar.header-bar.titlebar windowcontrols button,
window.background.csd headerbar.header-bar.titlebar windowcontrols button:hover,
window.background.csd headerbar.header-bar.titlebar windowcontrols button:active,
window.background.csd headerbar.header-bar.titlebar windowcontrols button:backdrop,
window.background.csd headerbar.header-bar.titlebar windowcontrols button:backdrop:hover,
window.background.csd headerbar.header-bar.titlebar windowcontrols button.close,
window.background.csd headerbar.header-bar.titlebar windowcontrols button.close:hover,
window.background.csd headerbar.header-bar.titlebar windowcontrols button.close:active,
window.background.csd headerbar.header-bar.titlebar windowcontrols button.close:backdrop,
window.background.csd headerbar.header-bar.titlebar windowcontrols button.close:backdrop:hover,
window.background.csd headerbar.header-bar.titlebar windowcontrols button.maximize,
window.background.csd headerbar.header-bar.titlebar windowcontrols button.maximize:hover,
window.background.csd headerbar.header-bar.titlebar windowcontrols button.maximize:active,
window.background.csd headerbar.header-bar.titlebar windowcontrols button.maximize:backdrop,
window.background.csd headerbar.header-bar.titlebar windowcontrols button.maximize:backdrop:hover,
window.background.csd headerbar.header-bar.titlebar windowcontrols button.minimize,
window.background.csd headerbar.header-bar.titlebar windowcontrols button.minimize:hover,
window.background.csd headerbar.header-bar.titlebar windowcontrols button.minimize:active,
window.background.csd headerbar.header-bar.titlebar windowcontrols button.minimize:backdrop,
window.background.csd headerbar.header-bar.titlebar windowcontrols button.minimize:backdrop:hover,
window.background.csd headerbar.header-bar.titlebar windowcontrols button.titlebutton,
window.background.csd headerbar.header-bar.titlebar windowcontrols button.titlebutton:hover,
window.background.csd headerbar.header-bar.titlebar windowcontrols button.titlebutton:active,
window.background.csd headerbar.header-bar.titlebar windowcontrols button.titlebutton.close,
window.background.csd headerbar.header-bar.titlebar windowcontrols button.titlebutton.close:hover,
window.background.csd headerbar.header-bar.titlebar windowcontrols button.titlebutton.close:active,
window.background.csd headerbar.header-bar.titlebar windowcontrols button.titlebutton.close:backdrop,
window.background.csd headerbar.header-bar.titlebar windowcontrols button.titlebutton.close:backdrop:hover,
window.background.csd headerbar.header-bar.titlebar windowcontrols button.titlebutton.maximize,
window.background.csd headerbar.header-bar.titlebar windowcontrols button.titlebutton.maximize:hover,
window.background.csd headerbar.header-bar.titlebar windowcontrols button.titlebutton.maximize:active,
window.background.csd headerbar.header-bar.titlebar windowcontrols button.titlebutton.maximize:backdrop,
window.background.csd headerbar.header-bar.titlebar windowcontrols button.titlebutton.maximize:backdrop:hover,
window.background.csd headerbar.header-bar.titlebar windowcontrols button.titlebutton.minimize,
window.background.csd headerbar.header-bar.titlebar windowcontrols button.titlebutton.minimize:hover,
window.background.csd headerbar.header-bar.titlebar windowcontrols button.titlebutton.minimize:active,
window.background.csd headerbar.header-bar.titlebar windowcontrols button.titlebutton.minimize:backdrop,
window.background.csd headerbar.header-bar.titlebar windowcontrols button.titlebutton.minimize:backdrop:hover {{
    min-width: {size}px;
    min-height: {size}px;
    padding: 0;
    margin: 0 {margin}px;
    border-radius: 9999px;
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
"""

TRAFFIC_LIGHTS_OVERRIDE = generate_traffic_lights_override(14, 8)

WINDOW_CORNERS_CSS_OVERRIDE = """
/* ── Mak macOS Window Corner & Geometry Consistency (16px) ──────────────── */
window,
window.background,
window.csd,
window.background.csd,
window.background.solid-csd,
window.solid-csd {
    border-radius: 16px;
}

window.csd.maximized,
window.csd.tiled,
window.csd.tiled-top,
window.csd.tiled-bottom,
window.csd.tiled-left,
window.csd.tiled-right,
window.background.maximized,
window.background.maximized.csd,
window.background.solid-csd.maximized,
window.background.csd.maximized,
window.maximized.csd,
window.maximized.solid-csd,
window.maximized,
window.background.tiled,
window.background.tiled-top,
window.background.tiled-right,
window.background.tiled-bottom,
window.background.tiled-left,
window.background.csd.tiled,
window.tiled.csd,
window.tiled {
    border-radius: 16px;
}

headerbar,
headerbar.default-decoration,
.titlebar,
window.csd > headerbar,
window.background.csd > headerbar,
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
window.tiled .titlebar {
    border-top-left-radius: 16px;
    border-top-right-radius: 16px;
}

window.background.maximized > contents,
window.background.maximized.csd > contents,
window.background.csd.maximized > contents,
window.maximized.csd > contents,
window.maximized > contents,
window.background.maximized > widget,
window.maximized > widget,
window.background.maximized > box,
window.maximized > box {
    border-radius: 16px;
}

window.background.chromium headerbar.header-bar.titlebar {
    border-radius: 16px 16px 0 0;
}

/* True Fullscreen Only */
window.fullscreen,
window.csd.fullscreen,
window.background.fullscreen,
window.background.fullscreen.csd,
window.background.csd.fullscreen,
window.fullscreen.csd {
    border-radius: 0;
    outline: none;
    box-shadow: none;
    border: none;
}

window.fullscreen headerbar,
window.fullscreen .titlebar,
window.background.fullscreen headerbar,
window.background.fullscreen.csd headerbar,
window.background.csd.fullscreen headerbar,
window.fullscreen.csd headerbar {
    border-radius: 0;
}
"""

def inject_theme_css(src_css_path, dst_css_path, palette, is_glassy, button_size=14, button_spacing=8):
    try:
        with open(src_css_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        content = ""

    color_keys = [
        "window_bg_color", "window_fg_color", "view_bg_color", "view_fg_color",
        "headerbar_bg_color", "headerbar_fg_color", "headerbar_border_color",
        "sidebar_bg_color", "sidebar_fg_color", "secondary_sidebar_bg_color",
        "card_bg_color", "card_fg_color", "dialog_bg_color", "dialog_fg_color",
        "popover_bg_color", "popover_fg_color", "placeholder_text_color"
    ]
    lines = content.splitlines()
    filtered = []
    for line in lines:
        stripped = line.strip()
        if any(stripped.startswith(f"@define-color {k} ") for k in color_keys):
            continue
        filtered.append(line)

    traffic_override = generate_traffic_lights_override(button_size, button_spacing)
    rules_to_append = [traffic_override, WINDOW_CORNERS_CSS_OVERRIDE]
    if is_glassy:
        rules_to_append.append(GLASSY_CONTAINER_RULES)

    final_content = palette.strip() + "\n\n" + "\n".join(filtered) + "\n\n" + "\n\n".join(rules_to_append) + "\n"
    with open(dst_css_path, "w", encoding="utf-8") as f:
        f.write(final_content)


def update_titlebar_buttons(button_size=None, button_spacing=None):
    """Dynamically regenerates GTK 4 and GTK 3 active CSS configurations with the new traffic light button size and spacing."""
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
            button_spacing = int(res.stdout.strip())
        except Exception:
            button_spacing = 8

    theme_key = get_current_theme()
    theme_info = THEMES.get(theme_key, THEMES["dark"])
    theme_name = theme_info["theme_name"]
    source_dir = os.path.join(THEMES_DIR, theme_name)
    is_glassy = theme_info.get("is_glassy", False)

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
                inject_theme_css(src_css, dst_css, palette_override, is_glassy, button_size, button_spacing)

    # GTK 3
    src_gtk3 = os.path.join(source_dir, "gtk-3.0")
    if os.path.exists(src_gtk3):
        for css_file in ["gtk.css", "gtk-dark.css"]:
            src_css = os.path.join(src_gtk3, css_file)
            dst_css = os.path.join(GTK3_CONFIG, css_file)
            if os.path.exists(src_css):
                inject_theme_css(src_css, dst_css, palette_override, is_glassy, button_size, button_spacing)

    ensure_settings_ini_decoration_layout()

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

        if os.path.exists(src_gtk4):
            # Generate gtk.css and gtk-dark.css with exact palette at top, no duplicate defines, and clean overrides
            for css_file in ["gtk.css", "gtk-dark.css"]:
                src_css = os.path.join(src_gtk4, css_file)
                dst_css = os.path.join(GTK4_CONFIG, css_file)
                if os.path.exists(src_css):
                    inject_theme_css(src_css, dst_css, palette_override, is_glassy, button_size, button_spacing)

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
                    inject_theme_css(src_css, dst_css, palette_override, is_glassy, button_size, button_spacing)

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
        w_border = theme_info.get("window_border_color", "(1.0, 1.0, 1.0, 0.16)")
        new_val = f"{{'padding': <{{'left': uint32 0, 'right': 0, 'top': 0, 'bottom': 0}}>, 'keepRoundedCorners': <{{'maximized': true, 'fullscreen': true}}>, 'borderRadius': <uint32 16>, 'smoothing': <0.8>, 'borderColor': <{w_border}>, 'enabled': <true>}}"
        subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.rounded-window-corners-reborn", "global-rounded-corner-settings", new_val], check=False)
        subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.rounded-window-corners-reborn", "border-width", "1"], check=False)
        subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.rounded-window-corners-reborn", "skip-libadwaita-app", "true"], check=False)
        subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.rounded-window-corners-reborn", "skip-libhandy-app", "true"], check=False)
        log.append(f"Updated window corner settings (radius 16, smoothing 0.8, border {w_border}, skip-libadwaita true).")
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
