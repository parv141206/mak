# SPDX-License-Identifier: GPL-3.0-or-later
# Mak Control Center: Unified macOS Experience Manager for GNOME
# Built with GTK 4, Libadwaita, and direct Gio/GSettings integration.

import os
import sys
import subprocess
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('Gio', '2.0')
from gi.repository import Gtk, Adw, Gio, GLib

from settings_bridge import MakSettingsBridge
import theme_manager

def create_spin_row(title, subtitle, lower, upper, step, val, digits=0, on_change=None):
    """Creates a smooth, reliable Adw.SpinRow with proper digits, step, page increment, and instant updates."""
    clean_val = round(float(val), digits) if digits > 0 else float(int(round(float(val))))
    clean_val = max(float(lower), min(float(upper), clean_val))
    adj = Gtk.Adjustment(
        value=clean_val,
        lower=float(lower),
        upper=float(upper),
        step_increment=float(step),
        page_increment=float(step * 5),
        page_size=0.0
    )
    row = Adw.SpinRow(title=title, subtitle=subtitle, adjustment=adj)
    row.set_digits(digits)
    row.set_numeric(True)
    row.set_snap_to_ticks(False)
    row.set_update_policy(Gtk.SpinButtonUpdatePolicy.ALWAYS)
    row.set_value(clean_val)
    if on_change:
        def _on_val_changed(r, _pspec):
            v = r.get_value()
            if digits == 0:
                on_change(int(round(v)))
            else:
                on_change(round(v, digits))
        row.connect("notify::value", _on_val_changed)
    return row

