# SPDX-License-Identifier: GPL-3.0-or-later
# Mak Settings Bridge: Unified Configuration Hub for Mak macOS Suite
# Connects the GTK 4 Control Center to Mak's unified schema and active Shell runtime.

import os
import re
import json
import subprocess
import gi

gi.require_version('Gio', '2.0')
gi.require_version('GLib', '2.0')
from gi.repository import Gio, GLib

HOME = os.path.expanduser("~")

def load_settings(schema_id, rel_dir=None):
    """Safely loads a Gio.Settings instance from local extension schema directories or system."""
    search_dirs = []
    if rel_dir:
        search_dirs.append(os.path.join(HOME, ".local/share/gnome-shell/extensions", rel_dir, "schemas"))
    search_dirs.append(os.path.join(os.path.dirname(__file__), "..", "mak-extension", "schemas"))
    search_dirs.append(os.path.join(HOME, ".local/share/gnome-shell/extensions/mak@local/schemas"))

    for d in search_dirs:
        d = os.path.abspath(d)
        if os.path.exists(d):
            try:
                src = Gio.SettingsSchemaSource.new_from_directory(d, None, False)
                s = src.lookup(schema_id, False)
                if s:
                    return Gio.Settings.new_full(s, None, None)
            except Exception:
                pass

    try:
        default_src = Gio.SettingsSchemaSource.get_default()
        if default_src and default_src.lookup(schema_id, True):
            return Gio.Settings.new(schema_id)
    except Exception:
        pass

    return None

