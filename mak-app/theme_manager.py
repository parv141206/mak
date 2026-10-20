# SPDX-License-Identifier: GPL-3.0-or-later
# Mak Theme Manager: Global Theme Synchronizer across Shell, GTK 2/3/4, and Flatpak

import os
import sys
import json
import subprocess
import shutil
import re

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
                "segmented": {"height": 22, "container_radius": 9999, "segment_radius": 9999},
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

def hex_to_rgba(hex_str, alpha=1.0):
    hex_str = hex_str.lstrip('#')
    if len(hex_str) == 3:
        hex_str = ''.join(c * 2 for c in hex_str)
    r = int(hex_str[0:2], 16)
    g = int(hex_str[2:4], 16)
    b = int(hex_str[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha:.2f})"

def deepen_hex(hex_str, factor=0.25):
    hex_str = hex_str.lstrip('#')
    if len(hex_str) == 3:
        hex_str = ''.join(c * 2 for c in hex_str)
    r = max(0, min(255, int(int(hex_str[0:2], 16) * factor)))
    g = max(0, min(255, int(int(hex_str[2:4], 16) * factor)))
    b = max(0, min(255, int(int(hex_str[4:6], 16) * factor)))
    return f"#{r:02x}{g:02x}{b:02x}"

THEME_FLAVORS = {
    "default": {
        "id": "default",
        "name": "macOS Native",
        "subtitle": "Sonoma Graphite / Apple White",
        "description": "Authentic macOS Sonoma native styling with precision-balanced graphite dark mode and crisp luminous light mode.",
        "dark": {
            "name": "Sonoma Graphite",
            "window_bg": "#242426",
            "window_fg": "#f5f5f7",
            "view_bg": "#1c1c1e",
            "view_fg": "#f5f5f7",
            "headerbar_bg": "#242426",
            "headerbar_solid_bg": "#242426",
            "headerbar_fg": "#ffffff",
            "sidebar_bg": "#242426",
            "sidebar_fg": "#f5f5f7",
            "card_bg": "#2c2c2e",
            "card_fg": "#f5f5f7",
            "dialog_bg": "#28282a",
            "dialog_fg": "#f5f5f7",
            "popover_bg": "#2c2c2e",
            "popover_fg": "#f5f5f7",
            "accent_color": "#007aff",
            "border_color": "rgba(255, 255, 255, 0.12)",
            "placeholder_text_color": "rgba(255, 255, 255, 0.45)",
            "dock_pill": "rgba(42, 42, 50, 0.40)",
            "dock_border": "rgba(255, 255, 255, 0.28)",
            "app_tint": "#242426",
            "gnome_accent": "blue"
        },
        "light": {
            "name": "Apple Crisp White",
            "window_bg": "#ececf0",
            "window_fg": "#1d1d1f",
            "view_bg": "#ffffff",
            "view_fg": "#1d1d1f",
            "headerbar_bg": "#ececf0",
            "headerbar_solid_bg": "#ececf0",
            "headerbar_fg": "#1d1d1f",
            "sidebar_bg": "#ececf0",
            "sidebar_fg": "#1d1d1f",
            "card_bg": "#ffffff",
            "card_fg": "#1d1d1f",
            "dialog_bg": "#ebebef",
            "dialog_fg": "#1d1d1f",
            "popover_bg": "#ffffff",
            "popover_fg": "#1d1d1f",
            "accent_color": "#007aff",
            "border_color": "rgba(0, 0, 0, 0.10)",
            "placeholder_text_color": "rgba(0, 0, 0, 0.45)",
            "dock_pill": "rgba(255, 255, 255, 0.42)",
            "dock_border": "rgba(255, 255, 255, 0.65)",
            "app_tint": "#ececf0",
            "gnome_accent": "blue"
        }
    },
    "catppuccin": {
        "id": "catppuccin",
        "name": "Catppuccin",
        "subtitle": "Mocha / Latte",
        "description": "Soothing pastel palette with deep Mocha velvety dark mode and warm comforting Latte light mode.",
        "dark": {
            "name": "Mocha",
            "window_bg": "#1e1e2e",
            "window_fg": "#cdd6f4",
            "view_bg": "#181825",
            "view_fg": "#cdd6f4",
            "headerbar_bg": "#1e1e2e",
            "headerbar_solid_bg": "#1e1e2e",
            "headerbar_fg": "#cdd6f4",
            "sidebar_bg": "#181825",
            "sidebar_fg": "#cdd6f4",
            "card_bg": "#313244",
            "card_fg": "#cdd6f4",
            "dialog_bg": "#181825",
            "dialog_fg": "#cdd6f4",
            "popover_bg": "#313244",
            "popover_fg": "#cdd6f4",
            "accent_color": "#cba6f7",
            "border_color": "rgba(203, 166, 247, 0.15)",
            "placeholder_text_color": "rgba(205, 214, 244, 0.45)",
            "dock_pill": "rgba(30, 30, 46, 0.45)",
            "dock_border": "rgba(203, 166, 247, 0.35)",
            "app_tint": "#1e1e2e",
            "gnome_accent": "purple"
        },
        "light": {
            "name": "Latte",
            "window_bg": "#eff1f5",
            "window_fg": "#4c4f69",
            "view_bg": "#ffffff",
            "view_fg": "#4c4f69",
            "headerbar_bg": "#e6e9ef",
            "headerbar_solid_bg": "#e6e9ef",
            "headerbar_fg": "#4c4f69",
            "sidebar_bg": "#e6e9ef",
            "sidebar_fg": "#4c4f69",
            "card_bg": "#ccd0da",
            "card_fg": "#4c4f69",
            "dialog_bg": "#e6e9ef",
            "dialog_fg": "#4c4f69",
            "popover_bg": "#eff1f5",
            "popover_fg": "#4c4f69",
            "accent_color": "#8839ef",
            "border_color": "rgba(136, 57, 239, 0.15)",
            "placeholder_text_color": "rgba(76, 79, 105, 0.45)",
            "dock_pill": "rgba(239, 241, 245, 0.55)",
            "dock_border": "rgba(136, 57, 239, 0.35)",
            "app_tint": "#eff1f5",
            "gnome_accent": "purple"
        }
    },
    "deep-teal": {
        "id": "deep-teal",
        "name": "Deep Teal",
        "subtitle": "Teal Abyss / Mint Ocean",
        "description": "Rich oceanic atmosphere featuring deep midnight teal waters and vibrant crisp mint accents.",
        "dark": {
            "name": "Teal Abyss",
            "window_bg": "#0b1d20",
            "window_fg": "#e0f2f1",
            "view_bg": "#0b1d20",
            "view_fg": "#e0f2f1",
            "headerbar_bg": "#0b1d20",
            "headerbar_solid_bg": "#0b1d20",
            "headerbar_fg": "#e0f2f1",
            "sidebar_bg": "#07171a",
            "sidebar_fg": "#e0f2f1",
            "card_bg": "#11282c",
            "card_fg": "#e0f2f1",
            "dialog_bg": "#0b1d20",
            "dialog_fg": "#e0f2f1",
            "popover_bg": "#11282c",
            "popover_fg": "#e0f2f1",
            "accent_color": "#20b2aa",
            "border_color": "rgba(32, 178, 170, 0.20)",
            "placeholder_text_color": "rgba(224, 242, 241, 0.45)",
            "dock_pill": "rgba(11, 29, 32, 0.50)",
            "dock_border": "rgba(32, 178, 170, 0.35)",
            "app_tint": "#0b1d20",
            "gnome_accent": "teal"
        },
        "light": {
            "name": "Mint Ocean",
            "window_bg": "#e6f4f3",
            "window_fg": "#0c2b2e",
            "view_bg": "#ffffff",
            "view_fg": "#0c2b2e",
            "headerbar_bg": "#d9eded",
            "headerbar_solid_bg": "#d9eded",
            "headerbar_fg": "#0c2b2e",
            "sidebar_bg": "#eaf4f3",
            "sidebar_fg": "#0c2b2e",
            "card_bg": "#ffffff",
            "card_fg": "#0c2b2e",
            "dialog_bg": "#d9eded",
            "dialog_fg": "#0c2b2e",
            "popover_bg": "#ffffff",
            "popover_fg": "#0c2b2e",
            "accent_color": "#008b8b",
            "border_color": "rgba(0, 139, 139, 0.15)",
            "placeholder_text_color": "rgba(12, 43, 46, 0.45)",
            "dock_pill": "rgba(230, 244, 243, 0.60)",
            "dock_border": "rgba(0, 139, 139, 0.35)",
            "app_tint": "#e6f4f3",
            "gnome_accent": "teal"
        }
    },
    "rose-pine": {
        "id": "rose-pine",
        "name": "Rosé Pine",
        "subtitle": "Rosé Pine / Dawn",
        "description": "All natural pine, faux fur, and delicate rose highlights inspired by moody Pacific Northwest tones.",
        "dark": {
            "name": "Rosé Pine Main",
            "window_bg": "#191724",
            "window_fg": "#e0def4",
            "view_bg": "#191724",
            "view_fg": "#e0def4",
            "headerbar_bg": "#191724",
            "headerbar_solid_bg": "#191724",
            "headerbar_fg": "#e0def4",
            "sidebar_bg": "#191724",
            "sidebar_fg": "#e0def4",
            "card_bg": "#26233a",
            "card_fg": "#e0def4",
            "dialog_bg": "#191724",
            "dialog_fg": "#e0def4",
            "popover_bg": "#26233a",
            "popover_fg": "#e0def4",
            "accent_color": "#eb6f92",
            "border_color": "rgba(235, 111, 146, 0.16)",
            "placeholder_text_color": "rgba(224, 222, 244, 0.45)",
            "dock_pill": "rgba(25, 23, 36, 0.50)",
            "dock_border": "rgba(235, 111, 146, 0.35)",
            "app_tint": "#191724",
            "gnome_accent": "purple"
        },
        "light": {
            "name": "Rosé Pine Dawn",
            "window_bg": "#faf4ed",
            "window_fg": "#575279",
            "view_bg": "#fffaf3",
            "view_fg": "#575279",
            "headerbar_bg": "#f2e9de",
            "headerbar_solid_bg": "#f2e9de",
            "headerbar_fg": "#575279",
            "sidebar_bg": "#f2e9de",
            "sidebar_fg": "#575279",
            "card_bg": "#ebdfcf",
            "card_fg": "#575279",
            "dialog_bg": "#f2e9de",
            "dialog_fg": "#575279",
            "popover_bg": "#fffaf3",
            "popover_fg": "#575279",
            "accent_color": "#d7827e",
            "border_color": "rgba(215, 130, 126, 0.18)",
            "placeholder_text_color": "rgba(87, 82, 121, 0.45)",
            "dock_pill": "rgba(250, 244, 237, 0.60)",
            "dock_border": "rgba(215, 130, 126, 0.35)",
            "app_tint": "#faf4ed",
            "gnome_accent": "purple"
        }
    },
    "tokyo-night": {
        "id": "tokyo-night",
        "name": "Tokyo Night",
        "subtitle": "Storm / Day",
        "description": "Clean, stylish dark and daylight palettes celebrating the neon twilight of downtown Tokyo.",
        "dark": {
            "name": "Tokyo Night Storm",
            "window_bg": "#24283b",
            "window_fg": "#c0caf5",
            "view_bg": "#1a1b26",
            "view_fg": "#c0caf5",
            "headerbar_bg": "#1f2335",
            "headerbar_solid_bg": "#1f2335",
            "headerbar_fg": "#c0caf5",
            "sidebar_bg": "#1a1b26",
            "sidebar_fg": "#c0caf5",
            "card_bg": "#292e42",
            "card_fg": "#c0caf5",
            "dialog_bg": "#1f2335",
            "dialog_fg": "#c0caf5",
            "popover_bg": "#292e42",
            "popover_fg": "#c0caf5",
            "accent_color": "#7aa2f7",
            "border_color": "rgba(122, 162, 247, 0.16)",
            "placeholder_text_color": "rgba(192, 202, 245, 0.45)",
            "dock_pill": "rgba(31, 35, 53, 0.50)",
            "dock_border": "rgba(122, 162, 247, 0.35)",
            "app_tint": "#24283b",
            "gnome_accent": "blue"
        },
        "light": {
            "name": "Tokyo Night Day",
            "window_bg": "#e1e2e7",
            "window_fg": "#3760bf",
            "view_bg": "#ffffff",
            "view_fg": "#3760bf",
            "headerbar_bg": "#d5d6db",
            "headerbar_solid_bg": "#d5d6db",
            "headerbar_fg": "#3760bf",
            "sidebar_bg": "#d5d6db",
            "sidebar_fg": "#3760bf",
            "card_bg": "#cbccd1",
            "card_fg": "#3760bf",
            "dialog_bg": "#d5d6db",
            "dialog_fg": "#3760bf",
            "popover_bg": "#ffffff",
            "popover_fg": "#3760bf",
            "accent_color": "#2e7de9",
            "border_color": "rgba(46, 125, 233, 0.15)",
            "placeholder_text_color": "rgba(55, 96, 191, 0.45)",
            "dock_pill": "rgba(225, 226, 231, 0.60)",
            "dock_border": "rgba(46, 125, 233, 0.35)",
            "app_tint": "#e1e2e7",
            "gnome_accent": "blue"
        }
    },
    "nord": {
        "id": "nord",
        "name": "Nord",
        "subtitle": "Polar Night / Snow Storm",
        "description": "Arctic, north-bluish clean aesthetic with cold polar slate tones and frosted icy highlights.",
        "dark": {
            "name": "Polar Night",
            "window_bg": "#2e3440",
            "window_fg": "#eceff4",
            "view_bg": "#242933",
            "view_fg": "#eceff4",
            "headerbar_bg": "#2e3440",
            "headerbar_solid_bg": "#2e3440",
            "headerbar_fg": "#eceff4",
            "sidebar_bg": "#242933",
            "sidebar_fg": "#eceff4",
            "card_bg": "#3b4252",
            "card_fg": "#eceff4",
            "dialog_bg": "#2e3440",
            "dialog_fg": "#eceff4",
            "popover_bg": "#3b4252",
            "popover_fg": "#eceff4",
            "accent_color": "#88c0d0",
            "border_color": "rgba(136, 192, 208, 0.16)",
            "placeholder_text_color": "rgba(236, 239, 244, 0.45)",
            "dock_pill": "rgba(46, 52, 64, 0.50)",
            "dock_border": "rgba(136, 192, 208, 0.35)",
            "app_tint": "#2e3440",
            "gnome_accent": "teal"
        },
        "light": {
            "name": "Snow Storm",
            "window_bg": "#eceff4",
            "window_fg": "#2e3440",
            "view_bg": "#ffffff",
            "view_fg": "#2e3440",
            "headerbar_bg": "#e5e9f0",
            "headerbar_solid_bg": "#e5e9f0",
            "headerbar_fg": "#2e3440",
            "sidebar_bg": "#e5e9f0",
            "sidebar_fg": "#2e3440",
            "card_bg": "#d8dee9",
            "card_fg": "#2e3440",
            "dialog_bg": "#e5e9f0",
            "dialog_fg": "#2e3440",
            "popover_bg": "#ffffff",
            "popover_fg": "#2e3440",
            "accent_color": "#5e81ac",
            "border_color": "rgba(94, 129, 172, 0.15)",
            "placeholder_text_color": "rgba(46, 52, 64, 0.45)",
            "dock_pill": "rgba(236, 239, 244, 0.60)",
            "dock_border": "rgba(94, 129, 172, 0.35)",
            "app_tint": "#eceff4",
            "gnome_accent": "blue"
        }
    },
    "dracula": {
        "id": "dracula",
        "name": "Dracula",
        "subtitle": "Vamp / Alucard",
        "description": "Legendary dark gothic aesthetic with vibrant neon purple, pink, and cyan highlights.",
        "dark": {
            "name": "Dracula Vamp",
            "window_bg": "#282a36",
            "window_fg": "#f8f8f2",
            "view_bg": "#21222c",
            "view_fg": "#f8f8f2",
            "headerbar_bg": "#282a36",
            "headerbar_solid_bg": "#282a36",
            "headerbar_fg": "#f8f8f2",
            "sidebar_bg": "#21222c",
            "sidebar_fg": "#f8f8f2",
            "card_bg": "#343746",
            "card_fg": "#f8f8f2",
            "dialog_bg": "#282a36",
            "dialog_fg": "#f8f8f2",
            "popover_bg": "#343746",
            "popover_fg": "#f8f8f2",
            "accent_color": "#bd93f9",
            "border_color": "rgba(189, 147, 249, 0.18)",
            "placeholder_text_color": "rgba(248, 248, 242, 0.45)",
            "dock_pill": "rgba(40, 42, 54, 0.50)",
            "dock_border": "rgba(189, 147, 249, 0.35)",
            "app_tint": "#282a36",
            "gnome_accent": "purple"
        },
        "light": {
            "name": "Dracula Alucard",
            "window_bg": "#f8f8f2",
            "window_fg": "#282a36",
            "view_bg": "#ffffff",
            "view_fg": "#282a36",
            "headerbar_bg": "#ecebe4",
            "headerbar_solid_bg": "#ecebe4",
            "headerbar_fg": "#282a36",
            "sidebar_bg": "#ecebe4",
            "sidebar_fg": "#282a36",
            "card_bg": "#deded4",
            "card_fg": "#282a36",
            "dialog_bg": "#ecebe4",
            "dialog_fg": "#282a36",
            "popover_bg": "#ffffff",
            "popover_fg": "#282a36",
            "accent_color": "#955ec7",
            "border_color": "rgba(149, 94, 199, 0.15)",
            "placeholder_text_color": "rgba(40, 42, 54, 0.45)",
            "dock_pill": "rgba(248, 248, 242, 0.60)",
            "dock_border": "rgba(149, 94, 199, 0.35)",
            "app_tint": "#f8f8f2",
            "gnome_accent": "purple"
        }
    },
    "gruvbox": {
        "id": "gruvbox",
        "name": "Gruvbox",
        "subtitle": "Gruvbox Dark / Light",
        "description": "Retro groove color scheme with warm earthy undertones and unmistakable retro orange accents.",
        "dark": {
            "name": "Gruvbox Dark",
            "window_bg": "#282828",
            "window_fg": "#ebdbb2",
            "view_bg": "#1d2021",
            "view_fg": "#ebdbb2",
            "headerbar_bg": "#282828",
            "headerbar_solid_bg": "#282828",
            "headerbar_fg": "#ebdbb2",
            "sidebar_bg": "#1d2021",
            "sidebar_fg": "#ebdbb2",
            "card_bg": "#3c3836",
            "card_fg": "#ebdbb2",
            "dialog_bg": "#282828",
            "dialog_fg": "#ebdbb2",
            "popover_bg": "#3c3836",
            "popover_fg": "#ebdbb2",
            "accent_color": "#fe8019",
            "border_color": "rgba(254, 128, 25, 0.18)",
            "placeholder_text_color": "rgba(235, 219, 178, 0.45)",
            "dock_pill": "rgba(40, 40, 40, 0.50)",
            "dock_border": "rgba(254, 128, 25, 0.35)",
            "app_tint": "#282828",
            "gnome_accent": "orange"
        },
        "light": {
            "name": "Gruvbox Light",
            "window_bg": "#fbf1c7",
            "window_fg": "#3c3836",
            "view_bg": "#ffffff",
            "view_fg": "#3c3836",
            "headerbar_bg": "#f2e5bc",
            "headerbar_solid_bg": "#f2e5bc",
            "headerbar_fg": "#3c3836",
            "sidebar_bg": "#f2e5bc",
            "sidebar_fg": "#3c3836",
            "card_bg": "#ebdbb2",
            "card_fg": "#3c3836",
            "dialog_bg": "#f2e5bc",
            "dialog_fg": "#3c3836",
            "popover_bg": "#ffffff",
            "popover_fg": "#3c3836",
            "accent_color": "#af3a03",
            "border_color": "rgba(175, 58, 3, 0.18)",
            "placeholder_text_color": "rgba(60, 56, 54, 0.45)",
            "dock_pill": "rgba(251, 241, 199, 0.60)",
            "dock_border": "rgba(175, 58, 3, 0.35)",
            "app_tint": "#fbf1c7",
            "gnome_accent": "orange"
        }
    },
    "cyberpunk": {
        "id": "cyberpunk",
        "name": "Cyberpunk",
        "subtitle": "Neon / Sunrise",
        "description": "High-octane synthwave and neon cyberpunk aesthetic with blazing magenta and cyan glows.",
        "dark": {
            "name": "Cyberpunk Neon",
            "window_bg": "#120e24",
            "window_fg": "#00f0ff",
            "view_bg": "#090614",
            "view_fg": "#00f0ff",
            "headerbar_bg": "#120e24",
            "headerbar_solid_bg": "#120e24",
            "headerbar_fg": "#00f0ff",
            "sidebar_bg": "#090614",
            "sidebar_fg": "#00f0ff",
            "card_bg": "#20183b",
            "card_fg": "#00f0ff",
            "dialog_bg": "#120e24",
            "dialog_fg": "#00f0ff",
            "popover_bg": "#20183b",
            "popover_fg": "#00f0ff",
            "accent_color": "#ff0055",
            "border_color": "rgba(0, 240, 255, 0.22)",
            "placeholder_text_color": "rgba(0, 240, 255, 0.45)",
            "dock_pill": "rgba(18, 14, 36, 0.55)",
            "dock_border": "rgba(0, 240, 255, 0.40)",
            "app_tint": "#120e24",
            "gnome_accent": "red"
        },
        "light": {
            "name": "Cyberpunk Sunrise",
            "window_bg": "#fbf0f8",
            "window_fg": "#2b1029",
            "view_bg": "#ffffff",
            "view_fg": "#2b1029",
            "headerbar_bg": "#f4dced",
            "headerbar_solid_bg": "#f4dced",
            "headerbar_fg": "#2b1029",
            "sidebar_bg": "#f4dced",
            "sidebar_fg": "#2b1029",
            "card_bg": "#eac3df",
            "card_fg": "#2b1029",
            "dialog_bg": "#f4dced",
            "dialog_fg": "#2b1029",
            "popover_bg": "#ffffff",
            "popover_fg": "#2b1029",
            "accent_color": "#d6006e",
            "border_color": "rgba(214, 0, 110, 0.18)",
            "placeholder_text_color": "rgba(43, 16, 41, 0.45)",
            "dock_pill": "rgba(251, 240, 248, 0.60)",
            "dock_border": "rgba(214, 0, 110, 0.35)",
            "app_tint": "#fbf0f8",
            "gnome_accent": "red"
        }
    },
    "monokai": {
        "id": "monokai",
        "name": "Monokai Pro",
        "subtitle": "Dark / Light",
        "description": "Refined pro developer color scheme with warm charcoal foundations and vibrant syntax accents.",
        "dark": {
            "name": "Monokai Pro Dark",
            "window_bg": "#2d2a2e",
            "window_fg": "#fcfcfa",
            "view_bg": "#221f22",
            "view_fg": "#fcfcfa",
            "headerbar_bg": "#2d2a2e",
            "headerbar_solid_bg": "#2d2a2e",
            "headerbar_fg": "#fcfcfa",
            "sidebar_bg": "#221f22",
            "sidebar_fg": "#fcfcfa",
            "card_bg": "#3a383d",
            "card_fg": "#fcfcfa",
            "dialog_bg": "#2d2a2e",
            "dialog_fg": "#fcfcfa",
            "popover_bg": "#3a383d",
            "popover_fg": "#fcfcfa",
            "accent_color": "#ffd866",
            "border_color": "rgba(255, 216, 102, 0.18)",
            "placeholder_text_color": "rgba(252, 252, 250, 0.45)",
            "dock_pill": "rgba(45, 42, 46, 0.50)",
            "dock_border": "rgba(255, 216, 102, 0.35)",
            "app_tint": "#2d2a2e",
            "gnome_accent": "yellow"
        },
        "light": {
            "name": "Monokai Pro Light",
            "window_bg": "#faf4f0",
            "window_fg": "#2d2a2e",
            "view_bg": "#ffffff",
            "view_fg": "#2d2a2e",
            "headerbar_bg": "#f0eae5",
            "headerbar_solid_bg": "#f0eae5",
            "headerbar_fg": "#2d2a2e",
            "sidebar_bg": "#f0eae5",
            "sidebar_fg": "#2d2a2e",
            "card_bg": "#e4dbd4",
            "card_fg": "#2d2a2e",
            "dialog_bg": "#f0eae5",
            "dialog_fg": "#2d2a2e",
            "popover_bg": "#ffffff",
            "popover_fg": "#2d2a2e",
            "accent_color": "#e05574",
            "border_color": "rgba(224, 85, 116, 0.18)",
            "placeholder_text_color": "rgba(45, 42, 46, 0.45)",
            "dock_pill": "rgba(250, 244, 240, 0.60)",
            "dock_border": "rgba(224, 85, 116, 0.35)",
            "app_tint": "#faf4f0",
            "gnome_accent": "red"
        }
    },
    "everforest": {
        "id": "everforest",
        "name": "Everforest",
        "subtitle": "Dark / Light",
        "description": "Comfortable, nature-inspired green palette designed to be easy on the eyes and organic.",
        "dark": {
            "name": "Everforest Dark",
            "window_bg": "#2d353b",
            "window_fg": "#d3c6aa",
            "view_bg": "#232a2e",
            "view_fg": "#d3c6aa",
            "headerbar_bg": "#2d353b",
            "headerbar_solid_bg": "#2d353b",
            "headerbar_fg": "#d3c6aa",
            "sidebar_bg": "#232a2e",
            "sidebar_fg": "#d3c6aa",
            "card_bg": "#343f44",
            "card_fg": "#d3c6aa",
            "dialog_bg": "#2d353b",
            "dialog_fg": "#d3c6aa",
            "popover_bg": "#343f44",
            "popover_fg": "#d3c6aa",
            "accent_color": "#a7c080",
            "border_color": "rgba(167, 192, 128, 0.18)",
            "placeholder_text_color": "rgba(211, 198, 170, 0.45)",
            "dock_pill": "rgba(45, 53, 59, 0.50)",
            "dock_border": "rgba(167, 192, 128, 0.35)",
            "app_tint": "#2d353b",
            "gnome_accent": "green"
        },
        "light": {
            "name": "Everforest Light",
            "window_bg": "#fdf6e3",
            "window_fg": "#5c6a72",
            "view_bg": "#ffffff",
            "view_fg": "#5c6a72",
            "headerbar_bg": "#f4ede0",
            "headerbar_solid_bg": "#f4ede0",
            "headerbar_fg": "#5c6a72",
            "sidebar_bg": "#f4ede0",
            "sidebar_fg": "#5c6a72",
            "card_bg": "#eae1ce",
            "card_fg": "#5c6a72",
            "dialog_bg": "#f4ede0",
            "dialog_fg": "#5c6a72",
            "popover_bg": "#ffffff",
            "popover_fg": "#5c6a72",
            "accent_color": "#8da101",
            "border_color": "rgba(141, 161, 1, 0.18)",
            "placeholder_text_color": "rgba(92, 106, 114, 0.45)",
            "dock_pill": "rgba(253, 246, 227, 0.60)",
            "dock_border": "rgba(141, 161, 1, 0.35)",
            "app_tint": "#fdf6e3",
            "gnome_accent": "green"
        }
    }
}

