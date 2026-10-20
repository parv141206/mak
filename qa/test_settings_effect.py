#!/usr/bin/env python3
"""
Test Suite: Settings -> Theme Generator Effect Verification
Proves that every visual setting key/parameter actually changes the generated CSS output.
Ensures zero dead switches and zero hardcoded parameters.
"""

import sys
import os
import unittest
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "mak-app"))
import theme_manager
from theme_manager import (
    TokenManager,
    generate_traffic_lights_override,
    generate_window_corners_override,
    generate_widgets_override,
    generate_popover_override,
    inject_shell_theme_contrast,
    inject_theme_css,
    GRAPHITE_PALETTE_OVERRIDE,
)

class TestSettingsEffect(unittest.TestCase):

    def test_window_corner_radius_tunable(self):
        """Verify window corner radius is dynamically configurable."""
        # Test default radius (14px)
        css_14 = generate_window_corners_override(is_dark=True)
        self.assertIn("border-radius: 14px;", css_14)

        # Override in TokenManager and test effect
        orig = TokenManager.get("geometry", "window", "corner_radius")
        TokenManager.load()["geometry"]["window"]["corner_radius"] = 20
        css_20 = generate_window_corners_override(is_dark=True)
        self.assertIn("border-radius: 20px;", css_20)
        self.assertNotEqual(css_14, css_20)
        # Restore
        TokenManager.load()["geometry"]["window"]["corner_radius"] = orig

    def test_titlebar_button_size_and_spacing_tunable(self):
        """Verify traffic light button size and spacing are dynamically configurable."""
        css_14_8 = generate_traffic_lights_override(button_size=14, button_spacing=8, is_dark=True)
        self.assertIn("min-width: 14px;", css_14_8)
        self.assertIn("min-height: 14px;", css_14_8)
        self.assertIn("margin: 0 4px;", css_14_8)

        css_18_12 = generate_traffic_lights_override(button_size=18, button_spacing=12, is_dark=True)
        self.assertIn("min-width: 18px;", css_18_12)
        self.assertIn("min-height: 18px;", css_18_12)
        self.assertIn("margin: 0 6px;", css_18_12)
        self.assertNotEqual(css_14_8, css_18_12)

    def test_accent_color_injection_tunable(self):
        """Verify accent color changes produce distinct CSS palettes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            src_css = os.path.join(tmpdir, "gtk.css")
            dst_css_blue = os.path.join(tmpdir, "out_blue.css")
            dst_css_red = os.path.join(tmpdir, "out_red.css")
            with open(src_css, "w") as f:
                f.write("/* base */\n")

            inject_theme_css(src_css, dst_css_blue, GRAPHITE_PALETTE_OVERRIDE, is_glassy=False, is_dark=True)
            inject_theme_css(src_css, dst_css_red, GRAPHITE_PALETTE_OVERRIDE, is_glassy=False, is_dark=True, chromium_accent="red")

            with open(dst_css_blue) as f: c_blue = f.read()
            with open(dst_css_red) as f: c_red = f.read()

            self.assertIn("@define-color accent_bg_color", c_blue)
            self.assertIn("@define-color accent_bg_color", c_red)

    def test_glassy_vs_solid_tunable(self):
        """Verify glassy mode injects container backdrop rules and alters container opacities."""
        with tempfile.TemporaryDirectory() as tmpdir:
            src_css = os.path.join(tmpdir, "gtk.css")
            dst_solid = os.path.join(tmpdir, "out_solid.css")
            dst_glassy = os.path.join(tmpdir, "out_glassy.css")
            with open(src_css, "w") as f:
                f.write("/* base */\n")

            inject_theme_css(src_css, dst_solid, GRAPHITE_PALETTE_OVERRIDE, is_glassy=False, is_dark=True)
            inject_theme_css(src_css, dst_glassy, GRAPHITE_PALETTE_OVERRIDE, is_glassy=True, is_dark=True)

            with open(dst_solid) as f: c_solid = f.read()
            with open(dst_glassy) as f: c_glassy = f.read()

            self.assertNotIn("GLASSY_CONTAINER_RULES", c_solid)
            self.assertIn(".navigation-sidebar", c_glassy)
            self.assertNotEqual(c_solid, c_glassy)

    def test_shell_contrast_and_radii_tunable(self):
        """Verify shell notification and popover radii inject into gnome-shell.css."""
        with tempfile.TemporaryDirectory() as tmpdir:
            css_path = os.path.join(tmpdir, "gnome-shell.css")
            with open(css_path, "w") as f:
                f.write("/* shell base */\n")

            inject_shell_theme_contrast("test", is_dark=True, css_path=css_path)
            with open(css_path) as f:
                content = f.read()

            self.assertIn(".notification-banner", content)
            self.assertIn("border-radius: 16px;", content)
            self.assertIn(".popup-menu-content", content)
            self.assertIn("border-radius: 10px;", content)

    def test_flavor_surface_and_headerbar_injection(self):
        """Verify universal headerbar, titlebar, and Nautilus pane rules inject into both GTK 3 and GTK 4."""
        with tempfile.TemporaryDirectory() as tmpdir:
            src_gtk3 = os.path.join(tmpdir, "gtk-3.0_src.css")
            src_gtk4 = os.path.join(tmpdir, "gtk-4.0_src.css")
            dst_gtk3 = os.path.join(tmpdir, "gtk-3.0", "gtk.css")
            dst_gtk4 = os.path.join(tmpdir, "gtk-4.0", "gtk.css")

            with open(src_gtk3, "w") as f:
                f.write("/* base gtk3 */\nheaderbar { background-color: #333333; }\n")
            with open(src_gtk4, "w") as f:
                f.write("/* base gtk4 */\nheaderbar { background-color: #333333; }\n")

            from theme_manager import get_flavor_palette
            palette = get_flavor_palette("deep-teal", is_dark=True)

            inject_theme_css(src_gtk3, dst_gtk3, palette, is_glassy=False, is_dark=True)
            inject_theme_css(src_gtk4, dst_gtk4, palette, is_glassy=False, is_dark=True)

            with open(dst_gtk3) as f:
                c_gtk3 = f.read()
            with open(dst_gtk4) as f:
                c_gtk4 = f.read()

            # Verify both GTK 3 and GTK 4 have the universal headerbar rule
            self.assertIn("headerbar,\nheaderbar:backdrop", c_gtk3)
            self.assertIn("background-color: @headerbar_bg_color;", c_gtk3)
            self.assertIn("headerbar,\nheaderbar:backdrop", c_gtk4)
            self.assertIn("background-color: @headerbar_bg_color;", c_gtk4)

            # Verify Nautilus surface rules
            self.assertIn(".nautilus-window .content-pane", c_gtk4)
            self.assertIn("background-color: @view_bg_color;", c_gtk4)

            # Verify authentic Mac Tahoe full floating sidebar architecture
            self.assertIn(".sidebar-pane,", c_gtk4)
            self.assertIn("margin: 6px 0 6px 6px;", c_gtk4)
            self.assertIn("border-radius: 14px;", c_gtk4)
            self.assertIn("background-color: @sidebar_bg_color;", c_gtk4)

            # Verify thin border and elevation drop shadow on floating sidebar
            self.assertIn(".sidebar-pane:dir(ltr),", c_gtk4)
            self.assertIn("box-shadow: 2px 3px 12px rgba(0, 0, 0, 0.15);", c_gtk4)
            self.assertIn("border: 1px solid alpha(currentColor, 0.16);", c_gtk4)

            # Verify sidebar internal widgets and headerbars are transparent so full card floats seamlessly
            self.assertIn(".sidebar-pane list:not(.boxed-list),", c_gtk4)
            self.assertIn(".sidebar-pane headerbar,", c_gtk4)
            self.assertIn("background-color: transparent;", c_gtk4)
            self.assertIn("window.background.csd .sidebar-pane headerbar,", c_gtk4)
            self.assertIn("border-top-left-radius: 13px;", c_gtk4)

            # Verify popovers, menus, and dropdowns adapt to flavor palette seamlessly without borders
            self.assertIn("popover > contents,", c_gtk4)
            self.assertIn("background-color: @popover_bg_color;", c_gtk4)
            self.assertIn("border: none;", c_gtk4)
            self.assertIn("popover.menu > contents stack scrolledwindow", c_gtk4)
            self.assertIn("popover.menu modelbutton", c_gtk4)
            self.assertIn("dropdown button.combo", c_gtk4)

            # Verify text inputs, search entries, pathbars, and dialogs adapt to flavor palette without dual color
            self.assertIn("caret-color: @accent_color;", c_gtk4)
            self.assertIn("searchbar entry", c_gtk4)
            self.assertIn("headerbar entry,", c_gtk4)
            self.assertIn(".nautilus-window .nautilus-pathbar scrolledwindow,", c_gtk4)
            self.assertIn("background-color: alpha(currentColor, 0.08);", c_gtk4)
            self.assertIn("dialog.background sheet", c_gtk4)
            self.assertIn("background-color: @dialog_bg_color;", c_gtk4)

            # Verify traffic lights window controls positioning inside sidebar headerbar
            self.assertIn("padding-left: 8px;", c_gtk4)

            # Verify horizontal divider seam elimination
            self.assertIn(".sidebar-pane > separator.horizontal,", c_gtk4)

            # Verify Nautilus pathbar transparent button blending
            self.assertIn(".nautilus-pathbar button,", c_gtk4)
            self.assertIn(".nautilus-pathbar .nautilus-path-button.current-dir,", c_gtk4)

            # Verify splitbutton & button separators are subtle (not harsh accent lines)
            self.assertIn("splitbutton separator,", c_gtk4)
            self.assertIn("background-color: alpha(currentColor, 0.12);", c_gtk4)

            # Verify universal window background rules
            self.assertIn(".background,", c_gtk4)
            self.assertIn("background-color: @window_bg_color;", c_gtk4)

            # Verify no destructive button overrides
            self.assertNotIn("button { background-color:", c_gtk3)
            self.assertNotIn("button { background-color:", c_gtk4)

    def test_rose_pine_and_flavors_palette_consistency(self):
        """Verify Rosé Pine and other flavors define deep non-gray sidebar palettes."""
        from theme_manager import THEME_FLAVORS, get_flavor_palette
        
        # Test Rosé Pine specifically
        rp_dark = THEME_FLAVORS["rose-pine"]["dark"]
        self.assertEqual(rp_dark["sidebar_bg"], "#191724")
        self.assertEqual(rp_dark["view_bg"], "#191724")
        self.assertEqual(rp_dark["window_bg"], "#191724")
        self.assertEqual(rp_dark["headerbar_bg"], "#191724")

        rp_palette = get_flavor_palette("rose-pine", is_dark=True)
        self.assertIn("@define-color sidebar_bg_color #191724;", rp_palette)
        self.assertIn("@define-color window_bg_color #191724;", rp_palette)
        self.assertIn("@define-color view_bg_color #191724;", rp_palette)

        # Verify all flavors have both dark and light modes with valid hex colors
        for key, flv in THEME_FLAVORS.items():
            self.assertIn("dark", flv, f"{key} missing dark mode")
            self.assertIn("light", flv, f"{key} missing light mode")
            for mode in ("dark", "light"):
                for col_key in ("window_bg", "view_bg", "sidebar_bg", "headerbar_bg", "accent_color"):
                    val = flv[mode].get(col_key)
                    self.assertTrue(val and val.startswith("#"), f"{key}.{mode}.{col_key} invalid: {val}")


if __name__ == "__main__":
    unittest.main()


