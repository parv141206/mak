#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Mak Control Center: Unified GTK 4 + Libadwaita Application for macOS Desktop Suite

import sys
import os
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('Gio', '2.0')
gi.require_version('GLib', '2.0')

from gi.repository import Gtk, Adw, Gio, GLib

import theme_manager
import autostart_manager
from settings_bridge import MakSettingsBridge

class MakAppWindow(Adw.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_title("Mak Control Center")
        self.set_default_size(980, 740)

        self.bridge = MakSettingsBridge()
        self._build_ui()

    def _build_ui(self):
        toolbar_view = Adw.ToolbarView()
        self.set_content(toolbar_view)

        header = Adw.HeaderBar()
        title = Adw.WindowTitle(title="Mak", subtitle="macOS Desktop Suite")
        header.set_title_widget(title)
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
        self._build_overview_page()
        self._build_dock_page()
        self._build_topbar_page()
        self._build_spotlight_page()
        self._build_windows_page()
        self._build_blur_page()
        self._build_theme_page()
        self._build_system_page()

        self.nav_list.connect("row-selected", self._on_nav_selected)
        first_row = self.nav_list.get_row_at_index(0)
        if first_row:
            self.nav_list.select_row(first_row)

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
            title="Quick Presets",
            description="Apply curated macOS desktop configurations in one click:"
        )
        page.add(presets_group)

        p1_row = Adw.ActionRow(
            title="macOS Sonoma Experience",
            subtitle="Floating bottom dock with 2.6x zoom, frosted menu bar, 12px window gaps, 16px squircle corners"
        )
        btn1 = Gtk.Button(label="Apply Preset")
        btn1.add_css_class("pill")
        btn1.connect("clicked", lambda *a: self._apply_preset_sonoma())
        p1_row.add_suffix(btn1)
        presets_group.add(p1_row)

        p2_row = Adw.ActionRow(
            title="Compact Productivity",
            subtitle="Smaller 48px auto-hiding dock, 6px clean window gaps, snappier animation physics"
        )
        btn2 = Gtk.Button(label="Apply Preset")
        btn2.add_css_class("pill")
        btn2.connect("clicked", lambda *a: self._apply_preset_compact())
        p2_row.add_suffix(btn2)
        presets_group.add(p2_row)

        summary_group = Adw.PreferencesGroup(title="Active Mak Features")
        page.add(summary_group)

        for feat, desc in [
            ("Floating Glass Dock", "Hardware-accelerated dynamic Gaussian blur, magnification zoom, downloads fan stack"),
            ("Top Bar and Apple Menu", "Native Apple logo menu, active app title, macOS accelerators, frosted panel blur"),
            ("Spotlight Search", "Keyboard-driven modal search (Super+Space) with calculator, files, and web fallback"),
            ("Window Management", "Anti-aliased squircle corners, outer screen margins, maximized gap retention, drop shadows"),
            ("AMOLED Dark Theme", "Pure midnight palette (#0c0d12) synchronized across GTK 2, 3, 4, Shell, and Flatpak")
        ]:
            r = Adw.ActionRow(title=feat, subtitle=desc)
            badge = Gtk.Label(label="Integrated")
            badge.add_css_class("pill")
            r.add_suffix(badge)
            summary_group.add(r)

    def _apply_preset_sonoma(self):
        self.bridge.set_icon_size(60)
        self.bridge.set_magnification(2.6)
        self.bridge.set_autohide_mode("dodge")
        self.bridge.set_gap_size(12)
        self.bridge.set_corner_radius(16)
        self.bridge.set_corner_smoothing(0.8)
        self.bridge.set_corner_border_width(1)

    def _apply_preset_compact(self):
        self.bridge.set_icon_size(46)
        self.bridge.set_magnification(2.0)
        self.bridge.set_autohide_mode("always")
        self.bridge.set_gap_size(6)
        self.bridge.set_corner_radius(12)
        self.bridge.set_corner_smoothing(0.6)
        self.bridge.set_corner_border_width(1)

    # ── 2. DOCK SETTINGS ──────────────────────────────────────────────────
    def _build_dock_page(self):
        page = Adw.PreferencesPage()
        self.stack.add_titled_with_icon(page, "dock", "Dock", "view-app-grid-symbolic")
        self._add_nav_item("dock", "Dock", "view-app-grid-symbolic")

        # Master Switch
        top_group = Adw.PreferencesGroup(title="macOS Floating Glass Dock")
        page.add(top_group)

        dock_en = Adw.SwitchRow(title="Enable Dock", subtitle="Show macOS-style floating dock")
        dock_en.set_active(self.bridge.get_dock_enabled())
        dock_en.connect("notify::active", lambda s, p: self.bridge.set_dock_enabled(s.get_active()))
        top_group.add(dock_en)

        # Group: Layout & Alignment
        geom_group = Adw.PreferencesGroup(title="Layout and Geometry")
        page.add(geom_group)

        pos_row = Adw.ComboRow(title="Screen Position")
        pos_row.set_model(Gtk.StringList.new(["Bottom", "Left", "Right"]))
        cur_pos = self.bridge.get_dock_position()
        pos_idx = 0 if cur_pos == "bottom" else (1 if cur_pos == "left" else 2)
        pos_row.set_selected(pos_idx)
        pos_row.connect("notify::selected", lambda r, p: self.bridge.set_dock_position(["bottom", "left", "right"][r.get_selected()]))
        geom_group.add(pos_row)

        align_row = Adw.ComboRow(title="Dock Alignment")
        align_row.set_model(Gtk.StringList.new(["Center", "Start", "End"]))
        cur_align = self.bridge.get_dock_alignment()
        align_idx = 0 if cur_align == "center" else (1 if cur_align == "start" else 2)
        align_row.set_selected(align_idx)
        align_row.connect("notify::selected", lambda r, p: self.bridge.set_dock_alignment(["center", "start", "end"][r.get_selected()]))
        geom_group.add(align_row)

        size_row = Adw.SpinRow(
            title="Resting Icon Size",
            subtitle="Base icon diameter in pixels",
            adjustment=Gtk.Adjustment(lower=24, upper=128, step_increment=4, value=self.bridge.get_icon_size())
        )
        size_row.connect("notify::value", lambda r, p: self.bridge.set_icon_size(int(r.get_value())))
        geom_group.add(size_row)

        spacing_row = Adw.SpinRow(
            title="Icon Spacing",
            subtitle="Horizontal gap between neighboring icons",
            adjustment=Gtk.Adjustment(lower=0, upper=48, step_increment=2, value=self.bridge.get_icon_spacing())
        )
        spacing_row.connect("notify::value", lambda r, p: self.bridge.set_icon_spacing(int(r.get_value())))
        geom_group.add(spacing_row)

        margin_row = Adw.SpinRow(
            title="Edge Floating Margin",
            subtitle="Floating gap between dock and monitor edge",
            adjustment=Gtk.Adjustment(lower=0, upper=24, step_increment=1, value=self.bridge.get_edge_margin())
        )
        margin_row.connect("notify::value", lambda r, p: self.bridge.set_edge_margin(int(r.get_value())))
        geom_group.add(margin_row)

        scale_row = Adw.SpinRow(
            title="Overall Dock Scale",
            subtitle="Scale multiplier for icons, padding, and pill",
            adjustment=Gtk.Adjustment(lower=0.5, upper=2.0, step_increment=0.05, value=self.bridge.get_dock_scale())
        )
        scale_row.connect("notify::value", lambda r, p: self.bridge.set_dock_scale(r.get_value()))
        geom_group.add(scale_row)

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

        mag_row = Adw.SpinRow(
            title="Peak Magnification Multiplier",
            subtitle="Peak magnification factor directly under cursor (e.g. 2.6x)",
            adjustment=Gtk.Adjustment(lower=1.0, upper=3.5, step_increment=0.1, value=self.bridge.get_magnification())
        )
        mag_row.connect("notify::value", lambda r, p: self.bridge.set_magnification(r.get_value()))
        phys_group.add(mag_row)

        zoom_range = Adw.SpinRow(
            title="Magnification Spread Radius",
            subtitle="Gaussian zoom propagation distance in pixels",
            adjustment=Gtk.Adjustment(lower=40, upper=500, step_increment=10, value=self.bridge.get_zoom_range())
        )
        zoom_range.connect("notify::value", lambda r, p: self.bridge.set_zoom_range(int(r.get_value())))
        phys_group.add(zoom_range)

        curve_row = Adw.SpinRow(
            title="Magnification Curve Shape",
            subtitle="Sharpness of zoom falloff curve (higher = sharper peak)",
            adjustment=Gtk.Adjustment(lower=0.5, upper=5.0, step_increment=0.1, value=self.bridge.get_magnification_curve())
        )
        curve_row.connect("notify::value", lambda r, p: self.bridge.set_magnification_curve(r.get_value()))
        phys_group.add(curve_row)

        spring_tens = Adw.SpinRow(
            title="Spring Tension",
            subtitle="Physics stiffness for magnification and bounce animations",
            adjustment=Gtk.Adjustment(lower=0.1, upper=1.0, step_increment=0.05, value=self.bridge.get_spring_tension())
        )
        spring_tens.connect("notify::value", lambda r, p: self.bridge.set_spring_tension(r.get_value()))
        phys_group.add(spring_tens)

        spring_damp = Adw.SpinRow(
            title="Spring Damping",
            subtitle="Physics damping factor (1.0 = critically damped without overshoot)",
            adjustment=Gtk.Adjustment(lower=0.2, upper=1.0, step_increment=0.05, value=self.bridge.get_spring_damping())
        )
        spring_damp.connect("notify::value", lambda r, p: self.bridge.set_spring_damping(r.get_value()))
        phys_group.add(spring_damp)

        lift_row = Adw.SpinRow(
            title="Hover Icon Lift",
            subtitle="Vertical displacement in pixels when hovered",
            adjustment=Gtk.Adjustment(lower=0, upper=24, step_increment=2, value=self.bridge.get_hover_lift())
        )
        lift_row.connect("notify::value", lambda r, p: self.bridge.set_hover_lift(int(r.get_value())))
        phys_group.add(lift_row)

        bounce_h = Adw.SpinRow(
            title="App Launch Bounce Height",
            subtitle="Peak launch bounce elevation in pixels (0 disables bounce)",
            adjustment=Gtk.Adjustment(lower=0, upper=80, step_increment=5, value=self.bridge.get_bounce_height())
        )
        bounce_h.connect("notify::value", lambda r, p: self.bridge.set_bounce_height(int(r.get_value())))
        phys_group.add(bounce_h)

        bounce_dec = Adw.SpinRow(
            title="Bounce Decay Factor",
            subtitle="Energy retention per hop (higher = gentler, longer bounces)",
            adjustment=Gtk.Adjustment(lower=0.30, upper=0.95, step_increment=0.05, value=self.bridge.get_bounce_decay())
        )
        bounce_dec.connect("notify::value", lambda r, p: self.bridge.set_bounce_decay(r.get_value()))
        phys_group.add(bounce_dec)

        # Group: Glass Pill & Appearance
        pill_group = Adw.PreferencesGroup(title="Glass Pill and Surface Appearance")
        page.add(pill_group)

        radius_row = Adw.SpinRow(
            title="Dock Pill Corner Radius",
            subtitle="Curvature rounding radius for dock background",
            adjustment=Gtk.Adjustment(lower=0, upper=40, step_increment=1, value=self.bridge.get_dock_radius())
        )
        radius_row.connect("notify::value", lambda r, p: self.bridge.set_dock_radius(int(r.get_value())))
        pill_group.add(radius_row)

        opac_row = Adw.SpinRow(
            title="Glass Pill Opacity",
            subtitle="Background translucency factor",
            adjustment=Gtk.Adjustment(lower=0.05, upper=1.0, step_increment=0.05, value=self.bridge.get_dock_opacity())
        )
        opac_row.connect("notify::value", lambda r, p: self.bridge.set_dock_opacity(r.get_value()))
        pill_group.add(opac_row)

        border_w = Adw.SpinRow(
            title="Pill Border Outline Width",
            subtitle="Glass border stroke thickness in pixels",
            adjustment=Gtk.Adjustment(lower=0, upper=6, step_increment=1, value=self.bridge.get_dock_border_width())
        )
        border_w.connect("notify::value", lambda r, p: self.bridge.set_dock_border_width(int(r.get_value())))
        pill_group.add(border_w)

        thick_auto = Adw.SwitchRow(title="Auto Pill Thickness", subtitle="Scale pill height automatically with resting icon size")
        thick_auto.set_active(self.bridge.get_pill_thickness_auto())
        thick_auto.connect("notify::active", lambda s, p: self.bridge.set_pill_thickness_auto(s.get_active()))
        pill_group.add(thick_auto)

        thick_row = Adw.SpinRow(
            title="Custom Pill Thickness",
            subtitle="Explicit dock pill depth when auto thickness is disabled",
            adjustment=Gtk.Adjustment(lower=36, upper=120, step_increment=4, value=self.bridge.get_pill_thickness())
        )
        thick_row.connect("notify::value", lambda r, p: self.bridge.set_pill_thickness(int(r.get_value())))
        pill_group.add(thick_row)

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

        delay_row = Adw.SpinRow(
            title="Autohide Delay",
            subtitle="Milliseconds before dock hides after pointer leaves",
            adjustment=Gtk.Adjustment(lower=0, upper=2000, step_increment=50, value=self.bridge.get_hide_delay())
        )
        delay_row.connect("notify::value", lambda r, p: self.bridge.set_hide_delay(int(r.get_value())))
        hide_group.add(delay_row)

        press_row = Adw.SpinRow(
            title="Edge Reveal Pressure",
            subtitle="Pressure barrier threshold in ms (0 = instant appearance)",
            adjustment=Gtk.Adjustment(lower=0, upper=1000, step_increment=25, value=self.bridge.get_reveal_pressure())
        )
        press_row.connect("notify::value", lambda r, p: self.bridge.set_reveal_pressure(int(r.get_value())))
        hide_group.add(press_row)

        handle_row = Adw.SwitchRow(title="Show Autohide Edge Handle", subtitle="Keep subtle dock glass border visible when hidden")
        handle_row.set_active(self.bridge.get_autohide_handle())
        handle_row.connect("notify::active", lambda s, p: self.bridge.set_autohide_handle(s.get_active()))
        hide_group.add(handle_row)

        dwell_row = Adw.SwitchRow(title="Pressure Sense Dwell", subtitle="Pointer must linger on screen edge before revealing")
        dwell_row.set_active(self.bridge.get_pressure_sense())
        dwell_row.connect("notify::active", lambda s, p: self.bridge.set_pressure_sense(s.get_active()))
        hide_group.add(dwell_row)

        lock_row = Adw.SwitchRow(title="Lock Dock Layout", subtitle="Prevent pinned icons from being dragged or rearranged")
        lock_row.set_active(self.bridge.get_dock_settings() if hasattr(self.bridge, "get_dock_settings") else False)
        hide_group.add(lock_row)

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

        ind_size = Adw.SpinRow(
            title="Indicator Dot Size",
            subtitle="Diameter in pixels",
            adjustment=Gtk.Adjustment(lower=3, upper=14, step_increment=1, value=self.bridge.get_indicator_size())
        )
        ind_size.connect("notify::value", lambda r, p: self.bridge.set_indicator_size(int(r.get_value())))
        ind_group.add(ind_size)

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

        down_max = Adw.SpinRow(
            title="Downloads Max Files",
            subtitle="Maximum files displayed in stack view",
            adjustment=Gtk.Adjustment(lower=3, upper=11, step_increment=1, value=self.bridge.get_downloads_max_files())
        )
        down_max.connect("notify::value", lambda r, p: self.bridge.set_downloads_max_files(int(r.get_value())))
        item_group.add(down_max)

        down_sort = Adw.ComboRow(title="Downloads Sort Order")
        down_sort.set_model(Gtk.StringList.new(["Newest First", "By Name", "By File Type"]))
        cur_sort = self.bridge.get_downloads_sort()
        sort_map = {"newest": 0, "name": 1, "type": 2}
        down_sort.set_selected(sort_map.get(cur_sort, 0))
        down_sort.connect("notify::selected", lambda r, p: self.bridge.set_downloads_sort(["newest", "name", "type"][r.get_selected()]))
        item_group.add(down_sort)

        mount_btn = Adw.SwitchRow(title="Show Mounted Drives", subtitle="Display mounted disks and disk images")
        mount_btn.set_active(self.bridge.get_show_mounted_devices())
        mount_btn.connect("notify::active", lambda s, p: self.bridge.set_show_mounted_devices(s.get_active()))
        item_group.add(mount_btn)

        remov_btn = Adw.SwitchRow(title="Show Removable Media", subtitle="Display USB sticks, phones, and digital cameras")
        remov_btn.set_active(self.bridge.get_show_removable_devices())
        remov_btn.connect("notify::active", lambda s, p: self.bridge.set_show_removable_devices(s.get_active()))
        item_group.add(remov_btn)

        net_btn = Adw.SwitchRow(title="Show Network Locations", subtitle="Display mounted network shares and servers")
        net_btn.set_active(self.bridge.get_show_network_devices())
        net_btn.connect("notify::active", lambda s, p: self.bridge.set_show_network_devices(s.get_active()))
        item_group.add(net_btn)

        # Group: Window Previews & Tooltips
        prev_group = Adw.PreferencesGroup(title="Window Previews and Tooltips")
        page.add(prev_group)

        prev_en = Adw.SwitchRow(title="Live Window Previews", subtitle="Show live window thumbnails on icon hover")
        prev_en.set_active(self.bridge.get_show_previews())
        prev_en.connect("notify::active", lambda s, p: self.bridge.set_show_previews(s.get_active()))
        prev_group.add(prev_en)

        prev_delay = Adw.SpinRow(
            title="Preview Delay",
            subtitle="Hover delay in ms before showing thumbnail",
            adjustment=Gtk.Adjustment(lower=100, upper=3000, step_increment=50, value=self.bridge.get_preview_delay())
        )
        prev_delay.connect("notify::value", lambda r, p: self.bridge.set_preview_delay(int(r.get_value())))
        prev_group.add(prev_delay)

        prev_size = Adw.SpinRow(
            title="Preview Max Size",
            subtitle="Maximum thumbnail width in pixels",
            adjustment=Gtk.Adjustment(lower=80, upper=400, step_increment=10, value=self.bridge.get_preview_size())
        )
        prev_size.connect("notify::value", lambda r, p: self.bridge.set_preview_size(int(r.get_value())))
        prev_group.add(prev_size)

        prev_close = Adw.SwitchRow(title="Close Button on Previews", subtitle="Show close button on top right of each thumbnail")
        prev_close.set_active(self.bridge.get_preview_close_buttons())
        prev_close.connect("notify::active", lambda s, p: self.bridge.set_preview_close_buttons(s.get_active()))
        prev_group.add(prev_close)

        tip_en = Adw.SwitchRow(title="Show Tooltips", subtitle="Show application title tooltip when hovering")
        tip_en.set_active(self.bridge.get_show_tooltip())
        tip_en.connect("notify::active", lambda s, p: self.bridge.set_show_tooltip(s.get_active()))
        prev_group.add(tip_en)

        tip_delay = Adw.SpinRow(
            title="Tooltip Delay",
            subtitle="Milliseconds before tooltip appears",
            adjustment=Gtk.Adjustment(lower=0, upper=2000, step_increment=25, value=self.bridge.get_tooltip_delay())
        )
        tip_delay.connect("notify::value", lambda r, p: self.bridge.set_tooltip_delay(int(r.get_value())))
        prev_group.add(tip_delay)

        genie_en = Adw.SwitchRow(title="Genie (Magic Lamp) Minimize Effect", subtitle="macOS magic lamp fluid minimize and restore animation")
        genie_en.set_active(self.bridge.get_enable_genie())
        genie_en.connect("notify::active", lambda s, p: self.bridge.set_enable_genie(s.get_active()))
        prev_group.add(genie_en)

        genie_dur = Adw.SpinRow(
            title="Genie Duration",
            subtitle="Magic lamp animation duration in ms",
            adjustment=Gtk.Adjustment(lower=50, upper=1000, step_increment=25, value=self.bridge.get_genie_duration())
        )
        genie_dur.connect("notify::value", lambda r, p: self.bridge.set_genie_duration(int(r.get_value())))
        prev_group.add(genie_dur)

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

        blur_rad = Adw.SpinRow(
            title="Blur Radius",
            subtitle="Frosted glass blur radius in pixels",
            adjustment=Gtk.Adjustment(lower=5, upper=100, step_increment=5, value=self.bridge.get_topbar_blur_radius())
        )
        blur_rad.connect("notify::value", lambda r, p: self.bridge.set_topbar_blur_radius(int(r.get_value())))
        pan_group.add(blur_rad)

        transp_row = Adw.SpinRow(
            title="Panel Transparency",
            subtitle="Background translucency factor",
            adjustment=Gtk.Adjustment(lower=0.0, upper=1.0, step_increment=0.05, value=self.bridge.get_topbar_transparency())
        )
        transp_row.connect("notify::value", lambda r, p: self.bridge.set_topbar_transparency(r.get_value()))
        pan_group.add(transp_row)

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

        # Modal Layout & Geometry
        mod_group = Adw.PreferencesGroup(title="Modal Geometry and Ranking")
        page.add(mod_group)

        w_row = Adw.SpinRow(
            title="Search Bar Width",
            subtitle="Modal window width in pixels",
            adjustment=Gtk.Adjustment(lower=400, upper=1200, step_increment=20, value=self.bridge.get_spotlight_width())
        )
        w_row.connect("notify::value", lambda r, p: self.bridge.set_spotlight_width(int(r.get_value())))
        mod_group.add(w_row)

        pos_row = Adw.ComboRow(title="Vertical Placement")
        pos_row.set_model(Gtk.StringList.new(["Center", "Top", "Bottom"]))
        cur_pos = self.bridge.get_spotlight_position()
        pos_map = {"center": 0, "top": 1, "bottom": 2}
        pos_row.set_selected(pos_map.get(cur_pos, 0))
        pos_row.connect("notify::selected", lambda r, p: self.bridge.set_spotlight_position(["center", "top", "bottom"][r.get_selected()]))
        mod_group.add(pos_row)

        opac_row = Adw.SpinRow(
            title="Background Glass Opacity",
            subtitle="Modal glass surface opacity percentage",
            adjustment=Gtk.Adjustment(lower=65, upper=100, step_increment=5, value=self.bridge.get_spotlight_opacity())
        )
        opac_row.connect("notify::value", lambda r, p: self.bridge.set_spotlight_opacity(int(r.get_value())))
        mod_group.add(opac_row)

        res_row = Adw.SpinRow(
            title="Maximum Search Results",
            subtitle="Number of results displayed simultaneously",
            adjustment=Gtk.Adjustment(lower=3, upper=20, step_increment=1, value=self.bridge.get_spotlight_max_results())
        )
        res_row.connect("notify::value", lambda r, p: self.bridge.set_spotlight_max_results(int(r.get_value())))
        mod_group.add(res_row)

        rank_row = Adw.SwitchRow(title="Adaptive Ranking", subtitle="Learn and prioritize frequently selected applications")
        rank_row.set_active(self.bridge.get_spotlight_adaptive_ranking())
        rank_row.connect("notify::active", lambda s, p: self.bridge.set_spotlight_adaptive_ranking(s.get_active()))
        mod_group.add(rank_row)

        # Search Providers
        prov_group = Adw.PreferencesGroup(title="Search Providers and Fallbacks")
        page.add(prov_group)

        engine_row = Adw.ComboRow(title="Default Web Search Engine")
        engine_row.set_model(Gtk.StringList.new(["Google", "DuckDuckGo", "Bing", "Brave", "Ecosia", "Kagi"]))
        cur_e = self.bridge.get_spotlight_search_engine()
        e_map = {"google": 0, "duckduckgo": 1, "bing": 2, "brave": 3, "ecosia": 4, "kagi": 5}
        engine_row.set_selected(e_map.get(cur_e, 0))
        engine_row.connect("notify::selected", lambda r, p: self.bridge.set_spotlight_search_engine(["google", "duckduckgo", "bing", "brave", "ecosia", "kagi"][r.get_selected()]))
        prov_group.add(engine_row)

        for title, sub, getter, setter in [
            ("Search Applications", "Find and launch desktop apps", self.bridge.get_spotlight_search_apps, self.bridge.set_spotlight_search_apps),
            ("Search Open Windows", "Switch directly to open windows across workspaces", self.bridge.get_spotlight_search_windows, self.bridge.set_spotlight_search_windows),
            ("Search Files and Documents", "Query local files, downloads, and recent documents", self.bridge.get_spotlight_search_files, self.bridge.set_spotlight_search_files),
            ("Search Clipboard History", "Find and paste previously copied text clips", self.bridge.get_spotlight_search_clipboard, self.bridge.set_spotlight_search_clipboard),
            ("Inline Calculator", "Evaluate mathematical expressions directly in search bar", self.bridge.get_spotlight_search_calc, self.bridge.set_spotlight_search_calc),
            ("Weather Forecast", "Instant weather forecast lookups via Open-Meteo", self.bridge.get_spotlight_search_weather, self.bridge.set_spotlight_search_weather),
            ("Dictionary Definitions", "Look up definitions of English words inline", self.bridge.get_spotlight_search_dictionary, self.bridge.set_spotlight_search_dictionary),
            ("Currency Conversions", "Live foreign currency exchange rates", self.bridge.get_spotlight_search_currency, self.bridge.set_spotlight_search_currency),
            ("System Commands", "Trigger lock, sleep, restart, and power off commands", self.bridge.get_spotlight_search_actions, self.bridge.set_spotlight_search_actions),
            ("GNOME Search Providers", "Include Contacts, Calendar, and GNOME Files results", self.bridge.get_spotlight_gnome_providers, self.bridge.set_spotlight_gnome_providers)
        ]:
            sw = Adw.SwitchRow(title=title, subtitle=sub)
            sw.set_active(getter())
            sw.connect("notify::active", lambda s, p, fn=setter: fn(s.get_active()))
            prov_group.add(sw)

    # ── 5. WINDOW MANAGEMENT ──────────────────────────────────────────────
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
        uni_gap.connect("notify::active", lambda s, p: self.bridge.set_gap_uniform(s.get_active()))
        gaps_group.add(uni_gap)

        gap_sz = Adw.SpinRow(
            title="Uniform Gap Size",
            subtitle="Margin in pixels applied to all edges",
            adjustment=Gtk.Adjustment(lower=0, upper=200, step_increment=2, value=self.bridge.get_gap_size())
        )
        gap_sz.connect("notify::value", lambda r, p: self.bridge.set_gap_size(int(r.get_value())))
        gaps_group.add(gap_sz)

        max_gaps = Adw.SwitchRow(title="Retain Gaps on Maximized Windows", subtitle="Preserve outer padding even when window is maximized")
        max_gaps.set_active(self.bridge.get_gaps_maximized())
        max_gaps.connect("notify::active", lambda s, p: self.bridge.set_gaps_maximized(s.get_active()))
        gaps_group.add(max_gaps)

        t_gap = Adw.SpinRow(
            title="Custom Top Margin",
            subtitle="Top edge gap in pixels",
            adjustment=Gtk.Adjustment(lower=0, upper=200, step_increment=2, value=self.bridge.get_gap_top())
        )
        t_gap.connect("notify::value", lambda r, p: self.bridge.set_gap_top(int(r.get_value())))
        gaps_group.add(t_gap)

        b_gap = Adw.SpinRow(
            title="Custom Bottom Margin",
            subtitle="Bottom edge gap in pixels",
            adjustment=Gtk.Adjustment(lower=0, upper=200, step_increment=2, value=self.bridge.get_gap_bottom())
        )
        b_gap.connect("notify::value", lambda r, p: self.bridge.set_gap_bottom(int(r.get_value())))
        gaps_group.add(b_gap)

        l_gap = Adw.SpinRow(
            title="Custom Left Margin",
            subtitle="Left edge gap in pixels",
            adjustment=Gtk.Adjustment(lower=0, upper=200, step_increment=2, value=self.bridge.get_gap_left())
        )
        l_gap.connect("notify::value", lambda r, p: self.bridge.set_gap_left(int(r.get_value())))
        gaps_group.add(l_gap)

        r_gap = Adw.SpinRow(
            title="Custom Right Margin",
            subtitle="Right edge gap in pixels",
            adjustment=Gtk.Adjustment(lower=0, upper=200, step_increment=2, value=self.bridge.get_gap_right())
        )
        r_gap.connect("notify::value", lambda r, p: self.bridge.set_gap_right(int(r.get_value())))
        gaps_group.add(r_gap)

        # Rounded Corners & Borders
        corn_group = Adw.PreferencesGroup(title="Rounded Corners and Window Borders")
        page.add(corn_group)

        corn_en = Adw.SwitchRow(title="Enable Rounded Corners", subtitle="Render anti-aliased squircle corners on application windows")
        corn_en.set_active(self.bridge.get_corners_enabled())
        corn_en.connect("notify::active", lambda s, p: self.bridge.set_corners_enabled(s.get_active()))
        corn_group.add(corn_en)

        rad_row = Adw.SpinRow(
            title="Window Corner Radius",
            subtitle="Corner curvature radius in pixels",
            adjustment=Gtk.Adjustment(lower=0, upper=40, step_increment=1, value=self.bridge.get_corner_radius())
        )
        rad_row.connect("notify::value", lambda r, p: self.bridge.set_corner_radius(int(r.get_value())))
        corn_group.add(rad_row)

        smooth_row = Adw.SpinRow(
            title="Apple Squircle Smoothing",
            subtitle="Curvature exponent for super-ellipse squircle corners (0.8 = authentic Apple curvature)",
            adjustment=Gtk.Adjustment(lower=0.0, upper=1.0, step_increment=0.05, value=self.bridge.get_corner_smoothing())
        )
        smooth_row.connect("notify::value", lambda r, p: self.bridge.set_corner_smoothing(r.get_value()))
        corn_group.add(smooth_row)

        border_w = Adw.SpinRow(
            title="Window Border Stroke Width",
            subtitle="Subtle macOS window border in pixels",
            adjustment=Gtk.Adjustment(lower=0, upper=10, step_increment=1, value=self.bridge.get_corner_border_width())
        )
        border_w.connect("notify::value", lambda r, p: self.bridge.set_corner_border_width(int(r.get_value())))
        corn_group.add(border_w)

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

        f_v = Adw.SpinRow(
            title="Focused Window Vertical Offset",
            subtitle="Vertical downward elevation in pixels",
            adjustment=Gtk.Adjustment(lower=0, upper=40, step_increment=1, value=self.bridge.get_focused_shadow_v_offset())
        )
        f_v.connect("notify::value", lambda r, p: self.bridge.set_focused_shadow_v_offset(int(r.get_value())))
        shad_group.add(f_v)

        f_blur = Adw.SpinRow(
            title="Focused Shadow Blur Radius",
            subtitle="Gaussian shadow softness for active window",
            adjustment=Gtk.Adjustment(lower=0, upper=80, step_increment=2, value=self.bridge.get_focused_shadow_blur())
        )
        f_blur.connect("notify::value", lambda r, p: self.bridge.set_focused_shadow_blur(int(r.get_value())))
        shad_group.add(f_blur)

        f_opac = Adw.SpinRow(
            title="Focused Shadow Opacity",
            subtitle="Shadow darkness percentage",
            adjustment=Gtk.Adjustment(lower=0, upper=100, step_increment=5, value=self.bridge.get_focused_shadow_opacity())
        )
        f_opac.connect("notify::value", lambda r, p: self.bridge.set_focused_shadow_opacity(int(r.get_value())))
        shad_group.add(f_opac)

        u_v = Adw.SpinRow(
            title="Background Window Vertical Offset",
            subtitle="Downward elevation for inactive windows",
            adjustment=Gtk.Adjustment(lower=0, upper=40, step_increment=1, value=self.bridge.get_unfocused_shadow_v_offset())
        )
        u_v.connect("notify::value", lambda r, p: self.bridge.set_unfocused_shadow_v_offset(int(r.get_value())))
        shad_group.add(u_v)

        u_blur = Adw.SpinRow(
            title="Background Shadow Blur Radius",
            subtitle="Shadow softness for inactive windows",
            adjustment=Gtk.Adjustment(lower=0, upper=80, step_increment=2, value=self.bridge.get_unfocused_shadow_blur())
        )
        u_blur.connect("notify::value", lambda r, p: self.bridge.set_unfocused_shadow_blur(int(r.get_value())))
        shad_group.add(u_blur)

        u_opac = Adw.SpinRow(
            title="Background Shadow Opacity",
            subtitle="Shadow darkness for inactive windows",
            adjustment=Gtk.Adjustment(lower=0, upper=100, step_increment=5, value=self.bridge.get_unfocused_shadow_opacity())
        )
        u_opac.connect("notify::value", lambda r, p: self.bridge.set_unfocused_shadow_opacity(int(r.get_value())))
        shad_group.add(u_opac)

    # ── 6. GLASS BLUR ENGINE ──────────────────────────────────────────────
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

        import shutil
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

        sigma_row = Adw.SpinRow(
            title="Blur Sigma Radius",
            subtitle="Gaussian blur spread intensity",
            adjustment=Gtk.Adjustment(lower=10, upper=80, step_increment=2, value=self.bridge.get_blur_sigma())
        )
        sigma_row.connect("notify::value", lambda r, p: self.bridge.set_blur_sigma(int(r.get_value())))
        tune_group.add(sigma_row)

        bright_row = Adw.SpinRow(
            title="Glass Brightness Multiplier",
            subtitle="Luminance factor behind glass surfaces",
            adjustment=Gtk.Adjustment(lower=0.2, upper=1.0, step_increment=0.05, value=self.bridge.get_blur_brightness())
        )
        bright_row.connect("notify::value", lambda r, p: self.bridge.set_blur_brightness(r.get_value()))
        tune_group.add(bright_row)

        noise_row = Adw.SpinRow(
            title="Film Grain and Noise",
            subtitle="Subtle analog texture on glass surfaces",
            adjustment=Gtk.Adjustment(lower=0.0, upper=0.5, step_increment=0.02, value=self.bridge.get_blur_noise_amount())
        )
        noise_row.connect("notify::value", lambda r, p: self.bridge.set_blur_noise_amount(r.get_value()))
        tune_group.add(noise_row)

        surf_group = Adw.PreferencesGroup(title="Target Desktop Surfaces")
        page.add(surf_group)

        for title, sub, getter, setter in [
            ("Top Menu Bar Blur", "Apply dynamic frosted blur behind the top panel", self.bridge.get_blur_panel, self.bridge.set_blur_panel),
            ("Dock Pill Blur", "Apply Gaussian glass blur behind dock pill", self.bridge.get_blur_dock, self.bridge.set_blur_dock),
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

        refr_str = Adw.SpinRow(
            title="Refraction Strength",
            subtitle="Optical bending scale along curved edges",
            adjustment=Gtk.Adjustment(lower=0.0, upper=1.0, step_increment=0.02, value=self.bridge.get_blur_refraction_strength())
        )
        refr_str.connect("notify::value", lambda r, p: self.bridge.set_blur_refraction_strength(r.get_value()))
        liq_group.add(refr_str)

        disp_row = Adw.SpinRow(
            title="Chromatic Color Dispersion",
            subtitle="Prism RGB channel wavelength splitting on glass bevels",
            adjustment=Gtk.Adjustment(lower=0.0, upper=0.5, step_increment=0.01, value=self.bridge.get_blur_chromatic_dispersion())
        )
        disp_row.connect("notify::value", lambda r, p: self.bridge.set_blur_chromatic_dispersion(r.get_value()))
        liq_group.add(disp_row)

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

        m_rad = Adw.SpinRow(
            title="Menu Corner Radius",
            subtitle="Curvature radius in pixels for context menus, Kiwi menu, and popups",
            adjustment=Gtk.Adjustment(lower=6, upper=32, step_increment=1, value=self.bridge.get_menu_corner_radius())
        )
        m_rad.connect("notify::value", lambda r, p: self.bridge.set_menu_corner_radius(int(r.get_value())))
        menu_group.add(m_rad)

        m_bw = Adw.SpinRow(
            title="Menu Border Width",
            subtitle="Hairline stroke width in pixels",
            adjustment=Gtk.Adjustment(lower=0, upper=4, step_increment=1, value=self.bridge.get_menu_border_width())
        )
        m_bw.connect("notify::value", lambda r, p: self.bridge.set_menu_border_width(int(r.get_value())))
        menu_group.add(m_bw)

        m_bopac = Adw.SpinRow(
            title="Menu Border Opacity",
            subtitle="Edge stroke alpha transparency factor",
            adjustment=Gtk.Adjustment(lower=0.0, upper=1.0, step_increment=0.02, value=self.bridge.get_menu_border_opacity())
        )
        m_bopac.connect("notify::value", lambda r, p: self.bridge.set_menu_border_opacity(r.get_value()))
        menu_group.add(m_bopac)

        m_spec = Adw.SwitchRow(
            title="Top Specular Highlight Rim",
            subtitle="Render subtle 1px overhead light reflection along the upper glass bevel"
        )
        m_spec.set_active(self.bridge.get_menu_specular_highlight())
        m_spec.connect("notify::active", lambda s, p: self.bridge.set_menu_specular_highlight(s.get_active()))
        menu_group.add(m_spec)

        m_bgopac = Adw.SpinRow(
            title="Menu Glass Translucency",
            subtitle="Background glass opacity for menus and dropdowns",
            adjustment=Gtk.Adjustment(lower=0.2, upper=1.0, step_increment=0.05, value=self.bridge.get_menu_bg_opacity())
        )
        m_bgopac.connect("notify::value", lambda r, p: self.bridge.set_menu_bg_opacity(r.get_value()))
        menu_group.add(m_bgopac)

        qs_rad = Adw.SpinRow(
            title="Control Center Corner Radius",
            subtitle="Curvature radius for Quick Settings popup card",
            adjustment=Gtk.Adjustment(lower=12, upper=40, step_increment=2, value=self.bridge.get_quick_settings_radius())
        )
        qs_rad.connect("notify::value", lambda r, p: self.bridge.set_quick_settings_radius(int(r.get_value())))
        menu_group.add(qs_rad)

        notif_rad = Adw.SpinRow(
            title="Notification Banner Corner Radius",
            subtitle="Curvature radius for desktop notification cards",
            adjustment=Gtk.Adjustment(lower=8, upper=32, step_increment=1, value=self.bridge.get_notification_radius())
        )
        notif_rad.connect("notify::value", lambda r, p: self.bridge.set_notification_radius(int(r.get_value())))
        menu_group.add(notif_rad)

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
        self.stack.add_titled_with_icon(page, "system", "System and Integration", "emblem-system-symbolic")
        self._add_nav_item("system", "System and Integration", "emblem-system-symbolic")

        sys_group = Adw.PreferencesGroup(title="Session and Autostart")
        page.add(sys_group)

        autostart_row = Adw.SwitchRow(
            title="Launch Mak at Login",
            subtitle="Start Mak Control Center silently in background when you sign in"
        )
        autostart_row.set_active(autostart_manager.is_autostart_enabled())
        autostart_row.connect("notify::active", lambda s, p: autostart_manager.set_autostart_enabled(s.get_active()))
        sys_group.add(autostart_row)

        reset_row = Adw.ActionRow(
            title="Reset to macOS Defaults",
            subtitle="Restore all dock, top bar, spotlight, corners, and gaps settings to factory defaults"
        )
        reset_btn = Gtk.Button(label="Restore Defaults")
        reset_btn.add_css_class("destructive-action")
        reset_btn.add_css_class("pill")
        reset_btn.connect("clicked", lambda *a: self._reset_defaults())
        reset_row.add_suffix(reset_btn)
        sys_group.add(reset_row)

        about_group = Adw.PreferencesGroup(title="About Mak macOS Suite")
        page.add(about_group)

        ver_row = Adw.ActionRow(title="Mak Suite Version", subtitle="Version 1.0 (Sonoma and Sequoia unified edition)")
        badge = Gtk.Label(label="Unified Architecture")
        badge.add_css_class("pill")
        ver_row.add_suffix(badge)
        about_group.add(ver_row)

    def _install_rounded_blur(self):
        import shutil, subprocess
        cmd = "echo '==> Installing gnome-rounded-blur for macOS Liquid Dynamic Blur...'; yay -S --needed gnome-rounded-blur; echo ''; echo 'Installation complete! Please log out and back in to load the new blur library.'; echo 'Press Enter to close...'; read"
        for term in ["gnome-terminal", "kgx", "kitty", "xterm", "foot"]:
            if shutil.which(term):
                if term == "gnome-terminal":
                    subprocess.Popen([term, "--", "bash", "-c", cmd])
                else:
                    subprocess.Popen([term, "-e", f"bash -c \"{cmd}\""])
                return

    def _reset_defaults(self):
        self._apply_preset_sonoma()

class MakApplication(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id="org.gnome.shell.extensions.mak.app",
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = MakAppWindow(application=self)
        win.present()

if __name__ == "__main__":
    app = MakApplication()
    sys.exit(app.run(sys.argv))