def get_flavor_palette(flavor_key, is_dark, is_glassy=False, is_amoled=False):
    if not flavor_key or flavor_key not in THEME_FLAVORS:
        flavor_key = "default"

    flv = THEME_FLAVORS[flavor_key]
    mode_dict = flv["dark"] if is_dark else flv["light"]

    window_bg = mode_dict["window_bg"]
    view_bg = mode_dict["view_bg"]
    headerbar_bg = mode_dict["headerbar_bg"]
    headerbar_solid_bg = mode_dict.get("headerbar_solid_bg", headerbar_bg)
    headerbar_fg = mode_dict.get("headerbar_fg", mode_dict["window_fg"])
    sidebar_bg = mode_dict.get("sidebar_bg", window_bg)
    sidebar_fg = mode_dict.get("sidebar_fg", mode_dict["window_fg"])
    card_bg = mode_dict["card_bg"]
    card_fg = mode_dict.get("card_fg", mode_dict["window_fg"])
    dialog_bg = mode_dict.get("dialog_bg", window_bg)
    dialog_fg = mode_dict.get("dialog_fg", mode_dict["window_fg"])
    popover_bg = mode_dict.get("popover_bg", card_bg)
    popover_fg = mode_dict.get("popover_fg", mode_dict["window_fg"])
    border_color = mode_dict.get("border_color", "rgba(255, 255, 255, 0.12)" if is_dark else "rgba(0, 0, 0, 0.10)")
    placeholder_text_color = mode_dict.get("placeholder_text_color", "rgba(255, 255, 255, 0.45)" if is_dark else "rgba(0, 0, 0, 0.45)")
    accent_color = mode_dict.get("accent_color", "#007aff")
    window_fg = mode_dict["window_fg"]
    view_fg = mode_dict["view_fg"]

    if is_amoled and is_dark and flavor_key == "default":
        window_bg = "#000000"
        view_bg = "#000000"
        headerbar_bg = "#0a0a0c"
        headerbar_solid_bg = "#0a0a0c"
        sidebar_bg = "#0a0a0c"
        card_bg = "#121214"
        dialog_bg = "#121214"
        popover_bg = "#141416"

    if is_glassy:
        window_bg = hex_to_rgba(window_bg, 0.75)
        view_bg = hex_to_rgba(view_bg, 0.68)
        headerbar_bg = hex_to_rgba(headerbar_bg, 0.75)
        sidebar_bg = hex_to_rgba(sidebar_bg, 0.75)
        card_bg = hex_to_rgba(card_bg, 0.72)
        dialog_bg = hex_to_rgba(dialog_bg, 0.82)
        popover_bg = hex_to_rgba(popover_bg, 0.82)

    mode_label = ("AMOLED " if is_amoled and is_dark else "") + ("Glass " if is_glassy else "Solid ") + ("Dark" if is_dark else "Light")

    return f"""/* ── Mak Flavor Palette: {flv['name']} ({mode_label}) ────────────────────────────── */
@define-color window_bg_color {window_bg};
@define-color window_fg_color {window_fg};
@define-color view_bg_color {view_bg};
@define-color view_fg_color {view_fg};
@define-color headerbar_bg_color {headerbar_bg};
@define-color headerbar_solid_bg {headerbar_solid_bg};
@define-color headerbar_fg_color {headerbar_fg};
@define-color headerbar_border_color {border_color};
@define-color sidebar_bg_color {sidebar_bg};
@define-color sidebar_fg_color {sidebar_fg};
@define-color secondary_sidebar_bg_color {sidebar_bg};
@define-color card_bg_color {card_bg};
@define-color card_fg_color {card_fg};
@define-color dialog_bg_color {dialog_bg};
@define-color dialog_fg_color {dialog_fg};
@define-color popover_bg_color {popover_bg};
@define-color popover_fg_color {popover_fg};
@define-color placeholder_text_color {placeholder_text_color};
@define-color theme_bg_color {window_bg};
@define-color theme_fg_color {window_fg};
@define-color theme_base_color {view_bg};
@define-color theme_text_color {view_fg};
@define-color theme_selected_bg_color @accent_color;
@define-color theme_selected_fg_color #ffffff;
@define-color theme_unfocused_bg_color {window_bg};
@define-color theme_unfocused_fg_color {window_fg};
@define-color theme_unfocused_base_color {view_bg};
@define-color theme_unfocused_text_color {view_fg};
@define-color accent_bg_color {accent_color};
@define-color accent_fg_color #ffffff;
@define-color accent_color {accent_color};
@define-color bg_color {window_bg};
@define-color fg_color {window_fg};
@define-color base_color {view_bg};
@define-color text_color {view_fg};
@define-color selected_bg_color @accent_color;
@define-color selected_fg_color #ffffff;
@define-color content_view_bg {view_bg};
@define-color text_view_bg {view_bg};
"""

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
@define-color theme_bg_color #242426;
@define-color theme_fg_color #f5f5f7;
@define-color theme_base_color #1c1c1e;
@define-color theme_text_color #f5f5f7;
@define-color theme_selected_bg_color @accent_color;
@define-color theme_selected_fg_color #ffffff;
@define-color theme_unfocused_bg_color #242426;
@define-color theme_unfocused_fg_color #f5f5f7;
@define-color theme_unfocused_base_color #1c1c1e;
@define-color theme_unfocused_text_color #f5f5f7;
@define-color accent_bg_color #007aff;
@define-color accent_fg_color #ffffff;
@define-color accent_color #007aff;
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
@define-color theme_bg_color #242426;
@define-color theme_fg_color #f5f5f7;
@define-color theme_base_color #1c1c1e;
@define-color theme_text_color #f5f5f7;
@define-color theme_selected_bg_color @accent_color;
@define-color theme_selected_fg_color #ffffff;
@define-color theme_unfocused_bg_color #242426;
@define-color theme_unfocused_fg_color #f5f5f7;
@define-color theme_unfocused_base_color #1c1c1e;
@define-color theme_unfocused_text_color #f5f5f7;
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
@define-color theme_bg_color #000000;
@define-color theme_fg_color #f5f5f7;
@define-color theme_base_color #000000;
@define-color theme_text_color #f5f5f7;
@define-color theme_selected_bg_color @accent_color;
@define-color theme_selected_fg_color #ffffff;
@define-color theme_unfocused_bg_color #000000;
@define-color theme_unfocused_fg_color #f5f5f7;
@define-color theme_unfocused_base_color #000000;
@define-color theme_unfocused_text_color #f5f5f7;
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
@define-color theme_bg_color #0a0a0c;
@define-color theme_fg_color #f5f5f7;
@define-color theme_base_color #000000;
@define-color theme_text_color #f5f5f7;
@define-color theme_selected_bg_color @accent_color;
@define-color theme_selected_fg_color #ffffff;
@define-color theme_unfocused_bg_color #0a0a0c;
@define-color theme_unfocused_fg_color #f5f5f7;
@define-color theme_unfocused_base_color #000000;
@define-color theme_unfocused_text_color #f5f5f7;
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
@define-color theme_bg_color #ececf0;
@define-color theme_fg_color #1d1d1f;
@define-color theme_base_color #ffffff;
@define-color theme_text_color #1d1d1f;
@define-color theme_selected_bg_color @accent_color;
@define-color theme_selected_fg_color #ffffff;
@define-color theme_unfocused_bg_color #ececf0;
@define-color theme_unfocused_fg_color #1d1d1f;
@define-color theme_unfocused_base_color #ffffff;
@define-color theme_unfocused_text_color #1d1d1f;
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
@define-color theme_bg_color #ececf0;
@define-color theme_fg_color #1d1d1f;
@define-color theme_base_color #ffffff;
@define-color theme_text_color #1d1d1f;
@define-color theme_selected_bg_color @accent_color;
@define-color theme_selected_fg_color #ffffff;
@define-color theme_unfocused_bg_color #ececf0;
@define-color theme_unfocused_fg_color #1d1d1f;
@define-color theme_unfocused_base_color #ffffff;
@define-color theme_unfocused_text_color #1d1d1f;
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
    chrome_size = max(11, min(14, int(button_size)))
    margin_left = TokenManager.get("geometry", "traffic_lights", "margin_left", default=13)

    if chromium_accent is None:
        try:
            res = subprocess.run(["gsettings", "get", "org.gnome.shell.extensions.mak", "chromium-topbar-accent"],
                                 capture_output=True, text=True)
            chromium_accent = res.stdout.strip().strip("'\"")
        except Exception:
            chromium_accent = "default"

    border_color = "rgba(255, 255, 255, 0.12)" if is_dark else "rgba(0, 0, 0, 0.10)"
    hairline = "rgba(255, 255, 255, 0.18)" if is_dark else "rgba(0, 0, 0, 0.18)"
    hairline_h = "rgba(255, 255, 255, 0.22)" if is_dark else "rgba(0, 0, 0, 0.22)"
    hairline_a = "rgba(255, 255, 255, 0.25)" if is_dark else "rgba(0, 0, 0, 0.25)"

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

window.background.chromium windowcontrols,
window.background.brave windowcontrols,
window.background.chromium headerbar windowcontrols,
window.background.brave headerbar windowcontrols,
window.background.chromium .titlebar windowcontrols,
window.background.brave .titlebar windowcontrols,
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

/* Universal Chrome, Chromium, Brave & Electron clean titlebar background */
headerbar.header-bar.titlebar,
window.background.chromium headerbar,
window.background.chromium headerbar.titlebar,
window.background.chromium headerbar.header-bar.titlebar,
window.background.brave headerbar,
window.background.brave headerbar.titlebar,
window.background.brave headerbar.header-bar.titlebar,
window.background.chrome headerbar,
window.background.chrome headerbar.titlebar,
window.background.chrome headerbar.header-bar.titlebar,
window.background.csd headerbar.header-bar.titlebar,
headerbar.titlebar.default-decoration,
window.csd headerbar.titlebar.default-decoration {{
    padding-left: 14px;
    padding-right: 18px;
    padding-top: 0;
    padding-bottom: 0;
    margin: 0;
    background: transparent;
    background-color: transparent;
    background-image: none;
    box-shadow: none;
    border: none;
    border-image: none;
}}

/* Chrome & Chromium Bubble / Notification / Popup Windows (high contrast fix) */
window.bubble,
window.background.bubble,
.bubble,
bubble,
window.background.chromium popover,
window.background.brave popover {{
    background-color: @card_bg_color;
    color: @card_fg_color;
    border: 1px solid {border_color};
    border-radius: 10px;
}}

window.bubble label,
window.background.bubble label,
.bubble label,
bubble label,
window.background.chromium popover label,
window.background.brave popover label {{
    color: @card_fg_color;
}}

/* ── Universal Traffic Lights Base Properties ── */
windowcontrols button,
windowcontrols button:backdrop,
headerbar windowcontrols button,
headerbar windowcontrols button:backdrop,
.titlebar windowcontrols button,
.titlebar windowcontrols button:backdrop,
window.background.csd windowcontrols button,
window.background.csd windowcontrols button:backdrop,
window.background.csd headerbar windowcontrols button,
window.background.csd headerbar windowcontrols button:backdrop,
windowcontrols > button,
windowcontrols > button:backdrop,
headerbar windowcontrols > button,
headerbar windowcontrols > button:backdrop,
.titlebar windowcontrols > button,
.titlebar windowcontrols > button:backdrop,
button.titlebutton,
button.titlebutton:backdrop,
headerbar button.titlebutton,
headerbar button.titlebutton:backdrop,
button.close,
button.close:backdrop,
button.minimize,
button.minimize:backdrop,
button.maximize,
button.maximize:backdrop,
headerbar.header-bar.titlebar windowcontrols button,
headerbar.header-bar.titlebar windowcontrols button:backdrop,
headerbar.header-bar.titlebar button.titlebutton,
headerbar.header-bar.titlebar button.titlebutton:backdrop,
window.background.chromium headerbar windowcontrols button,
window.background.chromium headerbar windowcontrols button:backdrop,
window.background.chromium windowcontrols button,
window.background.chromium windowcontrols button:backdrop,
window.background.brave headerbar windowcontrols button,
window.background.brave headerbar windowcontrols button:backdrop,
window.background.brave windowcontrols button,
window.background.brave windowcontrols button:backdrop {{
    background-color: transparent;
    background-image: none;
    border: none;
    box-shadow: none;
    border-radius: 9999px;
    padding: 0;
    margin: 0 {margin}px;
    margin-left: {margin}px;
    margin-right: {margin}px;
    margin-top: 0;
    margin-bottom: 0;
    min-width: {size}px;
    min-height: {size}px;
    color: transparent;
    -gtk-icon-source: none;
    -gtk-icon-shadow: none;
}}

/* Universally suppress GNOME symbolic icons (x, -, +) */
windowcontrols button image,
windowcontrols button:backdrop image,
windowcontrols button label,
windowcontrols button widget,
headerbar windowcontrols button image,
headerbar windowcontrols button:backdrop image,
headerbar windowcontrols button label,
headerbar windowcontrols button widget,
.titlebar windowcontrols button image,
.titlebar windowcontrols button:backdrop image,
.titlebar windowcontrols button label,
.titlebar windowcontrols button widget,
button.titlebutton image,
button.titlebutton:backdrop image,
button.titlebutton label,
button.close image,
button.close:backdrop image,
button.close label,
button.minimize image,
button.minimize:backdrop image,
button.minimize label,
button.maximize image,
button.maximize:backdrop image,
button.maximize label,
headerbar.header-bar.titlebar windowcontrols button image,
headerbar.header-bar.titlebar button.titlebutton image,
window.background.chromium headerbar windowcontrols button image,
window.background.brave headerbar windowcontrols button image {{
    -gtk-icon-source: none;
    color: transparent;
    opacity: 0;
    min-width: 0;
    min-height: 0;
    margin: 0;
    padding: 0;
    -gtk-icon-transform: scale(0);
    font-size: 0px;
}}