class MakAppWindow(Adw.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_title("Mak Control Center")
        self.set_default_size(980, 740)

        self.bridge = MakSettingsBridge()
        self._build_ui()

    def _build_ui(self):
        self.toast_overlay = Adw.ToastOverlay()
        self.set_content(self.toast_overlay)

        toolbar_view = Adw.ToolbarView()
        self.toast_overlay.set_child(toolbar_view)

        header = Adw.HeaderBar()
        title = Adw.WindowTitle(title="Mak", subtitle="macOS Desktop Suite")
        header.set_title_widget(title)

        reset_btn = Gtk.Button(label="Reset to Defaults")
        reset_btn.set_icon_name("edit-undo-symbolic")
        reset_btn.set_tooltip_text("Reset all settings across Mak to curated macOS authentic defaults")
        reset_btn.add_css_class("flat")
        reset_btn.connect("clicked", lambda *a: self._on_reset_to_defaults())
        header.pack_end(reset_btn)

        toolbar_view.add_top_bar(header)

        split_view = Adw.NavigationSplitView()
        split_view.set_min_sidebar_width(220)
        split_view.set_max_sidebar_width(280)
        toolbar_view.set_content(split_view)

        # Sidebar
        sidebar_page = Adw.NavigationPage(title="Navigation")
        sidebar_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        sidebar_box.set_margin_top(12)
        sidebar_box.set_margin_bottom(12)
        sidebar_box.set_margin_start(12)
        sidebar_box.set_margin_end(12)

        self.nav_list = Gtk.ListBox()
        self.nav_list.add_css_class("navigation-sidebar")
        sidebar_box.append(self.nav_list)
        sidebar_page.set_child(sidebar_box)
        split_view.set_sidebar(sidebar_page)

        # Content stack
        content_page = Adw.NavigationPage(title="Settings")
        self.stack = Adw.ViewStack()
        content_page.set_child(self.stack)
        split_view.set_content(content_page)

        # Build Comprehensive Settings Pages
        self._build_all_pages()

        self.nav_list.connect("row-selected", self._on_nav_selected)
        first_row = self.nav_list.get_row_at_index(0)
        if first_row:
            self.nav_list.select_row(first_row)

    def _build_all_pages(self):
        self._build_overview_page()
        self._build_dock_page()
        self._build_topbar_page()
        self._build_spotlight_page()
        self._build_windows_page()
        self._build_blur_page()
        self._build_theme_page()
        self._build_system_page()

    def _reload_all_pages(self):
        cur_tag = self.stack.get_visible_child_name()
        while child := self.stack.get_first_child():
            self.stack.remove(child)
        while row := self.nav_list.get_first_child():
            self.nav_list.remove(row)

        self._build_all_pages()

        if cur_tag:
            self.stack.set_visible_child_name(cur_tag)
            for i in range(8):
                row = self.nav_list.get_row_at_index(i)
                if row and getattr(row, "tag", None) == cur_tag:
                    self.nav_list.select_row(row)
                    break

    def _on_reset_to_defaults(self):
        self.bridge.reset_to_macos_defaults()
        self._reload_all_pages()
        toast = Adw.Toast.new("Restored authentic macOS recommended defaults across all systems!")
        toast.set_timeout(3)
        self.toast_overlay.add_toast(toast)

    def _add_nav_item(self, tag, title, icon_name):
        row = Adw.ActionRow(title=title)
        icon = Gtk.Image.new_from_icon_name(icon_name)
        row.add_prefix(icon)
        row.tag = tag
        self.nav_list.append(row)

    def _on_nav_selected(self, listbox, row):
        if row and hasattr(row, "tag"):
            self.stack.set_visible_child_name(row.tag)

    # ── 1. OVERVIEW & MAC EXPERIENCE ──────────────────────────────────────
    def _build_overview_page(self):
        page = Adw.PreferencesPage()
        self.stack.add_titled_with_icon(page, "overview", "Overview", "preferences-system-symbolic")
        self._add_nav_item("overview", "Overview", "preferences-system-symbolic")

        status_group = Adw.PreferencesGroup(title="macOS Desktop Suite Status")
        page.add(status_group)

        banner = Adw.Banner(title="All Mak systems are synchronized and running conflict-free.")
        banner.set_revealed(True)
        status_group.add(banner)

        master_switch = Adw.SwitchRow(
            title="Mak macOS Desktop Suite",
            subtitle="Unified engine powering Dock, Menu Bar, Spotlight, Window Gaps, and Corners"
        )
        master_switch.set_active(True)
        status_group.add(master_switch)

        presets_group = Adw.PreferencesGroup(
            title="Curated macOS Presets",
            description="Apply curated macOS desktop configurations in one click:"
        )
        page.add(presets_group)

        p1_row = Adw.ActionRow(
            title="Restore macOS Defaults",
            subtitle="Reset Dock, Menu Bar, Spotlight, Corners, Gaps, Liquid Glass, and Sonoma Graphite theme to optimal defaults"
        )
        btn1 = Gtk.Button(label="Reset Everything")
        btn1.add_css_class("suggested-action")
        btn1.add_css_class("pill")
        btn1.connect("clicked", lambda *a: self._on_reset_to_defaults())
        p1_row.add_suffix(btn1)
        presets_group.add(p1_row)

        comp_group = Adw.PreferencesGroup(title="Integrated Engines Status")
        page.add(comp_group)

        modules = [
            ("AquaDockPro Engine", "Dynamic spring magnification, genie minimization, fan stacks", self.bridge.get_dock_enabled, self.bridge.set_dock_enabled),
            ("Top Menu Bar and Island", "Apple menu, active app title, Bluetooth battery, and media pill", self.bridge.get_topbar_enabled, self.bridge.set_topbar_enabled),
            ("Spotlight Command Bar", "Fuzzy search, app indexing, math evaluations, and file queries", self.bridge.get_spotlight_enabled, self.bridge.set_spotlight_enabled),
            ("Window Management Gaps", "Dynamic outer screen padding on tiled and maximized windows", self.bridge.get_gaps_enabled, self.bridge.set_gaps_enabled),
            ("Continuous Rounded Corners", "GPU squircle anti-aliasing and depth shadows", self.bridge.get_corners_enabled, self.bridge.set_corners_enabled),
            ("Liquid Glass Blur Engine", "GPU-accelerated Snell-law refraction, dispersion, and Gaussian blur", self.bridge.get_blur_enabled, self.bridge.set_blur_enabled),
        ]

        for title, sub, getter, setter in modules:
            sw = Adw.SwitchRow(title=title, subtitle=sub)
            sw.set_active(getter())
            sw.connect("notify::active", lambda s, p, fn=setter: fn(s.get_active()))
            comp_group.add(sw)

    # ── 2. DOCK SETTINGS ──────────────────────────────────────────────────
    def _build_dock_page(self):
        page = Adw.PreferencesPage()
        self.stack.add_titled_with_icon(page, "dock", "Dock", "user-desktop-symbolic")
        self._add_nav_item("dock", "Dock", "user-desktop-symbolic")

        # Group: Master Switch
        top_group = Adw.PreferencesGroup(title="macOS Aqua Dock")
        page.add(top_group)

        dock_en = Adw.SwitchRow(title="Enable Aqua Dock", subtitle="Activate macOS-style floating dock")
        dock_en.set_active(self.bridge.get_dock_enabled())
        dock_en.connect("notify::active", lambda s, p: self.bridge.set_dock_enabled(s.get_active()))
        top_group.add(dock_en)

        # Group: Geometry & Alignment
        geom_group = Adw.PreferencesGroup(title="Dock Geometry and Layout")
        page.add(geom_group)

        pos_row = Adw.ComboRow(title="Screen Edge Position")
        pos_row.set_model(Gtk.StringList.new(["Bottom", "Left", "Right", "Top"]))
        cur_pos = self.bridge.get_dock_position()
        pos_map = {"bottom": 0, "left": 1, "right": 2, "top": 3}
        pos_row.set_selected(pos_map.get(cur_pos, 0))
        pos_row.connect("notify::selected", lambda r, p: self.bridge.set_dock_position(["bottom", "left", "right", "top"][r.get_selected()]))
        geom_group.add(pos_row)

        align_row = Adw.ComboRow(title="Alignment along Edge")
        align_row.set_model(Gtk.StringList.new(["Center", "Start", "End"]))
        cur_align = self.bridge.get_dock_alignment()
        align_idx = 0 if cur_align == "center" else (1 if cur_align == "start" else 2)
        align_row.set_selected(align_idx)
        align_row.connect("notify::selected", lambda r, p: self.bridge.set_dock_alignment(["center", "start", "end"][r.get_selected()]))
        geom_group.add(align_row)

        geom_group.add(create_spin_row("Resting Icon Size", "Base icon diameter in pixels", 24, 128, 4, self.bridge.get_icon_size(), digits=0, on_change=self.bridge.set_icon_size))
        geom_group.add(create_spin_row("Icon Spacing", "Horizontal gap between neighboring icons", 0, 48, 2, self.bridge.get_icon_spacing(), digits=0, on_change=self.bridge.set_icon_spacing))
        geom_group.add(create_spin_row("Edge Floating Margin", "Floating gap between dock and monitor edge", 0, 24, 1, self.bridge.get_edge_margin(), digits=0, on_change=self.bridge.set_edge_margin))
        geom_group.add(create_spin_row("Overall Dock Scale", "Scale multiplier for icons, padding, and pill", 0.5, 2.0, 0.05, self.bridge.get_dock_scale(), digits=2, on_change=self.bridge.set_dock_scale))

        shrink_row = Adw.SwitchRow(title="Auto Shrink to Fit", subtitle="Automatically downscale when dock would overflow display")
        shrink_row.set_active(self.bridge.get_auto_shrink())
        shrink_row.connect("notify::active", lambda s, p: self.bridge.set_auto_shrink(s.get_active()))
        geom_group.add(shrink_row)

        multi_mon = Adw.SwitchRow(title="Show Dock on All Monitors", subtitle="Render independent docks on every connected display")
        multi_mon.set_active(self.bridge.get_multi_monitor())
        multi_mon.connect("notify::active", lambda s, p: self.bridge.set_multi_monitor(s.get_active()))
        geom_group.add(multi_mon)

        iso_mon = Adw.SwitchRow(title="Isolate Monitors", subtitle="Only display running windows on that specific monitor's dock")
        iso_mon.set_active(self.bridge.get_isolate_monitors())
        iso_mon.connect("notify::active", lambda s, p: self.bridge.set_isolate_monitors(s.get_active()))
        geom_group.add(iso_mon)

        iso_ws = Adw.SwitchRow(title="Isolate Workspaces", subtitle="Only show running applications from active workspace")
        iso_ws.set_active(self.bridge.get_isolate_workspaces())
        iso_ws.connect("notify::active", lambda s, p: self.bridge.set_isolate_workspaces(s.get_active()))
        geom_group.add(iso_ws)

        # Group: Magnification & Physics
        phys_group = Adw.PreferencesGroup(title="Magnification and Physics Engine")
        page.add(phys_group)

        phys_group.add(create_spin_row("Peak Magnification Multiplier", "Peak magnification factor directly under cursor (e.g. 2.6x)", 1.0, 3.5, 0.1, self.bridge.get_magnification(), digits=1, on_change=self.bridge.set_magnification))
        phys_group.add(create_spin_row("Magnification Spread Radius", "Gaussian zoom propagation distance in pixels", 40, 500, 10, self.bridge.get_zoom_range(), digits=0, on_change=self.bridge.set_zoom_range))
        phys_group.add(create_spin_row("Magnification Curve Shape", "Sharpness of zoom falloff curve (higher = sharper peak)", 0.5, 5.0, 0.1, self.bridge.get_magnification_curve(), digits=1, on_change=self.bridge.set_magnification_curve))
        phys_group.add(create_spin_row("Spring Tension", "Physics stiffness for magnification and bounce animations", 0.1, 1.0, 0.05, self.bridge.get_spring_tension(), digits=2, on_change=self.bridge.set_spring_tension))
        phys_group.add(create_spin_row("Spring Damping", "Physics damping factor (1.0 = critically damped without overshoot)", 0.2, 1.0, 0.05, self.bridge.get_spring_damping(), digits=2, on_change=self.bridge.set_spring_damping))
        phys_group.add(create_spin_row("Hover Icon Lift", "Vertical displacement in pixels when hovered", 0, 24, 2, self.bridge.get_hover_lift(), digits=0, on_change=self.bridge.set_hover_lift))
        phys_group.add(create_spin_row("App Launch Bounce Height", "Peak launch bounce elevation in pixels (0 disables bounce)", 0, 80, 5, self.bridge.get_bounce_height(), digits=0, on_change=self.bridge.set_bounce_height))
        phys_group.add(create_spin_row("Bounce Decay Factor", "Energy retention per hop (higher = gentler, longer bounces)", 0.30, 0.95, 0.05, self.bridge.get_bounce_decay(), digits=2, on_change=self.bridge.set_bounce_decay))

        # Group: Glass Pill & Appearance
        pill_group = Adw.PreferencesGroup(title="Glass Pill and Surface Appearance")
        page.add(pill_group)

        pill_group.add(create_spin_row("Dock Pill Corner Radius", "Curvature rounding radius for dock background", 0, 40, 1, self.bridge.get_dock_radius(), digits=0, on_change=self.bridge.set_dock_radius))
        pill_group.add(create_spin_row("Glass Pill Opacity", "Background translucency factor (0 = fully transparent)", 0.0, 1.0, 0.05, self.bridge.get_dock_opacity(), digits=2, on_change=self.bridge.set_dock_opacity))
        pill_group.add(create_spin_row("Pill Border Outline Width", "Glass border stroke thickness in pixels", 0, 6, 1, self.bridge.get_dock_border_width(), digits=0, on_change=self.bridge.set_dock_border_width))

        thick_auto = Adw.SwitchRow(title="Auto Pill Thickness", subtitle="Scale pill height automatically with resting icon size")
        thick_auto.set_active(self.bridge.get_pill_thickness_auto())
        thick_auto.connect("notify::active", lambda s, p: self.bridge.set_pill_thickness_auto(s.get_active()))
        pill_group.add(thick_auto)

        pill_group.add(create_spin_row("Custom Pill Thickness", "Explicit dock pill depth when auto thickness is disabled", 36, 120, 4, self.bridge.get_pill_thickness(), digits=0, on_change=self.bridge.set_pill_thickness))

        # Group: Autohide & Pressure
        hide_group = Adw.PreferencesGroup(title="Autohide and Screen Edge Pressure")
        page.add(hide_group)

        hide_row = Adw.ComboRow(title="Autohide Behavior")
        hide_row.set_model(Gtk.StringList.new(["Never (Always Visible)", "Window Overlap (Intellihide)", "Always Autohide"]))
        cur_hide = self.bridge.get_autohide_mode()
        hide_idx = 0 if cur_hide == "never" else (1 if cur_hide == "dodge" else 2)
        hide_row.set_selected(hide_idx)
        hide_row.connect("notify::selected", lambda r, p: self.bridge.set_autohide_mode(["never", "dodge", "always"][r.get_selected()]))
        hide_group.add(hide_row)

        hide_group.add(create_spin_row("Autohide Delay", "Milliseconds before dock hides after pointer leaves", 0, 2000, 50, self.bridge.get_hide_delay(), digits=0, on_change=self.bridge.set_hide_delay))
        hide_group.add(create_spin_row("Edge Reveal Pressure", "Pressure barrier threshold in ms (0 = instant appearance)", 0, 1000, 25, self.bridge.get_reveal_pressure(), digits=0, on_change=self.bridge.set_reveal_pressure))

        handle_row = Adw.SwitchRow(title="Show Autohide Edge Handle", subtitle="Keep subtle dock glass border visible when hidden")
        handle_row.set_active(self.bridge.get_autohide_handle())
        handle_row.connect("notify::active", lambda s, p: self.bridge.set_autohide_handle(s.get_active()))
        hide_group.add(handle_row)

        dwell_row = Adw.SwitchRow(title="Pressure Sense Dwell", subtitle="Pointer must linger on screen edge before revealing")
        dwell_row.set_active(self.bridge.get_pressure_sense())
        dwell_row.connect("notify::active", lambda s, p: self.bridge.set_pressure_sense(s.get_active()))
        hide_group.add(dwell_row)

        # Group: Click Actions
        click_group = Adw.PreferencesGroup(title="Click and Interaction Actions")
        page.add(click_group)

        c2m = Adw.SwitchRow(title="Click Focused App to Minimize", subtitle="Clicking already focused app icon minimizes its windows")
        c2m.set_active(self.bridge.get_click_to_minimize())
        c2m.connect("notify::active", lambda s, p: self.bridge.set_click_to_minimize(s.get_active()))
        click_group.add(c2m)

        l_act = Adw.ComboRow(title="Primary Left Click Action")
        l_act.set_model(Gtk.StringList.new(["Smart Activate", "Minimize", "Cycle Windows", "Live Previews", "Do Nothing"]))
        cur_l = self.bridge.get_left_click_action()
        l_map = {"smart": 0, "minimize": 1, "cycle": 2, "preview": 3, "nothing": 4}
        l_act.set_selected(l_map.get(cur_l, 0))
        l_act.connect("notify::selected", lambda r, p: self.bridge.set_left_click_action(["smart", "minimize", "cycle", "preview", "nothing"][r.get_selected()]))
        click_group.add(l_act)

        m_act = Adw.ComboRow(title="Middle Click Action")
        m_act.set_model(Gtk.StringList.new(["New Window", "Smart Activate", "Do Nothing"]))
        cur_m = self.bridge.get_middle_click_action()
        m_map = {"new-window": 0, "smart": 1, "nothing": 2}
        m_act.set_selected(m_map.get(cur_m, 0))
        m_act.connect("notify::selected", lambda r, p: self.bridge.set_middle_click_action(["new-window", "smart", "nothing"][r.get_selected()]))
        click_group.add(m_act)

        s_act = Adw.ComboRow(title="Scroll Wheel Action")
        s_act.set_model(Gtk.StringList.new(["Minimize and Restore", "Cycle Windows", "Do Nothing"]))
        cur_s = self.bridge.get_scroll_action()
        s_map = {"minimize-restore": 0, "cycle": 1, "nothing": 2}
        s_act.set_selected(s_map.get(cur_s, 0))
        s_act.connect("notify::selected", lambda r, p: self.bridge.set_scroll_action(["minimize-restore", "cycle", "nothing"][r.get_selected()]))
        click_group.add(s_act)

        drag_row = Adw.SwitchRow(title="Drag Icon Outside to Launch", subtitle="Dragging an icon off dock launches it instantly")
        drag_row.set_active(self.bridge.get_drag_to_open())
        drag_row.connect("notify::active", lambda s, p: self.bridge.set_drag_to_open(s.get_active()))
        click_group.add(drag_row)

        # Group: Indicators & Badges
        ind_group = Adw.PreferencesGroup(title="Running Indicators and Notification Badges")
        page.add(ind_group)

        ind_style = Adw.ComboRow(title="Running Indicator Style")
        ind_style.set_model(Gtk.StringList.new(["Glow Dots", "Glowing Bar", "Single Dot", "Multiple Dots", "Solid Line", "Pill"]))
        cur_ind = self.bridge.get_indicator_style()
        ind_map = {"glow-dots": 0, "glow": 1, "dot": 2, "dots": 3, "line": 4, "pill": 5}
        ind_style.set_selected(ind_map.get(cur_ind, 0))
        ind_style.connect("notify::selected", lambda r, p: self.bridge.set_indicator_style(["glow-dots", "glow", "dot", "dots", "line", "pill"][r.get_selected()]))
        ind_group.add(ind_style)

        ind_group.add(create_spin_row("Indicator Dot Size", "Diameter in pixels", 3, 14, 1, self.bridge.get_indicator_size(), digits=0, on_change=self.bridge.set_indicator_size))

        win_cnt = Adw.SwitchRow(title="Show Multiple Window Dots", subtitle="Display multiple indicator dots when multiple windows are open")
        win_cnt.set_active(self.bridge.get_show_window_count())
        win_cnt.connect("notify::active", lambda s, p: self.bridge.set_show_window_count(s.get_active()))
        ind_group.add(win_cnt)

        badges_row = Adw.SwitchRow(title="Notification Badges", subtitle="Show unread message and notification counter over icons")
        badges_row.set_active(self.bridge.get_show_badges())
        badges_row.connect("notify::active", lambda s, p: self.bridge.set_show_badges(s.get_active()))
        ind_group.add(badges_row)

        # Group: Special Stacks & Items
        item_group = Adw.PreferencesGroup(title="Special Dock Stacks and Volumes")
        page.add(item_group)

        app_btn = Adw.SwitchRow(title="Show Applications Launcher Button", subtitle="Display Launchpad / App Grid button on the dock")
        app_btn.set_active(self.bridge.get_show_apps_button())
        app_btn.connect("notify::active", lambda s, p: self.bridge.set_show_apps_button(s.get_active()))
        item_group.add(app_btn)

        trash_btn = Adw.SwitchRow(title="Show Trash Can", subtitle="Display trash icon with dynamic empty and full states")
        trash_btn.set_active(self.bridge.get_show_trash())
        trash_btn.connect("notify::active", lambda s, p: self.bridge.set_show_trash(s.get_active()))
        item_group.add(trash_btn)

        down_btn = Adw.SwitchRow(title="Show Downloads Folder Stack", subtitle="macOS Downloads stack with bounce animation on new files")
        down_btn.set_active(self.bridge.get_show_downloads())
        down_btn.connect("notify::active", lambda s, p: self.bridge.set_show_downloads(s.get_active()))
        item_group.add(down_btn)

        down_view = Adw.ComboRow(title="Downloads Stack View")
        down_view.set_model(Gtk.StringList.new(["Fan", "Grid", "List"]))
        cur_v = self.bridge.get_downloads_view()
        down_view.set_selected(0 if cur_v == "fan" else (1 if cur_v == "grid" else 2))
        down_view.connect("notify::selected", lambda r, p: self.bridge.set_downloads_view(["fan", "grid", "list"][r.get_selected()]))
        item_group.add(down_view)

        item_group.add(create_spin_row("Downloads Max Files", "Maximum files displayed in stack view", 3, 20, 1, self.bridge.get_downloads_max_files(), digits=0, on_change=self.bridge.set_downloads_max_files))

        mount_btn = Adw.SwitchRow(title="Show Mounted Drives", subtitle="Display mounted disks and disk images")
        mount_btn.set_active(self.bridge.get_show_mounted_devices())
        mount_btn.connect("notify::active", lambda s, p: self.bridge.set_show_mounted_devices(s.get_active()))
        item_group.add(mount_btn)

        remov_btn = Adw.SwitchRow(title="Show Removable Media", subtitle="Display USB sticks, phones, and digital cameras")
        remov_btn.set_active(self.bridge.get_show_removable_devices())
        remov_btn.connect("notify::active", lambda s, p: self.bridge.set_show_removable_devices(s.get_active()))
        item_group.add(remov_btn)

        # Group: Window Previews & Tooltips
        prev_group = Adw.PreferencesGroup(title="Window Previews and Tooltips")
        page.add(prev_group)

        prev_en = Adw.SwitchRow(title="Live Window Previews", subtitle="Show live window thumbnails on icon hover")
        prev_en.set_active(self.bridge.get_show_previews())
        prev_en.connect("notify::active", lambda s, p: self.bridge.set_show_previews(s.get_active()))
        prev_group.add(prev_en)

        prev_group.add(create_spin_row("Preview Delay", "Hover delay in ms before showing thumbnail", 100, 3000, 50, self.bridge.get_preview_delay(), digits=0, on_change=self.bridge.set_preview_delay))
        prev_group.add(create_spin_row("Preview Max Size", "Maximum thumbnail width in pixels", 80, 400, 10, self.bridge.get_preview_size(), digits=0, on_change=self.bridge.set_preview_size))

        tip_en = Adw.SwitchRow(title="Show Tooltips", subtitle="Show application title tooltip when hovering")
        tip_en.set_active(self.bridge.get_show_tooltip())
        tip_en.connect("notify::active", lambda s, p: self.bridge.set_show_tooltip(s.get_active()))
        prev_group.add(tip_en)

        prev_group.add(create_spin_row("Tooltip Delay", "Milliseconds before tooltip appears", 0, 2000, 25, self.bridge.get_tooltip_delay(), digits=0, on_change=self.bridge.set_tooltip_delay))

        genie_en = Adw.SwitchRow(title="Genie (Magic Lamp) Minimize Effect", subtitle="macOS magic lamp fluid minimize and restore animation")
        genie_en.set_active(self.bridge.get_enable_genie())
        genie_en.connect("notify::active", lambda s, p: self.bridge.set_enable_genie(s.get_active()))
        prev_group.add(genie_en)

        prev_group.add(create_spin_row("Genie Duration", "Magic lamp animation duration in ms", 50, 1000, 25, self.bridge.get_genie_duration(), digits=0, on_change=self.bridge.set_genie_duration))

    # ── 3. TOP BAR & MENU ─────────────────────────────────────────────────
    def _build_topbar_page(self):
        page = Adw.PreferencesPage()
        self.stack.add_titled_with_icon(page, "topbar", "Menu Bar", "edit-find-symbolic")
        self._add_nav_item("topbar", "Menu Bar", "edit-find-symbolic")

        top_group = Adw.PreferencesGroup(title="macOS Menu Bar and Panel")
        page.add(top_group)

        bar_en = Adw.SwitchRow(title="Enable Menu Bar Enhancements", subtitle="Replace GNOME defaults with authentic macOS menu bar")
        bar_en.set_active(self.bridge.get_topbar_enabled())
        bar_en.connect("notify::active", lambda s, p: self.bridge.set_topbar_enabled(s.get_active()))
        top_group.add(bar_en)

        # Apple Menu & Branding
        apple_group = Adw.PreferencesGroup(title="Apple Menu and System Branding")
        page.add(apple_group)

        apple_en = Adw.SwitchRow(title="Apple Menu Button", subtitle="Display system menu at the far left of the panel")
        apple_en.set_active(self.bridge.get_apple_menu_enabled())
        apple_en.connect("notify::active", lambda s, p: self.bridge.set_apple_menu_enabled(s.get_active()))
        apple_group.add(apple_en)

        logo_row = Adw.ComboRow(title="Menu Logo Icon")
        logo_row.set_model(Gtk.StringList.new(["Apple Logo", "Arch Linux", "Fedora", "Debian", "Ubuntu", "Linux Tux"]))
        cur_icon = self.bridge.get_apple_icon()
        icon_map = {"apple": 0, "arch": 1, "fedora": 2, "debian": 3, "ubuntu": 4, "linux": 5}
        logo_row.set_selected(icon_map.get(cur_icon, 0))
        logo_row.connect("notify::selected", lambda r, p: self.bridge.set_apple_icon(["apple", "arch", "fedora", "debian", "ubuntu", "linux"][r.get_selected()]))
        apple_group.add(logo_row)

        app_title = Adw.SwitchRow(title="Active Application Title", subtitle="Show current running application name next to Apple menu")
        app_title.set_active(self.bridge.get_app_title_enabled())
        app_title.connect("notify::active", lambda s, p: self.bridge.set_app_title_enabled(s.get_active()))
        apple_group.add(app_title)

        hide_act = Adw.SwitchRow(title="Hide 'Activities' Button", subtitle="Remove default GNOME Activities button from top bar")
        hide_act.set_active(self.bridge.get_hide_activities())
        hide_act.connect("notify::active", lambda s, p: self.bridge.set_hide_activities(s.get_active()))
        apple_group.add(hide_act)

        accel_row = Adw.SwitchRow(title="macOS Accelerator Symbols", subtitle="Format keyboard shortcuts with Apple symbols (⌘ ⌥ ^ ⎋)")
        accel_row.set_active(self.bridge.get_macos_accelerators())
        accel_row.connect("notify::active", lambda s, p: self.bridge.set_macos_accelerators(s.get_active()))
        apple_group.add(accel_row)

        store_cmd = Adw.EntryRow(title="App Store Launcher Command")
        store_cmd.set_text(self.bridge.get_app_store_cmd())
        store_cmd.connect("changed", lambda e: self.bridge.set_app_store_cmd(e.get_text()))
        apple_group.add(store_cmd)

        # macOS Indicators & Dynamic Island
        ind_group = Adw.PreferencesGroup(title="macOS Indicators and Dynamic Island")
        page.add(ind_group)

        bt_bat = Adw.SwitchRow(
            title="Bluetooth Device Battery Indicator",
            subtitle="Show connected Bluetooth devices with battery percentage badges and status bars"
        )
        bt_bat.set_active(self.bridge.get_topbar_bluetooth_battery())
        bt_bat.connect("notify::active", lambda s, p: self.bridge.set_topbar_bluetooth_battery(s.get_active()))
        ind_group.add(bt_bat)

        media_pill = Adw.SwitchRow(
            title="Dynamic Media Island Pill",
            subtitle="Live macOS Dynamic Island playback pill with album art, waveform visualizer, and controls"
        )
        media_pill.set_active(self.bridge.get_topbar_media_pill())
        media_pill.connect("notify::active", lambda s, p: self.bridge.set_topbar_media_pill(s.get_active()))
        ind_group.add(media_pill)

        # Panel Appearance
        pan_group = Adw.PreferencesGroup(title="Panel Styling and Frosted Blur")
        page.add(pan_group)

        blur_en = Adw.SwitchRow(title="Frosted Glass Blur", subtitle="Dynamic blurred glass surface behind top menu bar")
        blur_en.set_active(self.bridge.get_topbar_blur())
        blur_en.connect("notify::active", lambda s, p: self.bridge.set_topbar_blur(s.get_active()))
        pan_group.add(blur_en)

        pan_group.add(create_spin_row("Blur Radius", "Frosted glass blur radius in pixels", 5, 100, 5, self.bridge.get_topbar_blur_radius(), digits=0, on_change=self.bridge.set_topbar_blur_radius))
        pan_group.add(create_spin_row("Panel Transparency", "Background translucency factor", 0.0, 1.0, 0.05, self.bridge.get_topbar_transparency(), digits=2, on_change=self.bridge.set_topbar_transparency))

        topbar_opaque = Adw.SwitchRow(
            title="Opaque Top Bar",
            subtitle="Specifically make top bar 100% solid and opaque while leaving dock, menus, and popups translucent & blurry"
        )
        topbar_opaque.set_active(self.bridge.get_topbar_opaque())
        topbar_opaque.connect("notify::active", lambda s, p: self.bridge.set_topbar_opaque(s.get_active()))
        pan_group.add(topbar_opaque)

        pill_style = Adw.SwitchRow(title="macOS Pill Button Style", subtitle="Format top bar indicator buttons as smooth pills")
        pill_style.set_active(self.bridge.get_topbar_pill_style())
        pill_style.connect("notify::active", lambda s, p: self.bridge.set_topbar_pill_style(s.get_active()))
        pan_group.add(pill_style)

        # Quick Settings Buttons
        qs_group = Adw.PreferencesGroup(title="Quick Settings Customization")
        page.add(qs_group)

        h_lock = Adw.SwitchRow(title="Hide Lock Screen Action", subtitle="Hide the lock button from quick settings popup")
        h_lock.set_active(self.bridge.get_hide_lock_button())
        h_lock.connect("notify::active", lambda s, p: self.bridge.set_hide_lock_button(s.get_active()))
        qs_group.add(h_lock)

        h_power = Adw.SwitchRow(title="Hide Power Action", subtitle="Hide the power off button from quick settings popup")
        h_power.set_active(self.bridge.get_hide_power_button())
        h_power.connect("notify::active", lambda s, p: self.bridge.set_hide_power_button(s.get_active()))
        qs_group.add(h_power)

        h_set = Adw.SwitchRow(title="Hide GNOME Settings Action", subtitle="Hide the settings gear button from quick settings popup")
        h_set.set_active(self.bridge.get_hide_settings_button())
        h_set.connect("notify::active", lambda s, p: self.bridge.set_hide_settings_button(s.get_active()))
        qs_group.add(h_set)

    # ── 4. SPOTLIGHT SEARCH ───────────────────────────────────────────────
    def _build_spotlight_page(self):
        page = Adw.PreferencesPage()
        self.stack.add_titled_with_icon(page, "spotlight", "Spotlight", "system-search-symbolic")
        self._add_nav_item("spotlight", "Spotlight", "system-search-symbolic")

        top_group = Adw.PreferencesGroup(title="Spotlight Search Modal")
        page.add(top_group)

        spot_en = Adw.SwitchRow(title="Enable Spotlight", subtitle="Keyboard-driven macOS command bar and search")
        spot_en.set_active(self.bridge.get_spotlight_enabled())
        spot_en.connect("notify::active", lambda s, p: self.bridge.set_spotlight_enabled(s.get_active()))
        top_group.add(spot_en)

        key_row = Adw.ActionRow(title="Keyboard Shortcut", subtitle="Press to open or close Spotlight modal")
        key_badge = Gtk.Label(label=self.bridge.get_spotlight_shortcut())
        key_badge.add_css_class("pill")
        key_row.add_suffix(key_badge)
        top_group.add(key_row)

        mod_group = Adw.PreferencesGroup(title="Modal Geometry and Ranking")
        page.add(mod_group)

        mod_group.add(create_spin_row("Search Bar Width", "Modal window width in pixels", 400, 1200, 20, self.bridge.get_spotlight_width(), digits=0, on_change=self.bridge.set_spotlight_width))

        pos_row = Adw.ComboRow(title="Vertical Placement")
        pos_row.set_model(Gtk.StringList.new(["Center", "Top", "Bottom"]))
        cur_pos = self.bridge.get_spotlight_position()
        pos_map = {"center": 0, "top": 1, "bottom": 2}
        pos_row.set_selected(pos_map.get(cur_pos, 0))
        pos_row.connect("notify::selected", lambda r, p: self.bridge.set_spotlight_position(["center", "top", "bottom"][r.get_selected()]))
        mod_group.add(pos_row)

        mod_group.add(create_spin_row("Background Glass Opacity", "Modal glass surface opacity percentage", 65, 100, 5, self.bridge.get_spotlight_opacity(), digits=0, on_change=self.bridge.set_spotlight_opacity))
        mod_group.add(create_spin_row("Maximum Search Results", "Number of results displayed simultaneously", 3, 20, 1, self.bridge.get_spotlight_max_results(), digits=0, on_change=self.bridge.set_spotlight_max_results))

        adapt_row = Adw.SwitchRow(title="Adaptive Ranking", subtitle="Learn and prioritize frequently opened applications")
        adapt_row.set_active(self.bridge.get_spotlight_adaptive_ranking())
        adapt_row.connect("notify::active", lambda s, p: self.bridge.set_spotlight_adaptive_ranking(s.get_active()))
        mod_group.add(adapt_row)

        prov_group = Adw.PreferencesGroup(title="Active Search Providers")
        page.add(prov_group)

        providers = [
            ("Applications", "Launch installed desktop apps", self.bridge.get_spotlight_search_apps, self.bridge.set_spotlight_search_apps),
            ("Open Windows", "Switch to existing running windows", self.bridge.get_spotlight_search_windows, self.bridge.set_spotlight_search_windows),
            ("Files and Documents", "Find recent and indexed user files", self.bridge.get_spotlight_search_files, self.bridge.set_spotlight_search_files),
            ("Clipboard History", "Search and paste recent clipboard items", self.bridge.get_spotlight_search_clipboard, self.bridge.set_spotlight_search_clipboard),
            ("Calculator and Math", "Real-time mathematical and scientific evaluations", self.bridge.get_spotlight_search_calc, self.bridge.set_spotlight_search_calc),
            ("Weather Forecast", "Instant weather condition reports", self.bridge.get_spotlight_search_weather, self.bridge.set_spotlight_search_weather),
        ]

        for title, sub, getter, setter in providers:
            sw = Adw.SwitchRow(title=title, subtitle=sub)
            sw.set_active(getter())
            sw.connect("notify::active", lambda s, p, fn=setter: fn(s.get_active()))
            prov_group.add(sw)

    # ── 5. WINDOW MANAGEMENT & CORNERS ────────────────────────────────────
    def _build_windows_page(self):
        page = Adw.PreferencesPage()
        self.stack.add_titled_with_icon(page, "windows", "Window Management", "preferences-desktop-display-symbolic")
        self._add_nav_item("windows", "Window Management", "preferences-desktop-display-symbolic")

        # Window Gaps
        gaps_group = Adw.PreferencesGroup(title="Outer Screen Window Gaps")
        page.add(gaps_group)

        gaps_en = Adw.SwitchRow(title="Enable Window Gaps", subtitle="Add elegant outer margins around application windows")
        gaps_en.set_active(self.bridge.get_gaps_enabled())
        gaps_en.connect("notify::active", lambda s, p: self.bridge.set_gaps_enabled(s.get_active()))
        gaps_group.add(gaps_en)

        uni_gap = Adw.SwitchRow(title="Uniform Gap on All Edges", subtitle="Use same padding size on top, bottom, left, and right")
        uni_gap.set_active(self.bridge.get_gap_uniform())
        gaps_group.add(uni_gap)

        uni_size_row = create_spin_row("Uniform Gap Size", "Margin in pixels applied to all edges", 0, 200, 2, self.bridge.get_gap_size(), digits=0, on_change=self.bridge.set_gap_size)
        gaps_group.add(uni_size_row)

        max_gaps = Adw.SwitchRow(title="Retain Gaps on Maximized Windows", subtitle="Preserve outer padding even when window is maximized")
        max_gaps.set_active(self.bridge.get_gaps_maximized())
        max_gaps.connect("notify::active", lambda s, p: self.bridge.set_gaps_maximized(s.get_active()))
        gaps_group.add(max_gaps)

        def _on_custom_gap(setter, val):
            if uni_gap.get_active():
                uni_gap.set_active(False)
            setter(val)

        top_row = create_spin_row("Custom Top Margin", "Top edge gap in pixels", 0, 200, 2, self.bridge.get_gap_top(), digits=0, on_change=lambda v: _on_custom_gap(self.bridge.set_gap_top, v))
        bottom_row = create_spin_row("Custom Bottom Margin", "Bottom edge gap in pixels", 0, 200, 2, self.bridge.get_gap_bottom(), digits=0, on_change=lambda v: _on_custom_gap(self.bridge.set_gap_bottom, v))
        left_row = create_spin_row("Custom Left Margin", "Left edge gap in pixels", 0, 200, 2, self.bridge.get_gap_left(), digits=0, on_change=lambda v: _on_custom_gap(self.bridge.set_gap_left, v))
        right_row = create_spin_row("Custom Right Margin", "Right edge gap in pixels", 0, 200, 2, self.bridge.get_gap_right(), digits=0, on_change=lambda v: _on_custom_gap(self.bridge.set_gap_right, v))

        gaps_group.add(top_row)
        gaps_group.add(bottom_row)
        gaps_group.add(left_row)
        gaps_group.add(right_row)

        def _update_gap_ui(is_uniform):
            uni_size_row.set_sensitive(is_uniform)
            top_row.set_sensitive(not is_uniform)
            bottom_row.set_sensitive(not is_uniform)
            left_row.set_sensitive(not is_uniform)
            right_row.set_sensitive(not is_uniform)

        _update_gap_ui(uni_gap.get_active())

        def _on_uni_toggled(s, _pspec):
            active = s.get_active()
            self.bridge.set_gap_uniform(active)
            _update_gap_ui(active)

        uni_gap.connect("notify::active", _on_uni_toggled)

        # Rounded Corners & Borders
        corn_group = Adw.PreferencesGroup(title="Rounded Corners and Window Borders")
        page.add(corn_group)

        corn_en = Adw.SwitchRow(title="Enable Rounded Corners", subtitle="Render anti-aliased squircle corners on application windows")
        corn_en.set_active(self.bridge.get_corners_enabled())
        corn_en.connect("notify::active", lambda s, p: self.bridge.set_corners_enabled(s.get_active()))
        corn_group.add(corn_en)

        corn_group.add(create_spin_row("Window Corner Radius", "Corner curvature radius in pixels", 0, 40, 1, self.bridge.get_corner_radius(), digits=0, on_change=self.bridge.set_corner_radius))
        corn_group.add(create_spin_row("Apple Squircle Smoothing", "Curvature exponent for super-ellipse squircle corners (0.8 = authentic Apple curvature)", 0.0, 1.0, 0.05, self.bridge.get_corner_smoothing(), digits=2, on_change=self.bridge.set_corner_smoothing))
        corn_group.add(create_spin_row("Window Border Stroke Width", "Subtle macOS window border in pixels", 0, 10, 1, self.bridge.get_corner_border_width(), digits=0, on_change=self.bridge.set_corner_border_width))
        corn_group.add(create_spin_row("Title Bar Button Size", "Diameter in pixels of macOS traffic light buttons (close, minimize, maximize)", 10, 22, 1, self.bridge.get_titlebar_button_size(), digits=0, on_change=self.bridge.set_titlebar_button_size))
        corn_group.add(create_spin_row("Title Bar Button Spacing", "Gap in pixels between traffic light buttons (closer or farther apart)", 0, 24, 1, self.bridge.get_titlebar_button_spacing(), digits=0, on_change=self.bridge.set_titlebar_button_spacing))

        unround_max = Adw.SwitchRow(title="Square Off Maximized Windows", subtitle="Disable rounded corners when a window is maximized")
        unround_max.set_active(self.bridge.get_unround_maximized())
        unround_max.connect("notify::active", lambda s, p: self.bridge.set_unround_maximized(s.get_active()))
        corn_group.add(unround_max)

        skip_adw = Adw.SwitchRow(title="Skip Libadwaita Apps", subtitle="Bypass corner shader for modern Libadwaita applications")
        skip_adw.set_active(self.bridge.get_skip_libadwaita())
        skip_adw.connect("notify::active", lambda s, p: self.bridge.set_skip_libadwaita(s.get_active()))
        corn_group.add(skip_adw)

        # Drop Shadows
        shad_group = Adw.PreferencesGroup(title="macOS Window Drop Shadows")
        page.add(shad_group)

        shad_en = Adw.SwitchRow(title="Enable Window Shadows", subtitle="Hardware accelerated drop shadows with realistic depth")
        shad_en.set_active(self.bridge.get_shadow_enabled())
        shad_en.connect("notify::active", lambda s, p: self.bridge.set_shadow_enabled(s.get_active()))
        shad_group.add(shad_en)

        shad_group.add(create_spin_row("Focused Window Vertical Offset", "Vertical downward elevation in pixels", 0, 40, 1, self.bridge.get_focused_shadow_v_offset(), digits=0, on_change=self.bridge.set_focused_shadow_v_offset))
        shad_group.add(create_spin_row("Focused Shadow Blur Radius", "Gaussian shadow softness for active window", 0, 80, 2, self.bridge.get_focused_shadow_blur(), digits=0, on_change=self.bridge.set_focused_shadow_blur))
        shad_group.add(create_spin_row("Focused Shadow Opacity", "Shadow darkness percentage", 0, 100, 5, self.bridge.get_focused_shadow_opacity(), digits=0, on_change=self.bridge.set_focused_shadow_opacity))
        shad_group.add(create_spin_row("Background Window Vertical Offset", "Downward elevation for inactive windows", 0, 40, 1, self.bridge.get_unfocused_shadow_v_offset(), digits=0, on_change=self.bridge.set_unfocused_shadow_v_offset))
        shad_group.add(create_spin_row("Background Shadow Blur Radius", "Shadow softness for inactive windows", 0, 80, 2, self.bridge.get_unfocused_shadow_blur(), digits=0, on_change=self.bridge.set_unfocused_shadow_blur))
        shad_group.add(create_spin_row("Background Shadow Opacity", "Shadow darkness for inactive windows", 0, 100, 5, self.bridge.get_unfocused_shadow_opacity(), digits=0, on_change=self.bridge.set_unfocused_shadow_opacity))

    # ── 6. BLUR ENGINE & LIQUID GLASS ─────────────────────────────────────
    def _build_blur_page(self):
        page = Adw.PreferencesPage()
        self.stack.add_titled_with_icon(page, "blur", "Glass Blur Engine", "view-reveal-symbolic")
        self._add_nav_item("blur", "Glass Blur Engine", "view-reveal-symbolic")

        # ── Community Dynamic Rounded Blur Engine (gnome-rounded-blur) ──
        comm_group = Adw.PreferencesGroup(
            title="macOS Liquid Dynamic Blur Engine",
            description="True real-time background blur with rounded corners across the Dock, Control Center, and Shell."
        )
        page.add(comm_group)

        is_rounded_blur_installed = os.path.exists("/usr/lib/girepository-1.0/Blur-1.0.typelib") or subprocess.run(["pacman", "-Q", "gnome-rounded-blur"], capture_output=True).returncode == 0

        if is_rounded_blur_installed:
            dyn_row = Adw.ActionRow(
                title="Dynamic Rounded Blur Engine (gnome-rounded-blur)",
                subtitle="Active — Live window transparency with native anti-aliased corner clipping is enabled."
            )
            dyn_icon = Gtk.Image.new_from_icon_name("emblem-ok-symbolic")
            dyn_icon.add_css_class("accent")
            dyn_row.add_prefix(dyn_icon)
            badge = Gtk.Label(label="Enabled")
            badge.add_css_class("pill")
            badge.add_css_class("success")
            dyn_row.add_suffix(badge)
            comm_group.add(dyn_row)
        else:
            dyn_row = Adw.ActionRow(
                title="Install gnome-rounded-blur for Live Window Blur",
                subtitle="GNOME Shell requires the community 'gnome-rounded-blur' library for live window blur with rounded corners. Currently using zero-korner static blur."
            )
            dyn_icon = Gtk.Image.new_from_icon_name("software-update-available-symbolic")
            dyn_row.add_prefix(dyn_icon)

            inst_btn = Gtk.Button(label="Install (AUR)")
            inst_btn.add_css_class("suggested-action")
            inst_btn.add_css_class("pill")
            inst_btn.connect("clicked", lambda *a: self._install_rounded_blur())
            dyn_row.add_suffix(inst_btn)
            comm_group.add(dyn_row)

        top_group = Adw.PreferencesGroup(title="Integrated Hardware Blur Engine")
        page.add(top_group)

        blur_en = Adw.SwitchRow(title="Enable Global Blur", subtitle="Dynamic GPU-accelerated frosted glass blur")
        blur_en.set_active(self.bridge.get_blur_enabled())
        blur_en.connect("notify::active", lambda s, p: self.bridge.set_blur_enabled(s.get_active()))
        top_group.add(blur_en)

        tune_group = Adw.PreferencesGroup(title="Gaussian Kernel and Surface Tuning")
        page.add(tune_group)

        tune_group.add(create_spin_row("Global Glass Opacity", "Master opacity for all glass surfaces (dock, top bar, menus). Overrides per-surface opacity when not at default (0.5).", 0.0, 1.0, 0.05, self.bridge.get_global_opacity(), digits=2, on_change=self.bridge.set_global_opacity))
        tune_group.add(create_spin_row("Blur Sigma Radius", "Gaussian blur spread intensity (0 = no blur)", 0, 80, 2, self.bridge.get_blur_sigma(), digits=0, on_change=self.bridge.set_blur_sigma))
        tune_group.add(create_spin_row("Glass Brightness Multiplier", "Luminance factor behind glass surfaces (0 = fully dark)", 0.0, 1.0, 0.05, self.bridge.get_blur_brightness(), digits=2, on_change=self.bridge.set_blur_brightness))
        tune_group.add(create_spin_row("Film Grain and Noise", "Subtle analog texture on glass surfaces", 0.0, 0.5, 0.02, self.bridge.get_blur_noise_amount(), digits=2, on_change=self.bridge.set_blur_noise_amount))
        tune_group.add(create_spin_row("Application Window Opacity", "Translucency factor for window surfaces (0.84 recommended for frosted glass)", 0.5, 1.0, 0.02, self.bridge.get_app_opacity(), digits=2, on_change=self.bridge.set_app_opacity))

        surf_group = Adw.PreferencesGroup(title="Target Desktop Surfaces")
        page.add(surf_group)

        for title, sub, getter, setter in [
            ("Top Menu Bar Blur", "Apply dynamic frosted blur behind the top panel", self.bridge.get_blur_panel, self.bridge.set_blur_panel),
            ("Dock Pill Blur", "Apply Gaussian glass blur behind dock pill", self.bridge.get_blur_dock, self.bridge.set_blur_dock),
            ("Application Window Blur", "Apply dynamic frosted glass blur behind active application windows", self.bridge.get_blur_applications, self.bridge.set_blur_applications),
            ("Activities Overview Blur", "Blur desktop wallpaper during window overview", self.bridge.get_blur_overview, self.bridge.set_blur_overview),
            ("App Folder Modal Blur", "Blur background dialogs behind app drawer folders", self.bridge.get_blur_appfolder, self.bridge.set_blur_appfolder)
        ]:
            sw = Adw.SwitchRow(title=title, subtitle=sub)
            sw.set_active(getter())
            sw.connect("notify::active", lambda s, p, fn=setter: fn(s.get_active()))
            surf_group.add(sw)

        # ── Liquid Glass Optical Refraction Shader ──
        liq_group = Adw.PreferencesGroup(
            title="Liquid Glass Refraction and Dispersion Shader",
            description="Hardware-accelerated Snell-law optical refraction, specular rim highlights, and chromatic edge splitting."
        )
        page.add(liq_group)

        liq_en = Adw.SwitchRow(
            title="Enable Liquid Glass Refraction",
            subtitle="Physics-based ray refraction that dynamically bends wallpaper and windows through glass edges"
        )
        liq_en.set_active(self.bridge.get_blur_liquid_glass())
        liq_en.connect("notify::active", lambda s, p: self.bridge.set_blur_liquid_glass(s.get_active()))
        liq_group.add(liq_en)

        liq_group.add(create_spin_row("Refraction Strength", "Optical bending scale along curved edges", 0.0, 1.0, 0.02, self.bridge.get_blur_refraction_strength(), digits=2, on_change=self.bridge.set_blur_refraction_strength))
        liq_group.add(create_spin_row("Chromatic Color Dispersion", "Prism RGB channel wavelength splitting on glass bevels", 0.0, 0.5, 0.01, self.bridge.get_blur_chromatic_dispersion(), digits=2, on_change=self.bridge.set_blur_chromatic_dispersion))

    # ── 7. APPEARANCE & THEMES ────────────────────────────────────────────
    def _build_theme_page(self):
        page = Adw.PreferencesPage()
        self.stack.add_titled_with_icon(page, "themes", "Appearance and Themes", "preferences-desktop-theme-symbolic")
        self._add_nav_item("themes", "Appearance and Themes", "preferences-desktop-theme-symbolic")

        theme_group = Adw.PreferencesGroup(
            title="Curated macOS Themes",
            description="Select a theme to apply consistently across Shell, GTK 2, 3, 4 (Libadwaita), and Flatpak:"
        )
        page.add(theme_group)

        current_theme = theme_manager.get_current_theme()
        self.theme_radios = {}
        for key, info in theme_manager.THEMES.items():
            row = Adw.ActionRow(title=info["name"], subtitle=info["description"])
            btn = Gtk.CheckButton()
            if self.theme_radios:
                first_btn = list(self.theme_radios.values())[0]
                btn.set_group(first_btn)
            btn.set_active(key == current_theme)
            btn.connect("toggled", self._on_theme_selected, key)
            row.add_prefix(btn)
            row.set_activatable_widget(btn)
            self.theme_radios[key] = btn
            theme_group.add(row)

        sync_group = Adw.PreferencesGroup(title="Global Ecosystem Synchronization")
        page.add(sync_group)

        apply_row = Adw.ActionRow(
            title="Apply Theme Globally",
            subtitle="Synchronizes GTK 4 (Libadwaita), GTK 3, GTK 2, Shell User Theme, and Flatpak overrides"
        )
        apply_btn = Gtk.Button(label="Apply Globally")
        apply_btn.add_css_class("suggested-action")
        apply_btn.add_css_class("pill")
        apply_btn.connect("clicked", self._apply_current_theme)
        apply_row.add_suffix(apply_btn)
        sync_group.add(apply_row)

        self.theme_status_label = Gtk.Label(label="Theme is synchronized across all systems.")
        self.theme_status_label.add_css_class("dim-label")
        self.theme_status_label.set_margin_top(8)
        sync_group.add(self.theme_status_label)

        # ── Shell UI & Menu Styling (macOS Unified Design) ──
        menu_group = Adw.PreferencesGroup(
            title="macOS Shell UI and Menu Styling",
            description="Fine-tune borders, corner curvature, and glass translucency across context menus, Kiwi menu, control center, and notifications:"
        )
        page.add(menu_group)

        menu_group.add(create_spin_row("Menu Corner Radius", "Curvature radius in pixels for context menus, Kiwi menu, and popups", 6, 32, 1, self.bridge.get_menu_corner_radius(), digits=0, on_change=self.bridge.set_menu_corner_radius))
        menu_group.add(create_spin_row("Menu Border Width", "Hairline stroke width in pixels", 0, 4, 1, self.bridge.get_menu_border_width(), digits=0, on_change=self.bridge.set_menu_border_width))
        menu_group.add(create_spin_row("Menu Border Opacity", "Edge stroke alpha transparency factor", 0.0, 1.0, 0.02, self.bridge.get_menu_border_opacity(), digits=2, on_change=self.bridge.set_menu_border_opacity))

        m_spec = Adw.SwitchRow(
            title="Top Specular Highlight Rim",
            subtitle="Render subtle 1px overhead light reflection along the upper glass bevel"
        )
        m_spec.set_active(self.bridge.get_menu_specular_highlight())
        m_spec.connect("notify::active", lambda s, p: self.bridge.set_menu_specular_highlight(s.get_active()))
        menu_group.add(m_spec)

        menu_group.add(create_spin_row("Menu Glass Translucency", "Background darkness and glass opacity of menus", 0.2, 1.0, 0.05, self.bridge.get_menu_bg_opacity(), digits=2, on_change=self.bridge.set_menu_bg_opacity))
        menu_group.add(create_spin_row("Control Center Corner Radius", "Curvature radius for Quick Settings popup card", 12, 40, 2, self.bridge.get_quick_settings_radius(), digits=0, on_change=self.bridge.set_quick_settings_radius))
        menu_group.add(create_spin_row("Notification Banner Corner Radius", "Curvature radius for desktop notification cards", 8, 32, 1, self.bridge.get_notification_radius(), digits=0, on_change=self.bridge.set_notification_radius))

    def _on_theme_selected(self, btn, key):
        if btn.get_active():
            self._selected_theme = key

    def _apply_current_theme(self, *args):
        selected = getattr(self, "_selected_theme", theme_manager.get_current_theme())
        res = theme_manager.apply_global_theme(selected)
        if res.get("success"):
            self.theme_status_label.set_text(f"✅ Successfully applied {theme_manager.THEMES[selected]['name']} globally!")
        else:
            self.theme_status_label.set_text("⚠️ Warning during theme sync. Check console logs.")

    # ── 8. SYSTEM & INTEGRATION ───────────────────────────────────────────
    def _build_system_page(self):
        page = Adw.PreferencesPage()
        self.stack.add_titled_with_icon(page, "system", "System", "preferences-system-details-symbolic")
        self._add_nav_item("system", "System", "preferences-system-details-symbolic")

        sys_group = Adw.PreferencesGroup(title="GNOME Shell Runtime Integration")
        page.add(sys_group)

        ext_state = Adw.ActionRow(title="Mak Master Extension", subtitle="Unified GJS runtime handling all macOS subsystems")
        state_badge = Gtk.Label(label="Active")
        state_badge.add_css_class("pill")
        state_badge.add_css_class("success")
        ext_state.add_suffix(state_badge)
        sys_group.add(ext_state)

        rst_row = Adw.ActionRow(title="Reload GNOME Shell Extension", subtitle="Trigger live reload of Mak GJS modules")
        rst_btn = Gtk.Button(label="Reload Extension")
        rst_btn.add_css_class("pill")
        rst_btn.connect("clicked", lambda *a: self._reload_extension())
        rst_row.add_suffix(rst_btn)
        sys_group.add(rst_row)

        reset_all_row = Adw.ActionRow(
            title="Reset All Settings to Defaults",
            subtitle="Restore all Dock, Top Bar, Corners, Gaps, Blur, and Themes to authentic macOS defaults"
        )
        reset_all_btn = Gtk.Button(label="Reset Defaults")
        reset_all_btn.add_css_class("destructive-action")
        reset_all_btn.add_css_class("pill")
        reset_all_btn.connect("clicked", lambda *a: self._on_reset_to_defaults())
        reset_all_row.add_suffix(reset_all_btn)
        sys_group.add(reset_all_row)

    def _reload_extension(self):
        try:
            subprocess.run(["gnome-extensions", "disable", "mak@local"], check=True)
            subprocess.run(["gnome-extensions", "enable", "mak@local"], check=True)
            toast = Adw.Toast.new("Mak extension reloaded successfully!")
            self.toast_overlay.add_toast(toast)
        except Exception as e:
            toast = Adw.Toast.new(f"Failed to reload extension: {e}")
            self.toast_overlay.add_toast(toast)

    def _install_rounded_blur(self):
        cmd = "yay -S --noconfirm gnome-rounded-blur || paru -S --noconfirm gnome-rounded-blur"
        try:
            subprocess.Popen(["kgx", "-e", f"bash -c '{cmd}; echo Done. Press enter to exit; read'"])
        except Exception:
            try:
                subprocess.Popen(["gnome-terminal", "--", "bash", "-c", f"{cmd}; echo Done. Press enter to exit; read"])
            except Exception as e:
                toast = Adw.Toast.new(f"Could not open terminal: {e}")
                self.toast_overlay.add_toast(toast)

class MakApplication(Adw.Application):
    def __init__(self):
        super().__init__(application_id="org.gnome.shell.extensions.mak.controlcenter",
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = MakAppWindow(application=self)
        win.present()

def main():
    app = MakApplication()
    return app.run(sys.argv)

if __name__ == "__main__":
    sys.exit(main())