class MakSettingsBridge:
    def __init__(self):
        self.mak = load_settings("org.gnome.shell.extensions.mak")
        self.dock = load_settings("org.gnome.shell.extensions.aqua-dock-pro", "aqua-dock-pro@shaque")
        self.corners = load_settings("org.gnome.shell.extensions.rounded-window-corners-reborn", "rounded-window-corners@fxgn")
        self.gaps = load_settings("org.gnome.shell.extensions.window-gap", "window-gap@amirhosseinkarimi.github.io")
        self.spotlight = load_settings("org.gnome.shell.extensions.superbar", "superbar@Furkan-rgb.github.io")
        self.topbar = load_settings("org.gnome.shell.extensions.kiwimenu", "kiwi-menu")
        self.blur = load_settings("org.gnome.shell.extensions.blur-my-shell", "blur-my-shell")
        self.bms_panel = load_settings("org.gnome.shell.extensions.blur-my-shell.panel")
        self.bms_popup = load_settings("org.gnome.shell.extensions.blur-my-shell.popup")
        self.bms_apps = load_settings("org.gnome.shell.extensions.blur-my-shell.applications")
        self.bms_dock = load_settings("org.gnome.shell.extensions.blur-my-shell.dash-to-dock")
        self.liquid_glass = load_settings("org.gnome.shell.extensions.liquid-glass@thinkingcoding1231.gmail.com")

    # ── Safe Getter / Setter Utilities ─────────────────────────────────────
    @staticmethod
    def _has_key(settings, key):
        if not settings or not key:
            return False
        try:
            schema = settings.props.settings_schema
            return schema is not None and schema.has_key(key)
        except Exception:
            return False

    def _set_b(self, mak_key, comp_settings, comp_key, val):
        if self._has_key(self.mak, mak_key):
            try: self.mak.set_boolean(mak_key, bool(val))
            except Exception as e: print(f"[Bridge] Error setting mak {mak_key}: {e}")
        if self._has_key(comp_settings, comp_key):
            try: comp_settings.set_boolean(comp_key, bool(val))
            except Exception as e: print(f"[Bridge] Error setting comp {comp_key}: {e}")

    def _get_b(self, mak_key, comp_settings, comp_key, default=False):
        if self._has_key(self.mak, mak_key):
            try: return self.mak.get_boolean(mak_key)
            except Exception: pass
        if self._has_key(comp_settings, comp_key):
            try: return comp_settings.get_boolean(comp_key)
            except Exception: pass
        return default

    def _set_i(self, mak_key, comp_settings, comp_key, val):
        if self._has_key(self.mak, mak_key):
            try: self.mak.set_int(mak_key, int(val))
            except Exception as e: print(f"[Bridge] Error setting mak {mak_key}: {e}")
        if self._has_key(comp_settings, comp_key):
            try: comp_settings.set_int(comp_key, int(val))
            except Exception as e: print(f"[Bridge] Error setting comp {comp_key}: {e}")

    def _get_i(self, mak_key, comp_settings, comp_key, default=0):
        if self._has_key(self.mak, mak_key):
            try: return self.mak.get_int(mak_key)
            except Exception: pass
        if self._has_key(comp_settings, comp_key):
            try: return comp_settings.get_int(comp_key)
            except Exception: pass
        return default

    def _set_d(self, mak_key, comp_settings, comp_key, val):
        if self._has_key(self.mak, mak_key):
            try: self.mak.set_double(mak_key, float(val))
            except Exception as e: print(f"[Bridge] Error setting mak {mak_key}: {e}")
        if self._has_key(comp_settings, comp_key):
            try: comp_settings.set_double(comp_key, float(val))
            except Exception as e: print(f"[Bridge] Error setting comp {comp_key}: {e}")

    def _get_d(self, mak_key, comp_settings, comp_key, default=0.0):
        if self._has_key(self.mak, mak_key):
            try: return self.mak.get_double(mak_key)
            except Exception: pass
        if self._has_key(comp_settings, comp_key):
            try: return comp_settings.get_double(comp_key)
            except Exception: pass
        return default

    def _set_s(self, mak_key, comp_settings, comp_key, val):
        if self._has_key(self.mak, mak_key):
            try: self.mak.set_string(mak_key, str(val))
            except Exception as e: print(f"[Bridge] Error setting mak {mak_key}: {e}")
        if self._has_key(comp_settings, comp_key):
            try: comp_settings.set_string(comp_key, str(val))
            except Exception as e: print(f"[Bridge] Error setting comp {comp_key}: {e}")

    def _get_s(self, mak_key, comp_settings, comp_key, default=""):
        if self._has_key(self.mak, mak_key):
            try: return self.mak.get_string(mak_key)
            except Exception: pass
        if self._has_key(comp_settings, comp_key):
            try: return comp_settings.get_string(comp_key)
            except Exception: pass
        return default

    # ── 1. DOCK SETTINGS ───────────────────────────────────────────────────
    # Master switch
    def get_dock_enabled(self): return self._get_b("dock-enabled", None, None, True)
    def set_dock_enabled(self, v): self._set_b("dock-enabled", None, None, v)

    # Geometry & Layout
    def get_dock_position(self): return self._get_s("dock-position", self.dock, "dock-position", "bottom")
    def set_dock_position(self, v): self._set_s("dock-position", self.dock, "dock-position", v)

    def get_dock_alignment(self): return self._get_s("dock-alignment", self.dock, "dock-alignment", "center")
    def set_dock_alignment(self, v): self._set_s("dock-alignment", self.dock, "dock-alignment", v)

    def get_icon_size(self): return self._get_i("icon-size", self.dock, "icon-size", 60)
    def set_icon_size(self, v): self._set_i("icon-size", self.dock, "icon-size", v)

    def get_icon_spacing(self): return self._get_i("icon-spacing", self.dock, "icon-spacing", 12)
    def set_icon_spacing(self, v): self._set_i("icon-spacing", self.dock, "icon-spacing", v)

    def get_edge_margin(self): return self._get_i("edge-margin", self.dock, "edge-margin", 4)
    def set_edge_margin(self, v): self._set_i("edge-margin", self.dock, "edge-margin", v)

    def get_dock_scale(self): return self._get_d("dock-scale", self.dock, "dock-scale", 1.0)
    def set_dock_scale(self, v): self._set_d("dock-scale", self.dock, "dock-scale", v)

    def get_auto_shrink(self): return self._get_b("auto-shrink-to-fit", self.dock, "auto-shrink-to-fit", True)
    def set_auto_shrink(self, v): self._set_b("auto-shrink-to-fit", self.dock, "auto-shrink-to-fit", v)

    def get_multi_monitor(self): return self._get_b("multi-monitor", self.dock, "multi-monitor", False)
    def set_multi_monitor(self, v): self._set_b("multi-monitor", self.dock, "multi-monitor", v)

    def get_isolate_monitors(self): return self._get_b("isolate-monitors", self.dock, "isolate-monitors", False)
    def set_isolate_monitors(self, v): self._set_b("isolate-monitors", self.dock, "isolate-monitors", v)

    def get_isolate_workspaces(self): return self._get_b("isolate-workspaces", self.dock, "isolate-workspaces", False)
    def set_isolate_workspaces(self, v): self._set_b("isolate-workspaces", self.dock, "isolate-workspaces", v)

    # Magnification & Physics
    def get_magnification(self): return self._get_d("magnification", self.dock, "magnification", 2.6)
    def set_magnification(self, v): self._set_d("magnification", self.dock, "magnification", v)

    def get_zoom_range(self): return self._get_i("zoom-range", self.dock, "zoom-range", 100)
    def set_zoom_range(self, v): self._set_i("zoom-range", self.dock, "zoom-range", v)

    def get_magnification_curve(self): return self._get_d("magnification-curve", self.dock, "magnification-curve", 2.0)
    def set_magnification_curve(self, v): self._set_d("magnification-curve", self.dock, "magnification-curve", v)

    def get_animation_smoothness(self): return self._get_i("animation-smoothness", self.dock, "animation-smoothness", 50)
    def set_animation_smoothness(self, v): self._set_i("animation-smoothness", self.dock, "animation-smoothness", v)

    def get_spring_tension(self): return self._get_d("spring-tension", self.dock, "spring-tension", 1.0)
    def set_spring_tension(self, v): self._set_d("spring-tension", self.dock, "spring-tension", v)

    def get_spring_damping(self): return self._get_d("spring-damping", self.dock, "spring-damping", 0.50)
    def set_spring_damping(self, v): self._set_d("spring-damping", self.dock, "spring-damping", v)

    def get_hover_lift(self): return self._get_i("hover-lift", self.dock, "hover-lift", 20)
    def set_hover_lift(self, v): self._set_i("hover-lift", self.dock, "hover-lift", v)

    def get_bounce_height(self): return self._get_i("bounce-height", self.dock, "bounce-height", 70)
    def set_bounce_height(self, v): self._set_i("bounce-height", self.dock, "bounce-height", v)

    def get_bounce_decay(self): return self._get_d("bounce-decay", self.dock, "bounce-decay", 0.50)
    def set_bounce_decay(self, v): self._set_d("bounce-decay", self.dock, "bounce-decay", v)

    # Appearance & Glass Pill
    def get_dock_radius(self): return self._get_i("dock-radius", self.dock, "dock-radius", 25)
    def set_dock_radius(self, v): self._set_i("dock-radius", self.dock, "dock-radius", v)

    def get_dock_opacity(self): return self._get_d("background-opacity", self.dock, "background-opacity", 0.25)
    def set_dock_opacity(self, v): self._set_d("background-opacity", self.dock, "background-opacity", v)

    def get_global_opacity(self): return self._get_d("global-opacity", None, None, 0.5)
    def set_global_opacity(self, v): self._set_d("global-opacity", None, None, v)

    def get_pill_color(self): return self._get_s("pill-color", self.dock, "pill-color", "rgb(255,255,255)")
    def set_pill_color(self, v): self._set_s("pill-color", self.dock, "pill-color", v)

    def get_dock_border_width(self): return self._get_i("border-width", self.dock, "border-width", 2)
    def set_dock_border_width(self, v): self._set_i("border-width", self.dock, "border-width", v)

    def get_dock_border_color(self): return self._get_s("border-color", self.dock, "border-color", "rgba(255,255,255,0.16)")
    def set_dock_border_color(self, v): self._set_s("border-color", self.dock, "border-color", v)

    def get_pill_thickness(self): return self._get_i("pill-thickness", self.dock, "pill-thickness", 88)
    def set_pill_thickness(self, v): self._set_i("pill-thickness", self.dock, "pill-thickness", v)

    def get_pill_thickness_auto(self): return self._get_b("pill-thickness-auto", self.dock, "pill-thickness-auto", True)
    def set_pill_thickness_auto(self, v): self._set_b("pill-thickness-auto", self.dock, "pill-thickness-auto", v)

    def get_dock_edge_bending(self):
        return self._get_d("dock-edge-bending", None, None, 0.42)

    def set_dock_edge_bending(self, v):
        self._set_d("dock-edge-bending", None, None, v)
        try:
            scale = max(2.0, float(v) * 28.0)
            subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.liquid-glass@thinkingcoding1231.gmail.com", "glass-displacement-scale", str(round(scale, 2))], check=False)
        except Exception:
            pass

    def get_dock_glass_level(self):
        return self._get_d("dock-glass-level", None, None, 0.60)

    def set_dock_glass_level(self, v):
        self._set_d("dock-glass-level", None, None, v)
        try:
            blur_rad = max(1, round(float(v) * 28.0))
            max_z = max(10.0, float(v) * 120.0)
            ior = 1.4 + float(v) * 1.0
            tint_str = max(0.04, min(0.20, float(v) * 0.16))
            subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.liquid-glass@thinkingcoding1231.gmail.com", "dock-blur-radius", str(blur_rad)], check=False)
            subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.liquid-glass@thinkingcoding1231.gmail.com", "glass-max-z", str(round(max_z, 1))], check=False)
            subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.liquid-glass@thinkingcoding1231.gmail.com", "glass-ior", str(round(ior, 2))], check=False)
            subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.liquid-glass@thinkingcoding1231.gmail.com", "dock-tint-strength", str(round(tint_str, 2))], check=False)
        except Exception:
            pass

    # Autohide & Interactions
    def get_autohide_mode(self): return self._get_s("auto-hide-mode", self.dock, "auto-hide-mode", "dodge")
    def set_autohide_mode(self, v): self._set_s("auto-hide-mode", self.dock, "auto-hide-mode", v)

    def get_hide_delay(self): return self._get_i("hide-delay", self.dock, "hide-delay", 200)
    def set_hide_delay(self, v): self._set_i("hide-delay", self.dock, "hide-delay", v)

    def get_reveal_pressure(self): return self._get_i("reveal-pressure", self.dock, "reveal-pressure", 200)
    def set_reveal_pressure(self, v): self._set_i("reveal-pressure", self.dock, "reveal-pressure", v)

    def get_autohide_handle(self): return self._get_b("show-autohide-handle", self.dock, "show-autohide-handle", True)
    def set_autohide_handle(self, v): self._set_b("show-autohide-handle", self.dock, "show-autohide-handle", v)

    def get_pressure_sense(self): return self._get_b("pressure-sense", self.dock, "pressure-sense", False)
    def set_pressure_sense(self, v): self._set_b("pressure-sense", self.dock, "pressure-sense", v)

    def get_pressure_sensitivity(self): return self._get_d("pressure-sense-sensitivity", self.dock, "pressure-sense-sensitivity", 0.5)
    def set_pressure_sensitivity(self, v): self._set_d("pressure-sense-sensitivity", self.dock, "pressure-sense-sensitivity", v)

    def get_click_to_minimize(self): return self._get_b("click-to-minimize", self.dock, "click-to-minimize", True)
    def set_click_to_minimize(self, v): self._set_b("click-to-minimize", self.dock, "click-to-minimize", v)

    def get_left_click_action(self): return self._get_s("left-click-action", self.dock, "left-click-action", "smart")
    def set_left_click_action(self, v): self._set_s("left-click-action", self.dock, "left-click-action", v)

    def get_middle_click_action(self): return self._get_s("middle-click-action", self.dock, "middle-click-action", "new-window")
    def set_middle_click_action(self, v): self._set_s("middle-click-action", self.dock, "middle-click-action", v)

    def get_scroll_action(self): return self._get_s("scroll-action", self.dock, "scroll-action", "minimize-restore")
    def set_scroll_action(self, v): self._set_s("scroll-action", self.dock, "scroll-action", v)

    def get_drag_to_open(self): return self._get_b("drag-to-open", self.dock, "drag-to-open", True)
    def set_drag_to_open(self, v): self._set_b("drag-to-open", self.dock, "drag-to-open", v)

    # Indicators & Badges
    def get_indicator_style(self): return self._get_s("indicator-style", self.dock, "indicator-style", "glow-dots")
    def set_indicator_style(self, v): self._set_s("indicator-style", self.dock, "indicator-style", v)

    def get_indicator_size(self): return self._get_i("indicator-size", self.dock, "indicator-size", 5)
    def set_indicator_size(self, v): self._set_i("indicator-size", self.dock, "indicator-size", v)

    def get_indicator_color(self): return self._get_s("indicator-color", self.dock, "indicator-color", "#ffffff")
    def set_indicator_color(self, v): self._set_s("indicator-color", self.dock, "indicator-color", v)

    def get_show_window_count(self): return self._get_b("show-window-count", self.dock, "show-window-count", True)
    def set_show_window_count(self, v): self._set_b("show-window-count", self.dock, "show-window-count", v)

    def get_show_badges(self): return self._get_b("show-badges", self.dock, "show-badges", True)
    def set_show_badges(self, v): self._set_b("show-badges", self.dock, "show-badges", v)

    def get_badge_color(self): return self._get_s("badge-color", self.dock, "badge-color", "rgba(224,48,48,1.0)")
    def set_badge_color(self, v): self._set_s("badge-color", self.dock, "badge-color", v)

    # Items & Stacks
    def get_show_apps_button(self): return self._get_b("show-apps-button", self.dock, "show-apps-button", True)
    def set_show_apps_button(self, v): self._set_b("show-apps-button", self.dock, "show-apps-button", v)

    def get_show_trash(self): return self._get_b("show-trash", self.dock, "show-trash", True)
    def set_show_trash(self, v): self._set_b("show-trash", self.dock, "show-trash", v)

    def get_show_downloads(self): return self._get_b("show-downloads", self.dock, "show-downloads", True)
    def set_show_downloads(self, v): self._set_b("show-downloads", self.dock, "show-downloads", v)

    def get_downloads_view(self): return self._get_s("downloads-view", self.dock, "downloads-view", "fan")
    def set_downloads_view(self, v): self._set_s("downloads-view", self.dock, "downloads-view", v)

    def get_downloads_max_files(self): return self._get_i("downloads-max-files", self.dock, "downloads-max-files", 11)
    def set_downloads_max_files(self, v): self._set_i("downloads-max-files", self.dock, "downloads-max-files", v)

    def get_downloads_sort(self): return self._get_s("downloads-sort", self.dock, "downloads-sort", "newest")
    def set_downloads_sort(self, v): self._set_s("downloads-sort", self.dock, "downloads-sort", v)

    def get_show_mounted_devices(self): return self._get_b("show-mounted-devices", self.dock, "show-mounted-devices", True)
    def set_show_mounted_devices(self, v): self._set_b("show-mounted-devices", self.dock, "show-mounted-devices", v)

    def get_show_removable_devices(self): return self._get_b("show-removable-devices", self.dock, "show-removable-devices", True)
    def set_show_removable_devices(self, v): self._set_b("show-removable-devices", self.dock, "show-removable-devices", v)

    def get_show_network_devices(self): return self._get_b("show-network-devices", self.dock, "show-network-devices", True)
    def set_show_network_devices(self, v): self._set_b("show-network-devices", self.dock, "show-network-devices", v)

    # Previews & Genie
    def get_show_previews(self): return self._get_b("show-previews", self.dock, "show-previews", True)
    def set_show_previews(self, v): self._set_b("show-previews", self.dock, "show-previews", v)

    def get_preview_delay(self): return self._get_i("preview-delay", self.dock, "preview-delay", 600)
    def set_preview_delay(self, v): self._set_i("preview-delay", self.dock, "preview-delay", v)

    def get_preview_size(self): return self._get_i("preview-size", self.dock, "preview-size", 200)
    def set_preview_size(self, v): self._set_i("preview-size", self.dock, "preview-size", v)

    def get_preview_window_mode(self): return self._get_s("preview-window-mode", self.dock, "preview-window-mode", "hidden")
    def set_preview_window_mode(self, v): self._set_s("preview-window-mode", self.dock, "preview-window-mode", v)

    def get_preview_close_buttons(self): return self._get_b("preview-close-buttons", self.dock, "preview-close-buttons", False)
    def set_preview_close_buttons(self, v): self._set_b("preview-close-buttons", self.dock, "preview-close-buttons", v)

    def get_show_tooltip(self): return self._get_b("show-tooltip", self.dock, "show-tooltip", True)
    def set_show_tooltip(self, v): self._set_b("show-tooltip", self.dock, "show-tooltip", v)

    def get_tooltip_delay(self): return self._get_i("tooltip-delay", self.dock, "tooltip-delay", 25)
    def set_tooltip_delay(self, v): self._set_i("tooltip-delay", self.dock, "tooltip-delay", v)

    def get_enable_genie(self): return self._get_b("enable-genie-effect", self.dock, "enable-genie-effect", True)
    def set_enable_genie(self, v): self._set_b("enable-genie-effect", self.dock, "enable-genie-effect", v)

    def get_genie_duration(self): return self._get_i("genie-duration", self.dock, "genie-duration", 120)
    def set_genie_duration(self, v): self._set_i("genie-duration", self.dock, "genie-duration", v)


    # ── 2. TOP BAR & APPLE MENU SETTINGS ───────────────────────────────────
    def get_topbar_enabled(self): return self._get_b("topbar-enabled", None, None, True)
    def set_topbar_enabled(self, v): self._set_b("topbar-enabled", None, None, v)

    def get_apple_menu_enabled(self): return self._get_b("topbar-apple-menu", None, None, True)
    def set_apple_menu_enabled(self, v): self._set_b("topbar-apple-menu", None, None, v)

    def get_apple_icon(self):
        val = self._get_s("topbar-apple-icon", None, None, "apple")
        return val

    def set_apple_icon(self, v):
        self._set_s("topbar-apple-icon", None, None, v)
        if self.topbar:
            # Map name to kiwi icon integer index: apple=10, arch=3, fedora=1, debian=2, ubuntu=8, linux=9
            mapping = {"apple": 10, "arch": 3, "fedora": 1, "debian": 2, "ubuntu": 8, "linux": 9}
            try: self.topbar.set_int("icon", mapping.get(v, 10))
            except Exception: pass

    def get_app_title_enabled(self): return self._get_b("topbar-app-title", None, None, True)
    def set_app_title_enabled(self, v): self._set_b("topbar-app-title", None, None, v)

    def get_hide_activities(self):
        if self.topbar:
            try: return self.topbar.get_boolean("activity-menu-visibility")
            except Exception: pass
        return self._get_b("topbar-hide-activities", None, None, True)

    def set_hide_activities(self, v):
        self._set_b("topbar-hide-activities", self.topbar, "activity-menu-visibility", v)

    def get_macos_accelerators(self): return self._get_b("topbar-macos-accelerators", self.topbar, "macos-accelerators", True)
    def set_macos_accelerators(self, v): self._set_b("topbar-macos-accelerators", self.topbar, "macos-accelerators", v)

    def get_app_store_cmd(self): return self._get_s("topbar-app-store-command", self.topbar, "app-store-command", "gnome-software")
    def set_app_store_cmd(self, v): self._set_s("topbar-app-store-command", self.topbar, "app-store-command", v)

    def get_hide_lock_button(self): return self._get_b("topbar-hide-lock-button", self.topbar, "hide-lock-button", False)
    def set_hide_lock_button(self, v): self._set_b("topbar-hide-lock-button", self.topbar, "hide-lock-button", v)

    def get_hide_power_button(self): return self._get_b("topbar-hide-power-button", self.topbar, "hide-power-button", False)
    def set_hide_power_button(self, v): self._set_b("topbar-hide-power-button", self.topbar, "hide-power-button", v)

    def get_hide_settings_button(self): return self._get_b("topbar-hide-settings-button", self.topbar, "hide-settings-button", False)
    def set_hide_settings_button(self, v): self._set_b("topbar-hide-settings-button", self.topbar, "hide-settings-button", v)

    def get_topbar_blur(self): return self._get_b("topbar-blur", None, None, True)
    def set_topbar_blur(self, v): self._set_b("topbar-blur", None, None, v)

    def get_topbar_blur_radius(self): return self._get_i("topbar-blur-radius", None, None, 28)
    def set_topbar_blur_radius(self, v): self._set_i("topbar-blur-radius", None, None, v)

    def get_topbar_transparency(self): return self._get_d("topbar-transparency", None, None, 0.35)
    def set_topbar_transparency(self, v): self._set_d("topbar-transparency", None, None, v)

    def get_topbar_opaque(self): return self._get_b("topbar-opaque", None, None, False)
    def set_topbar_opaque(self, v): self._set_b("topbar-opaque", None, None, v)

    def get_topbar_pill_style(self): return self._get_b("topbar-pill-style", None, None, True)
    def set_topbar_pill_style(self, v): self._set_b("topbar-pill-style", None, None, v)

    def get_topbar_bluetooth_battery(self): return self._get_b("topbar-bluetooth-battery", None, None, True)
    def set_topbar_bluetooth_battery(self, v): self._set_b("topbar-bluetooth-battery", None, None, v)

    def get_topbar_media_pill(self): return self._get_b("topbar-media-pill", None, None, True)
    def set_topbar_media_pill(self, v): self._set_b("topbar-media-pill", None, None, v)

    def get_topbar_mak_menu(self): return self._get_b("topbar-mak-menu", None, None, True)
    def set_topbar_mak_menu(self, v): self._set_b("topbar-mak-menu", None, None, v)

    def get_topbar_clipboard(self): return self._get_b("topbar-clipboard", None, None, True)
    def set_topbar_clipboard(self, v): self._set_b("topbar-clipboard", None, None, v)

    def get_clipboard_history_size(self): return self._get_i("clipboard-history-size", None, None, 30)
    def set_clipboard_history_size(self, v): self._set_i("clipboard-history-size", None, None, int(v))

    def get_topbar_caffeine(self): return self._get_b("topbar-caffeine", None, None, True)
    def set_topbar_caffeine(self, v): self._set_b("topbar-caffeine", None, None, v)

    def get_topbar_scratchpad(self): return self._get_b("topbar-scratchpad", None, None, True)
    def set_topbar_scratchpad(self, v): self._set_b("topbar-scratchpad", None, None, v)

    def get_dynamic_island_enabled(self): return self._get_b("dynamic-island-enabled", None, None, False)
    def set_dynamic_island_enabled(self, v): self._set_b("dynamic-island-enabled", None, None, v)

    def get_battery_percentage_mode(self): return self._get_s("battery-percentage-mode", None, None, "inside")
    def set_battery_percentage_mode(self, v): self._set_s("battery-percentage-mode", None, None, str(v))

    def get_battery_colored(self): return self._get_b("battery-colored", None, None, True)
    def set_battery_colored(self, v): self._set_b("battery-colored", None, None, v)

    # Top Bar, Control Center & Menu Item Colors
    def get_topbar_text_color(self): return self._get_s("topbar-text-color", None, None, "#ffffff")
    def set_topbar_text_color(self, v): self._set_s("topbar-text-color", None, None, str(v))

    def get_topbar_icon_color(self): return self._get_s("topbar-icon-color", None, None, "#ffffff")
    def set_topbar_icon_color(self, v): self._set_s("topbar-icon-color", None, None, str(v))

    def get_control_center_text_color(self): return self._get_s("control-center-text-color", None, None, "#ffffff")
    def set_control_center_text_color(self, v): self._set_s("control-center-text-color", None, None, str(v))

    def get_control_center_icon_color(self): return self._get_s("control-center-icon-color", None, None, "#ffffff")
    def set_control_center_icon_color(self, v): self._set_s("control-center-icon-color", None, None, str(v))

    def get_menu_text_color(self): return self._get_s("menu-text-color", None, None, "#ffffff")
    def set_menu_text_color(self, v): self._set_s("menu-text-color", None, None, str(v))


    # ── 3. SPOTLIGHT SEARCH SETTINGS ───────────────────────────────────────
    def get_spotlight_enabled(self): return self._get_b("spotlight-enabled", None, None, True)
    def set_spotlight_enabled(self, v): self._set_b("spotlight-enabled", None, None, v)

    def get_spotlight_shortcut(self):
        if self.spotlight:
            try:
                arr = self.spotlight.get_strv("toggle-shortcut")
                if arr: return arr[0]
            except Exception: pass
        if self.mak:
            try:
                arr = self.mak.get_strv("spotlight-shortcut")
                if arr: return arr[0]
            except Exception: pass
        return "<Super>space"

    def set_spotlight_shortcut(self, v):
        arr = [v] if v else ["<Super>space"]
        if self.mak:
            try: self.mak.set_strv("spotlight-shortcut", arr)
            except Exception: pass
        if self.spotlight:
            try: self.spotlight.set_strv("toggle-shortcut", arr)
            except Exception: pass

    def get_spotlight_width(self): return self._get_i("spotlight-width", self.spotlight, "bar-width", 640)
    def set_spotlight_width(self, v): self._set_i("spotlight-width", self.spotlight, "bar-width", v)

    def get_spotlight_position(self): return self._get_s("spotlight-position", self.spotlight, "bar-position", "center")
    def set_spotlight_position(self, v): self._set_s("spotlight-position", self.spotlight, "bar-position", v)

    def get_spotlight_opacity(self): return self._get_i("spotlight-opacity", self.spotlight, "background-opacity", 90)
    def set_spotlight_opacity(self, v): self._set_i("spotlight-opacity", self.spotlight, "background-opacity", v)

    def get_spotlight_max_results(self): return self._get_i("spotlight-max-results", self.spotlight, "max-results", 8)
    def set_spotlight_max_results(self, v): self._set_i("spotlight-max-results", self.spotlight, "max-results", v)

    def get_spotlight_adaptive_ranking(self): return self._get_b("spotlight-adaptive-ranking", self.spotlight, "adaptive-ranking-enabled", True)
    def set_spotlight_adaptive_ranking(self, v): self._set_b("spotlight-adaptive-ranking", self.spotlight, "adaptive-ranking-enabled", v)

    def get_spotlight_search_engine(self): return self._get_s("spotlight-default-search-engine", self.spotlight, "default-search-engine", "google")
    def set_spotlight_search_engine(self, v): self._set_s("spotlight-default-search-engine", self.spotlight, "default-search-engine", v)

    def get_spotlight_search_apps(self): return self._get_b("spotlight-search-apps", self.spotlight, "applications-search-enabled", True)
    def set_spotlight_search_apps(self, v): self._set_b("spotlight-search-apps", self.spotlight, "applications-search-enabled", v)

    def get_spotlight_search_windows(self): return self._get_b("spotlight-search-windows", self.spotlight, "windows-search-enabled", True)
    def set_spotlight_search_windows(self, v): self._set_b("spotlight-search-windows", self.spotlight, "windows-search-enabled", v)

    def get_spotlight_search_files(self): return self._get_b("spotlight-search-files", self.spotlight, "files-search-enabled", True)
    def set_spotlight_search_files(self, v): self._set_b("spotlight-search-files", self.spotlight, "files-search-enabled", v)

    def get_spotlight_search_clipboard(self): return self._get_b("spotlight-search-clipboard", self.spotlight, "clipboard-search-enabled", True)
    def set_spotlight_search_clipboard(self, v): self._set_b("spotlight-search-clipboard", self.spotlight, "clipboard-search-enabled", v)

    def get_spotlight_search_calc(self): return self._get_b("spotlight-search-calc", self.spotlight, "calculator-search-enabled", True)
    def set_spotlight_search_calc(self, v): self._set_b("spotlight-search-calc", self.spotlight, "calculator-search-enabled", v)

    def get_spotlight_search_weather(self): return self._get_b("spotlight-search-weather", self.spotlight, "weather-search-enabled", True)
    def set_spotlight_search_weather(self, v): self._set_b("spotlight-search-weather", self.spotlight, "weather-search-enabled", v)

    def get_spotlight_search_dictionary(self): return self._get_b("spotlight-search-dictionary", self.spotlight, "dictionary-search-enabled", True)
    def set_spotlight_search_dictionary(self, v): self._set_b("spotlight-search-dictionary", self.spotlight, "dictionary-search-enabled", v)

    def get_spotlight_search_currency(self): return self._get_b("spotlight-search-currency", self.spotlight, "currency-search-enabled", True)
    def set_spotlight_search_currency(self, v): self._set_b("spotlight-search-currency", self.spotlight, "currency-search-enabled", v)

    def get_spotlight_search_actions(self): return self._get_b("spotlight-search-system-actions", self.spotlight, "system-actions-search-enabled", True)
    def set_spotlight_search_actions(self, v): self._set_b("spotlight-search-system-actions", self.spotlight, "system-actions-search-enabled", v)

    def get_spotlight_gnome_providers(self): return self._get_b("spotlight-gnome-search-providers", self.spotlight, "gnome-search-providers-enabled", True)
    def set_spotlight_gnome_providers(self, v): self._set_b("spotlight-gnome-search-providers", self.spotlight, "gnome-search-providers-enabled", v)


    # ── 4. WINDOW GAPS SETTINGS ────────────────────────────────────────────
    def get_gaps_enabled(self): return self._get_b("gaps-enabled", None, None, True)
    def set_gaps_enabled(self, v):
        self._set_b("gaps-enabled", None, None, v)
        if not v and self.gaps:
            try: self.gaps.set_int("gap-size", 0)
            except Exception: pass
        elif v and self.gaps:
            try: self.gaps.set_int("gap-size", self.get_gap_size())
            except Exception: pass

    def get_gap_uniform(self): return self._get_b("gap-uniform", self.gaps, "uniform", True)
    def set_gap_uniform(self, v): self._set_b("gap-uniform", self.gaps, "uniform", v)

    def get_gap_size(self): return self._get_i("gap-size", self.gaps, "gap-size", 12)
    def set_gap_size(self, v): self._set_i("gap-size", self.gaps, "gap-size", v)

    def get_gap_top(self): return self._get_i("gap-top", self.gaps, "margin-top", 12)
    def set_gap_top(self, v): self._set_i("gap-top", self.gaps, "margin-top", v)

    def get_gap_bottom(self): return self._get_i("gap-bottom", self.gaps, "margin-bottom", 12)
    def set_gap_bottom(self, v): self._set_i("gap-bottom", self.gaps, "margin-bottom", v)

    def get_gap_left(self): return self._get_i("gap-left", self.gaps, "margin-left", 12)
    def set_gap_left(self, v): self._set_i("gap-left", self.gaps, "margin-left", v)

    def get_gap_right(self): return self._get_i("gap-right", self.gaps, "margin-right", 12)
    def set_gap_right(self, v): self._set_i("gap-right", self.gaps, "margin-right", v)

    def get_gaps_maximized(self): return self._get_b("gaps-maximized", None, None, True)
    def set_gaps_maximized(self, v): self._set_b("gaps-maximized", None, None, v)


    # ── 5. ROUNDED CORNERS, BORDERS & SHADOWS ──────────────────────────────
    def _read_corners_dict(self):
        if self.corners:
            try:
                v = self.corners.get_value("global-rounded-corner-settings")
                if v: return v.unpack()
            except Exception: pass
        return {}

    def _write_corners_dict(self, d):
        if self.corners:
            try:
                cur = self._read_corners_dict()
                cur.update(d)
                variant_dict = {
                    'padding': GLib.Variant('a{su}', cur.get('padding', {'left': 1, 'right': 1, 'top': 1, 'bottom': 1})),
                    'keepRoundedCorners': GLib.Variant('a{sb}', cur.get('keepRoundedCorners', {'maximized': True, 'fullscreen': True})),
                    'borderRadius': GLib.Variant('u', int(cur.get('borderRadius', 16))),
                    'smoothing': GLib.Variant('d', float(cur.get('smoothing', 0.8))),
                    'borderColor': GLib.Variant('(dddd)', cur.get('borderColor', (0.55, 0.55, 0.60, 0.70))),
                    'enabled': GLib.Variant('b', bool(cur.get('enabled', True)))
                }
                self.corners.set_value('global-rounded-corner-settings', GLib.Variant('a{sv}', variant_dict))
            except Exception as e:
                print(f"[Bridge] Error updating corners GVariant: {e}")

    def get_corners_enabled(self):
        c = self._read_corners_dict()
        if 'enabled' in c: return c['enabled']
        return self._get_b("corners-enabled", None, None, True)

    def set_corners_enabled(self, v):
        self._set_b("corners-enabled", None, None, v)
        self._write_corners_dict({'enabled': bool(v)})

    def get_corner_radius(self):
        c = self._read_corners_dict()
        if 'borderRadius' in c: return int(c['borderRadius'])
        return self._get_i("corner-radius", None, None, 16)

    def set_corner_radius(self, v):
        self._set_i("corner-radius", None, None, v)
        self._write_corners_dict({'borderRadius': int(v)})

    def get_corner_smoothing(self):
        c = self._read_corners_dict()
        if 'smoothing' in c: return float(c['smoothing'])
        return self._get_d("corner-smoothing", None, None, 0.8)

    def set_corner_smoothing(self, v):
        self._set_d("corner-smoothing", None, None, v)
        self._write_corners_dict({'smoothing': float(v)})

    def get_corner_border_width(self): return self._get_i("corner-border-width", self.corners, "border-width", 1)
    def set_corner_border_width(self, v): self._set_i("corner-border-width", self.corners, "border-width", v)

    def get_corner_border_color(self):
        c = self._read_corners_dict()
        if 'borderColor' in c:
            bc = c['borderColor']
            if isinstance(bc, (list, tuple)) and len(bc) >= 3:
                r = int(round(float(bc[0]) * 255))
                g = int(round(float(bc[1]) * 255))
                b = int(round(float(bc[2]) * 255))
                a = round(float(bc[3]), 2) if len(bc) > 3 else 1.0
                return f"rgba({r},{g},{b},{a})"
        return self._get_s("corner-border-color", None, None, "rgba(255,255,255,0.18)")

    def set_corner_border_color(self, v):
        self._set_s("corner-border-color", None, None, str(v))
        rgba = [1.0, 1.0, 1.0, 0.18]
        try:
            m = re.match(r"rgba?\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)(?:\s*,\s*([\d.]+))?\)", str(v))
            if m:
                r = float(m.group(1)) / 255.0
                g = float(m.group(2)) / 255.0
                b = float(m.group(3)) / 255.0
                a = float(m.group(4)) if m.group(4) is not None else 1.0
                rgba = [round(max(0.0, min(1.0, x)), 3) for x in (r, g, b, a)]
        except Exception:
            pass
        self._write_corners_dict({'borderColor': tuple(rgba)})

    def get_titlebar_button_size(self): return self._get_i("titlebar-button-size", None, None, 14)
    def set_titlebar_button_size(self, v):
        self._set_i("titlebar-button-size", None, None, v)
        try:
            from .theme_manager import update_titlebar_buttons
            update_titlebar_buttons(button_size=v)
        except Exception:
            try:
                import theme_manager
                theme_manager.update_titlebar_buttons(button_size=v)
            except Exception:
                pass

    def get_titlebar_button_spacing(self): return self._get_i("titlebar-button-spacing", None, None, 8)
    def set_titlebar_button_spacing(self, v):
        self._set_i("titlebar-button-spacing", None, None, v)
        try:
            from .theme_manager import update_titlebar_buttons
            update_titlebar_buttons(button_spacing=v)
        except Exception:
            try:
                import theme_manager
                theme_manager.update_titlebar_buttons(button_spacing=v)
            except Exception:
                pass

    def get_chromium_topbar_accent(self): return self._get_s("chromium-topbar-accent", None, None, "default")
    def set_chromium_topbar_accent(self, v):
        self._set_s("chromium-topbar-accent", None, None, v)
        try:
            from .theme_manager import update_titlebar_buttons
            update_titlebar_buttons(chromium_accent=v)
        except Exception:
            try:
                import theme_manager
                theme_manager.update_titlebar_buttons(chromium_accent=v)
            except Exception:
                pass

    def get_system_accent_color(self):
        try:
            return Gio.Settings.new("org.gnome.desktop.interface").get_string("accent-color")
        except Exception:
            return "purple"

    def set_system_accent_color(self, v):
        try:
            Gio.Settings.new("org.gnome.desktop.interface").set_string("accent-color", str(v))
        except Exception as e:
            print(f"[Bridge] Error setting system accent-color: {e}")

    def get_unround_maximized(self): return self._get_b("unround-maximized", None, None, False)
    def set_unround_maximized(self, v):
        self._set_b("unround-maximized", None, None, v)
        c = self._read_corners_dict()
        k = c.get('keepRoundedCorners', {'maximized': True, 'fullscreen': True})
        k['maximized'] = not v
        self._write_corners_dict({'keepRoundedCorners': k})

    def get_skip_libadwaita(self): return self._get_b("skip-libadwaita-app", self.corners, "skip-libadwaita-app", False)
    def set_skip_libadwaita(self, v): self._set_b("skip-libadwaita-app", self.corners, "skip-libadwaita-app", v)

    def get_skip_libhandy(self): return self._get_b("skip-libhandy-app", self.corners, "skip-libhandy-app", False)
    def set_skip_libhandy(self, v): self._set_b("skip-libhandy-app", self.corners, "skip-libhandy-app", v)

    # Window Drop Shadows
    def _read_shadow(self, key_name):
        if self.corners:
            try:
                v = self.corners.get_value(key_name)
                if v: return v.unpack()
            except Exception: pass
        return {}

    def _write_shadow(self, key_name, d):
        if self.corners:
            try:
                cur = self._read_shadow(key_name)
                cur.update(d)
                self.corners.set_value(key_name, GLib.Variant('a{si}', {
                    'verticalOffset': int(cur.get('verticalOffset', 4)),
                    'horizontalOffset': int(cur.get('horizontalOffset', 0)),
                    'blurOffset': int(cur.get('blurOffset', 28)),
                    'spreadRadius': int(cur.get('spreadRadius', 4)),
                    'opacity': int(cur.get('opacity', 60))
                }))
            except Exception as e:
                print(f"[Bridge] Error writing shadow {key_name}: {e}")

    def get_shadow_enabled(self): return self._get_b("shadow-enabled", None, None, True)
    def set_shadow_enabled(self, v): self._set_b("shadow-enabled", None, None, v)

    def get_focused_shadow_v_offset(self):
        s = self._read_shadow("focused-shadow")
        return s.get("verticalOffset", self._get_i("focused-shadow-v-offset", None, None, 4))
    def set_focused_shadow_v_offset(self, v):
        self._set_i("focused-shadow-v-offset", None, None, v)
        self._write_shadow("focused-shadow", {"verticalOffset": int(v)})

    def get_focused_shadow_blur(self):
        s = self._read_shadow("focused-shadow")
        return s.get("blurOffset", self._get_i("focused-shadow-blur", None, None, 28))
    def set_focused_shadow_blur(self, v):
        self._set_i("focused-shadow-blur", None, None, v)
        self._write_shadow("focused-shadow", {"blurOffset": int(v)})

    def get_focused_shadow_opacity(self):
        s = self._read_shadow("focused-shadow")
        return s.get("opacity", self._get_i("focused-shadow-opacity", None, None, 60))
    def set_focused_shadow_opacity(self, v):
        self._set_i("focused-shadow-opacity", None, None, v)
        self._write_shadow("focused-shadow", {"opacity": int(v)})

    def get_unfocused_shadow_v_offset(self):
        s = self._read_shadow("unfocused-shadow")
        return s.get("verticalOffset", self._get_i("unfocused-shadow-v-offset", None, None, 2))
    def set_unfocused_shadow_v_offset(self, v):
        self._set_i("unfocused-shadow-v-offset", None, None, v)
        self._write_shadow("unfocused-shadow", {"verticalOffset": int(v)})

    def get_unfocused_shadow_blur(self):
        s = self._read_shadow("unfocused-shadow")
        return s.get("blurOffset", self._get_i("unfocused-shadow-blur", None, None, 12))
    def set_unfocused_shadow_blur(self, v):
        self._set_i("unfocused-shadow-blur", None, None, v)
        self._write_shadow("unfocused-shadow", {"blurOffset": int(v)})

    def get_unfocused_shadow_opacity(self):
        s = self._read_shadow("unfocused-shadow")
        return s.get("opacity", self._get_i("unfocused-shadow-opacity", None, None, 65))
    def set_unfocused_shadow_opacity(self, v):
        self._set_i("unfocused-shadow-opacity", None, None, v)
        self._write_shadow("unfocused-shadow", {"opacity": int(v)})


    # ── 6. BLUR ENGINE SETTINGS ────────────────────────────────────────────
    def get_blur_enabled(self): return self._get_b("blur-enabled", None, None, True)
    def set_blur_enabled(self, v): self._set_b("blur-enabled", None, None, v)

    def get_blur_sigma(self): return self._get_i("blur-sigma", self.blur, "sigma", 30)
    def set_blur_sigma(self, v):
        self._set_i("blur-sigma", self.blur, "sigma", v)
        if self.bms_panel:
            try: self.bms_panel.set_int("sigma", int(v))
            except Exception: pass
        if self.bms_popup:
            try: self.bms_popup.set_int("sigma", int(v))
            except Exception: pass

    def get_blur_brightness(self): return self._get_d("blur-brightness", self.blur, "brightness", 0.65)
    def set_blur_brightness(self, v):
        self._set_d("blur-brightness", self.blur, "brightness", v)
        if self.bms_panel:
            try: self.bms_panel.set_double("brightness", float(v))
            except Exception: pass
        if self.bms_popup:
            try: self.bms_popup.set_double("brightness", float(v))
            except Exception: pass

    def get_blur_noise_amount(self): return self._get_d("blur-noise-amount", self.blur, "noise-amount", 0.0)
    def set_blur_noise_amount(self, v): self._set_d("blur-noise-amount", self.blur, "noise-amount", v)

    def get_blur_panel(self): return self._get_b("blur-panel", None, None, True)
    def set_blur_panel(self, v): self._set_b("blur-panel", None, None, v)

    # ── DOCK LIQUID GLASS & BLUR CONTROLS ──
    def get_dock_liquid_glass(self):
        return self._get_b("dock-blur", self.liquid_glass, "enable-dock-glass", True)

    def set_dock_liquid_glass(self, v):
        self._set_b("dock-blur", self.liquid_glass, "enable-dock-glass", v)
        if self.dock and self._has_key(self.dock, "dock-blur"):
            try: self.dock.set_boolean("dock-blur", bool(v))
            except Exception: pass
        if self.bms_dock and self._has_key(self.bms_dock, "blur"):
            try: self.bms_dock.set_boolean("blur", bool(v))
            except Exception: pass

    def get_dock_blur(self):
        return self.get_dock_liquid_glass()

    def set_dock_blur(self, v):
        self.set_dock_liquid_glass(v)

    def get_dock_blur_radius(self):
        return self._get_i("dock-blur-radius", self.liquid_glass, "dock-blur-radius", 24)

    def set_dock_blur_radius(self, v):
        self._set_i("dock-blur-radius", self.liquid_glass, "dock-blur-radius", v)
        if self.bms_dock and self._has_key(self.bms_dock, "sigma"):
            try:
                self.bms_dock.set_boolean("customize", True)
                self.bms_dock.set_int("sigma", int(v))
            except Exception: pass

    def get_dock_tint_strength(self):
        return self._get_d("dock-tint-strength", self.liquid_glass, "dock-tint-strength", 0.12)

    def set_dock_tint_strength(self, v):
        self._set_d("dock-tint-strength", self.liquid_glass, "dock-tint-strength", v)

    def get_dock_tint_color(self):
        return self._get_s("dock-tint-color", self.liquid_glass, "dock-tint-color", "#ffffff")

    def set_dock_tint_color(self, v):
        self._set_s("dock-tint-color", self.liquid_glass, "dock-tint-color", v)

    def get_dock_corner_radius(self):
        return self._get_i("dock-corner-radius", self.dock, "dock-radius", 24)

    def set_dock_corner_radius(self, v):
        self._set_i("dock-corner-radius", self.dock, "dock-radius", v)
        self._set_i("dock-radius", None, None, v)
        if self.liquid_glass and self._has_key(self.liquid_glass, "dock-corner-radius"):
            try: self.liquid_glass.set_double("dock-corner-radius", float(v))
            except Exception: pass

    def get_dock_brightness(self):
        if self.liquid_glass and self._has_key(self.liquid_glass, "dock-brightness"):
            return self.liquid_glass.get_double("dock-brightness")
        return 1.0

    def set_dock_brightness(self, v):
        if self.liquid_glass and self._has_key(self.liquid_glass, "dock-brightness"):
            try: self.liquid_glass.set_double("dock-brightness", float(v))
            except Exception as e: print(f"[Bridge] Error setting dock-brightness: {e}")

    def get_dock_saturation(self):
        if self.liquid_glass and self._has_key(self.liquid_glass, "dock-saturation"):
            return self.liquid_glass.get_double("dock-saturation")
        return 1.08

    def set_dock_saturation(self, v):
        if self.liquid_glass and self._has_key(self.liquid_glass, "dock-saturation"):
            try: self.liquid_glass.set_double("dock-saturation", float(v))
            except Exception as e: print(f"[Bridge] Error setting dock-saturation: {e}")

    def get_dock_contrast(self):
        if self.liquid_glass and self._has_key(self.liquid_glass, "dock-contrast"):
            return self.liquid_glass.get_double("dock-contrast")
        return 1.06

    def set_dock_contrast(self, v):
        if self.liquid_glass and self._has_key(self.liquid_glass, "dock-contrast"):
            try: self.liquid_glass.set_double("dock-contrast", float(v))
            except Exception as e: print(f"[Bridge] Error setting dock-contrast: {e}")

    def get_blur_dock(self):
        return self.get_dock_liquid_glass()

    def set_blur_dock(self, v):
        self.set_dock_liquid_glass(v)

    def get_dock_blur_sigma(self):
        return self.get_dock_blur_radius()

    def set_dock_blur_sigma(self, v):
        self.set_dock_blur_radius(v)

    def get_blur_overview(self): return self._get_b("blur-overview", None, None, True)
    def set_blur_overview(self, v): self._set_b("blur-overview", None, None, v)

    def get_blur_appfolder(self): return self._get_b("blur-appfolder", None, None, True)
    def set_blur_appfolder(self, v): self._set_b("blur-appfolder", None, None, v)

    def get_blur_liquid_glass(self): return self._get_b("blur-liquid-glass", None, None, True)
    def set_blur_liquid_glass(self, v): self._set_b("blur-liquid-glass", None, None, v)

    def get_blur_refraction_strength(self): return self._get_d("blur-refraction-strength", None, None, 0.42)
    def set_blur_refraction_strength(self, v): self._set_d("blur-refraction-strength", None, None, v)

    def get_blur_chromatic_dispersion(self): return self._get_d("blur-chromatic-dispersion", None, None, 0.08)
    def set_blur_chromatic_dispersion(self, v): self._set_d("blur-chromatic-dispersion", None, None, v)

    def get_blur_applications(self):
        return self._get_b("blur-applications", self.liquid_glass, "enable-application-glass", True)

    def set_blur_applications(self, v):
        self._set_b("blur-applications", self.liquid_glass, "enable-application-glass", v)
        if self.liquid_glass and self._has_key(self.liquid_glass, "application-glass-all-windows"):
            try:
                self.liquid_glass.set_boolean("application-glass-all-windows", v)
            except Exception: pass
        if self.bms_apps and self._has_key(self.bms_apps, "blur"):
            try:
                self.bms_apps.set_boolean("blur", v)
            except Exception: pass
        if self.bms and self._has_key(self.bms, "hacks-level"):
            try:
                self.bms.set_int("hacks-level", 2)
            except Exception: pass

    def get_app_blur_radius(self):
        return self._get_i("app-blur-radius", self.liquid_glass, "application-blur-radius", 14)

    def set_app_blur_radius(self, v):
        self._set_i("app-blur-radius", self.liquid_glass, "application-blur-radius", int(v))
        if self.bms_apps and self._has_key(self.bms_apps, "sigma"):
            try:
                self.bms_apps.set_boolean("customize", True)
                self.bms_apps.set_int("sigma", int(v))
            except Exception: pass

    def get_app_opacity(self):
        return self._get_d("app-opacity", self.liquid_glass, "application-content-opacity", 0.85)

    def set_app_opacity(self, v):
        val = max(0.50, min(1.0, float(v)))
        raw = int(round(val * 255.0))
        raw = max(50, min(255, raw))
        self._set_d("app-opacity", self.liquid_glass, "application-content-opacity", val)
        if self.bms_apps and self._has_key(self.bms_apps, "opacity"):
            try: self.bms_apps.set_int("opacity", raw)
            except Exception as e: print(f"[Bridge] Error setting app opacity: {e}")

    def get_app_glass_level(self):
        return self._get_d("app-glass-level", None, None, 0.50)

    def set_app_glass_level(self, v):
        self._set_d("app-glass-level", None, None, float(v))

    def get_app_tint_color(self):
        return self._get_s("app-tint-color", self.liquid_glass, "application-tint-color", "#ffffff")

    def set_app_tint_color(self, v):
        self._set_s("app-tint-color", self.liquid_glass, "application-tint-color", v)

    def get_app_tint_strength(self):
        return self._get_d("app-tint-strength", self.liquid_glass, "application-tint-strength", 0.05)

    def set_app_tint_strength(self, v):
        self._set_d("app-tint-strength", self.liquid_glass, "application-tint-strength", float(v))

    def get_app_corner_radius(self):
        return self.get_corner_radius()

    def set_app_corner_radius(self, v):
        self.set_corner_radius(v)
        if self.liquid_glass and self._has_key(self.liquid_glass, "application-corner-radius"):
            try: self.liquid_glass.set_double("application-corner-radius", float(v))
            except Exception: pass
        if self.bms_apps and self._has_key(self.bms_apps, "corner-radius"):
            try: self.bms_apps.set_int("corner-radius", int(v))
            except Exception: pass

    # ── 7. UI & MENU STYLING (macOS Unified Design) ────────────────────────
    def get_menu_corner_radius(self): return self._get_i("menu-corner-radius", None, None, 16)
    def set_menu_corner_radius(self, v): self._set_i("menu-corner-radius", None, None, v)

    def get_menu_border_width(self): return self._get_i("menu-border-width", None, None, 1)
    def set_menu_border_width(self, v): self._set_i("menu-border-width", None, None, v)

    def get_menu_border_opacity(self): return self._get_d("menu-border-opacity", None, None, 0.18)
    def set_menu_border_opacity(self, v): self._set_d("menu-border-opacity", None, None, v)

    def get_menu_specular_highlight(self): return self._get_b("menu-specular-highlight", None, None, True)
    def set_menu_specular_highlight(self, v): self._set_b("menu-specular-highlight", None, None, v)

    def get_menu_bg_opacity(self): return self._get_d("menu-bg-opacity", None, None, 0.72)
    def set_menu_bg_opacity(self, v): self._set_d("menu-bg-opacity", None, None, v)

    def get_quick_settings_radius(self): return self._get_i("quick-settings-radius", None, None, 28)
    def set_quick_settings_radius(self, v): self._set_i("quick-settings-radius", None, None, v)

    def get_notification_radius(self): return self._get_i("notification-radius", None, None, 18)
    def set_notification_radius(self, v): self._set_i("notification-radius", None, None, v)

    # ── Quick Settings Individual Liquid Glass Pills Mode ──
    def get_quick_settings_pills_mode(self):
        if self.liquid_glass and self._has_key(self.liquid_glass, "quick-settings-apply-to"):
            return self.liquid_glass.get_int("quick-settings-apply-to") == 1
        return True

    def set_quick_settings_pills_mode(self, v):
        if self.liquid_glass and self._has_key(self.liquid_glass, "quick-settings-apply-to"):
            try: self.liquid_glass.set_int("quick-settings-apply-to", 1 if v else 0)
            except Exception as e: print(f"[Bridge] Error setting quick-settings-apply-to: {e}")

    def get_quick_settings_toggle_radius(self):
        if self.liquid_glass and self._has_key(self.liquid_glass, "quick-settings-toggle-corner-radius"):
            return self.liquid_glass.get_double("quick-settings-toggle-corner-radius")
        return 18.0

    def set_quick_settings_toggle_radius(self, v):
        if self.liquid_glass and self._has_key(self.liquid_glass, "quick-settings-toggle-corner-radius"):
            try: self.liquid_glass.set_double("quick-settings-toggle-corner-radius", float(v))
            except Exception as e: print(f"[Bridge] Error setting quick-settings-toggle-corner-radius: {e}")

    def get_quick_settings_toggle_tint(self):
        if self.liquid_glass and self._has_key(self.liquid_glass, "quick-settings-toggle-tint-strength"):
            return self.liquid_glass.get_double("quick-settings-toggle-tint-strength")
        return 0.50

    def set_quick_settings_toggle_tint(self, v):
        if self.liquid_glass and self._has_key(self.liquid_glass, "quick-settings-toggle-tint-strength"):
            try: self.liquid_glass.set_double("quick-settings-toggle-tint-strength", float(v))
            except Exception as e: print(f"[Bridge] Error setting quick-settings-toggle-tint-strength: {e}")

    def get_quick_settings_blur_radius(self):
        if self.liquid_glass and self._has_key(self.liquid_glass, "quick-settings-blur-radius"):
            return self.liquid_glass.get_int("quick-settings-blur-radius")
        return 18

    def set_quick_settings_blur_radius(self, v):
        if self.liquid_glass and self._has_key(self.liquid_glass, "quick-settings-blur-radius"):
            try: self.liquid_glass.set_int("quick-settings-blur-radius", int(v))
            except Exception as e: print(f"[Bridge] Error setting quick-settings-blur-radius: {e}")

    # ── Control Center / Quick Settings Glass & Tint ──
    def get_cc_blur(self):
        return self._get_b("control-center-blur", self.liquid_glass, "enable-quick-settings-glass", True)

    def set_cc_blur(self, v):
        self._set_b("control-center-blur", self.liquid_glass, "enable-quick-settings-glass", v)

    def get_cc_blur_radius(self):
        return self._get_i("control-center-blur-radius", self.liquid_glass, "quick-settings-blur-radius", 18)

    def set_cc_blur_radius(self, v):
        self._set_i("control-center-blur-radius", self.liquid_glass, "quick-settings-blur-radius", v)

    def get_cc_glass_level(self):
        return self._get_d("control-center-glass-level", None, None, 0.60)

    def set_cc_glass_level(self, v):
        self._set_d("control-center-glass-level", None, None, v)

    def get_cc_tint_color(self):
        return self._get_s("control-center-tint-color", self.liquid_glass, "quick-settings-tint-color", "#ffffff")

    def set_cc_tint_color(self, v):
        self._set_s("control-center-tint-color", self.liquid_glass, "quick-settings-tint-color", v)

    def get_cc_tint_strength(self):
        return self._get_d("control-center-tint-strength", self.liquid_glass, "quick-settings-tint-strength", 0.08)

    def set_cc_tint_strength(self, v):
        self._set_d("control-center-tint-strength", self.liquid_glass, "quick-settings-tint-strength", v)

    def get_cc_radius(self):
        return self.get_quick_settings_radius()

    def set_cc_radius(self, v):
        self.set_quick_settings_radius(v)
        if self.liquid_glass and self._has_key(self.liquid_glass, "quick-settings-corner-radius"):
            try: self.liquid_glass.set_double("quick-settings-corner-radius", float(v))
            except Exception: pass

    # ── Menus & Popups Glass & Tint ──
    def get_menu_blur(self):
        return self._get_b("menu-blur", self.liquid_glass, "enable-menu-glass", True)

    def set_menu_blur(self, v):
        self._set_b("menu-blur", self.liquid_glass, "enable-menu-glass", v)
        if self.liquid_glass and self._has_key(self.liquid_glass, "enable-extra-menu-glass"):
            try: self.liquid_glass.set_boolean("enable-extra-menu-glass", bool(v))
            except Exception: pass

    def get_menu_blur_radius(self):
        return self._get_i("menu-blur-radius", self.liquid_glass, "menu-blur-radius", 16)

    def set_menu_blur_radius(self, v):
        self._set_i("menu-blur-radius", self.liquid_glass, "menu-blur-radius", v)
        if self.liquid_glass and self._has_key(self.liquid_glass, "panel-menu-blur-radius"):
            try: self.liquid_glass.set_int("panel-menu-blur-radius", int(v))
            except Exception: pass

    def get_menu_glass_level(self):
        return self._get_d("menu-glass-level", None, None, 0.60)

    def set_menu_glass_level(self, v):
        self._set_d("menu-glass-level", None, None, v)

    def get_menu_tint_color(self):
        return self._get_s("menu-tint-color", self.liquid_glass, "menu-tint-color", "#ffffff")

    def set_menu_tint_color(self, v):
        self._set_s("menu-tint-color", self.liquid_glass, "menu-tint-color", v)
        if self.liquid_glass and self._has_key(self.liquid_glass, "panel-menu-tint-color"):
            try: self.liquid_glass.set_string("panel-menu-tint-color", str(v))
            except Exception: pass

    def get_menu_tint_strength(self):
        return self._get_d("menu-tint-strength", self.liquid_glass, "menu-tint-strength", 0.08)

    def set_menu_tint_strength(self, v):
        self._set_d("menu-tint-strength", self.liquid_glass, "menu-tint-strength", v)
        if self.liquid_glass and self._has_key(self.liquid_glass, "panel-menu-tint-strength"):
            try: self.liquid_glass.set_double("panel-menu-tint-strength", float(v))
            except Exception: pass

    # ── Desktop Context Menu Glass & Tint ──
    def get_desktop_menu_blur(self):
        return self._get_b("desktop-menu-blur", self.liquid_glass, "enable-desktop-menu-glass", True)

    def set_desktop_menu_blur(self, v):
        self._set_b("desktop-menu-blur", self.liquid_glass, "enable-desktop-menu-glass", v)

    def get_desktop_menu_blur_radius(self):
        return self._get_i("desktop-menu-blur-radius", self.liquid_glass, "desktop-menu-blur-radius", 16)

    def set_desktop_menu_blur_radius(self, v):
        self._set_i("desktop-menu-blur-radius", self.liquid_glass, "desktop-menu-blur-radius", v)

    def get_desktop_menu_glass_level(self):
        return self._get_d("desktop-menu-glass-level", None, None, 0.60)

    def set_desktop_menu_glass_level(self, v):
        self._set_d("desktop-menu-glass-level", None, None, v)

    def get_desktop_menu_tint_color(self):
        return self._get_s("desktop-menu-tint-color", self.liquid_glass, "desktop-menu-tint-color", "#ffffff")

    def set_desktop_menu_tint_color(self, v):
        self._set_s("desktop-menu-tint-color", self.liquid_glass, "desktop-menu-tint-color", v)

    def get_desktop_menu_tint_strength(self):
        return self._get_d("desktop-menu-tint-strength", self.liquid_glass, "desktop-menu-tint-strength", 0.08)

    def set_desktop_menu_tint_strength(self, v):
        self._set_d("desktop-menu-tint-strength", self.liquid_glass, "desktop-menu-tint-strength", v)

    # ── Top Bar Glass & Tint ──
    def get_topbar_tint_color(self):
        return self._get_s("topbar-tint-color", self.liquid_glass, "top-bar-tint-color", "#ffffff")

    def set_topbar_tint_color(self, v):
        self._set_s("topbar-tint-color", self.liquid_glass, "top-bar-tint-color", v)

    def get_topbar_tint_strength(self):
        return self._get_d("topbar-tint-strength", self.liquid_glass, "top-bar-tint-strength", 0.08)

    def set_topbar_tint_strength(self, v):
        self._set_d("topbar-tint-strength", self.liquid_glass, "top-bar-tint-strength", v)

    # ── 8. RESET TO MACOS PREFERRED DEFAULTS ───────────────────────────────
    def reset_to_macos_defaults(self):
        """Resets all settings across Dock, Top Bar, Spotlight, Window Gaps, Corners,
        Blur Engine, and Themes to the curated authentic macOS defaults."""
        import theme_manager

        # Dock
        self.set_dock_enabled(True)
        self.set_dock_position("bottom")
        self.set_dock_alignment("center")
        self.set_icon_size(60)
        self.set_icon_spacing(10)
        self.set_edge_margin(4)
        self.set_dock_scale(1.0)
        self.set_auto_shrink(True)
        self.set_magnification(2.6)
        self.set_zoom_range(110)
        self.set_magnification_curve(2.0)
        self.set_animation_smoothness(50)
        self.set_spring_tension(1.0)
        self.set_spring_damping(0.50)
        self.set_hover_lift(20)
        self.set_bounce_height(70)
        self.set_bounce_decay(0.70)
        self.set_dock_radius(25)
        self.set_dock_opacity(0.25)
        self.set_dock_border_width(1)
        self.set_dock_border_color("rgba(255, 255, 255, 0.22)")
        self.set_autohide_mode("dodge")
        self.set_blur_dock(True)
        self.set_genie_duration(320)

        # Top Bar
        self.set_topbar_enabled(True)
        self.set_apple_menu_enabled(True)
        self.set_apple_icon("apple")
        self.set_app_title_enabled(True)
        self.set_hide_activities(True)
        self.set_macos_accelerators(True)
        self.set_topbar_blur(True)
        self.set_topbar_blur_radius(28)
        self.set_topbar_transparency(0.30)
        self.set_topbar_pill_style(True)
        self.set_topbar_bluetooth_battery(True)
        self.set_topbar_media_pill(True)

        # Spotlight
        self.set_spotlight_enabled(True)
        self.set_spotlight_width(640)
        self.set_spotlight_position("center")
        self.set_spotlight_opacity(90)
        self.set_spotlight_max_results(8)
        self.set_spotlight_adaptive_ranking(True)
        self.set_spotlight_search_apps(True)
        self.set_spotlight_search_windows(True)
        self.set_spotlight_search_files(True)
        self.set_spotlight_search_calc(True)
        self.set_spotlight_search_weather(True)

        # Window Gaps
        self.set_gaps_enabled(True)
        self.set_gap_uniform(True)
        self.set_gap_size(12)
        self.set_gaps_maximized(True)

        # Window Corners & Shadows
        self.set_corners_enabled(True)
        self.set_corner_radius(16)
        self.set_corner_smoothing(0.8)
        self.set_corner_border_width(1)
        self.set_corner_border_color("rgba(255, 255, 255, 0.18)")
        self.set_unround_maximized(False)
        self.set_shadow_enabled(True)
        self.set_focused_shadow_v_offset(5)
        self.set_focused_shadow_blur(36)
        self.set_focused_shadow_opacity(45)
        self.set_unfocused_shadow_v_offset(2)
        self.set_unfocused_shadow_blur(18)
        self.set_unfocused_shadow_opacity(32)

        # Blur & Liquid Glass Refraction
        self.set_blur_enabled(True)
        self.set_blur_sigma(30)
        self.set_blur_brightness(0.70)
        self.set_blur_noise_amount(0.0)
        self.set_blur_panel(True)
        self.set_blur_dock(True)
        self.set_blur_overview(True)
        self.set_blur_appfolder(True)
        self.set_blur_liquid_glass(True)
        self.set_blur_refraction_strength(0.42)
        self.set_blur_chromatic_dispersion(0.08)

        # UI & Menus
        self.set_menu_corner_radius(14)
        self.set_menu_border_width(1)
        self.set_menu_border_opacity(0.18)
        self.set_menu_specular_highlight(True)
        self.set_menu_bg_opacity(0.72)
        self.set_quick_settings_radius(24)
        self.set_notification_radius(18)

        # Top Bar & Control Center Colors
        self.set_topbar_text_color("#ffffff")
        self.set_topbar_icon_color("#ffffff")
        self.set_control_center_text_color("#ffffff")
        self.set_control_center_icon_color("#ffffff")
        self.set_menu_text_color("#ffffff")

        # Surface Tint & Glass
        self.set_dock_tint_color("#ffffff")
        self.set_dock_tint_strength(0.12)
        self.set_dock_edge_bending(0.42)
        self.set_dock_glass_level(0.60)
        self.set_dock_blur_radius(24)
        self.set_dock_corner_radius(24)
        self.set_topbar_tint_color("#ffffff")
        self.set_topbar_tint_strength(0.08)
        self.set_topbar_text_color("#ffffff")
        self.set_topbar_icon_color("#ffffff")
        self.set_cc_blur(True)
        self.set_cc_blur_radius(18)
        self.set_cc_glass_level(0.60)
        self.set_cc_tint_color("#ffffff")
        self.set_cc_tint_strength(0.08)
        self.set_cc_radius(20)
        self.set_control_center_text_color("#ffffff")
        self.set_control_center_icon_color("#ffffff")
        self.set_menu_blur(True)
        self.set_menu_blur_radius(16)
        self.set_menu_glass_level(0.60)
        self.set_menu_tint_color("#ffffff")
        self.set_menu_tint_strength(0.08)
        self.set_menu_corner_radius(14)
        self.set_menu_text_color("#ffffff")
        self.set_desktop_menu_blur(True)
        self.set_desktop_menu_blur_radius(16)
        self.set_desktop_menu_glass_level(0.60)
        self.set_desktop_menu_tint_color("#ffffff")
        self.set_desktop_menu_tint_strength(0.08)

        # Dock Liquid Glass & Quick Settings Pills
        self.set_dock_liquid_glass(True)
        self.set_dock_brightness(1.0)
        self.set_dock_saturation(1.08)
        self.set_dock_contrast(1.06)
        self.set_quick_settings_pills_mode(True)
        self.set_quick_settings_toggle_radius(18.0)
        self.set_quick_settings_toggle_tint(0.50)

        # Reset Liquid Glass Dock Shadow to Soft Apple Diffusion
        try:
            subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.liquid-glass@thinkingcoding1231.gmail.com", "shadow-intensity", "0.12"], check=False)
            subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.liquid-glass@thinkingcoding1231.gmail.com", "shadow-radius", "70.0"], check=False)
            subprocess.run(["gsettings", "set", "org.gnome.shell.extensions.liquid-glass@thinkingcoding1231.gmail.com", "enable-desktop-menu-glass", "false"], check=False)
        except Exception:
            pass

        # Apply Current macOS Theme with updated widget overrides
        try:
            import theme_manager
            curr_th = theme_manager.get_current_theme() or "dark"
            theme_manager.apply_global_theme(curr_th)
        except Exception as e:
            print(f"[Bridge] Error resetting theme: {e}")

    def export_settings_json(self, filepath=None):
        """Exports the complete Mak desktop configuration across all schemas to a JSON file."""
        if not filepath:
            os.makedirs(os.path.join(HOME, ".config", "mak"), exist_ok=True)
            filepath = os.path.join(HOME, ".config", "mak", "mak_settings_export.json")

        schemas = [
            "org.gnome.shell.extensions.mak",
            "org.gnome.shell.extensions.aqua-dock-pro",
            "org.gnome.shell.extensions.rounded-window-corners-reborn",
            "org.gnome.shell.extensions.window-gap",
            "org.gnome.shell.extensions.superbar",
            "org.gnome.shell.extensions.kiwimenu",
            "org.gnome.shell.extensions.blur-my-shell",
            "org.gnome.shell.extensions.blur-my-shell.panel",
            "org.gnome.shell.extensions.blur-my-shell.popup",
            "org.gnome.shell.extensions.blur-my-shell.applications",
            "org.gnome.shell.extensions.blur-my-shell.dash-to-dock",
            "org.gnome.shell.extensions.liquid-glass@thinkingcoding1231.gmail.com",
            "org.gnome.desktop.interface",
        ]
        data = {}
        for schema in schemas:
            res = subprocess.run(["gsettings", "list-keys", schema], capture_output=True, text=True)
            if res.returncode != 0:
                continue
            keys = [k.strip() for k in res.stdout.strip().splitlines() if k.strip()]
            if not keys:
                continue
            data[schema] = {}
            for key in keys:
                if schema == "org.gnome.desktop.interface" and key not in (
                    "gtk-theme", "icon-theme", "cursor-theme", "color-scheme",
                    "font-name", "document-font-name", "monospace-font-name"
                ):
                    continue
                r = subprocess.run(["gsettings", "get", schema, key], capture_output=True, text=True)
                if r.returncode == 0:
                    data[schema][key] = r.stdout.strip()

        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return filepath, len(data.get("org.gnome.shell.extensions.mak", {}))

    def import_settings_json(self, filepath):
        """Imports Mak desktop configuration from a JSON file and applies it to active schemas."""
        if not os.path.exists(filepath):
            return False, 0
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"[Bridge] Error reading JSON: {e}")
            return False, 0

        applied_count = 0
        for schema, keys in data.items():
            if not isinstance(keys, dict):
                continue
            res = subprocess.run(["gsettings", "list-keys", schema], capture_output=True, text=True)
            if res.returncode != 0:
                continue
            valid_keys = set(res.stdout.strip().splitlines())
            for key, val in keys.items():
                if key in valid_keys:
                    val_str = str(val)
                    subprocess.run(["gsettings", "set", schema, key, val_str], check=False)
                    applied_count += 1

        # Re-initialize active Gio.Settings handles
        self.__init__()

        # Re-apply current theme
        try:
            import theme_manager
            curr_th = theme_manager.get_current_theme() or "dark"
            theme_manager.apply_global_theme(curr_th)
        except Exception as e:
            print(f"[Bridge] Theme reapply error: {e}")

        return True, applied_count