/* ── Close Button (Red: #ff5c60) ── */
window.background.csd windowcontrols button.close,
window.background.csd windowcontrols button.close:backdrop,
window.background.csd headerbar windowcontrols button.close,
window.background.csd headerbar windowcontrols button.close:backdrop,
windowcontrols button.close,
windowcontrols button.close:backdrop,
headerbar windowcontrols button.close,
headerbar windowcontrols button.close:backdrop,
.titlebar windowcontrols button.close,
.titlebar windowcontrols button.close:backdrop,
windowcontrols > button.close,
windowcontrols > button.close:backdrop,
headerbar windowcontrols > button.close,
headerbar windowcontrols > button.close:backdrop,
.titlebar windowcontrols > button.close,
.titlebar windowcontrols > button.close:backdrop,
button.titlebutton.close,
button.titlebutton.close:backdrop,
headerbar button.titlebutton.close,
headerbar button.titlebutton.close:backdrop,
button.close,
button.close:backdrop,
headerbar.header-bar.titlebar windowcontrols button.close,
headerbar.header-bar.titlebar windowcontrols button.close:backdrop,
headerbar.header-bar.titlebar button.close,
headerbar.header-bar.titlebar button.close:backdrop,
window.background.chromium headerbar windowcontrols button.close,
window.background.chromium headerbar windowcontrols button.close:backdrop,
window.background.chromium windowcontrols button.close,
window.background.chromium windowcontrols button.close:backdrop,
window.background.brave headerbar windowcontrols button.close,
window.background.brave headerbar windowcontrols button.close:backdrop,
window.background.brave windowcontrols button.close,
window.background.brave windowcontrols button.close:backdrop {{
    background-image: radial-gradient(circle at center, #ff5c60 0px, #ff5c60 5.5px, {hairline} 5.5px, {hairline} 6.5px, transparent 7px);
    background-repeat: no-repeat;
    background-position: center;
    background-size: {size}px {size}px;
}}

window.background.csd windowcontrols button.close:hover,
window.background.csd windowcontrols button.close:backdrop:hover,
window.background.csd headerbar windowcontrols button.close:hover,
window.background.csd headerbar windowcontrols button.close:backdrop:hover,
windowcontrols button.close:hover,
windowcontrols button.close:backdrop:hover,
headerbar windowcontrols button.close:hover,
headerbar windowcontrols button.close:backdrop:hover,
.titlebar windowcontrols button.close:hover,
.titlebar windowcontrols button.close:backdrop:hover,
windowcontrols > button.close:hover,
windowcontrols > button.close:backdrop:hover,
headerbar windowcontrols > button.close:hover,
headerbar windowcontrols > button.close:backdrop:hover,
.titlebar windowcontrols > button.close:hover,
.titlebar windowcontrols > button.close:backdrop:hover,
button.titlebutton.close:hover,
button.titlebutton.close:backdrop:hover,
headerbar button.titlebutton.close:hover,
headerbar button.titlebutton.close:backdrop:hover,
button.close:hover,
button.close:backdrop:hover,
window.background.chromium headerbar windowcontrols button.close:hover,
window.background.chromium windowcontrols button.close:hover,
window.background.brave headerbar windowcontrols button.close:hover,
window.background.brave windowcontrols button.close:hover {{
    background-image: radial-gradient(circle at center, #e0443e 0px, #e0443e 5.5px, {hairline_h} 5.5px, {hairline_h} 6.5px, transparent 7px);
    background-repeat: no-repeat;
    background-position: center;
    background-size: {size}px {size}px;
}}

window.background.csd windowcontrols button.close:active,
window.background.csd windowcontrols button.close:backdrop:active,
window.background.csd headerbar windowcontrols button.close:active,
window.background.csd headerbar windowcontrols button.close:backdrop:active,
windowcontrols button.close:active,
windowcontrols button.close:backdrop:active,
headerbar windowcontrols button.close:active,
headerbar windowcontrols button.close:backdrop:active,
.titlebar windowcontrols button.close:active,
.titlebar windowcontrols button.close:backdrop:active,
windowcontrols > button.close:active,
windowcontrols > button.close:backdrop:active,
headerbar windowcontrols > button.close:active,
headerbar windowcontrols > button.close:backdrop:active,
.titlebar windowcontrols > button.close:active,
.titlebar windowcontrols > button.close:backdrop:active,
button.titlebutton.close:active,
button.titlebutton.close:backdrop:active,
headerbar button.titlebutton.close:active,
headerbar button.titlebutton.close:backdrop:active,
button.close:active,
button.close:backdrop:active,
window.background.chromium headerbar windowcontrols button.close:active,
window.background.chromium windowcontrols button.close:active,
window.background.brave headerbar windowcontrols button.close:active,
window.background.brave windowcontrols button.close:active {{
    background-image: radial-gradient(circle at center, #bf302a 0px, #bf302a 5.5px, {hairline_a} 5.5px, {hairline_a} 6.5px, transparent 7px);
    background-repeat: no-repeat;
    background-position: center;
    background-size: {size}px {size}px;
}}

/* ── Minimize Button (Yellow: #fac800) ── */
window.background.csd windowcontrols button.minimize,
window.background.csd windowcontrols button.minimize:backdrop,
window.background.csd headerbar windowcontrols button.minimize,
window.background.csd headerbar windowcontrols button.minimize:backdrop,
windowcontrols button.minimize,
windowcontrols button.minimize:backdrop,
headerbar windowcontrols button.minimize,
headerbar windowcontrols button.minimize:backdrop,
.titlebar windowcontrols button.minimize,
.titlebar windowcontrols button.minimize:backdrop,
windowcontrols > button.minimize,
windowcontrols > button.minimize:backdrop,
headerbar windowcontrols > button.minimize,
headerbar windowcontrols > button.minimize:backdrop,
.titlebar windowcontrols > button.minimize,
.titlebar windowcontrols > button.minimize:backdrop,
button.titlebutton.minimize,
button.titlebutton.minimize:backdrop,
headerbar button.titlebutton.minimize,
headerbar button.titlebutton.minimize:backdrop,
button.minimize,
button.minimize:backdrop,
headerbar.header-bar.titlebar windowcontrols button.minimize,
headerbar.header-bar.titlebar windowcontrols button.minimize:backdrop,
headerbar.header-bar.titlebar button.minimize,
headerbar.header-bar.titlebar button.minimize:backdrop,
window.background.chromium headerbar windowcontrols button.minimize,
window.background.chromium headerbar windowcontrols button.minimize:backdrop,
window.background.chromium windowcontrols button.minimize,
window.background.chromium windowcontrols button.minimize:backdrop,
window.background.brave headerbar windowcontrols button.minimize,
window.background.brave headerbar windowcontrols button.minimize:backdrop,
window.background.brave windowcontrols button.minimize,
window.background.brave windowcontrols button.minimize:backdrop {{
    background-image: radial-gradient(circle at center, #fac800 0px, #fac800 5.5px, {hairline} 5.5px, {hairline} 6.5px, transparent 7px);
    background-repeat: no-repeat;
    background-position: center;
    background-size: {size}px {size}px;
}}

window.background.csd windowcontrols button.minimize:hover,
window.background.csd windowcontrols button.minimize:backdrop:hover,
window.background.csd headerbar windowcontrols button.minimize:hover,
window.background.csd headerbar windowcontrols button.minimize:backdrop:hover,
windowcontrols button.minimize:hover,
windowcontrols button.minimize:backdrop:hover,
headerbar windowcontrols button.minimize:hover,
headerbar windowcontrols button.minimize:backdrop:hover,
.titlebar windowcontrols button.minimize:hover,
.titlebar windowcontrols button.minimize:backdrop:hover,
windowcontrols > button.minimize:hover,
windowcontrols > button.minimize:backdrop:hover,
headerbar windowcontrols > button.minimize:hover,
headerbar windowcontrols > button.minimize:backdrop:hover,
.titlebar windowcontrols > button.minimize:hover,
.titlebar windowcontrols > button.minimize:backdrop:hover,
button.titlebutton.minimize:hover,
button.titlebutton.minimize:backdrop:hover,
headerbar button.titlebutton.minimize:hover,
headerbar button.titlebutton.minimize:backdrop:hover,
button.minimize:hover,
button.minimize:backdrop:hover,
window.background.chromium headerbar windowcontrols button.minimize:hover,
window.background.chromium windowcontrols button.minimize:hover,
window.background.brave headerbar windowcontrols button.minimize:hover,
window.background.brave windowcontrols button.minimize:hover {{
    background-image: radial-gradient(circle at center, #dea123 0px, #dea123 5.5px, {hairline_h} 5.5px, {hairline_h} 6.5px, transparent 7px);
    background-repeat: no-repeat;
    background-position: center;
    background-size: {size}px {size}px;
}}

window.background.csd windowcontrols button.minimize:active,
window.background.csd windowcontrols button.minimize:backdrop:active,
window.background.csd headerbar windowcontrols button.minimize:active,
window.background.csd headerbar windowcontrols button.minimize:backdrop:active,
windowcontrols button.minimize:active,
windowcontrols button.minimize:backdrop:active,
headerbar windowcontrols button.minimize:active,
headerbar windowcontrols button.minimize:backdrop:active,
.titlebar windowcontrols button.minimize:active,
.titlebar windowcontrols button.minimize:backdrop:active,
windowcontrols > button.minimize:active,
windowcontrols > button.minimize:backdrop:active,
headerbar windowcontrols > button.minimize:active,
headerbar windowcontrols > button.minimize:backdrop:active,
.titlebar windowcontrols > button.minimize:active,
.titlebar windowcontrols > button.minimize:backdrop:active,
button.titlebutton.minimize:active,
button.titlebutton.minimize:backdrop:active,
headerbar button.titlebutton.minimize:active,
headerbar button.titlebutton.minimize:backdrop:active,
button.minimize:active,
button.minimize:backdrop:active,
window.background.chromium headerbar windowcontrols button.minimize:active,
window.background.chromium windowcontrols button.minimize:active,
window.background.brave headerbar windowcontrols button.minimize:active,
window.background.brave windowcontrols button.minimize:active {{
    background-image: radial-gradient(circle at center, #c38c1a 0px, #c38c1a 5.5px, {hairline_a} 5.5px, {hairline_a} 6.5px, transparent 7px);
    background-repeat: no-repeat;
    background-position: center;
    background-size: {size}px {size}px;
}}

/* ── Maximize / Zoom Button (Green: #35c759) ── */
window.background.csd windowcontrols button.maximize,
window.background.csd windowcontrols button.maximize:backdrop,
window.background.csd headerbar windowcontrols button.maximize,
window.background.csd headerbar windowcontrols button.maximize:backdrop,
windowcontrols button.maximize,
windowcontrols button.maximize:backdrop,
headerbar windowcontrols button.maximize,
headerbar windowcontrols button.maximize:backdrop,
.titlebar windowcontrols button.maximize,
.titlebar windowcontrols button.maximize:backdrop,
windowcontrols > button.maximize,
windowcontrols > button.maximize:backdrop,
headerbar windowcontrols > button.maximize,
headerbar windowcontrols > button.maximize:backdrop,
.titlebar windowcontrols > button.maximize,
.titlebar windowcontrols > button.maximize:backdrop,
button.titlebutton.maximize,
button.titlebutton.maximize:backdrop,
headerbar button.titlebutton.maximize,
headerbar button.titlebutton.maximize:backdrop,
button.maximize,
button.maximize:backdrop,
headerbar.header-bar.titlebar windowcontrols button.maximize,
headerbar.header-bar.titlebar windowcontrols button.maximize:backdrop,
headerbar.header-bar.titlebar button.maximize,
headerbar.header-bar.titlebar button.maximize:backdrop,
window.background.chromium headerbar windowcontrols button.maximize,
window.background.chromium headerbar windowcontrols button.maximize:backdrop,
window.background.chromium windowcontrols button.maximize,
window.background.chromium windowcontrols button.maximize:backdrop,
window.background.brave headerbar windowcontrols button.maximize,
window.background.brave headerbar windowcontrols button.maximize:backdrop,
window.background.brave windowcontrols button.maximize,
window.background.brave windowcontrols button.maximize:backdrop {{
    background-image: radial-gradient(circle at center, #35c759 0px, #35c759 5.5px, {hairline} 5.5px, {hairline} 6.5px, transparent 7px);
    background-repeat: no-repeat;
    background-position: center;
    background-size: {size}px {size}px;
}}

window.background.csd windowcontrols button.maximize:hover,
window.background.csd windowcontrols button.maximize:backdrop:hover,
window.background.csd headerbar windowcontrols button.maximize:hover,
window.background.csd headerbar windowcontrols button.maximize:backdrop:hover,
windowcontrols button.maximize:hover,
windowcontrols button.maximize:backdrop:hover,
headerbar windowcontrols button.maximize:hover,
headerbar windowcontrols button.maximize:backdrop:hover,
.titlebar windowcontrols button.maximize:hover,
.titlebar windowcontrols button.maximize:backdrop:hover,
windowcontrols > button.maximize:hover,
windowcontrols > button.maximize:backdrop:hover,
headerbar windowcontrols > button.maximize:hover,
headerbar windowcontrols > button.maximize:backdrop:hover,
.titlebar windowcontrols > button.maximize:hover,
.titlebar windowcontrols > button.maximize:backdrop:hover,
button.titlebutton.maximize:hover,
button.titlebutton.maximize:backdrop:hover,
headerbar button.titlebutton.maximize:hover,
headerbar button.titlebutton.maximize:backdrop:hover,
button.maximize:hover,
button.maximize:backdrop:hover,
window.background.chromium headerbar windowcontrols button.maximize:hover,
window.background.chromium windowcontrols button.maximize:hover,
window.background.brave headerbar windowcontrols button.maximize:hover,
window.background.brave windowcontrols button.maximize:hover {{
    background-image: radial-gradient(circle at center, #1aab29 0px, #1aab29 5.5px, {hairline_h} 5.5px, {hairline_h} 6.5px, transparent 7px);
    background-repeat: no-repeat;
    background-position: center;
    background-size: {size}px {size}px;
}}

window.background.csd windowcontrols button.maximize:active,
window.background.csd windowcontrols button.maximize:backdrop:active,
window.background.csd headerbar windowcontrols button.maximize:active,
window.background.csd headerbar windowcontrols button.maximize:backdrop:active,
windowcontrols button.maximize:active,
windowcontrols button.maximize:backdrop:active,
headerbar windowcontrols button.maximize:active,
headerbar windowcontrols button.maximize:backdrop:active,
.titlebar windowcontrols button.maximize:active,
.titlebar windowcontrols button.maximize:backdrop:active,
windowcontrols > button.maximize:active,
windowcontrols > button.maximize:backdrop:active,
headerbar windowcontrols > button.maximize:active,
headerbar windowcontrols > button.maximize:backdrop:active,
.titlebar windowcontrols > button.maximize:active,
.titlebar windowcontrols > button.maximize:backdrop:active,
button.titlebutton.maximize:active,
button.titlebutton.maximize:backdrop:active,
headerbar button.titlebutton.maximize:active,
headerbar button.titlebutton.maximize:backdrop:active,
button.maximize:active,
button.maximize:backdrop:active,
window.background.chromium headerbar windowcontrols button.maximize:active,
window.background.chromium windowcontrols button.maximize:active,
window.background.brave headerbar windowcontrols button.maximize:active,
window.background.brave windowcontrols button.maximize:active {{
    background-image: radial-gradient(circle at center, #138f20 0px, #138f20 5.5px, {hairline_a} 5.5px, {hairline_a} 6.5px, transparent 7px);
    background-repeat: no-repeat;
    background-position: center;
    background-size: {size}px {size}px;
}}

/* ── Inactive / Backdrop window traffic lights ── */
window:backdrop windowcontrols button:not(:hover),
window.background.csd:backdrop windowcontrols button:not(:hover),
headerbar:backdrop windowcontrols button:not(:hover),
.titlebar:backdrop windowcontrols button:not(:hover),
windowcontrols button:backdrop:not(:hover),
headerbar windowcontrols button:backdrop:not(:hover),
.titlebar windowcontrols button:backdrop:not(:hover),
window.background.csd headerbar windowcontrols button:backdrop:not(:hover),
window.background.chromium:backdrop windowcontrols button:not(:hover),
window.background.brave:backdrop windowcontrols button:not(:hover),
window.background.chromium:backdrop button.titlebutton:not(:hover),
window.background.brave:backdrop button.titlebutton:not(:hover) {{
    opacity: 0.55;
    background-color: transparent;
    box-shadow: none;
    border: none;
}}

windowcontrols button:hover,
headerbar windowcontrols button:hover,
.titlebar windowcontrols button:hover,
windowcontrols button:backdrop:hover,
headerbar windowcontrols button:backdrop:hover,
.titlebar windowcontrols button:backdrop:hover,
window.background.chromium windowcontrols button:hover,
window.background.brave windowcontrols button:hover,
window.background.chromium:backdrop windowcontrols button:hover,
window.background.brave:backdrop windowcontrols button:hover {{
    opacity: 1.0;
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
        active_subtle = "rgba(0, 0, 0, 0.12)"
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
        active_subtle = "rgba(255, 255, 255, 0.18)"

    linked_bg = "#ffffff" if not is_dark else ("#18181a" if is_amoled else "rgba(255, 255, 255, 0.10)")
    linked_border = f"1px solid {border_color}"
    linked_shadow = "0 1px 2px rgba(0, 0, 0, 0.05), 0 0 1px rgba(0, 0, 0, 0.04)" if not is_dark else "0 1px 3px rgba(0, 0, 0, 0.30)"
    linked_divider = f"1px solid {border_color}"
    linked_hover = "rgba(0, 0, 0, 0.06)" if not is_dark else "rgba(255, 255, 255, 0.10)"
    linked_active = "rgba(0, 0, 0, 0.12)" if not is_dark else "rgba(255, 255, 255, 0.18)"

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
    margin-top: 10px;
    margin-bottom: 2px;
    padding: 2px 8px;
    min-height: 18px;
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
.nautilus-window placessidebar .navigation-sidebar > row:not(.sidebar-placeholder-row),
#NautilusFileChooser placessidebar row,
#NautilusFileChooser .navigation-sidebar > row {{
    border-radius: 6px;
    margin: 1px 6px;
    padding: 2px 8px;
    min-height: 24px;
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
    min-height: 16px;
    min-width: 16px;
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
.nautilus-window placessidebar .navigation-sidebar > row:hover:not(:selected):not(.heading):not(.sidebar-placeholder-row),
#NautilusFileChooser placessidebar row:hover:not(:selected):not(.heading),
#NautilusFileChooser .navigation-sidebar > row:hover:not(:selected):not(.heading) {{
    background-color: {sidebar_hover_bg};
    color: {text_primary};
    border-radius: 6px;
    margin: 1px 6px;
    padding: 2px 8px;
    min-height: 24px;
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
.nautilus-window placessidebar .navigation-sidebar > row:active:not(:selected):not(.heading):not(.sidebar-placeholder-row),
#NautilusFileChooser placessidebar row:active:not(:selected):not(.heading),
#NautilusFileChooser .navigation-sidebar > row:active:not(:selected):not(.heading) {{
    background-color: {sidebar_selected_bg};
    color: {text_primary};
    border-radius: 6px;
    margin: 1px 6px;
    padding: 2px 8px;
    min-height: 24px;
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
.nautilus-window placessidebar .navigation-sidebar > row:selected:not(.sidebar-placeholder-row),
.nautilus-window .sidebar-pane placessidebar .navigation-sidebar:not(.view) > row:selected,
#NautilusFileChooser .sidebar-pane placessidebar .navigation-sidebar:not(.view) > row:selected,
#NautilusFileChooser placessidebar row:selected,
#NautilusFileChooser .navigation-sidebar > row:selected {{
    background-color: {sidebar_selected_bg};
    color: {text_primary};
    font-weight: 600;
    border-radius: 6px;
    margin: 1px 6px;
    padding: 2px 8px;
    min-height: 24px;
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
.nautilus-window placessidebar .navigation-sidebar > row:selected:hover:not(.sidebar-placeholder-row),
.nautilus-window .sidebar-pane placessidebar .navigation-sidebar:not(.view) > row:selected:hover,
#NautilusFileChooser .sidebar-pane placessidebar .navigation-sidebar:not(.view) > row:selected:hover,
#NautilusFileChooser placessidebar row:selected:hover,
#NautilusFileChooser .navigation-sidebar > row:selected:hover {{
    background-color: {sidebar_selected_hover_bg};
    color: {text_primary};
    font-weight: 600;
    border-radius: 6px;
    margin: 1px 6px;
    padding: 2px 8px;
    min-height: 24px;
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
.nautilus-window placessidebar .navigation-sidebar > row:selected:active:not(.sidebar-placeholder-row),
.nautilus-window .sidebar-pane placessidebar .navigation-sidebar:not(.view) > row:selected:active,
#NautilusFileChooser .sidebar-pane placessidebar .navigation-sidebar:not(.view) > row:selected:active,
#NautilusFileChooser placessidebar row:selected:active,
#NautilusFileChooser .navigation-sidebar > row:selected:active {{
    background-color: {sidebar_selected_active_bg};
    color: {text_primary};
    font-weight: 600;
    border-radius: 6px;
    margin: 1px 6px;
    padding: 2px 8px;
    min-height: 24px;
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

/* 10. Column Header Titles (Apple Flat Sans Typography - 100% Transparent, No Box) */
columnview header,
columnview > header,
columnview header.activatable,
columnview header cell,
columnview header button,
columnview header > button,
columnview header cell button,
columnview header cell > button,
columnview.view > header,
columnview.view > header > button,
columnview.view header button,
columnview.view header.activatable button,
treeview.view > header,
treeview.view > header > button,
treeview header,
treeview header button,
treeview header > button,
.nautilus-window columnview header,
.nautilus-window columnview > header,
.nautilus-window columnview header.activatable,
.nautilus-window columnview header cell,
.nautilus-window columnview header button,
.nautilus-window columnview header > button,
.nautilus-window columnview header cell button,
.nautilus-window columnview header.activatable button,
.nautilus-window .nautilus-list-view columnview header,
.nautilus-window .nautilus-list-view columnview header button,
.nautilus-window .nautilus-list-view header,
.nautilus-window .nautilus-list-view header button,
.nautilus-list-view header,
.nautilus-list-view header button,
.nautilus-list-view columnview header,
.nautilus-list-view columnview header button,
.nautilus-list-view columnview header > button,
.content-pane columnview header,
.content-pane columnview header button,
.content-pane columnview header cell button,
.content-pane .columnview.header,
.content-pane .columnview.header button,
.content-pane .columnview.header > button,
.content-pane box.columnview.header,
.content-pane box.columnview.header button,
.content-pane box.columnview.header > button,
.columnview.header,
.columnview.header button,
.columnview.header > button,
box.columnview.header,
box.columnview.header button,
box.columnview.header > button,
.columnview button,
#NautilusColumnViewHeader,
#NautilusColumnViewHeader button {{
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
    outline: none;
    padding: 3px 10px;
    min-height: 26px;
    border-bottom: 1px solid {border_color};
}}

columnview header button,
columnview header cell,
columnview.view > header > button,
.columnview.header button,
box.columnview.header button,
.content-pane .columnview.header button,
.content-pane box.columnview.header button,
.nautilus-window columnview header button,
.nautilus-window columnview header cell,
.nautilus-list-view columnview header button,
#NautilusColumnViewHeader button {{
    border-right: 1px solid {border_color};
}}

columnview header button:last-child,
columnview header cell:last-child,
columnview.view > header > button:last-child,
.columnview.header button:last-child,
box.columnview.header button:last-child,
.content-pane .columnview.header button:last-child,
.content-pane box.columnview.header button:last-child,
.nautilus-window columnview header button:last-child,
.nautilus-window columnview header cell:last-child,
.nautilus-list-view columnview header button:last-child,
#NautilusColumnViewHeader button:last-child {{
    border-right: none;
}}

columnview header button:hover,
columnview header > button:hover,
columnview header cell button:hover,
columnview.view > header > button:hover,
treeview.view > header > button:hover,
treeview header button:hover,
.columnview.header button:hover,
box.columnview.header button:hover,
.content-pane .columnview.header button:hover,
.content-pane box.columnview.header button:hover,
.nautilus-window columnview header button:hover,
.nautilus-window .nautilus-list-view header button:hover,
.nautilus-list-view header button:hover,
.nautilus-list-view columnview header button:hover,
.content-pane columnview header button:hover,
#NautilusColumnViewHeader button:hover {{
    background: {hover_subtle};
    background-color: {hover_subtle};
    background-image: none;
    border: none;
    border-radius: 0;
    box-shadow: none;
    color: {text_primary};
    border-bottom: 1px solid {border_color};
    border-right: 1px solid {border_color};
}}

columnview header button:last-child:hover,
.columnview.header button:last-child:hover,
box.columnview.header button:last-child:hover,
.content-pane .columnview.header button:last-child:hover,
.content-pane box.columnview.header button:last-child:hover,
.nautilus-window columnview header button:last-child:hover,
.nautilus-list-view columnview header button:last-child:hover,
#NautilusColumnViewHeader button:last-child:hover {{
    border-right: none;
}}

columnview header button:active,
columnview header button:checked,
columnview header > button:active,
columnview header > button:checked,
treeview header button:active,
treeview header button:checked,
.columnview.header button:active,
.columnview.header button:checked,
box.columnview.header button:active,
box.columnview.header button:checked,
.content-pane .columnview.header button:active,
.content-pane .columnview.header button:checked,
.content-pane box.columnview.header button:active,
.content-pane box.columnview.header button:checked,
.nautilus-window columnview header button:active,
.nautilus-window columnview header button:checked,
.nautilus-window .nautilus-list-view header button:active,
.nautilus-window .nautilus-list-view header button:checked,
.nautilus-list-view columnview header button:active,
.nautilus-list-view columnview header button:checked {{
    background: {active_subtle};
    background-color: {active_subtle};
    background-image: none;
    border: none;
    border-radius: 0;
    box-shadow: none;
    color: {text_primary};
    border-bottom: 1px solid {border_color};
    border-right: 1px solid {border_color};
}}

columnview header button:focus,
columnview header button:focus-visible,
columnview header button:focus-within,
columnview header > button:focus,
columnview header > button:focus-visible,
treeview header button:focus,
treeview header button:focus-visible,
.columnview.header button:focus,
.columnview.header button:focus-visible,
box.columnview.header button:focus,
box.columnview.header button:focus-visible,
.content-pane .columnview.header button:focus,
.content-pane .columnview.header button:focus-visible,
.content-pane box.columnview.header button:focus,
.content-pane box.columnview.header button:focus-visible,
.nautilus-window columnview header button:focus,
.nautilus-window columnview header button:focus-visible,
.nautilus-list-view columnview header button:focus,
.nautilus-list-view columnview header button:focus-visible,
#NautilusColumnViewHeader button:focus,
#NautilusColumnViewHeader button:focus-visible {{
    outline: none;
    box-shadow: none;
    background: transparent;
    background-color: transparent;
    background-image: none;
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

/* 14. Pathbar Transparent Buttons (apple/toolbars/ & Apple Finder) */
.nautilus-window .nautilus-pathbar,
#NautilusFileChooser .nautilus-pathbar,
filechooser .path-bar,
filechooser pathbar,
.path-bar,
pathbar,
nautilus-path-bar {{
    background: transparent;
    background-color: transparent;
    border: none;
    box-shadow: none;
    padding: 0;
    margin: 0 4px;
}}

.nautilus-path-button,
.path-button,
.nautilus-window .nautilus-pathbar button,
.nautilus-window nautilus-path-bar button,
.nautilus-window nautilus-path-bar .nautilus-path-button,
#NautilusFileChooser .nautilus-pathbar button,
filechooser .path-bar button,
filechooser pathbar button,
filechooser stack button,
.path-bar button,
pathbar button,
nautilus-path-bar button,
nautilus-path-bar .nautilus-path-button,
headerbar .path-bar button,
headerbar pathbar button,
headerbar nautilus-path-bar button,
headerbar nautilus-path-bar .nautilus-path-button {{
    border-radius: 9999px;
    background: transparent;
    background-color: transparent;
    background-image: none;
    border: none;
    padding: 2px 8px;
    margin: 0 1px;
    min-height: 22px;
    font-size: 13px;
    font-weight: 500;
    color: {text_primary};
    box-shadow: none;
    transition: background-color 80ms ease;
}}

.nautilus-path-button:hover,
.path-button:hover,
.nautilus-window .nautilus-pathbar button:hover,
.nautilus-window nautilus-path-bar button:hover,
.nautilus-window nautilus-path-bar .nautilus-path-button:hover,
#NautilusFileChooser .nautilus-pathbar button:hover,
filechooser .path-bar button:hover,
filechooser pathbar button:hover,
filechooser stack button:hover,
.path-bar button:hover,
pathbar button:hover,
nautilus-path-bar button:hover,
nautilus-path-bar .nautilus-path-button:hover,
headerbar .path-bar button:hover,
headerbar pathbar button:hover,
headerbar nautilus-path-bar button:hover {{
    background: {hover_subtle};
    background-color: {hover_subtle};
    border: none;
    box-shadow: none;
}}

/* 15. History Navigation Controls (< and >) - Authentic Apple macOS 27 Capsule Pill */
NautilusHistoryControls,
.navigation-controls,
headerbar .navigation-controls,
.nautilus-window headerbar .navigation-controls,
#NautilusFileChooser headerbar .navigation-controls {{
    background-color: {linked_bg};
    background-image: none;
    border: {linked_border};
    box-shadow: {linked_shadow};
    border-radius: 9999px;
    padding: 2px;
    margin: 0 4px;
}}

