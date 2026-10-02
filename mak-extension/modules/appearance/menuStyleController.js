// SPDX-License-Identifier: GPL-3.0-or-later
// Mak Menu & Shell UI Style Controller
// Manages consistent macOS dual-layer borders, continuous corner radii, and specular highlights across GNOME Shell.

import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import St from 'gi://St';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';

export class MenuStyleController {
    constructor(extension) {
        this._extension = extension;
        this._settings = extension.getSettings('org.gnome.shell.extensions.mak');
        this._interfaceSettings = new Gio.Settings({ schema_id: 'org.gnome.desktop.interface' });
        this._settingsChangedId = 0;
        this._interfaceChangedId = 0;
        this._styleFile = null;
        this._isLoaded = false;
    }

    enable() {
        const extPath = this._extension.path;
        this._stylePath = GLib.build_filenamev([extPath, 'dynamic-menus.css']);
        this._styleFile = Gio.File.new_for_path(this._stylePath);

        this._settingsChangedId = this._settings.connect('changed', (s, key) => {
            if (key.startsWith('menu-') || key.startsWith('quick-settings-') ||
                key.startsWith('notification-') || key === 'global-opacity') {
                this.updateStyles();
            }
        });

        this._interfaceChangedId = this._interfaceSettings.connect('changed', (s, key) => {
            if (key === 'gtk-theme' || key === 'color-scheme') {
                this.updateStyles();
            }
        });

        this.updateStyles();
        console.log('[Mak Appearance] Menu & Shell UI styling controller active.');
    }

    disable() {
        if (this._settingsChangedId) {
            this._settings.disconnect(this._settingsChangedId);
            this._settingsChangedId = 0;
        }

        if (this._interfaceChangedId) {
            this._interfaceSettings.disconnect(this._interfaceChangedId);
            this._interfaceChangedId = 0;
        }

        this._unloadCustomStylesheet();

        try {
            if (this._styleFile && this._styleFile.query_exists(null)) {
                this._styleFile.delete(null);
            }
        } catch (e) {}

        this._styleFile = null;
        this._isLoaded = false;
    }

