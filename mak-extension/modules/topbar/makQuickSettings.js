// SPDX-License-Identifier: GPL-3.0-or-later
// Mak Quick Settings Widget: Compact On-The-Go Settings & Theme Switcher for Top Bar

import Clutter from 'gi://Clutter';
import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import GObject from 'gi://GObject';
import St from 'gi://St';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import * as PanelMenu from 'resource:///org/gnome/shell/ui/panelMenu.js';
import * as PopupMenu from 'resource:///org/gnome/shell/ui/popupMenu.js';
import * as Util from 'resource:///org/gnome/shell/misc/util.js';

const _uid = Math.floor(Math.random() * 10000000);

export const MakQuickSettingsButton = GObject.registerClass(
    { GTypeName: `MakQuickSettingsButton_${_uid}` },
    class MakQuickSettingsButton extends PanelMenu.Button {
        _init(extension) {
            super._init(0.5, 'Mak Quick Settings', false);
            this._extension = extension;
            this._settings = extension.getSettings('org.gnome.shell.extensions.mak');
            this._interfaceSettings = new Gio.Settings({ schema_id: 'org.gnome.desktop.interface' });
            this.add_style_class_name('mak-quick-settings-button');

            // Topbar Icon
            const iconPath = extension.path + '/icons/mak-icon-symbolic.svg';
            const gicon = Gio.icon_new_for_string(iconPath);
            this._icon = new St.Icon({
                gicon: gicon,
                style_class: 'system-status-icon mak-qs-panel-icon',
                y_align: Clutter.ActorAlign.CENTER,
            });
            this.add_child(this._icon);

            // Configure Popup Menu
            this.menu.box.add_style_class_name('mak-qs-menu');
            this._buildPopup();

            // Listen for external settings changes
            this._settingsChangedId = this._settings.connect('changed', (s, key) => {
                this._onSettingsChanged(key);
            });
        }

        _buildPopup() {
            this.menu.removeAll();

            const mainBox = new St.BoxLayout({
                vertical: true,
                style_class: 'mak-qs-container',
            });
            this.menu.box.add_child(mainBox);

            // ── 1. HEADER ROW ──
            const headerBox = new St.BoxLayout({
                vertical: false,
                style_class: 'mak-qs-header',
                y_align: Clutter.ActorAlign.CENTER,
            });

            const headerIcon = new St.Icon({
                gicon: this._icon.gicon,
                style_class: 'mak-qs-header-icon',
                y_align: Clutter.ActorAlign.CENTER,
            });
            headerBox.add_child(headerIcon);

            const titleBox = new St.BoxLayout({
                vertical: true,
                x_expand: true,
                y_align: Clutter.ActorAlign.CENTER,
            });
            const titleLabel = new St.Label({
                text: 'Mak Desktop',
                style_class: 'mak-qs-title',
            });
            const subLabel = new St.Label({
                text: 'Quick Controls',
                style_class: 'mak-qs-subtitle',
            });
            titleBox.add_child(titleLabel);
            titleBox.add_child(subLabel);
            headerBox.add_child(titleBox);

            const openAppBtn = new St.Button({
                label: 'Open App ↗',
                style_class: 'mak-qs-open-btn button',
                y_align: Clutter.ActorAlign.CENTER,
            });
            openAppBtn.connect('clicked', () => {
                this.menu.close();
                const appScript = GLib.build_filenamev([GLib.get_home_dir(), 'projects', 'mak', 'mak-app', 'main.py']);
                Util.spawnCommandLine(`python3 "${appScript}"`);
            });
            headerBox.add_child(openAppBtn);
            mainBox.add_child(headerBox);

            // ── 2. SEPARATOR ──
            mainBox.add_child(new St.BoxLayout({ style_class: 'mak-qs-divider' }));

            // ── 3. THEME SWITCHER SECTION ──
            const themeSection = new St.BoxLayout({ vertical: true, style_class: 'mak-qs-section' });
            themeSection.add_child(new St.Label({
                text: 'APPEARANCE & THEME',
                style_class: 'mak-qs-section-title',
            }));

            const themes = [
                { key: 'dark', label: 'Dark Solid' },
                { key: 'dark-glassy', label: 'Dark Glass' },
                { key: 'amoled-glassy', label: 'AMOLED' },
                { key: 'light-glassy', label: 'Light Glass' },
            ];

            const themeRow = new St.BoxLayout({ vertical: false, style_class: 'mak-qs-theme-row' });
            this._themeButtons = {};

            const currGtkTheme = this._interfaceSettings ? this._interfaceSettings.get_string('gtk-theme') : '';
            const currThemeKey = this._detectCurrentThemeKey(currGtkTheme);

            themes.forEach(t => {
                const btn = new St.Button({
                    label: t.label,
                    style_class: 'mak-qs-theme-btn' + (currThemeKey === t.key ? ' active' : ''),
                    x_expand: true,
                });
                btn.connect('clicked', () => {
                    this._applyTheme(t.key);
                });
                this._themeButtons[t.key] = btn;
                themeRow.add_child(btn);
            });
            themeSection.add_child(themeRow);
            mainBox.add_child(themeSection);

            // ── 4. CHROMIUM TOPBAR ACCENT ──
            const accentSection = new St.BoxLayout({ vertical: true, style_class: 'mak-qs-section' });
            accentSection.add_child(new St.Label({
                text: 'BROWSER TOPBAR (CHROME / BRAVE)',
                style_class: 'mak-qs-section-title',
            }));

            const accents = [
                { key: 'default', color: '#3c3c43', tooltip: 'Default System' },
                { key: 'blue', color: '#2563eb', tooltip: 'Ocean Blue' },
                { key: 'teal', color: '#0d9488', tooltip: 'Teal Wave' },
                { key: 'purple', color: '#8b5cf6', tooltip: 'Mac Purple' },
                { key: 'rose', color: '#f43f5e', tooltip: 'Nordic Rose' },
                { key: 'amber', color: '#f59e0b', tooltip: 'Amber Sunset' },
                { key: 'midnight', color: '#09090b', tooltip: 'Pitch Midnight' },
            ];

            const accentRow = new St.BoxLayout({ vertical: false, style_class: 'mak-qs-accent-row' });
            this._accentButtons = {};
            const currAccent = this._settings.get_string('chromium-topbar-accent') || 'default';

            accents.forEach(a => {
                const btn = new St.Button({
                    style_class: 'mak-qs-accent-btn' + (currAccent === a.key ? ' active' : ''),
                    style: `background-color: ${a.color};`,
                    x_expand: true,
                });
                btn.connect('clicked', () => {
                    this._applyChromiumAccent(a.key);
                });
                this._accentButtons[a.key] = btn;
                accentRow.add_child(btn);
            });
            accentSection.add_child(accentRow);
            mainBox.add_child(accentSection);

            // ── 5. SEPARATOR ──
            mainBox.add_child(new St.BoxLayout({ style_class: 'mak-qs-divider' }));

            // ── 6. QUICK TOGGLES ──
            const togglesSection = new St.BoxLayout({ vertical: true, style_class: 'mak-qs-section' });
            togglesSection.add_child(new St.Label({
                text: 'QUICK TOGGLES',
                style_class: 'mak-qs-section-title',
            }));

            const toggleList = [
                { key: 'blur-enabled', label: 'Frosted Glass Blur', default: true },
                { key: 'dock-enabled', label: 'Aqua Dock', default: true },
                { key: 'topbar-opaque', label: 'Opaque Top Bar', default: false },
                { key: 'gaps-enabled', label: 'Window Gaps', default: true },
            ];

            const gridBox = new St.BoxLayout({ vertical: true, style_class: 'mak-qs-toggles-grid' });
            this._toggleButtons = {};

            toggleList.forEach(item => {
                const row = new St.BoxLayout({
                    vertical: false,
                    style_class: 'mak-qs-toggle-row',
                    y_align: Clutter.ActorAlign.CENTER,
                });

                const label = new St.Label({
                    text: item.label,
                    style_class: 'mak-qs-toggle-label',
                    x_expand: true,
                    y_align: Clutter.ActorAlign.CENTER,
                });
                row.add_child(label);

                const isEnabled = this._settings.get_boolean(item.key);
                const switchBtn = new St.Button({
                    label: isEnabled ? 'ON' : 'OFF',
                    style_class: 'mak-qs-switch-btn' + (isEnabled ? ' active' : ''),
                    y_align: Clutter.ActorAlign.CENTER,
                });

                switchBtn.connect('clicked', () => {
                    const current = this._settings.get_boolean(item.key);
                    this._settings.set_boolean(item.key, !current);
                });

                this._toggleButtons[item.key] = switchBtn;
                row.add_child(switchBtn);
                gridBox.add_child(row);
            });
            togglesSection.add_child(gridBox);
            mainBox.add_child(togglesSection);

            // ── 7. SEPARATOR ──
            mainBox.add_child(new St.BoxLayout({ style_class: 'mak-qs-divider' }));

            // ── 8. TRAFFIC LIGHT STEPPERS ──
            const buttonsSection = new St.BoxLayout({ vertical: true, style_class: 'mak-qs-section' });
            buttonsSection.add_child(new St.Label({
                text: 'TRAFFIC LIGHT CONTROLS',
                style_class: 'mak-qs-section-title',
            }));

            // Button Size Stepper
            const sizeRow = new St.BoxLayout({
                vertical: false,
                style_class: 'mak-qs-stepper-row',
                y_align: Clutter.ActorAlign.CENTER,
            });
            sizeRow.add_child(new St.Label({
                text: 'Button Size',
                style_class: 'mak-qs-toggle-label',
                x_expand: true,
                y_align: Clutter.ActorAlign.CENTER,
            }));

            const currSize = this._settings.get_int('titlebar-button-size') || 14;
            const sizeMinus = new St.Button({ label: '−', style_class: 'mak-qs-step-btn' });
            this._sizeLabel = new St.Label({ text: `${currSize}px`, style_class: 'mak-qs-step-val', y_align: Clutter.ActorAlign.CENTER });
            const sizePlus = new St.Button({ label: '+', style_class: 'mak-qs-step-btn' });

            sizeMinus.connect('clicked', () => this._adjustButtonSetting('titlebar-button-size', -1, 10, 22));
            sizePlus.connect('clicked', () => this._adjustButtonSetting('titlebar-button-size', 1, 10, 22));

            sizeRow.add_child(sizeMinus);
            sizeRow.add_child(this._sizeLabel);
            sizeRow.add_child(sizePlus);
            buttonsSection.add_child(sizeRow);

            // Button Spacing Stepper
            const spaceRow = new St.BoxLayout({
                vertical: false,
                style_class: 'mak-qs-stepper-row',
                y_align: Clutter.ActorAlign.CENTER,
            });
            spaceRow.add_child(new St.Label({
                text: 'Button Spacing',
                style_class: 'mak-qs-toggle-label',
                x_expand: true,
                y_align: Clutter.ActorAlign.CENTER,
            }));

            const currSpacing = this._settings.get_int('titlebar-button-spacing') || 8;
            const spaceMinus = new St.Button({ label: '−', style_class: 'mak-qs-step-btn' });
            this._spacingLabel = new St.Label({ text: `${currSpacing}px`, style_class: 'mak-qs-step-val', y_align: Clutter.ActorAlign.CENTER });
            const spacePlus = new St.Button({ label: '+', style_class: 'mak-qs-step-btn' });

            spaceMinus.connect('clicked', () => this._adjustButtonSetting('titlebar-button-spacing', -2, 0, 24));
            spacePlus.connect('clicked', () => this._adjustButtonSetting('titlebar-button-spacing', 2, 0, 24));

            spaceRow.add_child(spaceMinus);
            spaceRow.add_child(this._spacingLabel);
            spaceRow.add_child(spacePlus);
            buttonsSection.add_child(spaceRow);

            mainBox.add_child(buttonsSection);
        }

        _detectCurrentThemeKey(themeName) {
            const name = (themeName || '').toLowerCase();
            const isGlassy = name.includes('glassy');
            if (name.includes('amoled')) return isGlassy ? 'amoled-glassy' : 'amoled';
            if (name.includes('light')) return isGlassy ? 'light-glassy' : 'light';
            return isGlassy ? 'dark-glassy' : 'dark';
        }

        _applyTheme(key) {
            Object.keys(this._themeButtons).forEach(k => {
                if (k === key) this._themeButtons[k].add_style_class_name('active');
                else this._themeButtons[k].remove_style_class_name('active');
            });
            const script = GLib.build_filenamev([GLib.get_home_dir(), 'projects', 'mak', 'mak-app', 'theme_manager.py']);
            Util.spawnCommandLine(`python3 "${script}" "${key}"`);
        }

        _applyChromiumAccent(key) {
            this._settings.set_string('chromium-topbar-accent', key);
            Object.keys(this._accentButtons).forEach(k => {
                if (k === key) this._accentButtons[k].add_style_class_name('active');
                else this._accentButtons[k].remove_style_class_name('active');
            });
            const script = GLib.build_filenamev([GLib.get_home_dir(), 'projects', 'mak', 'mak-app', 'theme_manager.py']);
            Util.spawnCommandLine(`python3 "${script}" --accent "${key}"`);
        }

        _adjustButtonSetting(key, delta, minVal, maxVal) {
            let val = this._settings.get_int(key);
            val = Math.max(minVal, Math.min(maxVal, val + delta));
            this._settings.set_int(key, val);

            if (key === 'titlebar-button-size') {
                if (this._sizeLabel) this._sizeLabel.set_text(`${val}px`);
            } else if (key === 'titlebar-button-spacing') {
                if (this._spacingLabel) this._spacingLabel.set_text(`${val}px`);
            }

            const size = this._settings.get_int('titlebar-button-size');
            const spacing = this._settings.get_int('titlebar-button-spacing');
            const script = GLib.build_filenamev([GLib.get_home_dir(), 'projects', 'mak', 'mak-app', 'theme_manager.py']);
            Util.spawnCommandLine(`python3 "${script}" --buttons ${size} ${spacing}`);
        }

        _onSettingsChanged(key) {
            if (this._toggleButtons[key]) {
                const isEnabled = this._settings.get_boolean(key);
                const btn = this._toggleButtons[key];
                btn.set_label(isEnabled ? 'ON' : 'OFF');
                if (isEnabled) btn.add_style_class_name('active');
                else btn.remove_style_class_name('active');
            } else if (key === 'chromium-topbar-accent') {
                const curr = this._settings.get_string('chromium-topbar-accent');
                Object.keys(this._accentButtons).forEach(k => {
                    if (k === curr) this._accentButtons[k].add_style_class_name('active');
                    else this._accentButtons[k].remove_style_class_name('active');
                });
            } else if (key === 'titlebar-button-size') {
                if (this._sizeLabel) {
                    this._sizeLabel.set_text(`${this._settings.get_int(key)}px`);
                }
            } else if (key === 'titlebar-button-spacing') {
                if (this._spacingLabel) {
                    this._spacingLabel.set_text(`${this._settings.get_int(key)}px`);
                }
            }
        }

        destroy() {
            if (this._settingsChangedId) {
                try { this._settings.disconnect(this._settingsChangedId); } catch (e) {}
                this._settingsChangedId = 0;
            }
            this._interfaceSettings = null;
            super.destroy();
        }
    }
);