NautilusHistoryControls:backdrop,
.navigation-controls:backdrop {{
    background-color: {linked_bg};
    border: {linked_border};
    box-shadow: {linked_shadow};
    opacity: 0.90;
}}

NautilusHistoryControls > box,
NautilusHistoryControls box {{
    background: transparent;
    background-color: transparent;
    background-image: none;
    border: none;
    box-shadow: none;
    padding: 0;
    margin: 0;
    border-spacing: 0;
}}

NautilusHistoryControls button,
NautilusHistoryControls #back_button,
NautilusHistoryControls #forward_button,
.navigation-controls button,
headerbar .navigation-controls button,
.nautilus-window headerbar .navigation-controls button,
.nautilus-window headerbar > windowhandle > box > widget > box.start > stack > widget > box > button,
.nautilus-window headerbar > windowhandle > box > widget > box.start > box > stack > widget > box > button,
#NautilusFileChooser headerbar > windowhandle > box > widget > box.start > stack > widget > box > button,
#NautilusFileChooser headerbar > windowhandle > box > widget > box.start > box > stack > widget > box > button {{
    min-height: 22px;
    min-width: 26px;
    padding: 2px 8px;
    margin: 0;
    background: transparent;
    background-color: transparent;
    background-image: none;
    border: none;
    box-shadow: none;
    color: {text_primary};
    transition: background-color 80ms ease;
}}

NautilusHistoryControls button:hover,
NautilusHistoryControls #back_button:hover,
NautilusHistoryControls #forward_button:hover,
.navigation-controls button:hover,
headerbar .navigation-controls button:hover,
.nautilus-window headerbar .navigation-controls button:hover,
.nautilus-window headerbar > windowhandle > box > widget > box.start > stack > widget > box > button:hover,
.nautilus-window headerbar > windowhandle > box > widget > box.start > box > stack > widget > box > button:hover,
#NautilusFileChooser headerbar > windowhandle > box > widget > box.start > stack > widget > box > button:hover,
#NautilusFileChooser headerbar > windowhandle > box > widget > box.start > box > stack > widget > box > button:hover {{
    background: {linked_hover};
    background-color: {linked_hover};
    border: none;
    box-shadow: none;
}}

NautilusHistoryControls button:active,
NautilusHistoryControls #back_button:active,
NautilusHistoryControls #forward_button:active,
.navigation-controls button:active,
headerbar .navigation-controls button:active,
.nautilus-window headerbar .navigation-controls button:active {{
    background: {active_subtle};
    background-color: {active_subtle};
    border: none;
    box-shadow: none;
}}

NautilusHistoryControls button:disabled,
NautilusHistoryControls #back_button:disabled,
NautilusHistoryControls #forward_button:disabled,
.navigation-controls button:disabled,
headerbar .navigation-controls button:disabled,
.nautilus-window headerbar .navigation-controls button:disabled,
.nautilus-window headerbar > windowhandle > box > widget > box.start > stack > widget > box > button:disabled,
.nautilus-window headerbar > windowhandle > box > widget > box.start > box > stack > widget > box > button:disabled,
#NautilusFileChooser headerbar > windowhandle > box > widget > box.start > stack > widget > box > button:disabled,
#NautilusFileChooser headerbar > windowhandle > box > widget > box.start > box > stack > widget > box > button:disabled {{
    opacity: 0.35;
    background: transparent;
    background-color: transparent;
}}

/* Seamless Apple Pill halves: left half <, right half > with 0px gap */
NautilusHistoryControls button:first-child,
NautilusHistoryControls #back_button,
.navigation-controls button:first-child {{
    border-top-left-radius: 9999px;
    border-bottom-left-radius: 9999px;
    border-top-right-radius: 0;
    border-bottom-right-radius: 0;
    border-right: none;
    margin-right: -3px;
    margin-left: 0;
}}

NautilusHistoryControls button:last-child,
NautilusHistoryControls #forward_button,
.navigation-controls button:last-child {{
    border-top-right-radius: 9999px;
    border-bottom-right-radius: 9999px;
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
    border-left: {linked_divider};
    margin-left: -3px;
    margin-right: 0;
}}

/* 15b. NautilusViewControls (AdwSplitButton) & Headerbar Buttons */
NautilusViewControls,
NautilusViewControls splitbutton,
.nautilus-window splitbutton {{
    background-color: {linked_bg};
    background-image: none;
    border: {linked_border};
    box-shadow: {linked_shadow};
    border-radius: 9999px;
    padding: 2px;
    margin: 0 4px;
}}

NautilusViewControls splitbutton:backdrop,
.nautilus-window splitbutton:backdrop {{
    background-color: {linked_bg};
    border: {linked_border};
    box-shadow: {linked_shadow};
    opacity: 0.90;
}}

NautilusViewControls splitbutton > button,
NautilusViewControls splitbutton > menubutton,
NautilusViewControls splitbutton > menubutton > button,
.nautilus-window splitbutton > button,
.nautilus-window splitbutton > menubutton,
.nautilus-window splitbutton > menubutton > button {{
    background: transparent;
    background-color: transparent;
    background-image: none;
    border: none;
    box-shadow: none;
    outline: none;
    min-height: 22px;
    min-width: 22px;
    padding: 2px 6px;
    margin: 0;
    color: {text_primary};
    transition: background-color 80ms ease, color 80ms ease;
}}

NautilusViewControls splitbutton > button:dir(ltr),
NautilusViewControls splitbutton > button:first-child:dir(ltr),
.nautilus-window splitbutton > button:dir(ltr) {{
    border-top-left-radius: 9999px;
    border-bottom-left-radius: 9999px;
    border-top-right-radius: 0;
    border-bottom-right-radius: 0;
    border-right: none;
}}

NautilusViewControls splitbutton > menubutton > button:dir(ltr),
NautilusViewControls splitbutton > menubutton:last-child > button:dir(ltr),
.nautilus-window splitbutton > menubutton > button:dir(ltr) {{
    border-top-right-radius: 9999px;
    border-bottom-right-radius: 9999px;
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
    border-left: none;
}}

NautilusViewControls splitbutton > separator,
.nautilus-window splitbutton > separator {{
    min-width: 1px;
    min-height: 14px;
    background-color: {border_color};
    margin: 2px 0;
    padding: 0;
    border: none;
}}

NautilusViewControls splitbutton > button:hover,
NautilusViewControls splitbutton > menubutton > button:hover,
.nautilus-window splitbutton > button:hover,
.nautilus-window splitbutton > menubutton > button:hover {{
    background: {linked_hover};
    background-color: {linked_hover};
    border: none;
    box-shadow: none;
}}

NautilusViewControls splitbutton > button:active,
NautilusViewControls splitbutton > menubutton > button:active,
.nautilus-window splitbutton > button:active,
.nautilus-window splitbutton > menubutton > button:active {{
    background: {linked_active};
    background-color: {linked_active};
    border: none;
    box-shadow: none;
}}

.nautilus-window headerbar button#new_folder_button,
.nautilus-window headerbar button#search_button,
.nautilus-window headerbar button#show_sidebar_button,
.nautilus-window headerbar togglebutton#search_button,
.nautilus-window headerbar togglebutton#show_sidebar_button {{
    border-radius: 9999px;
    background: transparent;
    background-color: transparent;
    background-image: none;
    border: none;
    box-shadow: none;
    min-height: 26px;
    min-width: 26px;
    padding: 3px;
    margin: 0 2px;
    color: {text_primary};
}}

.nautilus-window headerbar button#new_folder_button:hover,
.nautilus-window headerbar button#search_button:hover,
.nautilus-window headerbar button#show_sidebar_button:hover,
.nautilus-window headerbar togglebutton#search_button:hover,
.nautilus-window headerbar togglebutton#show_sidebar_button:hover {{
    background: {hover_subtle};
    background-color: {hover_subtle};
    border: none;
    box-shadow: none;
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
    min-height: 26px;
    border-radius: 9999px;
    padding: 3px 16px;
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
    seg_container_radius = TokenManager.get("geometry", "segmented", "container_radius", default=9999)
    seg_radius = TokenManager.get("geometry", "segmented", "segment_radius", default=9999)
    seg_pad = TokenManager.get("geometry", "segmented", "padding", default=2)

    entry_radius = TokenManager.get("geometry", "entries", "corner_radius", default=5)
    entry_height = TokenManager.get("geometry", "entries", "height_regular", default=22)
    entry_pad_x = TokenManager.get("geometry", "entries", "padding_x", default=8)
    focus_ring_w = TokenManager.get("geometry", "entries", "focus_ring_width", default=3)

    color_well_height = TokenManager.get("geometry", "color_wells", "height", default=22)
    color_well_radius = TokenManager.get("geometry", "color_wells", "corner_radius", default=4)
    image_well_radius = TokenManager.get("geometry", "image_wells", "corner_radius", default=5)

    if not is_dark:
        border_col = TokenManager.get("colors", "light", "border", default="rgba(0, 0, 0, 0.12)")
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
        linked_bg = "#ffffff"
        linked_border = f"{btn_border_width}px solid rgba(0, 0, 0, 0.10)"
        linked_shadow = "0 1px 2px rgba(0, 0, 0, 0.05), 0 0 1px rgba(0, 0, 0, 0.04)"
        linked_divider = "1px solid rgba(0, 0, 0, 0.10)"
        linked_divider_color = "rgba(0, 0, 0, 0.10)"
        linked_hover = "rgba(0, 0, 0, 0.06)"
        linked_active = "rgba(0, 0, 0, 0.12)"
        linked_checked = "rgba(0, 0, 0, 0.10)"
        linked_checked_fg = "#1d1d1f"
        linked_checked_shadow = "0 1px 2px rgba(0, 0, 0, 0.08)"
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
        linked_bg = "#18181a" if is_amoled else ("rgba(255, 255, 255, 0.08)" if is_glassy else "rgba(255, 255, 255, 0.10)")
        linked_border = f"{btn_border_width}px solid {border_col}"
        linked_shadow = "0 1px 3px rgba(0, 0, 0, 0.30)"
        linked_divider = f"1px solid {border_col}"
        linked_divider_color = border_col
        linked_hover = "rgba(255, 255, 255, 0.10)"
        linked_active = "rgba(255, 255, 255, 0.18)"
        linked_checked = "rgba(255, 255, 255, 0.20)"
        linked_checked_fg = "#ffffff"
        linked_checked_shadow = "0 1px 2px rgba(0, 0, 0, 0.30)"
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

/* Universal macOS Titlebar & Headerbar Styling */
headerbar,
.titlebar,
window headerbar,
window.csd headerbar,
window.background.csd headerbar,
window.background headerbar {{
    background: @headerbar_bg_color;
    background-color: @headerbar_bg_color;
    background-image: none;
    border-bottom: 1px solid {border_col};
    box-shadow: none;
    color: @headerbar_fg_color;
}}



/* 1. Universal In-Window Push Buttons (Dialogs, content pages, settings) */
dialog button:not(.titlebutton):not(.close):not(.minimize):not(.maximize):not(.flat):not(.suggested-action):not(.destructive-action),
adwdialog button:not(.titlebutton):not(.close):not(.minimize):not(.maximize):not(.flat):not(.suggested-action):not(.destructive-action),
adwalertdialog button:not(.titlebutton):not(.close):not(.minimize):not(.maximize):not(.flat):not(.suggested-action):not(.destructive-action),
messagedialog button:not(.titlebutton):not(.close):not(.minimize):not(.maximize):not(.flat):not(.suggested-action):not(.destructive-action),
window.dialog button:not(.titlebutton):not(.close):not(.minimize):not(.maximize):not(.flat):not(.suggested-action):not(.destructive-action),
preferencespage button:not(.titlebutton):not(.close):not(.minimize):not(.maximize):not(.flat):not(.suggested-action):not(.destructive-action),
preferencesgroup button:not(.titlebutton):not(.close):not(.minimize):not(.maximize):not(.flat):not(.suggested-action):not(.destructive-action),
box.content button:not(.titlebutton):not(.close):not(.minimize):not(.maximize):not(.flat):not(.suggested-action):not(.destructive-action),
.boxed-list button:not(.titlebutton):not(.close):not(.minimize):not(.maximize):not(.flat):not(.suggested-action):not(.destructive-action) {{
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

box.content button:not(.titlebutton):not(.close):not(.minimize):not(.maximize):not(.flat):not(.suggested-action):not(.destructive-action):hover,
preferencespage button:not(.titlebutton):not(.close):not(.minimize):not(.maximize):not(.flat):not(.suggested-action):not(.destructive-action):hover,
dialog button:not(.titlebutton):not(.close):not(.minimize):not(.maximize):not(.flat):not(.suggested-action):not(.destructive-action):hover,
adwdialog button:not(.titlebutton):not(.close):not(.minimize):not(.maximize):not(.flat):not(.suggested-action):not(.destructive-action):hover,
adwalertdialog button:not(.titlebutton):not(.close):not(.minimize):not(.maximize):not(.flat):not(.suggested-action):not(.destructive-action):hover,
messagedialog button:not(.titlebutton):not(.close):not(.minimize):not(.maximize):not(.flat):not(.suggested-action):not(.destructive-action):hover {{
    background-color: {btn_hover};
    color: {btn_fg};
}}

box.content button:not(.titlebutton):not(.close):not(.minimize):not(.maximize):not(.flat):not(.suggested-action):not(.destructive-action):active,
preferencespage button:not(.titlebutton):not(.close):not(.minimize):not(.maximize):not(.flat):not(.suggested-action):not(.destructive-action):active,
dialog button:not(.titlebutton):not(.close):not(.minimize):not(.maximize):not(.flat):not(.suggested-action):not(.destructive-action):active,
adwdialog button:not(.titlebutton):not(.close):not(.minimize):not(.maximize):not(.flat):not(.suggested-action):not(.destructive-action):active,
adwalertdialog button:not(.titlebutton):not(.close):not(.minimize):not(.maximize):not(.flat):not(.suggested-action):not(.destructive-action):active,
messagedialog button:not(.titlebutton):not(.close):not(.minimize):not(.maximize):not(.flat):not(.suggested-action):not(.destructive-action):active {{
    background-color: {btn_active};
}}

box.content button:not(.titlebutton):not(.close):not(.minimize):not(.maximize):not(.flat):not(.suggested-action):not(.destructive-action):checked,
preferencespage button:not(.titlebutton):not(.close):not(.minimize):not(.maximize):not(.flat):not(.suggested-action):not(.destructive-action):checked,
dialog button:not(.titlebutton):not(.close):not(.minimize):not(.maximize):not(.flat):not(.suggested-action):not(.destructive-action):checked,
adwdialog button:not(.titlebutton):not(.close):not(.minimize):not(.maximize):not(.flat):not(.suggested-action):not(.destructive-action):checked,
adwalertdialog button:not(.titlebutton):not(.close):not(.minimize):not(.maximize):not(.flat):not(.suggested-action):not(.destructive-action):checked,
messagedialog button:not(.titlebutton):not(.close):not(.minimize):not(.maximize):not(.flat):not(.suggested-action):not(.destructive-action):checked {{
    background-color: @accent_bg_color;
    color: @accent_fg_color;
}}

button:not(.titlebutton):not(.close):not(.minimize):not(.maximize):not(.circular):disabled {{
    opacity: 0.35;
    box-shadow: none;
}}

/* Cards, Group Boxes, Frames & Boxed Lists (Apple 10px Rounded Form Cards) */
frame,
frame > border,
.boxed-list,
preferencesgroup > box,
.card,
button.card,
.card.activatable,
checkbutton.selection-mode,
.style-item,
.style-item button,
flowboxchild.card,
flowboxchild.style-item {{
    border-radius: 10px;
    background-color: @card_bg_color;
    border: 1px solid {border_col};
}}

.boxed-list > row:first-child,
preferencesgroup > box > row:first-child {{
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
}}

.boxed-list > row:last-child,
preferencesgroup > box > row:last-child {{
    border-bottom-left-radius: 10px;
    border-bottom-right-radius: 10px;
}}

.boxed-list > row:not(:last-child),
preferencesgroup > box > row:not(:last-child) {{
    border-bottom: 1px solid {border_col};
}}

/* Disclosure Controls (apple/disclosure controls/) */
expander > title,
expander-widget > title {{
    min-height: 24px;
    padding: 3px 6px;
    border-radius: 5px;
    transition: background-color 80ms ease;
}}

expander > title:hover,
expander-widget > title:hover {{
    background-color: {hover_subtle};
}}

expander > title > arrow,
expander arrow {{
    min-width: 16px;
    min-height: 16px;
    color: {dim_label};
    transition: transform 150ms ease;
}}

expander > title > arrow:checked,
expander:checked arrow {{
    color: @accent_bg_color;
}}

checkbutton.selection-mode:checked,
.style-item:checked,
button.card:checked {{
    border-radius: 10px;
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

/* 2. macOS Headerbar & Titlebar Icon Buttons (Flat, borderless at rest, subtle rounded 5px pill on hover) */
headerbar button:not(.suggested-action):not(.destructive-action):not(.titlebutton):not(.close):not(.minimize):not(.maximize),
.titlebar button:not(.suggested-action):not(.destructive-action):not(.titlebutton):not(.close):not(.minimize):not(.maximize),
window headerbar button:not(.suggested-action):not(.destructive-action):not(.titlebutton):not(.close):not(.minimize):not(.maximize),
window.csd headerbar button:not(.suggested-action):not(.destructive-action):not(.titlebutton):not(.close):not(.minimize):not(.maximize),
headerbar menubutton > button,
headerbar menubutton:not(.flat) > button,
.titlebar menubutton > button,
.titlebar menubutton:not(.flat) > button,
headerbar menubutton.flat > button,
headerbar dropdown > button,
.titlebar dropdown > button,
headerbar togglebutton,
headerbar button.toggle,
.toolbar button:not(.suggested-action):not(.destructive-action),
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
    border-radius: {btn_radius}px;
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
headerbar menubutton:not(.flat) > button:hover,
.titlebar menubutton > button:hover,
.titlebar menubutton:not(.flat) > button:hover,
headerbar menubutton.flat > button:hover,
headerbar dropdown > button:hover,
.titlebar dropdown > button:hover,
headerbar togglebutton:hover,
headerbar button.toggle:hover,
.toolbar button:hover,
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
headerbar menubutton:not(.flat) > button:active,
.titlebar menubutton > button:active,
.titlebar menubutton:not(.flat) > button:active,
headerbar menubutton.flat > button:active,
headerbar dropdown > button:active,
.titlebar dropdown > button:active,
headerbar togglebutton:active,
headerbar button.toggle:active,
.toolbar button:active,
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
headerbar togglebutton:checked,
headerbar button.toggle:checked,
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

/* 3. macOS Breadcrumbs & Pathbar Controls (apple/toolbars/ & Apple Finder) */
.nautilus-path-button,
.path-button,
nautilus-path-bar button,
nautilus-path-bar .nautilus-path-button,
.nautilus-window .nautilus-pathbar button,
.nautilus-window nautilus-path-bar button,
#NautilusFileChooser .nautilus-pathbar button,
.path-bar button,
pathbar button,
filechooser .path-bar button,
filechooser pathbar button,
filechooser stack button,
headerbar .path-bar button,
headerbar pathbar button,
headerbar nautilus-path-bar button {{
    border-radius: 4px;
    background: transparent;
    background-color: transparent;
    background-image: none;
    border: none;
    box-shadow: none;
    padding: 2px 6px;
    margin: 0 1px;
    min-height: 22px;
    font-size: 13px;
    font-weight: 500;
    color: {btn_fg};
    transition: background-color 80ms ease;
}}

.nautilus-path-button:hover,
.path-button:hover,
nautilus-path-bar button:hover,
.nautilus-window .nautilus-pathbar button:hover,
.nautilus-window nautilus-path-bar button:hover,
#NautilusFileChooser .nautilus-pathbar button:hover,
.path-bar button:hover,
pathbar button:hover,
filechooser .path-bar button:hover,
filechooser pathbar button:hover,
headerbar .path-bar button:hover,
headerbar pathbar button:hover,
headerbar nautilus-path-bar button:hover {{
    background: transparent;
    background-color: {hover_subtle};
    border: none;
    box-shadow: none;
}}

/* 4. macOS Flat Column & Tree Headers (apple/lists and tables/2__column_headers.png) */
columnview header,
columnview > header,
columnview header.activatable,
columnview header cell,
columnview header button,
columnview header > button,
columnview header cell button,
columnview header cell > button,
columnview.view > header,
columnview.view > header > button,
columnview.view header button,
columnview.view header.activatable button,
treeview.view > header,
treeview.view > header > button,
treeview header,
treeview header button,
treeview header > button,
.nautilus-window columnview header,
.nautilus-window columnview > header,
.nautilus-window columnview header.activatable,
.nautilus-window columnview header cell,
.nautilus-window columnview header button,
.nautilus-window columnview header > button,
.nautilus-window columnview header cell button,
.nautilus-window columnview header.activatable button,
.nautilus-window .nautilus-list-view columnview header,
.nautilus-window .nautilus-list-view columnview header button,
.nautilus-window .nautilus-list-view header,
.nautilus-window .nautilus-list-view header button,
.nautilus-list-view header,
.nautilus-list-view header button,
.nautilus-list-view columnview header,
.nautilus-list-view columnview header button,
.nautilus-list-view columnview header > button,
.content-pane columnview header,
.content-pane columnview header button,
.content-pane columnview header cell button,
.content-pane .columnview.header,
.content-pane .columnview.header button,
.content-pane .columnview.header > button,
.content-pane box.columnview.header,
.content-pane box.columnview.header button,
.content-pane box.columnview.header > button,
.columnview.header,
.columnview.header button,
.columnview.header > button,
box.columnview.header,
box.columnview.header button,
box.columnview.header > button,
.columnview button,
#NautilusColumnViewHeader,
#NautilusColumnViewHeader button {{
    color: {dim_label};
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
    outline: none;
    padding: 3px 10px;
    min-height: 26px;
    border-bottom: 1px solid {border_col};
}}

columnview header button,
columnview header cell,
columnview.view > header > button,
.columnview.header button,
box.columnview.header button,
.content-pane .columnview.header button,
.content-pane box.columnview.header button,
.nautilus-window columnview header button,
.nautilus-window columnview header cell,
.nautilus-list-view columnview header button,
#NautilusColumnViewHeader button {{
    border-right: 1px solid {border_col};
}}

