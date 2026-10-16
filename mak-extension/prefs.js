// SPDX-License-Identifier: GPL-3.0-or-later
// Mak Extension Preferences (GTK 4 / Libadwaita)

import Adw from 'gi://Adw';
import Gio from 'gi://Gio';
import Gtk from 'gi://Gtk';
import Gdk from 'gi://Gdk?version=4.0';
import { ExtensionPreferences, gettext as _ } from 'resource:///org/gnome/Shell/Extensions/js/extensions/prefs.js';

export default class MakPreferences extends ExtensionPreferences {
    fillPreferencesWindow(window) {
        const settings = this.getSettings('org.gnome.shell.extensions.mak');

        // Helper: Toggle switch
        const addSwitch = (group, title, subtitle, key) => {
            const row = new Adw.SwitchRow({
                title: _(title),
                subtitle: _(subtitle),
            });
            group.add(row);
            settings.bind(key, row, 'active', Gio.SettingsBindFlags.DEFAULT);
            return row;
        };

        // Helper: Integer spin row
        const addIntRow = (group, title, subtitle, key, lower, upper, step) => {
            const row = new Adw.SpinRow({
                title: _(title),
                subtitle: _(subtitle),
                adjustment: new Gtk.Adjustment({
                    lower,
                    upper,
                    step_increment: step,
                    page_increment: step * 5,
                    value: settings.get_int(key),
                }),
            });
            group.add(row);
            settings.bind(key, row, 'value', Gio.SettingsBindFlags.DEFAULT);
            return row;
        };

        // Helper: Double spin row
        const addDoubleRow = (group, title, subtitle, key, lower, upper, step) => {
            const row = new Adw.SpinRow({
                title: _(title),
                subtitle: _(subtitle),
                digits: 2,
                adjustment: new Gtk.Adjustment({
                    lower,
                    upper,
                    step_increment: step,
                    page_increment: step * 2,
                    value: settings.get_double(key),
                }),
            });
            group.add(row);
            settings.bind(key, row, 'value', Gio.SettingsBindFlags.DEFAULT);
            return row;
        };

        // Helper: Native color picker row
        const addColorRow = (group, title, subtitle, key, defaultColor = '#ffffff') => {
            const row = new Adw.ActionRow({
                title: _(title),
                subtitle: _(subtitle),
            });
            const dialog = new Gtk.ColorDialog({ with_alpha: false });
            const btn = new Gtk.ColorDialogButton({ dialog });
            const currentColor = settings.get_string(key) || defaultColor;
            const rgba = new Gdk.RGBA();
            try {
                rgba.parse(currentColor);
            } catch (e) {
                rgba.parse(defaultColor);
            }
            btn.set_rgba(rgba);

            btn.connect('notify::rgba', () => {
                const c = btn.get_rgba();
                const r = Math.round(c.red * 255).toString(16).padStart(2, '0');
                const g = Math.round(c.green * 255).toString(16).padStart(2, '0');
                const b = Math.round(c.blue * 255).toString(16).padStart(2, '0');
                settings.set_string(key, `#${r}${g}${b}`);
            });

            row.add_suffix(btn);
            group.add(row);
            return row;
        };

        // ── 1. General & Modules Page ─────────────────────────────────────
        const generalPage = new Adw.PreferencesPage({
            title: _('Features'),
            icon_name: 'preferences-system-symbolic',
        });
        window.add(generalPage);

        const modulesGroup = new Adw.PreferencesGroup({
            title: _('Active Components'),
            description: _('Toggle modules in the unified Mak suite.'),
        });
        generalPage.add(modulesGroup);

        addSwitch(modulesGroup, 'macOS Dock', 'Floating glass dock with spring magnification and blur', 'dock-enabled');
        addSwitch(modulesGroup, 'macOS Top Bar', 'Apple menu, active window title, and frosted panel', 'topbar-enabled');
        addSwitch(modulesGroup, 'Spotlight Search', 'Instant keyboard-driven command & search bar (Super+Space)', 'spotlight-enabled');
        addSwitch(modulesGroup, 'Window Gaps', 'Outer gaps around windows, even when maximized', 'gaps-enabled');
        addSwitch(modulesGroup, 'Rounded Corners', 'Smooth anti-aliased squircle window corners', 'corners-enabled');

        // ── 2. Dock Settings Page ─────────────────────────────────────────
        const dockPage = new Adw.PreferencesPage({
            title: _('Dock'),
            icon_name: 'view-app-grid-symbolic',
        });
        window.add(dockPage);

        const dockOpticsGroup = new Adw.PreferencesGroup({
            title: _('Dock Appearance & Glass Optics'),
            description: _('Hardware-accelerated liquid glass, refraction depth, and color tinting.'),
        });
        dockPage.add(dockOpticsGroup);

        addSwitch(dockOpticsGroup, 'Dynamic Glass Blur', 'Hardware accelerated Gaussian & refraction glass blur behind dock', 'dock-blur');
        addIntRow(dockOpticsGroup, 'Blur Radius', 'Optical blur radius in pixels', 'dock-blur-radius', 0, 100, 2);
        addDoubleRow(dockOpticsGroup, 'Glass Refraction Level', 'Optical depth, frosted glass thickness, and lens intensity', 'dock-glass-level', 0.0, 1.0, 0.05);
        addDoubleRow(dockOpticsGroup, 'Edge Refraction Bending', 'Snell-law optical curvature bending along dock glass pill edges', 'dock-edge-bending', 0.0, 1.0, 0.05);
        addColorRow(dockOpticsGroup, 'Glass Tint Color', 'Color layer blended over the dock glass refraction', 'dock-tint-color', '#ffffff');
        addDoubleRow(dockOpticsGroup, 'Tint Strength / Opacity', 'Intensity factor for the dock glass tint layer', 'dock-tint-strength', 0.0, 1.0, 0.02);
        addIntRow(dockOpticsGroup, 'Dock Corner Radius', 'Corner curvature radius of the dock glass pill', 'dock-corner-radius', 0, 40, 1);

        const dockBehaviorGroup = new Adw.PreferencesGroup({
            title: _('Dock Behavior'),
        });
        dockPage.add(dockBehaviorGroup);
        addSwitch(dockBehaviorGroup, 'Magnification Zoom', 'Smooth cursor magnification effect', 'dock-magnification');
        addSwitch(dockBehaviorGroup, 'Autohide', 'Hide dock automatically when overlapping windows', 'dock-autohide');

        // ── 3. Top Bar Page ───────────────────────────────────────────────
        const topbarPage = new Adw.PreferencesPage({
            title: _('Top Bar'),
            icon_name: 'edit-find-symbolic',
        });
        window.add(topbarPage);

        const topbarGroup = new Adw.PreferencesGroup({
            title: _('Panel Elements & Glass'),
        });
        topbarPage.add(topbarGroup);

        addSwitch(topbarGroup, 'Apple Menu', 'Show system Apple menu on the far left', 'topbar-apple-menu');
        addSwitch(topbarGroup, 'Active App Title', 'Show current focused application title in the bar', 'topbar-app-title');
        addSwitch(topbarGroup, 'Frosted Glass Blur', 'Enable background blur on top panel', 'topbar-blur');
        addSwitch(topbarGroup, 'Opaque Top Bar', 'Make top bar specifically solid opaque while keeping menus and dock blurry', 'topbar-opaque');
        addIntRow(topbarGroup, 'Blur Radius', 'Optical blur radius in pixels for top panel', 'topbar-blur-radius', 0, 60, 2);
        addColorRow(topbarGroup, 'Glass Tint Color', 'Color layer blended over top bar glass', 'topbar-tint-color', '#ffffff');
        addDoubleRow(topbarGroup, 'Tint Strength', 'Intensity of the top panel glass tint', 'topbar-tint-strength', 0.0, 1.0, 0.02);

        const topbarColorsGroup = new Adw.PreferencesGroup({
            title: _('Top Bar Colors'),
            description: _('Explicit foreground color overrides for indicators and controls.'),
        });
        topbarPage.add(topbarColorsGroup);
        addColorRow(topbarColorsGroup, 'Items Text Color', 'Text color for clock, app title, and menus', 'topbar-text-color', '#ffffff');
        addColorRow(topbarColorsGroup, 'Symbolic Icons Color', 'Color for tray indicators, status symbols, and control icons', 'topbar-icon-color', '#ffffff');

        // ── 4. Control Center / Quick Settings Page ───────────────────────
        const ccPage = new Adw.PreferencesPage({
            title: _('Control Center'),
            icon_name: 'preferences-other-symbolic',
        });
        window.add(ccPage);

        const ccOpticsGroup = new Adw.PreferencesGroup({
            title: _('Control Center Glass & Optics'),
            description: _('Independent floating liquid glass capsules, refraction, and color tinting.'),
        });
        ccPage.add(ccOpticsGroup);

        addSwitch(ccOpticsGroup, 'Hardware Glass Blur', 'Hardware accelerated liquid glass behind Quick Settings', 'control-center-blur');
        addIntRow(ccOpticsGroup, 'Blur Radius', 'Optical blur radius in pixels', 'control-center-blur-radius', 0, 100, 2);
        addDoubleRow(ccOpticsGroup, 'Glass Refraction Level', 'Optical depth and refraction factor for Quick Settings pills', 'control-center-glass-level', 0.0, 1.0, 0.05);
        addColorRow(ccOpticsGroup, 'Pill Glass Tint Color', 'Color layer blended over the individual liquid glass capsules', 'control-center-tint-color', '#ffffff');
        addDoubleRow(ccOpticsGroup, 'Tint Strength / Opacity', 'Intensity factor for Quick Settings capsule tint', 'control-center-tint-strength', 0.0, 1.0, 0.02);
        addIntRow(ccOpticsGroup, 'Container Corner Radius', 'Corner radius for Quick Settings dropdown submenus', 'quick-settings-radius', 0, 32, 1);

        const ccColorsGroup = new Adw.PreferencesGroup({
            title: _('Item Colors'),
            description: _('Explicit foreground color overrides for toggles, sliders, and icons.'),
        });
        ccPage.add(ccColorsGroup);
        addColorRow(ccColorsGroup, 'Text Color', 'Explicit text color for toggles, battery pill, and labels', 'control-center-text-color', '#ffffff');
        addColorRow(ccColorsGroup, 'Icon Color', 'Explicit symbolic icon color for quick toggles and sliders', 'control-center-icon-color', '#ffffff');

        // ── 5. Menus & Popups Page ────────────────────────────────────────
        const menuPage = new Adw.PreferencesPage({
            title: _('Menus'),
            icon_name: 'emblem-system-symbolic',
        });
        window.add(menuPage);

        const menuOpticsGroup = new Adw.PreferencesGroup({
            title: _('Dropdown Menus & Popups'),
            description: _('Kiwi Apple menu, system indicators, app menus, and calendar dropdown.'),
        });
        menuPage.add(menuOpticsGroup);

        addSwitch(menuOpticsGroup, 'Menu Glass Blur', 'Enable liquid glass blur on popup menus and dropdowns', 'menu-blur');
        addIntRow(menuOpticsGroup, 'Blur Radius', 'Optical blur radius in pixels', 'menu-blur-radius', 0, 100, 2);
        addDoubleRow(menuOpticsGroup, 'Glass Refraction Level', 'Optical refraction depth for menus', 'menu-glass-level', 0.0, 1.0, 0.05);
        addColorRow(menuOpticsGroup, 'Menu Tint Color', 'Color layer blended over menu glass', 'menu-tint-color', '#ffffff');
        addDoubleRow(menuOpticsGroup, 'Tint Strength / Opacity', 'Intensity factor for menu tint layer', 'menu-tint-strength', 0.0, 1.0, 0.02);
        addColorRow(menuOpticsGroup, 'Menu Text Color', 'Explicit text color for menu items', 'menu-text-color', '#ffffff');
        addIntRow(menuOpticsGroup, 'Menu Corner Radius', 'Corner curvature radius in pixels', 'menu-corner-radius', 0, 32, 1);

        const desktopMenuGroup = new Adw.PreferencesGroup({
            title: _('Desktop Right-Click Context Menu'),
            description: _('Liquid glass refraction and tint applied to the desktop wallpaper right-click menu.'),
        });
        menuPage.add(desktopMenuGroup);

        addSwitch(desktopMenuGroup, 'Desktop Menu Glass', 'Enable liquid glass refraction on desktop right-click context menu', 'desktop-menu-blur');
        addIntRow(desktopMenuGroup, 'Blur Radius', 'Optical blur radius in pixels for desktop context menu', 'desktop-menu-blur-radius', 0, 100, 2);
        addDoubleRow(desktopMenuGroup, 'Glass Refraction Level', 'Optical depth and refraction factor', 'desktop-menu-glass-level', 0.0, 1.0, 0.05);
        addColorRow(desktopMenuGroup, 'Desktop Menu Tint Color', 'Color layer blended over desktop context menu', 'desktop-menu-tint-color', '#ffffff');
        addDoubleRow(desktopMenuGroup, 'Tint Strength / Opacity', 'Intensity factor for desktop menu tint', 'desktop-menu-tint-strength', 0.0, 1.0, 0.02);

        // ── 6. Windows Page ───────────────────────────────────────────────
        const winPage = new Adw.PreferencesPage({
            title: _('Windows'),
            icon_name: 'preferences-desktop-display-symbolic',
        });
        window.add(winPage);

        const winGroup = new Adw.PreferencesGroup({
            title: _('Gaps & Rounded Corners'),
        });
        winPage.add(winGroup);

        addIntRow(winGroup, 'Outer Window Gap Size', 'Margin in pixels around windows (including maximized)', 'gap-size', 0, 48, 2);
        addIntRow(winGroup, 'Window Corner Radius', 'Squircle corner radius in pixels', 'corner-radius', 0, 32, 1);
    }
}