    updateStyles() {
        const radius = this._settings.get_int('menu-corner-radius');
        const borderWidth = this._settings.get_int('menu-border-width');
        const qsRadius = this._settings.get_int('quick-settings-radius');
        const notifRadius = this._settings.get_int('notification-radius');

        const colorScheme = this._interfaceSettings ? this._interfaceSettings.get_string('color-scheme') : '';
        const gtkTheme = this._interfaceSettings ? this._interfaceSettings.get_string('gtk-theme') : '';
        const isLight = (colorScheme === 'prefer-light') || gtkTheme.toLowerCase().includes('light');
        const isAmoled = gtkTheme.toLowerCase().includes('amoled');

        let bgR = 32, bgG = 32, bgB = 36;
        let menuOpacity = 0.65;
        let textColor = '#f5f5f7';
        let secondaryTextColor = 'rgba(255, 255, 255, 0.55)';
        let itemHoverBg = 'rgba(255, 255, 255, 0.12)';
        let itemActiveBg = 'rgba(255, 255, 255, 0.22)';
        let itemSelectedBg = 'rgba(255, 255, 255, 0.16)';
        let itemHoverColor = '#ffffff';
        let separatorColor = 'rgba(255, 255, 255, 0.10)';
        let borderStrokeColor = 'rgba(255, 255, 255, 0.14)';
        let boxShadow = '0 12px 32px rgba(0, 0, 0, 0.45), 0 2px 8px rgba(0, 0, 0, 0.22)';
        let qsBoxShadow = '0 16px 40px rgba(0, 0, 0, 0.55), 0 3px 10px rgba(0, 0, 0, 0.28)';
        let pillBodyBg = `rgba(28, 28, 34, ${menuOpacity})`;
        let qsTileBg = 'rgba(255, 255, 255, 0.10)';
        let qsTileHoverBg = 'rgba(255, 255, 255, 0.16)';
        let btHeaderBorder = 'rgba(255, 255, 255, 0.12)';
        let btEmptyText = 'rgba(255, 255, 255, 0.5)';
        let btHoverBg = 'rgba(255, 255, 255, 0.12)';
        let btBarBg = 'rgba(255, 255, 255, 0.2)';
        let btText = 'rgba(255, 255, 255, 0.8)';

        if (isLight) {
            bgR = 246; bgG = 246; bgB = 248;
            menuOpacity = 0.72;
            textColor = '#1d1d1f';
            secondaryTextColor = 'rgba(0, 0, 0, 0.55)';
            itemHoverBg = 'rgba(0, 0, 0, 0.06)';
            itemActiveBg = 'rgba(0, 0, 0, 0.12)';
            itemSelectedBg = 'rgba(0, 0, 0, 0.09)';
            itemHoverColor = '#000000';
            separatorColor = 'rgba(0, 0, 0, 0.08)';
            borderStrokeColor = 'rgba(0, 0, 0, 0.12)';
            boxShadow = '0 10px 30px rgba(0, 0, 0, 0.16), 0 2px 6px rgba(0, 0, 0, 0.08)';
            qsBoxShadow = '0 14px 34px rgba(0, 0, 0, 0.18), 0 3px 8px rgba(0, 0, 0, 0.08)';
            pillBodyBg = `rgba(255, 255, 255, ${menuOpacity})`;
            qsTileBg = 'rgba(0, 0, 0, 0.05)';
            qsTileHoverBg = 'rgba(0, 0, 0, 0.09)';
            btHeaderBorder = 'rgba(0, 0, 0, 0.10)';
            btEmptyText = 'rgba(0, 0, 0, 0.45)';
            btHoverBg = 'rgba(0, 0, 0, 0.06)';
            btBarBg = 'rgba(0, 0, 0, 0.15)';
            btText = 'rgba(0, 0, 0, 0.75)';
        } else if (isAmoled) {
            bgR = 10; bgG = 10; bgB = 12;
            menuOpacity = 0.85;
            textColor = '#ffffff';
            secondaryTextColor = 'rgba(255, 255, 255, 0.60)';
            itemHoverBg = 'rgba(255, 255, 255, 0.15)';
            itemActiveBg = 'rgba(255, 255, 255, 0.25)';
            itemSelectedBg = 'rgba(255, 255, 255, 0.18)';
            itemHoverColor = '#ffffff';
            separatorColor = 'rgba(255, 255, 255, 0.12)';
            borderStrokeColor = 'rgba(255, 255, 255, 0.18)';
            boxShadow = '0 14px 36px rgba(0, 0, 0, 0.75), 0 2px 8px rgba(0, 0, 0, 0.35)';
            qsBoxShadow = '0 18px 44px rgba(0, 0, 0, 0.85), 0 4px 12px rgba(0, 0, 0, 0.45)';
            pillBodyBg = `rgba(10, 10, 12, ${menuOpacity})`;
            qsTileBg = 'rgba(255, 255, 255, 0.12)';
            qsTileHoverBg = 'rgba(255, 255, 255, 0.18)';
            btHeaderBorder = 'rgba(255, 255, 255, 0.14)';
            btEmptyText = 'rgba(255, 255, 255, 0.5)';
            btHoverBg = 'rgba(255, 255, 255, 0.14)';
            btBarBg = 'rgba(255, 255, 255, 0.22)';
            btText = 'rgba(255, 255, 255, 0.8)';
        }

        const borderCss = borderWidth > 0
            ? `${borderWidth}px solid ${borderStrokeColor}`
            : `1px solid ${borderStrokeColor}`;

        const css = `/* Generated by Mak Appearance Controller */
/* ── Unified macOS Popup Menus, Context Menus & Kiwi Menu ─────────────────── */
.popup-menu-boxpointer,
.candidate-popup-boxpointer {
    -arrow-rise: 0px !important;
    -arrow-border-width: 0px !important;
    -arrow-border-radius: 0px !important;
    -arrow-background-color: transparent !important;
    -arrow-border-color: transparent !important;
    box-shadow: none !important;
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
}

.popup-menu-content,
.popup-sub-menu,
.candidate-popup-content {
    border-radius: ${radius}px !important;
    border: ${borderCss} !important;
    background-color: rgba(${bgR}, ${bgG}, ${bgB}, ${menuOpacity.toFixed(2)}) !important;
    box-shadow: ${boxShadow} !important;
    padding: 6px !important;
}

/* ── Menu Items & Hover States ────────────────────────────────────────────── */
.popup-menu-item {
    border-radius: ${Math.max(4, radius - 8)}px !important;
    margin: 2px 4px !important;
    padding: 6px 12px !important;
    transition-duration: 100ms !important;
    color: ${textColor} !important;
}

.popup-menu-item StLabel {
    color: ${textColor} !important;
}

.popup-menu-item:hover,
.popup-menu-item:focus {
    background-color: ${itemHoverBg} !important;
    color: ${itemHoverColor} !important;
}

.popup-menu-item:hover StLabel,
.popup-menu-item:focus StLabel {
    color: ${itemHoverColor} !important;
}

.popup-menu-item:active {
    background-color: ${itemActiveBg} !important;
    color: ${itemHoverColor} !important;
}

.popup-menu-item:active StLabel {
    color: ${itemHoverColor} !important;
}

.popup-menu-item.selected {
    background-color: ${itemSelectedBg} !important;
    color: ${itemHoverColor} !important;
}

.popup-menu-item.selected StLabel {
    color: ${itemHoverColor} !important;
}

/* Submenu section headers (e.g. Kiwi recent items "Applications", "Documents") */
.popup-menu-item.section-header,
.popup-menu-item.section-header StLabel {
    color: ${secondaryTextColor} !important;
    font-weight: 600 !important;
    font-size: 0.85em !important;
    letter-spacing: 0.02em !important;
}

/* ── Separator ────────────────────────────────────────────────────────────── */
.popup-separator-menu-item {
    margin: 5px 8px !important;
    padding: 0 !important;
}

.popup-separator-menu-item .popup-separator-menu-item-separator {
    height: 1px !important;
    background-color: ${separatorColor} !important;
}

/* ── Calendar & DateMenu Styling (macOS Clock Dropdown) ───────────────────── */
.datemenu-calendar-column {
    spacing: 12px;
}

.datemenu-date-button {
    color: ${textColor} !important;
}

.datemenu-date-button .day-label {
    font-size: 1.4em !important;
    font-weight: bold !important;
    color: ${textColor} !important;
}

.datemenu-date-button .date-label {
    font-size: 1.1em !important;
    color: ${secondaryTextColor} !important;
}

.datemenu-today-button {
    color: ${secondaryTextColor} !important;
}

.datemenu-today-button:hover {
    color: ${itemHoverColor} !important;
}

/* Calendar month header and arrow buttons */
.calendar-month-header {
    color: ${textColor} !important;
    font-weight: bold !important;
}

.calendar-month-header .calendar-month-label {
    color: ${textColor} !important;
    font-weight: bold !important;
    font-size: 1.05em !important;
}

.calendar-change-month-back,
.calendar-change-month-forward {
    color: ${textColor} !important;
    border-radius: 9999px !important;
}

.calendar-change-month-back:hover,
.calendar-change-month-forward:hover {
    background-color: ${itemHoverBg} !important;
    color: ${itemHoverColor} !important;
}

/* Calendar Day Grid */
.calendar-day-heading {
    color: ${secondaryTextColor} !important;
    font-weight: 600 !important;
    font-size: 0.85em !important;
    padding: 4px !important;
}

.calendar-day-base {
    color: ${textColor} !important;
    border-radius: 9999px !important;
    font-weight: normal !important;
    text-align: center;
    margin: 2px !important;
}

.calendar-day-base:hover,
.calendar-day-base:focus {
    background-color: ${itemHoverBg} !important;
    color: ${itemHoverColor} !important;
}

.calendar-day-base:active {
    background-color: ${itemActiveBg} !important;
    color: ${itemHoverColor} !important;
}

.calendar-day-base:selected {
    background-color: #9A57A3 !important;
    color: #ffffff !important;
    font-weight: bold !important;
}

/* Today circle */
.calendar-day-base.calendar-today {
    background-color: #9A57A3 !important;
    color: #ffffff !important;
    font-weight: bold !important;
    border-radius: 9999px !important;
}

.calendar-non-work-day {
    color: ${secondaryTextColor} !important;
}

.calendar-other-month-day {
    color: ${secondaryTextColor} !important;
    opacity: 0.45 !important;
}

.calendar-week-number {
    color: ${secondaryTextColor} !important;
    font-size: 0.8em !important;
    opacity: 0.6 !important;
}

/* DateMenu Messages / Events / Weather / World Clocks */
.message-list-section-title,
.events-section-title,
.world-clocks-header,
.weather-header {
    color: ${textColor} !important;
    font-weight: bold !important;
    font-size: 0.9em !important;
    letter-spacing: 0.02em !important;
}

.message-list {
    color: ${textColor} !important;
}

.message {
    background-color: ${qsTileBg} !important;
    border-radius: 14px !important;
    color: ${textColor} !important;
    padding: 8px 12px !important;
}

.message:hover {
    background-color: ${qsTileHoverBg} !important;
}

.message-title {
    color: ${textColor} !important;
    font-weight: 600 !important;
}

.message-body {
    color: ${secondaryTextColor} !important;
}

.message-secondary-timestamp {
    color: ${secondaryTextColor} !important;
    font-size: 0.8em !important;
}

.weather-box,
.world-clocks-grid {
    color: ${textColor} !important;
}

/* ── Fast User Switching Menu (parv@arch Dropdown) ────────────────────────── */
.mak-user-menu-item {
    padding: 6px 12px !important;
    border-radius: 8px !important;
}

.mak-user-row-box {
    spacing: 10px;
}

.mak-user-avatar-frame {
    border-radius: 9999px !important;
    background-color: ${itemHoverBg} !important;
}

.mak-user-text-box {
    spacing: 2px;
}

.mak-user-name-label {
    font-weight: 600 !important;
    color: ${textColor} !important;
    font-size: 0.95em !important;
}

.mak-user-sub-label {
    color: ${secondaryTextColor} !important;
    font-size: 0.82em !important;
}

.mak-user-current-check {
    color: #9A57A3 !important;
}

.mak-user-menu-item:hover .mak-user-name-label {
    color: ${itemHoverColor} !important;
}

/* ── Quick Settings Control Center ────────────────────────────────────────── */
.quick-settings,
.quick-toggle-menu {
    border-radius: ${qsRadius}px !important;
    border: ${borderCss} !important;
    background-color: rgba(${bgR}, ${bgG}, ${bgB}, ${menuOpacity.toFixed(2)}) !important;
    box-shadow: ${qsBoxShadow} !important;
    color: ${textColor} !important;
}

.quick-settings StLabel,
.quick-toggle-menu StLabel {
    color: ${textColor} !important;
}

.quick-settings StIcon,
.quick-toggle-menu StIcon {
    color: ${textColor} !important;
}

/* Header Action Buttons (Screenshot, Settings, Lock, Power) */
.quick-settings-system-item .icon-button,
.quick-settings .icon-button,
.quick-settings .button {
    color: ${textColor} !important;
    background-color: ${qsTileBg} !important;
    border-radius: 9999px !important;
}

.quick-settings-system-item .icon-button StIcon,
.quick-settings .icon-button StIcon,
.quick-settings .button StIcon {
    color: ${textColor} !important;
}

.quick-settings-system-item .icon-button:hover,
.quick-settings .icon-button:hover,
.quick-settings .button:hover {
    background-color: ${qsTileHoverBg} !important;
    color: ${itemHoverColor} !important;
}

.quick-settings-system-item .icon-button:hover StIcon,
.quick-settings .icon-button:hover StIcon,
.quick-settings .button:hover StIcon {
    color: ${itemHoverColor} !important;
}

/* Quick Slider (Volume, Brightness) */
.quick-slider {
    background-color: ${qsTileBg} !important;
    border-radius: 24px !important;
}

.quick-slider StIcon,
.quick-slider .icon-button StIcon {
    color: ${textColor} !important;
}

/* Quick Toggles (Wi-Fi, Bluetooth, Dark Style, Night Light, etc.) */
.quick-toggle,
.quick-toggle-has-menu {
    background-color: ${qsTileBg} !important;
    border-radius: 9999px !important;
}

.quick-toggle:hover,
.quick-toggle-has-menu:hover {
    background-color: ${qsTileHoverBg} !important;
}

/* Unchecked Toggles: crisp contrast text and icons */
.quick-toggle:not(:checked) StIcon,
.quick-toggle:not(:checked) .quick-toggle-icon,
.quick-toggle-has-menu:not(:checked) StIcon,
.quick-toggle-has-menu:not(:checked) .quick-toggle-icon,
.quick-toggle-has-menu:not(:checked) .quick-toggle-menu-button StIcon {
    color: ${textColor} !important;
}

.quick-toggle:not(:checked) StLabel,
.quick-toggle-has-menu:not(:checked) StLabel {
    color: ${textColor} !important;
}

.quick-toggle-has-menu:not(:checked) .quick-toggle-menu-button {
    color: ${secondaryTextColor} !important;
}

/* Checked / Active Toggles: purple accent with crisp WHITE text and icons */
.quick-toggle:checked,
.quick-toggle-has-menu:checked,
.quick-toggle-has-menu .quick-toggle:checked {
    background-color: #9A57A3 !important;
    color: #ffffff !important;
}

.quick-toggle:checked StIcon,
.quick-toggle:checked .quick-toggle-icon,
.quick-toggle-has-menu:checked StIcon,
.quick-toggle-has-menu:checked .quick-toggle-icon,
.quick-toggle-has-menu:checked .quick-toggle-menu-button StIcon {
    color: #ffffff !important;
}

.quick-toggle:checked StLabel,
.quick-toggle-has-menu:checked StLabel,
.quick-toggle-has-menu:checked .quick-toggle-title,
.quick-toggle-has-menu:checked .quick-toggle-subtitle {
    color: #ffffff !important;
}

.quick-toggle-has-menu:checked .quick-toggle-menu-button {
    color: #ffffff !important;
}

/* Battery status in Quick Settings */
.quick-settings .battery-bar,
.quick-settings .battery-label,
.quick-settings-system-item StLabel {
    color: ${textColor} !important;
}

/* ── Notification Banners ─────────────────────────────────────────────────── */
.notification-banner {
    border-radius: ${notifRadius}px !important;
    border: ${borderCss} !important;
    background-color: rgba(${bgR}, ${bgG}, ${bgB}, ${menuOpacity.toFixed(2)}) !important;
    box-shadow: ${qsBoxShadow} !important;
    color: ${textColor} !important;
}

.notification-banner StLabel {
    color: ${textColor} !important;
}

/* ── Modal Dialogs ────────────────────────────────────────────────────────── */
.modal-dialog {
    border-radius: ${Math.max(16, radius + 4)}px !important;
    border: ${borderCss} !important;
    background-color: rgba(${bgR}, ${bgG}, ${bgB}, ${menuOpacity.toFixed(2)}) !important;
    box-shadow: ${qsBoxShadow} !important;
    color: ${textColor} !important;
}

.modal-dialog StLabel {
    color: ${textColor} !important;
}

/* ── Bluetooth Battery Indicator ─────────────────────────────────────────── */
.mak-bt-panel-box {
    spacing: 4px;
    padding: 0 4px;
}
.mak-bt-panel-label {
    font-size: 0.85em;
    font-weight: 600;
    margin-right: 2px;
}
.mak-bt-panel-bar-bg {
    height: 3px;
    width: 16px;
    background-color: ${btBarBg};
    border-radius: 2px;
    margin-top: 1px;
}
.mak-bt-panel-bar-fill {
    height: 3px;
    border-radius: 2px;
}
.mak-bt-fill-green { background-color: #34c759 !important; }
.mak-bt-fill-orange { background-color: #ff9500 !important; }
.mak-bt-fill-red { background-color: #ff3b30 !important; }
.mak-bt-container {
    spacing: 8px;
    padding: 6px;
    min-width: 250px;
}
.mak-bt-header {
    padding-bottom: 6px;
    border-bottom: 1px solid ${btHeaderBorder};
}
.mak-bt-header-label {
    font-weight: 700;
    font-size: 1.05em;
    color: ${textColor} !important;
}
.mak-bt-devices {
    spacing: 6px;
    padding-top: 4px;
}
.mak-bt-empty {
    color: ${btEmptyText};
    font-style: italic;
    text-align: center;
    padding: 12px;
}
.mak-bt-device-item {
    spacing: 10px;
    padding: 6px 10px;
    border-radius: 8px;
    transition-duration: 100ms;
}
.mak-bt-device-item:hover {
    background-color: ${btHoverBg};
}
.mak-bt-device-icon { icon-size: 16px; }
.mak-bt-device-label {
    font-size: 0.95em;
    color: ${textColor} !important;
}
.mak-bt-battery-box { spacing: 6px; }
.mak-bt-progress-bg {
    height: 6px;
    width: 55px;
    background-color: ${btBarBg};
    border-radius: 3px;
}
.mak-bt-progress-fill {
    height: 6px;
    background-color: #34c759;
    border-radius: 3px;
}
.mak-bt-battery-text {
    font-size: 0.85em;
    color: ${btText};
    width: 35px;
    text-align: right;
}

/* ── Dynamic Media / Music Pill ───────────────────────────────────────────── */
.music-pill-container {
    background: transparent !important;
    margin: 0 8px;
}
.pill-body {
    background-color: ${pillBodyBg} !important;
    border: ${borderCss} !important;
    border-radius: 20px !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
    transition: width 0.3s ease, height 0.3s ease, border-radius 0.3s ease, transform 0.3s ease;
}
.pill-body:hover {
    transform: translateY(-1px) scale(1.02);
}
.music-pill-expanded {
    background-color: rgba(${bgR}, ${bgG}, ${bgB}, ${menuOpacity.toFixed(2)}) !important;
    border: ${borderCss} !important;
    border-radius: ${radius}px !important;
    padding: 16px;
    box-shadow: ${qsBoxShadow} !important;
    min-width: 300px;
}

/* ── macOS Recording & Screen Sharing Glowing Status Badges ───────────────── */
.screen-recording-indicator,
.screen-sharing-indicator {
    background-color: rgba(255, 69, 58, 0.28) !important;
    border: 1px solid rgba(255, 69, 58, 0.6) !important;
    border-radius: 12px !important;
    box-shadow: 0 0 10px rgba(255, 69, 58, 0.5) !important;
    margin: 2px 4px !important;
    padding: 0 8px !important;
    color: #ff453a !important;
}

.screen-sharing-indicator {
    background-color: rgba(10, 132, 255, 0.28) !important;
    border-color: rgba(10, 132, 255, 0.6) !important;
    box-shadow: 0 0 10px rgba(10, 132, 255, 0.5) !important;
    color: #0a84ff !important;
}
`;

        try {
            GLib.file_set_contents(this._stylePath, css);
            this._reloadCustomStylesheet();
        } catch (err) {
            console.warn('[Mak Appearance] Error writing dynamic stylesheet:', err);
        }
    }

    _reloadCustomStylesheet() {
        this._unloadCustomStylesheet();

        try {
            const themeContext = St.ThemeContext.get_for_stage(global.stage);
            const theme = themeContext?.get_theme();
            if (theme && this._styleFile) {
                theme.load_stylesheet(this._styleFile);
                this._isLoaded = true;
            }
        } catch (err) {
            console.warn('[Mak Appearance] Error loading custom stylesheet:', err);
        }
    }

    _unloadCustomStylesheet() {
        if (this._isLoaded && this._styleFile) {
            try {
                const themeContext = St.ThemeContext.get_for_stage(global.stage);
                const theme = themeContext?.get_theme();
                if (theme) {
                    theme.unload_stylesheet(this._styleFile);
                }
            } catch (err) {
                console.warn('[Mak Appearance] Error unloading stylesheet:', err);
            }
            this._isLoaded = false;
        }
    }
}