columnview header button:last-child,
columnview header cell:last-child,
columnview.view > header > button:last-child,
.columnview.header button:last-child,
box.columnview.header button:last-child,
.content-pane .columnview.header button:last-child,
.content-pane box.columnview.header button:last-child,
.nautilus-window columnview header button:last-child,
.nautilus-window columnview header cell:last-child,
.nautilus-list-view columnview header button:last-child,
#NautilusColumnViewHeader button:last-child {{
    border-right: none;
}}

columnview header button:hover,
columnview header > button:hover,
columnview header cell button:hover,
columnview.view > header > button:hover,
treeview.view > header > button:hover,
treeview header button:hover,
.columnview.header button:hover,
box.columnview.header button:hover,
.content-pane .columnview.header button:hover,
.content-pane box.columnview.header button:hover,
.nautilus-window columnview header button:hover,
.nautilus-window .nautilus-list-view header button:hover,
.nautilus-list-view header button:hover,
.nautilus-list-view columnview header button:hover,
.content-pane columnview header button:hover,
#NautilusColumnViewHeader button:hover {{
    background: {hover_subtle};
    background-color: {hover_subtle};
    background-image: none;
    border: none;
    border-radius: 0;
    box-shadow: none;
    color: {btn_fg};
    border-bottom: 1px solid {border_col};
    border-right: 1px solid {border_col};
}}

columnview header button:last-child:hover,
.columnview.header button:last-child:hover,
box.columnview.header button:last-child:hover,
.content-pane .columnview.header button:last-child:hover,
.content-pane box.columnview.header button:last-child:hover,
.nautilus-window columnview header button:last-child:hover,
.nautilus-list-view columnview header button:last-child:hover,
#NautilusColumnViewHeader button:last-child:hover {{
    border-right: none;
}}

columnview header button:active,
columnview header button:checked,
columnview header > button:active,
columnview header > button:checked,
treeview header button:active,
treeview header button:checked,
.columnview.header button:active,
.columnview.header button:checked,
box.columnview.header button:active,
box.columnview.header button:checked,
.content-pane .columnview.header button:active,
.content-pane .columnview.header button:checked,
.content-pane box.columnview.header button:active,
.content-pane box.columnview.header button:checked,
.nautilus-window columnview header button:active,
.nautilus-window columnview header button:checked,
.nautilus-window .nautilus-list-view header button:active,
.nautilus-window .nautilus-list-view header button:checked,
.nautilus-list-view columnview header button:active,
.nautilus-list-view columnview header button:checked {{
    background: {active_subtle};
    background-color: {active_subtle};
    background-image: none;
    border: none;
    border-radius: 0;
    box-shadow: none;
    color: {btn_fg};
    border-bottom: 1px solid {border_col};
    border-right: 1px solid {border_col};
}}

columnview header button:focus,
columnview header button:focus-visible,
columnview header button:focus-within,
columnview header > button:focus,
columnview header > button:focus-visible,
treeview header button:focus,
treeview header button:focus-visible,
.columnview.header button:focus,
.columnview.header button:focus-visible,
box.columnview.header button:focus,
box.columnview.header button:focus-visible,
.content-pane .columnview.header button:focus,
.content-pane .columnview.header button:focus-visible,
.content-pane box.columnview.header button:focus,
.content-pane box.columnview.header button:focus-visible,
.nautilus-window columnview header button:focus,
.nautilus-window columnview header button:focus-visible,
.nautilus-list-view columnview header button:focus,
.nautilus-list-view columnview header button:focus-visible,
#NautilusColumnViewHeader button:focus,
#NautilusColumnViewHeader button:focus-visible {{
    outline: none;
    box-shadow: none;
    background: transparent;
    background-color: transparent;
    background-image: none;
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
headerbar menubutton > button,
headerbar menubutton.flat > button,
.titlebar dropdown > button,
.titlebar menubutton > button {{
    background-color: transparent;
    background-image: none;
    border: none;
    box-shadow: none;
}}

headerbar dropdown > button:hover,
headerbar menubutton > button:hover,
.titlebar dropdown > button:hover,
.titlebar menubutton > button:hover {{
    background-color: {hover_subtle};
}}

