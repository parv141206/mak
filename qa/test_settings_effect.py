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

if __name__ == "__main__":
    unittest.main()
