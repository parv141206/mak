// SPDX-License-Identifier: GPL-3.0-or-later
// Mak Extension Preferences (GTK 4 / Libadwaita)

import Adw from 'gi://Adw';
import Gio from 'gi://Gio';
import Gtk from 'gi://Gtk';
import { ExtensionPreferences, gettext as _ } from 'resource:///org/gnome/Shell/Extensions/js/extensions/prefs.js';

export default class MakPreferences extends ExtensionPreferences {
    fillPreferencesWindow(window) {
        const settings = this.getSettings('org.gnome.shell.extensions.mak');

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

        const addSwitch = (group, title, subtitle, key) => {
            const row = new Adw.SwitchRow({
                title: _(title),
                subtitle: _(subtitle),
            });
            group.add(row);
            settings.bind(key, row, 'active', Gio.SettingsBindFlags.DEFAULT);
            return row;
        };

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

        const dockGroup = new Adw.PreferencesGroup({
            title: _('Dock Appearance & Glass Blur'),
        });
        dockPage.add(dockGroup);

        addSwitch(dockGroup, 'Dynamic Glass Blur', 'Native Gaussian background blur behind the dock pill', 'dock-blur');

        const blurRadiusRow = new Adw.SpinRow({
            title: _('Blur Radius'),
            subtitle: _('Intensity of the frosted glass blur'),
            adjustment: new Gtk.Adjustment({ lower: 0, upper: 100, step_increment: 2, value: settings.get_int('dock-blur-radius') }),
        });
        dockGroup.add(blurRadiusRow);
        settings.bind('dock-blur-radius', blurRadiusRow, 'value', Gio.SettingsBindFlags.DEFAULT);

        const cornerRadiusRow = new Adw.SpinRow({
            title: _('Dock Corner Radius'),
            subtitle: _('Curvature of the dock glass pill'),
            adjustment: new Gtk.Adjustment({ lower: 0, upper: 40, step_increment: 1, value: settings.get_int('dock-corner-radius') }),
        });
        dockGroup.add(cornerRadiusRow);
        settings.bind('dock-corner-radius', cornerRadiusRow, 'value', Gio.SettingsBindFlags.DEFAULT);

        addSwitch(dockGroup, 'Magnification Zoom', 'Smooth cursor magnification effect', 'dock-magnification');
        addSwitch(dockGroup, 'Autohide', 'Hide dock automatically when overlapping windows', 'dock-autohide');

        // ── 3. Top Bar Page ───────────────────────────────────────────────
        const topbarPage = new Adw.PreferencesPage({
            title: _('Top Bar'),
            icon_name: 'edit-find-symbolic',
        });
        window.add(topbarPage);

        const topbarGroup = new Adw.PreferencesGroup({
            title: _('Panel Elements'),
        });
        topbarPage.add(topbarGroup);

        addSwitch(topbarGroup, 'Apple Menu', 'Show system Apple menu on the far left', 'topbar-apple-menu');
        addSwitch(topbarGroup, 'Active App Title', 'Show current focused application title in the bar', 'topbar-app-title');
        addSwitch(topbarGroup, 'Frosted Glass Blur', 'Enable background blur on top panel', 'topbar-blur');

        // ── 4. Windows Page ───────────────────────────────────────────────
        const winPage = new Adw.PreferencesPage({
            title: _('Windows'),
            icon_name: 'preferences-desktop-display-symbolic',
        });
        window.add(winPage);

        const winGroup = new Adw.PreferencesGroup({
            title: _('Gaps & Rounded Corners'),
        });
        winPage.add(winGroup);

        const gapRow = new Adw.SpinRow({
            title: _('Outer Window Gap Size'),
            subtitle: _('Margin in pixels around windows (including maximized)'),
            adjustment: new Gtk.Adjustment({ lower: 0, upper: 48, step_increment: 2, value: settings.get_int('gap-size') }),
        });
        winGroup.add(gapRow);
        settings.bind('gap-size', gapRow, 'value', Gio.SettingsBindFlags.DEFAULT);

        const cornerRow = new Adw.SpinRow({
            title: _('Window Corner Radius'),
            subtitle: _('Squircle corner radius in pixels'),
            adjustment: new Gtk.Adjustment({ lower: 0, upper: 32, step_increment: 1, value: settings.get_int('corner-radius') }),
        });
        winGroup.add(cornerRow);
        settings.bind('corner-radius', cornerRow, 'value', Gio.SettingsBindFlags.DEFAULT);
    }
}