headerbar dropdown > button:active,
headerbar menubutton > button:active,
.titlebar dropdown > button:active,
.titlebar menubutton > button:active {{
    background-color: {active_subtle};
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

/* 12b. Unified Toolbars, Searchbars, Actionbars & 16px Separators */
toolbar,
.toolbar,
searchbar,
searchbar > revealer > box,
actionbar,
actionbar > revealer > box {{
    background-color: @headerbar_bg_color;
    color: @headerbar_fg_color;
    border: none;
}}

actionbar,
actionbar > revealer > box {{
    border-top: 1px solid {border_col};
    padding: 6px 14px;
}}

toolbar separator,
.toolbar separator,
headerbar separator,
actionbar separator {{
    min-height: 16px;
    min-width: 1px;
    margin: 4px 6px;
    background-color: {border_col};
    border: none;
    box-shadow: none;
}}

toolbar button:not(.suggested-action):not(.destructive-action),
.toolbar button:not(.suggested-action):not(.destructive-action) {{
    background: transparent;
    background-color: transparent;
    background-image: none;
    border: none;
    box-shadow: none;
    border-radius: 5px;
    min-height: 24px;
    padding: 3px 8px;
    color: {btn_fg};
    transition: background-color 80ms ease, color 80ms ease;
}}

toolbar button:not(.suggested-action):not(.destructive-action):hover,
.toolbar button:not(.suggested-action):not(.destructive-action):hover {{
    background-color: {hover_subtle};
}}

toolbar button:not(.suggested-action):not(.destructive-action):active,
.toolbar button:not(.suggested-action):not(.destructive-action):active {{
    background-color: {active_subtle};
}}

toolbar button:not(.suggested-action):not(.destructive-action):checked,
.toolbar button:not(.suggested-action):not(.destructive-action):checked {{
    background-color: @accent_bg_color;
    color: #ffffff;
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

/* 15. macOS Alerts, Sheets & Dialog Boxes (apple/alerts/12_bg.png 20px radius, 26px capsule buttons) */
window.dialog,
dialog,
messagedialog,
.messagedialog,
window.message,
adwdialog,
adwalertdialog,
alertdialog,
.alertdialog,
window.alertdialog {{
    border-radius: 20px;
    background-color: @dialog_bg_color;
    color: @dialog_fg_color;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.35), 0 3px 10px rgba(0, 0, 0, 0.16), 0 0 0 1px {dialog_ring};
}}

window.dialog > contents,
dialog > contents,
adwdialog > contents,
adwalertdialog > contents {{
    border-radius: 20px;
    padding: 20px 24px;
}}

window.dialog headerbar,
dialog headerbar,
messagedialog headerbar,
adwdialog headerbar {{
    border-top-left-radius: 20px;
    border-top-right-radius: 20px;
}}

window.dialog .dialog-action-area button,
dialog .dialog-action-area button,
messagedialog .dialog-action-area button,
window.dialog .response-area button,
dialog .response-area button,
messagedialog .response-area button,
adwdialog .dialog-action-area button,
adwdialog .response-area button,
adwalertdialog button {{
    min-height: 26px;
    border-radius: 9999px;
    padding: 3px 16px;
    font-weight: 500;
}}

/* Nautilus & Standard History Navigation Controls (< >) - Authentic macOS 27 Capsule Pill */
NautilusHistoryControls,
.navigation-controls,
headerbar .navigation-controls,
.nautilus-window headerbar .navigation-controls,
#NautilusFileChooser headerbar .navigation-controls {{
    background-color: {linked_bg};
    background-image: none;
    border: {linked_border};
    box-shadow: {linked_shadow};
    border-radius: 9999px;
    padding: 2px;
    margin: 0 4px;
}}

NautilusHistoryControls:backdrop,
.navigation-controls:backdrop {{
    background-color: {linked_bg};
    border: {linked_border};
    box-shadow: {linked_shadow};
    opacity: 0.90;
}}

NautilusHistoryControls > box,
NautilusHistoryControls box {{
    background: transparent;
    border: none;
    box-shadow: none;
    padding: 0;
    margin: 0;
    border-spacing: 0;
}}

NautilusHistoryControls button,
NautilusHistoryControls button:not(.flat),
NautilusHistoryControls #back_button,
NautilusHistoryControls #forward_button,
.navigation-controls button,
.navigation-controls button:not(.flat),
.nautilus-window NautilusHistoryControls button,
.nautilus-window .navigation-controls button {{
    background: transparent;
    background-color: transparent;
    background-image: none;
    border: none;
    box-shadow: none;
    padding: 2px 8px;
    min-height: 22px;
    min-width: 26px;
    margin: 0;
    color: {btn_fg};
    transition: background-color 80ms ease;
}}

NautilusHistoryControls button:hover,
NautilusHistoryControls #back_button:hover,
NautilusHistoryControls #forward_button:hover,
.navigation-controls button:hover,
.nautilus-window NautilusHistoryControls button:hover,
.nautilus-window .navigation-controls button:hover {{
    background: {linked_hover};
    background-color: {linked_hover};
    border: none;
    box-shadow: none;
}}

NautilusHistoryControls button:active,
NautilusHistoryControls #back_button:active,
NautilusHistoryControls #forward_button:active,
.navigation-controls button:active,
.nautilus-window NautilusHistoryControls button:active,
.nautilus-window .navigation-controls button:active {{
    background: {active_subtle};
    background-color: {active_subtle};
    border: none;
    box-shadow: none;
}}

NautilusHistoryControls button:first-child,
.navigation-controls button:first-child {{
    border-top-left-radius: 9999px;
    border-bottom-left-radius: 9999px;
    border-top-right-radius: 0;
    border-bottom-right-radius: 0;
    border-right: none;
    margin-right: -3px;
    margin-left: 0;
}}

NautilusHistoryControls button:last-child,
.navigation-controls button:last-child,
NautilusHistoryControls button + button,
NautilusHistoryControls #back_button + #forward_button,
.navigation-controls button + button {{
    border-top-right-radius: 9999px;
    border-bottom-right-radius: 9999px;
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
    border-left: {linked_divider};
    margin-left: -3px;
    margin-right: 0;
}}

/* 16. Segmented Controls (.linked, stackswitcher, viewswitcher) & Split Buttons (AdwSplitButton) */
/* Segmented Control Capsule Container (macOS pill container) */
window headerbar .linked:not(.path-bar):not(nautilus-path-bar),
window .titlebar .linked:not(.path-bar):not(nautilus-path-bar),
window headerbar box.linked:not(.path-bar):not(nautilus-path-bar),
window .titlebar box.linked:not(.path-bar):not(nautilus-path-bar),
window headerbar stackswitcher,
window .titlebar stackswitcher,
window headerbar viewswitcher,
window .titlebar viewswitcher,
window .linked:not(.path-bar):not(nautilus-path-bar),
window box.linked:not(.path-bar):not(nautilus-path-bar),
window stackswitcher,
window viewswitcher,
headerbar .linked:not(.path-bar):not(nautilus-path-bar),
.titlebar .linked:not(.path-bar):not(nautilus-path-bar),
headerbar box.linked:not(.path-bar):not(nautilus-path-bar),
.titlebar box.linked:not(.path-bar):not(nautilus-path-bar),
headerbar stackswitcher,
.titlebar stackswitcher,
headerbar viewswitcher,
.titlebar viewswitcher,
.linked:not(.path-bar):not(nautilus-path-bar),
box.linked:not(.path-bar):not(nautilus-path-bar),
stackswitcher,
viewswitcher,
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

/* Inner buttons of Segmented Controls - seamless flush at rest */
window headerbar .linked > button,
window headerbar .linked > button.flat,
window headerbar box.linked > button,
window headerbar box.linked > button.flat,
window headerbar stackswitcher > button,
window headerbar stackswitcher > button.flat,
window headerbar viewswitcher > button,
window headerbar viewswitcher > button.flat,
window .linked > button,
window .linked > button.flat,
window box.linked > button,
window box.linked > button.flat,
window stackswitcher > button,
window stackswitcher > button.flat,
window viewswitcher > button,
window viewswitcher > button.flat,
headerbar .linked > button,
headerbar .linked > button.flat,
headerbar box.linked > button,
headerbar box.linked > button.flat,
headerbar stackswitcher > button,
headerbar stackswitcher > button.flat,
headerbar viewswitcher > button,
headerbar viewswitcher > button.flat,
.linked > button,
.linked > button.flat,
box.linked > button,
box.linked > button.flat,
stackswitcher > button,
viewswitcher > button {{
    min-height: 22px;
    min-width: 22px;
    padding: 2px 8px;
    border-radius: {seg_radius}px;
    margin: 0;
    background: transparent;
    background-color: transparent;
    background-image: none;
    border: none;
    box-shadow: none;
    outline: none;
    color: {btn_fg};
    font-size: 13px;
    font-weight: 400;
    transition: background-color 80ms ease, color 80ms ease;
}}

/* Segmented Control Hover */
window headerbar .linked > button:hover:not(:checked),
window headerbar box.linked > button:hover:not(:checked),
window headerbar stackswitcher > button:hover:not(:checked),
window headerbar viewswitcher > button:hover:not(:checked),
window .linked > button:hover:not(:checked),
window box.linked > button:hover:not(:checked),
headerbar .linked > button:hover:not(:checked),
headerbar box.linked > button:hover:not(:checked),
headerbar stackswitcher > button:hover:not(:checked),
headerbar viewswitcher > button:hover:not(:checked),
.linked > button:hover:not(:checked),
box.linked > button:hover:not(:checked),
stackswitcher > button:hover:not(:checked),
viewswitcher > button:hover:not(:checked) {{
    background-color: {linked_hover};
    color: {btn_fg};
    box-shadow: none;
}}

/* Segmented Control Active / Pressed */
window headerbar .linked > button:active:not(:checked),
window headerbar box.linked > button:active:not(:checked),
window .linked > button:active:not(:checked),
window box.linked > button:active:not(:checked),
headerbar .linked > button:active:not(:checked),
headerbar box.linked > button:active:not(:checked),
.linked > button:active:not(:checked),
box.linked > button:active:not(:checked),
stackswitcher > button:active:not(:checked),
viewswitcher > button:active:not(:checked) {{
    background-color: {linked_active};
    color: {btn_fg};
    box-shadow: none;
}}

/* Selected / Checked Segment (Elevated macOS Segment Plate) */
window headerbar .linked > button:checked,
window headerbar .linked > button.flat:checked,
window headerbar .linked > button.toggle:checked,
window headerbar .linked > togglebutton:checked,
window headerbar box.linked > button:checked,
window headerbar box.linked > button.flat:checked,
window headerbar box.linked > button.toggle:checked,
window headerbar box.linked > togglebutton:checked,
window headerbar stackswitcher > button:checked,
window headerbar viewswitcher > button:checked,
window .linked > button:checked,
window .linked > button.flat:checked,
window .linked > button.toggle:checked,
window .linked > togglebutton:checked,
window box.linked > button:checked,
headerbar .linked > button:checked,
headerbar .linked > button.toggle:checked,
headerbar .linked > togglebutton:checked,
headerbar box.linked > button:checked,
headerbar box.linked > button.toggle:checked,
headerbar box.linked > togglebutton:checked,
headerbar stackswitcher > button:checked,
headerbar viewswitcher > button:checked,
.linked > button:checked,
.linked > button.toggle:checked,
.linked > togglebutton:checked,
box.linked > button:checked,
box.linked > button.toggle:checked,
box.linked > togglebutton:checked,
stackswitcher > button:checked,
viewswitcher > button:checked {{
    background-color: {linked_checked};
    color: {linked_checked_fg};
    box-shadow: {linked_checked_shadow};
    border-radius: 9999px;
    border: none;
    font-weight: 500;
}}

/* Subtle hairline divider between adjacent unselected segments */
.linked > button:not(:checked) + button:not(:checked),
.linked > button.toggle:not(:checked) + button.toggle:not(:checked),
box.linked > button:not(:checked) + button:not(:checked),
box.linked > button.toggle:not(:checked) + button.toggle:not(:checked),
headerbar .linked > button:not(:checked) + button:not(:checked),
headerbar .linked > button.toggle:not(:checked) + button.toggle:not(:checked),
headerbar box.linked > button:not(:checked) + button:not(:checked),
headerbar box.linked > button.toggle:not(:checked) + button.toggle:not(:checked),
stackswitcher > button:not(:checked) + button:not(:checked),
viewswitcher > button:not(:checked) + button:not(:checked) {{
    border-left: {linked_divider};
}}


/* ── macOS 27 Apple HIG Toolbar Capsules, Controls & Backdrop Consistency ── */
/* 1. Neutralize all rogue backgrounds/borders on buttons inside headerbars and capsules (excluding traffic lights) */
headerbar button:not(.titlebutton):not(.close):not(.minimize):not(.maximize),
headerbar button:backdrop:not(.titlebutton):not(.close):not(.minimize):not(.maximize),
.titlebar button:not(.titlebutton):not(.close):not(.minimize):not(.maximize),
.titlebar button:backdrop:not(.titlebutton):not(.close):not(.minimize):not(.maximize),
window headerbar button:not(.titlebutton):not(.close):not(.minimize):not(.maximize),
window headerbar button:backdrop:not(.titlebutton):not(.close):not(.minimize):not(.maximize),
headerbar menubutton > button,
headerbar menubutton > button:backdrop,
headerbar menubutton.flat > button,
headerbar menubutton.flat > button:backdrop,
headerbar splitbutton > button,
headerbar splitbutton > button:focus,
headerbar splitbutton > button:focus-visible,
headerbar splitbutton > button:focus-within,
headerbar splitbutton > button:backdrop,
headerbar splitbutton > menubutton > button,
headerbar splitbutton > menubutton > button:focus,
headerbar splitbutton > menubutton > button:focus-visible,
headerbar splitbutton > menubutton > button:backdrop,
splitbutton > button,
splitbutton > button:focus,
splitbutton > button:focus-visible,
splitbutton > button:focus-within,
splitbutton > button:backdrop,
splitbutton > menubutton > button,
splitbutton > menubutton > button:focus,
splitbutton > menubutton > button:focus-visible,
splitbutton > menubutton > button:backdrop,
window headerbar splitbutton > button,
window headerbar splitbutton > button:focus,
window headerbar splitbutton > button:focus-visible,
window headerbar splitbutton > button:focus-within,
window headerbar splitbutton > button:backdrop,
window headerbar splitbutton > menubutton > button,
window headerbar splitbutton > menubutton > button:focus,
window headerbar splitbutton > menubutton > button:focus-visible,
window headerbar splitbutton > menubutton > button:backdrop,
headerbar .linked > button,
headerbar .linked > button:backdrop,
headerbar box.linked > button,
headerbar box.linked > button:backdrop,
.linked > button,
.linked > button:backdrop,
box.linked > button,
box.linked > button:backdrop,
viewswitcher > button,
viewswitcher > button:backdrop,
headerbar viewswitcher > button,
headerbar viewswitcher > button:backdrop {{
    background: transparent;
    background-color: transparent;
    background-image: none;
    border: none;
    box-shadow: none;
    color: {btn_fg};
}}

/* 2. Elevated Capsule Containers in Headerbars */
window headerbar .linked:not(.path-bar):not(nautilus-path-bar),
window headerbar box.linked:not(.path-bar):not(nautilus-path-bar),
window headerbar stackswitcher,
window headerbar viewswitcher,
headerbar .linked:not(.path-bar):not(nautilus-path-bar),
headerbar box.linked:not(.path-bar):not(nautilus-path-bar),
headerbar stackswitcher,
headerbar viewswitcher,
.linked:not(.path-bar):not(nautilus-path-bar),
box.linked:not(.path-bar):not(nautilus-path-bar),
stackswitcher,
viewswitcher,
NautilusHistoryControls,
.navigation-controls,
headerbar .navigation-controls,
headerbar splitbutton,
.titlebar splitbutton,
window headerbar splitbutton,
window .titlebar splitbutton,
splitbutton {{
    background-color: {linked_bg};
    background-image: none;
    border: {linked_border};
    box-shadow: {linked_shadow};
    border-radius: 9999px;
    margin: 0 4px;
    padding: 2px;
}}

window headerbar .linked:backdrop,
window headerbar box.linked:backdrop,
headerbar .linked:backdrop,
headerbar box.linked:backdrop,
.linked:backdrop,
box.linked:backdrop,
stackswitcher:backdrop,
viewswitcher:backdrop,
headerbar viewswitcher:backdrop,
headerbar splitbutton:backdrop,
window headerbar splitbutton:backdrop,
splitbutton:backdrop,
NautilusHistoryControls:backdrop,
.navigation-controls:backdrop {{
    background-color: {linked_bg};
    background-image: none;
    border: {linked_border};
    box-shadow: {linked_shadow};
    opacity: 0.90;
}}

/* 3. Inner buttons of Toolbar Capsules */
headerbar .linked > button,
headerbar .linked > button.toggle,
headerbar box.linked > button,
headerbar box.linked > button.toggle,
headerbar viewswitcher > button,
headerbar viewswitcher > button.toggle,
.linked > button,
.linked > button.toggle,
box.linked > button,
box.linked > button.toggle,
viewswitcher > button,
viewswitcher > button.toggle,
headerbar splitbutton > button,
headerbar splitbutton > menubutton > button,
splitbutton > button,
splitbutton > menubutton > button,
NautilusHistoryControls button,
.navigation-controls button {{
    min-height: 22px;
    min-width: 22px;
    padding: 2px 8px;
    border-radius: 9999px;
    margin: 0;
    background: transparent;
    background-color: transparent;
    background-image: none;
    border: none;
    box-shadow: none;
    color: {btn_fg};
    transition: background-color 80ms ease, color 80ms ease;
}}

/* 4. Active / Checked Inset Capsule Pill (Apple macOS HIG) */
headerbar .linked > button:checked,
headerbar .linked > button:checked:backdrop,
headerbar .linked > button.toggle:checked,
headerbar .linked > button.toggle:checked:backdrop,
headerbar box.linked > button:checked,
headerbar box.linked > button:checked:backdrop,
headerbar box.linked > button.toggle:checked,
headerbar box.linked > button.toggle:checked:backdrop,
headerbar viewswitcher > button:checked,
headerbar viewswitcher > button:checked:backdrop,
headerbar viewswitcher > button.toggle:checked,
headerbar viewswitcher > button.toggle:checked:backdrop,
.linked > button:checked,
.linked > button:checked:backdrop,
.linked > button.toggle:checked,
.linked > button.toggle:checked:backdrop,
box.linked > button:checked,
box.linked > button:checked:backdrop,
box.linked > button.toggle:checked,
box.linked > button.toggle:checked:backdrop,
viewswitcher > button:checked,
viewswitcher > button:checked:backdrop,
viewswitcher > button.toggle:checked,
viewswitcher > button.toggle:checked:backdrop,
stackswitcher > button:checked,
stackswitcher > button:checked:backdrop {{
    background-color: {linked_checked};
    color: {linked_checked_fg};
    box-shadow: {linked_checked_shadow};
    border-radius: 9999px;
    border: none;
    font-weight: 500;
}}

/* 5. Hover and Pressed States */
headerbar .linked > button:hover:not(:checked),
headerbar box.linked > button:hover:not(:checked),
headerbar viewswitcher > button:hover:not(:checked),
.linked > button:hover:not(:checked),
box.linked > button:hover:not(:checked),
viewswitcher > button:hover:not(:checked),
headerbar splitbutton > button:hover,
headerbar splitbutton > menubutton > button:hover,
splitbutton > button:hover,
splitbutton > menubutton > button:hover,
NautilusHistoryControls button:hover,
.navigation-controls button:hover {{
    background-color: {linked_hover};
    border: none;
    box-shadow: none;
}}

headerbar .linked > button:active:not(:checked),
headerbar box.linked > button:active:not(:checked),
headerbar viewswitcher > button:active:not(:checked),
.linked > button:active:not(:checked),
box.linked > button:active:not(:checked),
viewswitcher > button:active:not(:checked),
headerbar splitbutton > button:active,
headerbar splitbutton > menubutton > button:active,
splitbutton > button:active,
splitbutton > menubutton > button:active,
NautilusHistoryControls button:active,
.navigation-controls button:active {{
    background-color: {linked_active};
    border: none;
    box-shadow: none;
}}

/* 6. Hairline Dividers Between Adjacent Unchecked Segments */
headerbar .linked > button:not(:checked) + button:not(:checked),
headerbar .linked > button.toggle:not(:checked) + button.toggle:not(:checked),
headerbar box.linked > button:not(:checked) + button:not(:checked),
headerbar box.linked > button.toggle:not(:checked) + button.toggle:not(:checked),
headerbar viewswitcher > button:not(:checked) + button:not(:checked),
headerbar viewswitcher > button.toggle:not(:checked) + button.toggle:not(:checked),
.linked > button:not(:checked) + button:not(:checked),
.linked > button.toggle:not(:checked) + button.toggle:not(:checked),
box.linked > button:not(:checked) + button:not(:checked),
box.linked > button.toggle:not(:checked) + button.toggle:not(:checked),
viewswitcher > button:not(:checked) + button:not(:checked),
viewswitcher > button.toggle:not(:checked) + button.toggle:not(:checked),
stackswitcher > button:not(:checked) + button:not(:checked),
NautilusHistoryControls button + button,
.navigation-controls button + button {{
    border-left: {linked_divider};
}}

/* 7. Splitbutton Hairline Separator */
window headerbar splitbutton > separator,
window splitbutton > separator,
headerbar splitbutton > separator,
splitbutton > separator {{
    min-width: 1px;
    min-height: 14px;
    background-color: {linked_divider_color};
    margin: 2px 0;
    padding: 0;
    border: none;
}}

/* 8. Directional Radii inside Split Buttons */
splitbutton > button:dir(ltr),
splitbutton > button:first-child:dir(ltr),
headerbar splitbutton > button:dir(ltr),
headerbar splitbutton > button:first-child:dir(ltr) {{
    border-top-left-radius: 9999px;
    border-bottom-left-radius: 9999px;
    border-top-right-radius: 0;
    border-bottom-right-radius: 0;
    border-right: none;
}}

splitbutton > menubutton > button:dir(ltr),
splitbutton > menubutton:last-child > button:dir(ltr),
headerbar splitbutton > menubutton > button:dir(ltr),
headerbar splitbutton > menubutton:last-child > button:dir(ltr) {{
    border-top-right-radius: 9999px;
    border-bottom-right-radius: 9999px;
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
    border-left: none;
}}

splitbutton > button:dir(rtl),
splitbutton > button:first-child:dir(rtl),
headerbar splitbutton > button:dir(rtl),
headerbar splitbutton > button:first-child:dir(rtl) {{
    border-top-right-radius: 9999px;
    border-bottom-right-radius: 9999px;
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
    border-left: none;
}}

splitbutton > menubutton > button:dir(rtl),
splitbutton > menubutton:last-child > button:dir(rtl),
headerbar splitbutton > menubutton > button:dir(rtl),
headerbar splitbutton > menubutton:last-child > button:dir(rtl) {{
    border-top-left-radius: 9999px;
    border-bottom-left-radius: 9999px;
    border-top-right-radius: 0;
    border-bottom-right-radius: 0;
    border-right: none;
}}

/* 17. macOS Color Wells & Image Wells (apple/color wells/ & apple/image wells/) */
colorbutton,
button.color {{
    padding: 2px 4px;
    min-height: {color_well_height}px;
    border-radius: {btn_radius}px;
}}

colorbutton colorswatch,
button.color colorswatch,
colorswatch {{
    border-radius: {color_well_radius}px;
    min-width: 28px;
    min-height: 16px;
    border: 1px solid {border_col};
}}

colorswatch:selected,
colorswatch:focus {{
    box-shadow: 0 0 0 2px @accent_bg_color;
}}

colorswatch.circular,
button.color.circular {{
    border-radius: 9999px;
    min-width: 24px;
    min-height: 24px;
    padding: 0;
}}

picture,
.image-well,
frame.image-well,
image.well {{
    border-radius: {image_well_radius}px;
    border: 1px solid {border_col};
    padding: 2px;
}}
"""


def inject_theme_css(src_css_path, dst_css_path, palette, is_glassy, button_size=14, button_spacing=8, chromium_accent=None, is_dark=True, sync_repo=False):
    # Safety guard: NEVER overwrite or truncate master theme assets in ~/.themes or repo themes
    if (os.path.abspath(dst_css_path) == os.path.abspath(src_css_path) or "/themes/" in dst_css_path or "/.themes/" in dst_css_path) and not os.path.exists(src_css_path + ".base"):
        return

    base_path = src_css_path + ".base"
    read_path = base_path if os.path.exists(base_path) else src_css_path
    try:
        with open(read_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        content = ""

    # Strip any legacy overrides if present in old files
    override_markers = [
        "/* ── Mak macOS Sonoma Refined Interactive Widgets",
        "/* ── Universal Mak Widgets & Control Metrics Override",
        "/* === Mak Suite Refinements",
        "/* ── Mak Clean macOS Traffic Light Button Controls",
        "/* ── Mak macOS Window Corner",
        "/* ── Mak Dynamic Customizations",
        "/* ── Mak Flavor Palette:",
        "/* ── Mak Flavor Clean Surface Mapping",
        "/* ── Mak Flavor Window & Surface Palette Mapping"
    ]
    base_end = len(content)
    for om in override_markers:
        pos = content.find(om)
        if pos != -1 and pos < base_end:
            base_end = pos

    content = content[:base_end].strip()

    # Filter out existing @define-color definitions that our palette overrides
    palette_keys = [
        "window_bg_color", "window_fg_color", "view_bg_color", "view_fg_color",
        "headerbar_bg_color", "headerbar_solid_bg", "headerbar_fg_color", "headerbar_border_color",
        "sidebar_bg_color", "sidebar_fg_color", "secondary_sidebar_bg_color",
        "card_bg_color", "card_fg_color", "dialog_bg_color", "dialog_fg_color",
        "popover_bg_color", "popover_fg_color", "placeholder_text_color",
        "theme_bg_color", "theme_fg_color", "theme_base_color", "theme_text_color",
        "theme_selected_bg_color", "theme_selected_fg_color",
        "theme_unfocused_bg_color", "theme_unfocused_fg_color",
        "theme_unfocused_base_color", "theme_unfocused_text_color",
        "accent_bg_color", "accent_fg_color", "accent_color",
        "bg_color", "fg_color", "base_color", "text_color",
        "selected_bg_color", "selected_fg_color", "content_view_bg", "text_view_bg"
    ]
    lines = content.splitlines()
    imports = []
    rest_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("@import ") or "/* Kiwi (is not Apple)" in line:
            imports.append(line)
            continue
        if any(stripped.startswith(f"@define-color {k} ") or stripped.startswith(f"@define-color {k};") for k in palette_keys):
            continue
        rest_lines.append(line)

    clean_body = "\n".join(rest_lines).strip()
    clean_body = re.sub(
        r"box-shadow:\s*0 0 0 6px (?:#242424|#ffffff), 0 32px 0 6px (?:#242424|#ffffff), 0 -32px 0 6px (?:#242424|#ffffff)",
        "box-shadow: 0 0 0 6px @window_bg_color, 0 32px 0 6px @window_bg_color, 0 -32px 0 6px @window_bg_color",
        clean_body
    )
    clean_body = re.sub(
        r"box-shadow:\s*9000px 0 0 9999px (?:#242424|#ffffff)",
        "box-shadow: 9000px 0 0 9999px @window_bg_color",
        clean_body
    )
    clean_body = re.sub(
        r"box-shadow:\s*-9000px 0 0 9999px (?:#242424|#ffffff)",
        "box-shadow: -9000px 0 0 9999px @window_bg_color",
        clean_body
    )
    clean_body = re.sub(
        r"(\.nautilus-window\s+\.content-pane,\s*#NautilusFileChooser\s+\.content-pane,\s*\.nautilus-file-chooser\s+\.content-pane\s*\{\s*background-color:\s*)(?:#242424|#ffffff);",
        r"\1@view_bg_color;",
        clean_body
    )
    clean_body = re.sub(
        r"(\.nautilus-window\s+\.content-pane:backdrop,\s*#NautilusFileChooser\s+\.content-pane:backdrop,\s*\.nautilus-file-chooser\s+\.content-pane:backdrop\s*\{\s*background-color:\s*)(?:#242424|#ffffff);",
        r"\1@window_bg_color;",
        clean_body
    )
    clean_body = re.sub(
        r"(popover(?:\.menu)?(?:\.background)?\s*>\s*(?:contents|arrow)\s*\{[^}]*background-color:\s*)#333333;",
        r"\1@popover_bg_color;",
        clean_body
    )
    clean_body = re.sub(
        r"(popover(?:\.menu)?(?:\.background)?\s*>\s*(?:contents|arrow)\s*\{[^}]*border:\s*)[^;]+;",
        r"\1none;",
        clean_body
    )
    clean_body = re.sub(
        r"popover\s*>\s*contents\s+stack\s+scrolledwindow(?::not\(\.view\))?\s*>\s*viewport\s*\{[^}]*\}",
        "popover > contents stack scrolledwindow:not(.view) > viewport { background-color: transparent; border: none; }",
        clean_body
    )
    clean_body = re.sub(
        r"headerbar\s+entry\s*\{[^}]*inset\s+1px\s+1px[^}]*\}",
        "headerbar entry { background-color: alpha(currentColor, 0.08); background-image: none; box-shadow: none; border: none; }",
        clean_body
    )
    clean_body = re.sub(
        r"headerbar\s+entry:hover\s*\{[^}]*inset\s+1px\s+1px[^}]*\}",
        "headerbar entry:hover { background-color: alpha(currentColor, 0.10); background-image: none; box-shadow: none; border: none; }",
        clean_body
    )
    import_block = "\n".join(imports).strip()

    is_gtk4 = "gtk-4.0" in dst_css_path or "gtk-3.0" not in dst_css_path
    kiwi_ext_path = os.path.expanduser("~/.local/share/gnome-shell/extensions/kiwi@kemma")
    kiwi_block = ""
    if os.path.exists(kiwi_ext_path):
        if is_gtk4:
            kiwi_block = """/* Kiwi (is not Apple) - managed imports: begin */
@import url("file:///home/parv/.local/share/gnome-shell/extensions/kiwi@kemma/css/titlebuttons4.css");
@import url("file:///home/parv/.local/share/gnome-shell/extensions/kiwi@kemma/css/titlebuttons-size-small4.css");
@import url("file:///home/parv/.local/share/gnome-shell/extensions/kiwi@kemma/css/fixes4.css");
/* Kiwi (is not Apple) - managed imports: end */"""
        else:
            kiwi_block = """/* Kiwi (is not Apple) - managed imports: begin */
@import url("file:///home/parv/.local/share/gnome-shell/extensions/kiwi@kemma/css/titlebuttons3.css");
@import url("file:///home/parv/.local/share/gnome-shell/extensions/kiwi@kemma/css/titlebuttons-size-small3.css");
@import url("file:///home/parv/.local/share/gnome-shell/extensions/kiwi@kemma/css/fixes3.css");
/* Kiwi (is not Apple) - managed imports: end */"""

    parts = []
    if kiwi_block:
        parts.append(kiwi_block)
    elif import_block:
        parts.append(import_block)

    if palette:
        parts.append(palette.strip())

    if is_gtk4 and clean_body:
        parts.append(clean_body)

    if is_glassy:
        parts.append(GLASSY_CONTAINER_RULES.strip())

    safe_surface_rules = """
/* ── Mak Flavor Clean Surface Mapping (Zero-Impact on Buttons & Controls) ── */

/* Universal Headerbars & Titlebars (GTK3, GTK4, Libadwaita, libdecor) */
headerbar,
headerbar:backdrop,
headerbar.titlebar,
headerbar.titlebar:backdrop,
.titlebar,
.titlebar:backdrop,
window headerbar,
window headerbar:backdrop,
window.csd headerbar,
window.csd headerbar:backdrop,
window.background.csd headerbar,
window.background.csd headerbar:backdrop,
toolbarview > headerbar,
toolbarview > headerbar:backdrop,
navigation-split-view > .content-pane headerbar,
navigation-split-view > .content-pane headerbar:backdrop,
overlay-split-view > .content-pane headerbar,
overlay-split-view > .content-pane headerbar:backdrop,
.content-pane headerbar,
.content-pane headerbar:backdrop,
window.background.csd > dialog-host > widget > widget > box > leaflet > headerbar.titlebar.tweak-titlebar-left,
window.background.csd > dialog-host > widget > widget > box > leaflet > headerbar.titlebar.tweak-titlebar-right,
window.background.csd > contents > leaflet.unfolded > box > headerbar,
window.background.csd > contents > leaflet.unfolded > box > stack > widget > box > widget > headerbar,
window.background.csd > contents > leaflet.unfolded > box > stack > widget > overlay > leaflet.folded > box > headerbar,
window.background.csd > widget > leaflet.unfolded > box > headerbar,
window.background.csd > widget > leaflet.unfolded > box > stack > widget > box > widget > headerbar,
window.background.csd > widget > leaflet.unfolded > box > stack > widget > overlay > leaflet.folded > box > headerbar,
.nautilus-window headerbar,
.nautilus-window headerbar:backdrop,
.nautilus-window .content-pane headerbar,
.nautilus-window .content-pane headerbar:backdrop,
.nautilus-window toolbarview > headerbar,
.nautilus-window toolbarview > headerbar:backdrop,
.nautilus-window .content-pane toolbarview > headerbar,
.nautilus-window .content-pane toolbarview > headerbar:backdrop {
  background-color: @headerbar_bg_color;
  color: @headerbar_fg_color;
  border-color: @headerbar_border_color;
}

/* Headerbar searchbars & revealer boxes */
window.background.csd > dialog-host > widget > widget > box > leaflet > box > searchbar > revealer > box,
window.background.csd > contents > leaflet.unfolded > box > searchbar > revealer > box,
window.background.csd > widget > leaflet.unfolded > box > searchbar > revealer > box {
  background-color: @headerbar_bg_color;
  color: @headerbar_fg_color;
}

/* Universal Background Overrides - Eliminates hardcoded dark gray leaking from clean_body */
.background,
.background.view,
.background:backdrop,
window,
window:backdrop,
window.background,
window.background:backdrop,
window.csd,
window.csd:backdrop,
window.background.csd,
window.background.csd:backdrop,
window.view,
window.view:backdrop,
window.background.view,
window.background.view:backdrop,
dialog-host,
dialog-host:backdrop,
toastoverlay,
toastoverlay:backdrop,
navigation-split-view,
navigation-split-view:backdrop,
overlay-split-view,
overlay-split-view:backdrop,
split-view,
split-view:backdrop,
leaflet,
leaflet:backdrop,
leaflet.unfolded,
leaflet.unfolded:backdrop,
.nautilus-window,
.nautilus-window:backdrop,
#NautilusFileChooser,
#NautilusFileChooser:backdrop,
.nautilus-file-chooser,
.nautilus-file-chooser:backdrop {
  background-color: @window_bg_color;
  color: @window_fg_color;
}

/* ── Authentic Mac Tahoe Full Floating Sidebar Architecture ── */

/* Full Floating Sidebar Card Surface (encompasses traffic lights & places list) */
.sidebar-pane,
.sidebar-pane:first-child,
.content-pane .sidebar-pane,
.content-pane .sidebar-pane:first-child,
.sidebar-pane .content-pane,
.sidebar-pane .content-pane:first-child,
overlay-split-view > .sidebar-pane,
overlay-split-view > .sidebar-pane:first-child,
navigation-split-view > .sidebar-pane,
navigation-split-view > .sidebar-pane:first-child,
split-view > .sidebar-pane,
split-view > .sidebar-pane:first-child,
.nautilus-window .sidebar-pane,
.nautilus-window .sidebar-pane:first-child,
#NautilusFileChooser .sidebar-pane,
#NautilusFileChooser .sidebar-pane:first-child,
.nautilus-file-chooser .sidebar-pane,
.nautilus-file-chooser .sidebar-pane:first-child {
  background-image: linear-gradient(to bottom, rgba(0, 0, 0, 0.03), transparent 80%, rgba(255, 255, 255, 0.03));
  color: @sidebar_fg_color;
  border-radius: 14px;
  background-color: @sidebar_bg_color;
  border: 1px solid alpha(currentColor, 0.16);
}

/* Floating Card Margins and Elevation Drop Shadow for ALL apps */
.sidebar-pane:dir(ltr),
.sidebar-pane:first-child:dir(ltr),
.sidebar-pane:dir(ltr) banner > revealer > widget,
.content-pane .sidebar-pane:dir(ltr),
.content-pane .sidebar-pane:first-child:dir(ltr),
.content-pane .sidebar-pane:dir(ltr) banner > revealer > widget,
.sidebar-pane .content-pane:dir(ltr),
.sidebar-pane .content-pane:first-child:dir(ltr),
.sidebar-pane .content-pane:dir(ltr) banner > revealer > widget,
overlay-split-view > .sidebar-pane:dir(ltr),
overlay-split-view > .sidebar-pane:first-child:dir(ltr),
navigation-split-view > .sidebar-pane:dir(ltr),
navigation-split-view > .sidebar-pane:first-child:dir(ltr),
split-view > .sidebar-pane:dir(ltr),
split-view > .sidebar-pane:first-child:dir(ltr),
.nautilus-window .sidebar-pane:dir(ltr),
.nautilus-window .sidebar-pane:first-child:dir(ltr),
.nautilus-window .sidebar-pane:dir(ltr) banner > revealer > widget,
#NautilusFileChooser .sidebar-pane:dir(ltr),
#NautilusFileChooser .sidebar-pane:first-child:dir(ltr),
#NautilusFileChooser .sidebar-pane:dir(ltr) banner > revealer > widget,
.nautilus-file-chooser .sidebar-pane:dir(ltr),
.nautilus-file-chooser .sidebar-pane:first-child:dir(ltr),
.nautilus-file-chooser .sidebar-pane:dir(ltr) banner > revealer > widget {
  margin: 6px 0 6px 6px;
  box-shadow: 2px 3px 12px rgba(0, 0, 0, 0.15);
  border: 1px solid alpha(currentColor, 0.16);
}

.sidebar-pane:dir(rtl),
.sidebar-pane:first-child:dir(rtl),
.sidebar-pane:dir(rtl) banner > revealer > widget,
.content-pane .sidebar-pane:dir(rtl),
.content-pane .sidebar-pane:first-child:dir(rtl),
.content-pane .sidebar-pane:dir(rtl) banner > revealer > widget,
.sidebar-pane .content-pane:dir(rtl),
.sidebar-pane .content-pane:first-child:dir(rtl),
.sidebar-pane .content-pane:dir(rtl) banner > revealer > widget,
overlay-split-view > .sidebar-pane:dir(rtl),
overlay-split-view > .sidebar-pane:first-child:dir(rtl),
navigation-split-view > .sidebar-pane:dir(rtl),
navigation-split-view > .sidebar-pane:first-child:dir(rtl),
split-view > .sidebar-pane:dir(rtl),
split-view > .sidebar-pane:first-child:dir(rtl),
.nautilus-window .sidebar-pane:dir(rtl),
.nautilus-window .sidebar-pane:first-child:dir(rtl),
.nautilus-window .sidebar-pane:dir(rtl) banner > revealer > widget,
#NautilusFileChooser .sidebar-pane:dir(rtl),
#NautilusFileChooser .sidebar-pane:first-child:dir(rtl),
#NautilusFileChooser .sidebar-pane:dir(rtl) banner > revealer > widget,
.nautilus-file-chooser .sidebar-pane:dir(rtl),
.nautilus-file-chooser .sidebar-pane:first-child:dir(rtl),
.nautilus-file-chooser .sidebar-pane:dir(rtl) banner > revealer > widget {
  margin: 6px 6px 6px 0;
  box-shadow: -2px 3px 12px rgba(0, 0, 0, 0.15);
  border: 1px solid alpha(currentColor, 0.16);
}

/* Sidebar Backdrop (Unfocused Window) */
.sidebar-pane:backdrop,
.sidebar-pane:first-child:backdrop,
.content-pane .sidebar-pane:backdrop,
.sidebar-pane .content-pane:backdrop,
.nautilus-window .sidebar-pane:backdrop,
.nautilus-window .sidebar-pane:first-child:backdrop,
#NautilusFileChooser .sidebar-pane:backdrop,
.nautilus-file-chooser .sidebar-pane:backdrop {
  transition: background-color 150ms cubic-bezier(0, 0, 0.2, 1);
  background-color: alpha(@window_fg_color, 0.015);
  background-image: none;
  box-shadow: none;
  border: 1px solid alpha(currentColor, 0.08);
}

.sidebar-pane:backdrop:dir(ltr),
.sidebar-pane:backdrop:dir(ltr) banner > revealer > widget,
.sidebar-pane:backdrop.end:dir(rtl),
.sidebar-pane:backdrop.end:dir(rtl) banner > revealer > widget,
.sidebar-pane:backdrop:dir(rtl),
.sidebar-pane:backdrop:dir(rtl) banner > revealer > widget,
.sidebar-pane:backdrop.end:dir(ltr),
.sidebar-pane:backdrop.end:dir(ltr) banner > revealer > widget,
.nautilus-window .sidebar-pane:backdrop:dir(ltr),
.nautilus-window .sidebar-pane:backdrop:dir(ltr) banner > revealer > widget,
.nautilus-window .sidebar-pane:backdrop.end:dir(rtl),
.nautilus-window .sidebar-pane:backdrop.end:dir(rtl) banner > revealer > widget,
.nautilus-window .sidebar-pane:backdrop:dir(rtl),
.nautilus-window .sidebar-pane:backdrop:dir(rtl) banner > revealer > widget,
.nautilus-window .sidebar-pane:backdrop.end:dir(ltr),
.nautilus-window .sidebar-pane:backdrop.end:dir(ltr) banner > revealer > widget,
#NautilusFileChooser .sidebar-pane:backdrop:dir(ltr),
#NautilusFileChooser .sidebar-pane:backdrop:dir(ltr) banner > revealer > widget,
#NautilusFileChooser .sidebar-pane:backdrop.end:dir(rtl),
#NautilusFileChooser .sidebar-pane:backdrop.end:dir(rtl) banner > revealer > widget,
.nautilus-file-chooser .sidebar-pane:backdrop:dir(ltr),
.nautilus-file-chooser .sidebar-pane:backdrop:dir(ltr) banner > revealer > widget,
.nautilus-file-chooser .sidebar-pane:backdrop.end:dir(rtl),
.nautilus-file-chooser .sidebar-pane:backdrop.end:dir(rtl) banner > revealer > widget {
  box-shadow: none;
}

/* Sidebar Internal Widgets: Strictly transparent so card radius & thin border shine through */
.sidebar-pane list:not(.boxed-list),
.sidebar-pane .frame,
.sidebar-pane .sidebar,
.sidebar-pane .toolbar,
.sidebar-pane .navigation-sidebar,
.sidebar-pane placessidebar,
.sidebar-pane placessidebar viewport,
.sidebar-pane scrolledwindow,
.sidebar-pane scrolledwindow viewport,
.sidebar-pane viewport,
.sidebar-pane searchbar > revealer > box,
.nautilus-window .sidebar-pane placessidebar,
#NautilusFileChooser .sidebar-pane placessidebar,
.nautilus-file-chooser .sidebar-pane placessidebar {
  background-color: transparent;
  background-image: none;
  box-shadow: none;
  border: none;
}

/* Sidebar headerbars - strictly transparent with top rounded corners to seamlessly blend into top of floating card */
window.background.csd .sidebar-pane headerbar,
window.background.csd .sidebar-pane headerbar:backdrop,
window.background.csd .sidebar-pane windowhandle,
window.background.csd .sidebar-pane toolbarview,
window.background.csd .sidebar-pane toolbarview > .top-bar,
window.background.csd .sidebar-pane toolbarview > .top-bar headerbar,
window.background.csd overlay-split-view > .sidebar-pane headerbar,
window.background.csd overlay-split-view > .sidebar-pane headerbar:backdrop,
window.background.csd navigation-split-view > .sidebar-pane headerbar,
window.background.csd navigation-split-view > .sidebar-pane headerbar:backdrop,
window.background.csd split-view > .sidebar-pane headerbar,
window.background.csd split-view > .sidebar-pane headerbar:backdrop,
window.background.csd .nautilus-window .sidebar-pane headerbar,
window.background.csd .nautilus-window .sidebar-pane headerbar:backdrop,
window.background.csd #NautilusFileChooser .sidebar-pane headerbar,
window.background.csd #NautilusFileChooser .sidebar-pane headerbar:backdrop,
window.background.csd .nautilus-file-chooser .sidebar-pane headerbar,
window.background.csd .nautilus-file-chooser .sidebar-pane headerbar:backdrop,
window.csd .sidebar-pane headerbar,
window.csd .sidebar-pane headerbar:backdrop,
window.background .sidebar-pane headerbar,
window.background .sidebar-pane headerbar:backdrop,
window .sidebar-pane headerbar,
window .sidebar-pane headerbar:backdrop,
.sidebar-pane headerbar,
.sidebar-pane headerbar:backdrop,
.sidebar-pane windowhandle,
.sidebar-pane > toolbarview > revealer > windowhandle > box > headerbar,
.sidebar-pane > toolbarview > revealer > windowhandle > box > headerbar:backdrop,
.sidebar-pane toolbarview,
.sidebar-pane toolbarview > .top-bar,
.sidebar-pane toolbarview > .top-bar.raised,
.sidebar-pane toolbarview > .top-bar.border,
.sidebar-pane toolbarview > .top-bar.raised.border,
.sidebar-pane toolbarview > .top-bar > revealer,
.sidebar-pane toolbarview > .top-bar > revealer > windowhandle,
.sidebar-pane toolbarview > .top-bar > revealer > windowhandle > box,
overlay-split-view > .sidebar-pane headerbar,
overlay-split-view > .sidebar-pane headerbar:backdrop,
overlay-split-view > .sidebar-pane toolbarview > .top-bar,
navigation-split-view > .sidebar-pane headerbar,
navigation-split-view > .sidebar-pane headerbar:backdrop,
navigation-split-view > .sidebar-pane toolbarview > .top-bar,
split-view > .sidebar-pane headerbar,
split-view > .sidebar-pane headerbar:backdrop,
split-view > .sidebar-pane toolbarview > .top-bar,
.nautilus-window .sidebar-pane headerbar,
.nautilus-window .sidebar-pane headerbar:backdrop,
#NautilusFileChooser .sidebar-pane headerbar,
#NautilusFileChooser .sidebar-pane headerbar:backdrop,
.nautilus-file-chooser .sidebar-pane headerbar,
.nautilus-file-chooser .sidebar-pane headerbar:backdrop {
  background-color: transparent;
  background-image: none;
  color: @headerbar_fg_color;
  box-shadow: none;
  border: none;
  border-top-left-radius: 13px;
  border-top-right-radius: 13px;
}

/* Traffic lights / window controls positioning in floating sidebar headerbar */
.sidebar-pane headerbar windowcontrols:not(.empty).start:dir(ltr),
.sidebar-pane headerbar windowcontrols:not(.empty).end:dir(rtl) {
  margin-right: 0;
  padding-left: 8px;
  padding-right: 0;
}

.sidebar-pane headerbar windowcontrols:not(.empty).start:dir(rtl),
.sidebar-pane headerbar windowcontrols:not(.empty).end:dir(ltr) {
  margin-left: 0;
  padding-left: 0;
  padding-right: 8px;
}

.sidebar-pane headerbar windowcontrols button.close,
.sidebar-pane headerbar windowcontrols button.maximize,
.sidebar-pane headerbar windowcontrols button.minimize {
  margin: 0 1px;
}

/* Hide horizontal separator seam between headerbar and placessidebar */
.sidebar-pane > separator.horizontal,
.sidebar-pane separator,
.nautilus-window .sidebar-pane > separator.horizontal,
.nautilus-window .sidebar-pane separator {
  background-color: transparent;
  background-image: none;
  border: none;
  box-shadow: none;
  min-height: 0;
  opacity: 0;
}

/* Legacy GTK3 and Non-split Sidebars */
window.background.csd > dialog-host > widget > widget > box > leaflet list.navigation-sidebar,
window.background.csd > contents > leaflet.unfolded > box > scrolledwindow > viewport > widget > stack > list.navigation-sidebar,
window.background.csd > widget > leaflet.unfolded > box > scrolledwindow > viewport > widget > stack > list.navigation-sidebar,
window.background.csd > contents > leaflet.unfolded > box > scrolledwindow > viewport > widget > stack > box > list.navigation-sidebar,
window.background.csd > widget > leaflet.unfolded > box > scrolledwindow > viewport > widget > stack > box > list.navigation-sidebar,
sidebar,
sidebar:backdrop,
.sidebar:not(.sidebar-pane),
.sidebar:not(.sidebar-pane):backdrop {
  background-color: @sidebar_bg_color;
  color: @sidebar_fg_color;
}

/* Content Pane Surfaces (Nautilus, Libadwaita & GTK Views) */
.content-pane,
.content-pane:backdrop,
overlay-split-view > .content-pane,
overlay-split-view > .content-pane:backdrop,
navigation-split-view > .content-pane,
navigation-split-view > .content-pane:backdrop,
split-view > .content-pane,
split-view > .content-pane:backdrop,
.content-pane > toolbarview,
.content-pane scrolledwindow,
.content-pane scrolledwindow.view,
.content-pane .view,
.nautilus-window .content-pane,
.nautilus-window .content-pane:backdrop,
.nautilus-window .content-pane > toolbarview,
.nautilus-window .content-pane scrolledwindow,
.nautilus-window .content-pane scrolledwindow.view,
.nautilus-window .content-pane .view,
.nautilus-window .nautilus-list-view,
.nautilus-window .nautilus-grid-view,
.nautilus-window .nautilus-network-view,
.nautilus-window columnview,
.nautilus-window columnview.view,
.nautilus-window listview,
.nautilus-window gridview,
.nautilus-window .view,
.nautilus-window .view:backdrop,
#NautilusFileChooser .content-pane,
#NautilusFileChooser .content-pane:backdrop,
.nautilus-file-chooser .content-pane,
.nautilus-file-chooser .content-pane:backdrop,
.nautilus-list-view,
.nautilus-grid-view,
.nautilus-network-view,
columnview,
columnview.view,
listview,
gridview,
.view,
.view:backdrop,
window.background.csd > contents > leaflet.unfolded > box > stack.background,
window.background.csd > widget > leaflet.unfolded > box > stack.background,
window.background > contents > toastoverlay > leaflet > box,
window.background > widget > toastoverlay > leaflet > box {
  background-color: @view_bg_color;
  color: @view_fg_color;
}

/* Nautilus columnview header buttons & pathbar */
columnview.view > header > button,
columnview.view > header > button:backdrop,
.nautilus-window columnview.view > header > button,
.nautilus-window columnview.view > header > button:backdrop {
  background-color: transparent;
  color: @headerbar_fg_color;
  border-color: @headerbar_border_color;
}

columnview.view > header > button:hover,
columnview.view > header > button:active,
.nautilus-window columnview.view > header > button:hover,
.nautilus-window columnview.view > header > button:active {
  background-color: alpha(currentColor, 0.08);
  color: @headerbar_fg_color;
}

/* Nautilus pathbar and path buttons */
.nautilus-pathbar,
#NautilusPathBar,
nautilus-path-bar {
  background-color: alpha(currentColor, 0.08);
  color: @headerbar_fg_color;
  border-radius: 9999px;
  border: none;
  box-shadow: none;
}

.nautilus-pathbar scrolledwindow,
.nautilus-pathbar scrolledwindow.view,
.nautilus-pathbar scrolledwindow viewport,
.nautilus-pathbar > scrolledwindow,
.nautilus-pathbar > scrolledwindow > viewport,
.nautilus-pathbar box,
.nautilus-pathbar menubutton,
.nautilus-pathbar menubutton > button,
.nautilus-window .nautilus-pathbar scrolledwindow,
.nautilus-window .nautilus-pathbar scrolledwindow viewport,
.nautilus-window .nautilus-pathbar button,
.nautilus-window .nautilus-pathbar .nautilus-path-button,
.nautilus-window .content-pane .nautilus-pathbar scrolledwindow,
.nautilus-window .content-pane .nautilus-pathbar scrolledwindow viewport,
#NautilusPathBar scrolledwindow,
#NautilusPathBar scrolledwindow viewport,
#NautilusPathBar box,
#NautilusPathBar menubutton,
#NautilusPathBar menubutton > button,
nautilus-path-bar scrolledwindow,
nautilus-path-bar scrolledwindow viewport,
nautilus-path-bar button,
.nautilus-pathbar button,
.nautilus-pathbar button:backdrop,
.nautilus-pathbar .nautilus-path-button,
.nautilus-pathbar .nautilus-path-button:backdrop,
.nautilus-pathbar .nautilus-path-button.current-dir,
.nautilus-pathbar .nautilus-path-button.current-dir:backdrop,
#NautilusPathBar button,
#NautilusPathBar button:backdrop,
#NautilusPathBar #NautilusPathButton,
#NautilusPathBar #NautilusPathButton:backdrop,
#NautilusPathBar #NautilusPathButton.current-dir,
#NautilusPathBar #NautilusPathButton.current-dir:backdrop,
#NautilusPathBar .nautilus-path-button,
#NautilusPathBar .nautilus-path-button:backdrop,
#NautilusPathBar .nautilus-path-button.current-dir,
#NautilusPathBar .nautilus-path-button.current-dir:backdrop {
  background: transparent;
  background-color: transparent;
  background-image: none;
  box-shadow: none;
  border: none;
  color: @headerbar_fg_color;
}

.nautilus-pathbar button:hover,
.nautilus-pathbar .nautilus-path-button:hover,
#NautilusPathBar button:hover,
#NautilusPathBar #NautilusPathButton:hover,
#NautilusPathBar .nautilus-path-button:hover {
  background-color: alpha(currentColor, 0.08);
  color: @headerbar_fg_color;
  box-shadow: none;
}

.nautilus-pathbar button:active,
.nautilus-pathbar .nautilus-path-button:active,
#NautilusPathBar button:active,
#NautilusPathBar #NautilusPathButton:active,
#NautilusPathBar .nautilus-path-button:active {
  background-color: alpha(currentColor, 0.14);
  color: @headerbar_fg_color;
  box-shadow: none;
}

/* Sidebar selected row */
.navigation-sidebar > row:selected,
.navigation-sidebar:not(.view) > row:selected,
placessidebar .navigation-sidebar > row:selected,
.sidebar-pane placessidebar .navigation-sidebar:not(.view) > row:selected,
.sidebar-pane list.navigation-sidebar:not(.view) > row:selected,
.nautilus-window .sidebar-pane placessidebar .navigation-sidebar:not(.view) > row:selected {
  color: @accent_color;
  background-color: alpha(@accent_color, 0.18);
}

/* Splitbuttons, Linked Buttons and Toolbar Separators */
splitbutton separator,
headerbar splitbutton separator,
.linked separator,
button separator,
.linked > separator,
headerbar separator,
headerbar separator:backdrop {
  background-color: alpha(currentColor, 0.12);
  min-width: 1px;
}

overlay-split-view > separator,
navigation-split-view > separator,
split-view > separator,
overlay-split-view > border,
navigation-split-view > border {
  background-color: transparent;
  background-image: none;
  border: none;
  box-shadow: none;
}

/* General Content Separators */
separator,
separator:backdrop {
  background-color: @headerbar_border_color;
}

/* ComboRow Dropdowns & Popovers (Generous width to prevent truncated text) */
row.combo popover > contents {
  min-width: 240px;
}

row.combo listview.inline {
  min-width: 110px;
}

/* ── Mak Flavor Popover & Dropdown Menu Styling ── */
popover,
popover:backdrop,
popover.menu,
popover.menu:backdrop,
popover.background,
popover.background:backdrop,
popover.menu.background,
popover.menu.background:backdrop,
window popover,
window.csd popover,
window.background.csd popover,
.menu.background,
menubutton > popover,
menubutton > popover.menu,
popover:focus,
popover:focus-visible,
popover:focus-within,
popover.menu:focus,
popover.menu:focus-visible,
popover.menu:focus-within {
  background-color: transparent;
  color: @popover_fg_color;
  border: none;
  outline: none;
  box-shadow: none;
}

popover > arrow,
popover > contents,
popover.menu > arrow,
popover.menu > contents,
popover.menu.background > contents {
  background-color: @popover_bg_color;
  background-image: none;
  color: @popover_fg_color;
  border: none;
  outline: none;
  border-radius: 12px;
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.35);
}

/* Tooltips and popups - strictly borderless */
tooltip,
.tooltip,
popover.tooltip,
popover.background.tooltip {
  border: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

/* Popover internal containers - strictly transparent so outer card background-color fills 100% seamlessly */
popover scrolledwindow,
popover viewport,
popover stack,
popover box,
popover list,
popover > contents scrolledwindow,
popover > contents viewport,
popover > contents stack,
popover > contents box,
popover > contents stack scrolledwindow > viewport,
popover > contents stack scrolledwindow:not(.view) > viewport,
popover.menu scrolledwindow,
popover.menu viewport,
popover.menu stack,
popover.menu box,
popover.menu > contents scrolledwindow,
popover.menu > contents viewport,
popover.menu > contents stack,
popover.menu > contents box,
popover.menu > contents stack scrolledwindow > viewport,
popover.menu > contents stack scrolledwindow:not(.view) > viewport {
  background-color: transparent;
  background-image: none;
  border: none;
  box-shadow: none;
}

popover modelbutton,
popover.menu modelbutton,
modelbutton.flat {
  color: @popover_fg_color;
  background-color: transparent;
  background-image: none;
  border-radius: 6px;
}

popover modelbutton:hover,
popover.menu modelbutton:hover,
popover.menu modelbutton:hover:focus,
modelbutton.flat:hover {
  background-color: alpha(currentColor, 0.08);
  color: @popover_fg_color;
}

popover modelbutton:selected,
popover modelbutton:selected:active,
popover.menu modelbutton:selected,
popover.menu modelbutton:selected:active,
modelbutton.flat:selected,
modelbutton.flat:active {
  background-color: @accent_bg_color;
  color: #ffffff;
}

popover modelbutton accelerator,
popover.menu modelbutton accelerator,
popover.menu accelerator {
  color: alpha(@popover_fg_color, 0.55);
}

popover separator,
popover.menu separator {
  background-color: @headerbar_border_color;
  margin: 4px 6px;
  min-height: 1px;
}

popover listview,
popover listview > row,
dropdown popover listview,
dropdown popover listview > row {
  color: @popover_fg_color;
  background-color: transparent;
  border-radius: 6px;
}

popover listview > row:hover,
dropdown popover listview > row:hover {
  background-color: alpha(currentColor, 0.08);
  color: @popover_fg_color;
}

popover listview > row:selected,
dropdown popover listview > row:selected {
  background-color: @accent_bg_color;
  color: #ffffff;
}

/* Dropdowns and Comboboxes */
dropdown,
combobox {
  color: @window_fg_color;
}

dropdown button.combo,
combobox button.combo,
dropdown > button,
combobox > button {
  color: @window_fg_color;
}

dropdown button.combo arrow,
combobox button.combo arrow {
  color: @window_fg_color;
}

headerbar dropdown button.combo,
headerbar combobox button.combo,
headerbar dropdown > button,
headerbar combobox > button {
  color: @headerbar_fg_color;
}

headerbar dropdown button.combo arrow,
headerbar combobox button.combo arrow {
  color: @headerbar_fg_color;
}

/* ── Mak Flavor Text Inputs, Entries & Searchbars ── */
entry,
spinbutton > text,
searchbar entry,
entry.search,
entry.location-entry {
  background-color: alpha(currentColor, 0.06);
  background-image: none;
  box-shadow: none;
  border: none;
  border-radius: 6px;
  color: @window_fg_color;
  caret-color: @accent_color;
}

entry placeholder,
spinbutton > text placeholder,
searchbar entry placeholder {
  color: @placeholder_text_color;
}

entry:focus,
entry:focus-within,
spinbutton > text:focus,
spinbutton > text:focus-within,
searchbar entry:focus,
searchbar entry:focus-within,
entry.search:focus,
entry.search:focus-within,
entry.location-entry:focus,
entry.location-entry:focus-within {
  background-color: alpha(currentColor, 0.09);
  background-image: none;
  border: none;
  box-shadow: 0 0 0 2px alpha(@accent_color, 0.35);
  color: @window_fg_color;
}

entry > text > selection,
spinbutton > text > selection,
searchbar entry > text > selection {
  background-color: alpha(@accent_color, 0.35);
  color: @window_fg_color;
}

/* Headerbar, Pathbar & Top-bar Entry overrides - clean, seamless, borderless & flavor-tinted */
headerbar entry,
headerbar entry:hover,
headerbar entry:backdrop,
.top-bar entry,
.top-bar entry:hover,
.top-bar entry:backdrop,
.nautilus-window headerbar entry,
.nautilus-window .top-bar entry,
.nautilus-pathbar,
#NautilusPathBar,
nautilus-path-bar,
.nautilus-pathbar:backdrop,
#NautilusPathBar:backdrop {
  background-color: alpha(currentColor, 0.08);
  background-image: none;
  box-shadow: none;
  border: none;
  color: @headerbar_fg_color;
  caret-color: @accent_color;
  border-radius: 9999px;
}

headerbar entry:focus,
headerbar entry:focus-within,
.top-bar entry:focus,
.top-bar entry:focus-within,
.nautilus-window headerbar entry:focus,
.nautilus-window headerbar entry:focus-within {
  background-color: alpha(currentColor, 0.11);
  background-image: none;
  border: none;
  box-shadow: 0 0 0 2px alpha(@accent_color, 0.35);
  color: @headerbar_fg_color;
}

headerbar entry placeholder,
.top-bar entry placeholder {
  color: alpha(@headerbar_fg_color, 0.5);
}

headerbar entry > text > selection,
.top-bar entry > text > selection {
  background-color: alpha(@accent_color, 0.35);
  color: @headerbar_fg_color;
}

/* Searchbars & Revealer Boxes */
searchbar,
searchbar > revealer > box,
searchbar:not(.inline) > revealer > box {
  background-color: @headerbar_bg_color;
  color: @headerbar_fg_color;
  border-color: @headerbar_border_color;
}

/* Dialogs, Sheets, and Modals */
dialog,
dialog.background,
dialog.background sheet,
dialog-host > dialog.background sheet {
  background-color: @dialog_bg_color;
  color: @dialog_fg_color;
  border-color: @headerbar_border_color;
}

/* GTK3 Menus & Menubars - Borderless & Clean */
menu,
menu:backdrop,
menubar > menu,
menubar > menu:backdrop,
.menu,
.menu:backdrop {
  background-color: @popover_bg_color;
  color: @popover_fg_color;
  border: none;
  outline: none;
  box-shadow: none;
}

menu menuitem,
menubar menuitem,
.menu menuitem {
  color: @popover_fg_color;
  background-color: transparent;
}

menu menuitem:hover,
menubar menuitem:hover,
.menu menuitem:hover {
  background-color: alpha(currentColor, 0.08);
  color: @popover_fg_color;
}

menu menuitem:selected,
menubar menuitem:selected,
.menu menuitem:selected {
  background-color: @accent_bg_color;
  color: #ffffff;
}

menu separator,
menubar separator,
.menu separator {
  background-color: @headerbar_border_color;
}

window.background > contents > toastoverlay > leaflet > box + separator + box,
window.background > widget > toastoverlay > leaflet > box + separator + box {
  background-color: @window_bg_color;
  color: @window_fg_color;
}

/* Explicit absolute suppression of popover and popup container wireframe borders */
popover,
popover:backdrop,
popover.menu,
popover.menu:backdrop,
popover.background,
popover.background:backdrop,
popover.menu.background,
popover.menu.background:backdrop,
popover:focus,
popover:focus-visible,
popover:focus-within,
popover.menu:focus,
popover.menu:focus-visible,
popover.menu:focus-within,
window popover,
window.csd popover,
window.background.csd popover,
.menu {
  border: none;
  outline: none;
  box-shadow: none;
}
"""
    parts.append(safe_surface_rules.strip())

    custom_rules = []
    # 1. Chromium headerbar accent
    if chromium_accent and chromium_accent != "default":
        acc_info = CHROMIUM_ACCENT_PALETTES.get(chromium_accent)
        if acc_info:
            color = acc_info["dark"] if is_dark else acc_info["light"]
            custom_rules.append(f"""
/* ── Mak Chromium Topbar Accent ─────────────────────────────────── */
window.background.chromium,
window.background.chromium headerbar.header-bar.titlebar,
window.background.chromium headerbar.titlebar {{
    background-color: {color};
}}
""")

    # 2. Button size and spacing (only if non-default)
    if (button_size and button_size != 14) or (button_spacing and button_spacing != 8):
        bs = button_size or 14
        sp = button_spacing or 8
        half_sp = sp // 2
        custom_rules.append(f"""
/* ── Mak Traffic Light Metrics ──────────────────────────────────── */
headerbar windowcontrols button.close,
headerbar windowcontrols button.maximize,
headerbar windowcontrols button.minimize,
windowcontrols button.close,
windowcontrols button.maximize,
windowcontrols button.minimize {{
    min-width: {bs}px;
    min-height: {bs}px;
    background-size: {bs}px {bs}px;
    margin: 0 {half_sp}px;
}}
""")

    if custom_rules:
        parts.append("/* ── Mak Dynamic Customizations ─────────────────────────────────── */\n" + "\n".join(custom_rules))

    final_content = "\n\n".join(parts) + "\n"

    os.makedirs(os.path.dirname(dst_css_path), exist_ok=True)
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
    is_amoled = "amoled" in theme_key

    try:
        res_flv = subprocess.run(["gsettings", "get", "org.gnome.shell.extensions.mak", "theme-flavor"],
                                 capture_output=True, text=True)
        flavor_key = res_flv.stdout.strip().strip("'\"")
        if not flavor_key or flavor_key not in THEME_FLAVORS:
            flavor_key = "default"
    except Exception:
        flavor_key = "default"

    palette_override = get_flavor_palette(flavor_key, is_dark, is_glassy=is_glassy, is_amoled=is_amoled)

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

def inject_shell_theme_contrast(theme_name, is_dark, is_amoled=False, css_path=None, flavor_key=None):
    if css_path is None:
        css_path = os.path.join(THEMES_DIR, theme_name, "gnome-shell", "gnome-shell.css")
    if not os.path.exists(css_path):
        return
    try:
        with open(css_path, "r", encoding="utf-8") as f:
            content = f.read()

        marker = "/* ── Mak Shell Contrast & Liquid Glass Refraction Tuning ── */"
        if marker in content:
            content = content.split(marker)[0].rstrip()

        popover_r = TokenManager.get("geometry", "popovers", "corner_radius", default=10)
        item_r = TokenManager.get("geometry", "menus", "item_radius", default=4)
        notif_r = TokenManager.get("geometry", "notifications", "corner_radius", default=16)
        btn_r = TokenManager.get("geometry", "buttons", "corner_radius", default=5)

        if flavor_key is None:
            try:
                res_flv = subprocess.run(["gsettings", "get", "org.gnome.shell.extensions.mak", "theme-flavor"], capture_output=True, text=True)
                flavor_key = res_flv.stdout.strip().strip("'\"")
                if not flavor_key or flavor_key not in THEME_FLAVORS:
                    flavor_key = "default"
            except Exception:
                flavor_key = "default"

        flv = THEME_FLAVORS.get(flavor_key, THEME_FLAVORS["default"])
        mode_dict = flv["dark"] if is_dark else flv["light"]

        if not is_dark:
            bg_color = hex_to_rgba(mode_dict.get("window_bg", "#ececf0"), 0.82)
            banner_bg = hex_to_rgba(mode_dict.get("card_bg", "#ffffff"), 0.86)
            border_color = mode_dict.get("border_color", "rgba(0, 0, 0, 0.08)")
            fg_color = mode_dict.get("window_fg", "#1d1d1f")
            hover_bg = hex_to_rgba(mode_dict.get("accent_color", "#000000"), 0.10)
            selected_acc = mode_dict.get("accent_color", "#007aff")
            shadow = "0 12px 32px rgba(0, 0, 0, 0.16)"
        else:
            raw_bg = mode_dict.get("window_bg", "#242426")
            raw_card = mode_dict.get("card_bg", "#2c2c2e")
            if is_amoled:
                raw_bg = deepen_hex(raw_bg, 0.3)
                raw_card = deepen_hex(raw_card, 0.5)
            bg_color = hex_to_rgba(raw_bg, 0.85 if is_amoled else 0.82)
            banner_bg = hex_to_rgba(raw_card, 0.88 if is_amoled else 0.86)
            border_color = mode_dict.get("border_color", "rgba(255, 255, 255, 0.08)")
            fg_color = mode_dict.get("window_fg", "#f5f5f7")
            hover_bg = hex_to_rgba(mode_dict.get("accent_color", "#ffffff"), 0.14)
            selected_acc = mode_dict.get("accent_color", "#007aff")
            shadow = "0 12px 32px rgba(0, 0, 0, 0.28)"

        block = f"""\n\n{marker}
.popup-menu-content {{
    background-color: {bg_color};
    color: {fg_color};
    border: 1px solid {border_color};
    box-shadow: {shadow};
    border-radius: {popover_r}px;
    padding: 6px;
}}

.popup-menu-item {{
    color: {fg_color};
    font-weight: 500;
    border-radius: {item_r}px;
    min-height: 24px;
    padding: 3px 10px;
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
    background-color: {selected_acc};
    color: #ffffff;
}}

.popup-menu-item:selected StLabel {{
    color: #ffffff;
}}

.notification-banner {{
    background-color: {banner_bg};
    color: {fg_color};
    border: 1px solid {border_color};
    border-radius: {notif_r}px;
    padding: 12px 14px;
    box-shadow: {shadow};
}}

.notification-banner StLabel {{
    color: {fg_color};
}}

.notification-banner .message,
.notification-banner .message-box,
.notification-banner .message-content,
.notification-banner .message-header,
.notification-banner .message-body,
.notification-banner .message-header-content,
.notification-banner .message-title,
.notification-banner StBoxLayout,
.notification-banner StBin {{
    background-color: transparent;
    background-image: none;
    border: none;
    box-shadow: none;
}}

.notification-banner .message-close-button,
.notification-banner .message .message-header .message-close-button {{
    background-color: transparent;
    border: none;
    box-shadow: none;
    border-radius: 9999px;
    padding: 2px;
    min-height: 18px;
    min-width: 18px;
    color: {fg_color};
    opacity: 0.65;
}}

.notification-banner .message-close-button:hover,
.notification-banner .message .message-header .message-close-button:hover {{
    background-color: {hover_bg};
    opacity: 1.0;
}}

.notification-button {{
    border-radius: {btn_r}px;
    min-height: 24px;
    padding: 2px 12px;
    font-weight: 500;
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

    try:
        res_flv = subprocess.run(["gsettings", "get", "org.gnome.shell.extensions.mak", "theme-flavor"],
                                 capture_output=True, text=True)
        flavor_key = res_flv.stdout.strip().strip("'\"")
        if not flavor_key or flavor_key not in THEME_FLAVORS:
            flavor_key = "default"
    except Exception:
        flavor_key = "default"

    # 2. GNOME Shell Theme
    try:
        inject_shell_theme_contrast(theme_name, is_dark=is_dark, is_amoled=is_amoled, flavor_key=flavor_key)
        subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.user-theme", "name", theme_name], check=True)
        log.append(f"Set GNOME Shell theme to '{theme_name}' and injected contrast styling.")
    except Exception as e:
        log.append(f"Error setting Shell theme: {e}")

    # 3. GTK 4 / Libadwaita Configuration
    try:
        os.makedirs(GTK4_CONFIG, exist_ok=True)
        src_gtk4 = os.path.join(source_dir, "gtk-4.0")
        palette_override = get_flavor_palette(flavor_key, is_dark, is_glassy=theme_info["is_glassy"], is_amoled=is_amoled)

        is_glassy = theme_info["is_glassy"]
        if is_glassy:
            try:
                subprocess.run(["dconf", "write", "/org/gnome/shell/extensions/blur-my-shell/applications/blur", "true"], check=False)
            except Exception:
                pass
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
        flv_dict = THEME_FLAVORS.get(flavor_key, THEME_FLAVORS["default"])
        flv_mode = flv_dict["dark"] if is_dark else flv_dict["light"]
        dock_pill = flv_mode.get("dock_pill", theme_info.get("dock_pill_color", "rgba(42, 42, 50, 0.40)"))
        dock_border = flv_mode.get("dock_border", theme_info.get("dock_border_color", "rgba(255, 255, 255, 0.28)"))
        app_tint = flv_mode.get("app_tint", "#242426" if is_dark else "#ececf0")
        subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.aqua-dock-pro", "pill-color", dock_pill], check=False)
        subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.aqua-dock-pro", "border-color", dock_border], check=False)
        subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.mak", "pill-color", dock_pill], check=False)
        subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.mak", "border-color", dock_border], check=False)
        subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.mak", "app-tint-color", app_tint], check=False)
        log.append(f"Updated dock pill color to '{dock_pill}', border to '{dock_border}', and app tint to '{app_tint}'.")
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

        new_val = f"{{'padding': <{{'left': uint32 0, 'right': 0, 'top': 0, 'bottom': 0}}>, 'keepRoundedCorners': <{{'maximized': true, 'fullscreen': false}}>, 'borderRadius': <uint32 16>, 'smoothing': <0.8>, 'borderColor': <{tuple_str}>, 'enabled': <true>}}"
        subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.rounded-window-corners-reborn", "global-rounded-corner-settings", new_val], check=False)
        subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.rounded-window-corners-reborn", "border-width", "1"], check=False)
        subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.rounded-window-corners-reborn", "skip-libadwaita-app", "false"], check=False)
        subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.rounded-window-corners-reborn", "skip-libhandy-app", "false"], check=False)
        subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.mak", "corner-border-color", w_border], check=False)
        subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.mak", "corner-border-width", "1"], check=False)
        subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.mak", "skip-libadwaita-app", "false"], check=False)
        subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.mak", "skip-libhandy-app", "false"], check=False)
        subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.mak", "unround-maximized", "false"], check=False)
        subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.mak", "corner-radius", "16"], check=False)
        log.append(f"Updated window corner settings (radius 16, smoothing 0.8, border-width 1, keep-maximized true, skip-libadwaita false).")
    except Exception as e:
        log.append(f"Error updating window corners border: {e}")

    # 9. Sync Application Translucency / Blur (Blur-my-shell & Liquid Glass)
    try:
        if is_glassy:
            app_radius = 14
            app_opacity = 0.85
            app_tint_color = '#ffffff'
            app_tint_strength = 0.05
            try:
                res_r = subprocess.run(["gsettings", "get", "org.gnome.shell.extensions.mak", "app-blur-radius"], capture_output=True, text=True)
                if res_r.returncode == 0 and res_r.stdout.strip().isdigit():
                    app_radius = int(res_r.stdout.strip())
            except Exception: pass
            try:
                res_o = subprocess.run(["gsettings", "get", "org.gnome.shell.extensions.mak", "app-opacity"], capture_output=True, text=True)
                if res_o.returncode == 0:
                    app_opacity = float(res_o.stdout.strip())
            except Exception: pass
            try:
                res_c = subprocess.run(["gsettings", "get", "org.gnome.shell.extensions.mak", "app-tint-color"], capture_output=True, text=True)
                if res_c.returncode == 0 and res_c.stdout.strip():
                    app_tint_color = res_c.stdout.strip().strip("'\"")
            except Exception: pass
            try:
                res_s = subprocess.run(["gsettings", "get", "org.gnome.shell.extensions.mak", "app-tint-strength"], capture_output=True, text=True)
                if res_s.returncode == 0:
                    app_tint_strength = float(res_s.stdout.strip())
            except Exception: pass
            app_refr = 0.50
            app_chroma = 0.20
            app_refl = 0.25
            try:
                res_lvl = subprocess.run(["gsettings", "get", "org.gnome.shell.extensions.mak", "app-glass-level"], capture_output=True, text=True)
                if res_lvl.returncode == 0:
                    app_refr = float(res_lvl.stdout.strip())
            except Exception: pass
            try:
                res_chr = subprocess.run(["gsettings", "get", "org.gnome.shell.extensions.mak", "app-chroma-strength"], capture_output=True, text=True)
                if res_chr.returncode == 0:
                    app_chroma = float(res_chr.stdout.strip())
            except Exception: pass
            try:
                res_ref = subprocess.run(["gsettings", "get", "org.gnome.shell.extensions.mak", "app-edge-reflection"], capture_output=True, text=True)
                if res_ref.returncode == 0:
                    app_refl = float(res_ref.stdout.strip())
            except Exception: pass

            raw_op = int(round(app_opacity * 255.0))
            disp_scale = max(1.0, app_refr * 32.0)
            subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.blur-my-shell.applications", "blur", "true"], check=False)
            subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.blur-my-shell.applications", "opacity", str(raw_op)], check=False)
            subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.blur-my-shell.applications", "sigma", str(app_radius)], check=False)
            subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.liquid-glass@thinkingcoding1231.gmail.com", "enable-application-glass", "true"], check=False)
            subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.liquid-glass@thinkingcoding1231.gmail.com", "application-glass-all-windows", "true"], check=False)
            subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.liquid-glass@thinkingcoding1231.gmail.com", "application-content-opacity", str(app_opacity)], check=False)
            subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.liquid-glass@thinkingcoding1231.gmail.com", "application-blur-radius", str(app_radius)], check=False)
            subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.liquid-glass@thinkingcoding1231.gmail.com", "application-tint-color", app_tint_color], check=False)
            subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.liquid-glass@thinkingcoding1231.gmail.com", "application-tint-strength", str(app_tint_strength)], check=False)
            subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.liquid-glass@thinkingcoding1231.gmail.com", "application-displacement-scale", str(disp_scale)], check=False)
            subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.liquid-glass@thinkingcoding1231.gmail.com", "application-chroma-strength", str(app_chroma)], check=False)
            subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.liquid-glass@thinkingcoding1231.gmail.com", "application-edge-reflection", str(app_refl)], check=False)
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


def apply_flavor(flavor_key):
    """
    Applies an aesthetic theme flavor palette across GTK 4, GTK 3, Shell, Dock, and Desktop accents.
    Changes ONLY colors; preserves 100% of widget elements, buttons, and geometry.
    """
    if flavor_key not in THEME_FLAVORS:
        flavor_key = "default"

    # Save to GSettings
    try:
        subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.mak", "theme-flavor", flavor_key], check=False)
    except Exception:
        pass

    theme_key = get_current_theme()
    theme_info = THEMES.get(theme_key, THEMES["dark"])
    is_dark = theme_info.get("is_dark", True)
    is_glassy = theme_info.get("is_glassy", False)
    is_amoled = "amoled" in theme_key

    # 1. Regenerate GTK 4 and GTK 3 stylesheets
    update_titlebar_buttons()

    # 2. Update Shell theme contrast styling
    try:
        inject_shell_theme_contrast(theme_info["theme_name"], is_dark=is_dark, is_amoled=is_amoled, flavor_key=flavor_key)
    except Exception as e:
        print(f"[ThemeManager] Error updating shell contrast for flavor: {e}")

    # 3. Update Dock and tint colors
    flv = THEME_FLAVORS[flavor_key]
    mode_dict = flv["dark"] if is_dark else flv["light"]

    dock_pill = mode_dict.get("dock_pill", theme_info.get("dock_pill_color", "rgba(42, 42, 50, 0.40)"))
    dock_border = mode_dict.get("dock_border", theme_info.get("dock_border_color", "rgba(255, 255, 255, 0.28)"))
    app_tint = mode_dict.get("app_tint", mode_dict.get("window_bg", "#242426"))
    gnome_accent = mode_dict.get("gnome_accent", "purple")

    try:
        subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.mak", "pill-color", dock_pill], check=False)
        subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.aqua-dock-pro", "pill-color", dock_pill], check=False)
        subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.mak", "border-color", dock_border], check=False)
        subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.aqua-dock-pro", "border-color", dock_border], check=False)
        subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.mak", "app-tint-color", app_tint], check=False)
        subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.mak", "dock-tint-color", app_tint], check=False)
        subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.mak", "topbar-tint-color", app_tint], check=False)
    except Exception as e:
        print(f"[ThemeManager] Error updating dock/tint colors: {e}")

    # 4. Update GNOME desktop interface accent
    if gnome_accent:
        try:
            subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "accent-color", gnome_accent], check=False)
        except Exception:
            pass

    return {"success": True, "flavor": flavor_key}


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

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    repo_themes = os.path.join(repo_root, "themes")
    target_dirs = [THEMES_DIR]
    if os.path.exists(repo_themes):
        target_dirs.append(repo_themes)

    for target_dir in target_dirs:
        for key, info in THEMES.items():
            theme_name = info["theme_name"]
            is_glassy = info["is_glassy"]
            is_dark = info["is_dark"]
            palette = palette_map.get(key, GRAPHITE_PALETTE_OVERRIDE)
            source_dir = os.path.join(target_dir, theme_name)
            if not os.path.exists(source_dir):
                continue
            for gver in ["gtk-4.0", "gtk-3.0"]:
                gdir = os.path.join(source_dir, gver)
                if not os.path.exists(gdir):
                    continue
                for css_file in ["gtk.css", "gtk-dark.css"]:
                    src_css = os.path.join(gdir, css_file)
                    base_css = src_css + ".base"
                    read_src = base_css if os.path.exists(base_css) else src_css
                    if os.path.exists(read_src):
                        inject_theme_css(read_src, src_css, palette, is_glassy, button_size, button_spacing, chromium_accent=chromium_accent, is_dark=is_dark)

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

        # Stage and inject shell theme contrast
        d_shell_css = os.path.join(dst_tdir, "gnome-shell", "gnome-shell.css")
        if os.path.exists(d_shell_css):
            inject_shell_theme_contrast(tname, is_dark, is_amoled=info.get("is_amoled", False), css_path=d_shell_css)

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

