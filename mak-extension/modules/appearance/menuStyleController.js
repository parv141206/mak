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
        const borderOpacity = this._settings.get_double('menu-border-opacity');
        const specular = this._settings.get_boolean('menu-specular-highlight');
        const globalOpacity = this._settings.get_double('global-opacity');
        const configuredMenuOpacity = this._settings.get_double('menu-bg-opacity');
        const bgOpacity = (globalOpacity !== 0.5) ? globalOpacity : configuredMenuOpacity;
        const qsRadius = this._settings.get_int('quick-settings-radius');
        const notifRadius = this._settings.get_int('notification-radius');

        const colorScheme = this._interfaceSettings ? this._interfaceSettings.get_string('color-scheme') : '';
        const gtkTheme = this._interfaceSettings ? this._interfaceSettings.get_string('gtk-theme') : '';
        const isLight = (colorScheme === 'prefer-light') || gtkTheme.toLowerCase().includes('light');
        const isAmoled = gtkTheme.toLowerCase().includes('amoled');

        let bgR = 36, bgG = 36, bgB = 42;
        let textColor = '#f0f0f0';
        let itemHoverBg = 'rgba(255, 255, 255, 0.14)';
        let itemActiveBg = 'rgba(255, 255, 255, 0.24)';
        let itemSelectedBg = 'rgba(255, 255, 255, 0.18)';
        let itemHoverColor = '#ffffff';
        let separatorColor = 'rgba(255, 255, 255, 0.10)';
        let borderStrokeColor = `rgba(255, 255, 255, ${borderOpacity.toFixed(2)})`;
        let topSpecularColor = `rgba(255, 255, 255, ${Math.min(1.0, borderOpacity + 0.18).toFixed(2)})`;
        let pillBodyBg = `rgba(28, 28, 34, ${bgOpacity.toFixed(2)})`;
        let btHeaderBorder = 'rgba(255, 255, 255, 0.12)';
        let btEmptyText = 'rgba(255, 255, 255, 0.5)';
        let btHoverBg = 'rgba(255, 255, 255, 0.12)';
        let btBarBg = 'rgba(255, 255, 255, 0.2)';
        let btText = 'rgba(255, 255, 255, 0.8)';

        if (isLight) {
            bgR = 246; bgG = 246; bgB = 248;
            textColor = '#1d1d1f';
            itemHoverBg = 'rgba(0, 0, 0, 0.08)';
            itemActiveBg = 'rgba(0, 0, 0, 0.15)';
            itemSelectedBg = 'rgba(0, 0, 0, 0.12)';
            itemHoverColor = '#000000';
            separatorColor = 'rgba(0, 0, 0, 0.10)';
            borderStrokeColor = `rgba(0, 0, 0, ${Math.max(0.12, borderOpacity * 0.45).toFixed(2)})`;
            topSpecularColor = 'rgba(255, 255, 255, 0.85)';
            pillBodyBg = `rgba(255, 255, 255, ${bgOpacity.toFixed(2)})`;
            btHeaderBorder = 'rgba(0, 0, 0, 0.10)';
            btEmptyText = 'rgba(0, 0, 0, 0.45)';
            btHoverBg = 'rgba(0, 0, 0, 0.07)';
            btBarBg = 'rgba(0, 0, 0, 0.15)';
            btText = 'rgba(0, 0, 0, 0.75)';
        } else if (isAmoled) {
            bgR = 0; bgG = 0; bgB = 0;
            textColor = '#f0f0f0';
            itemHoverBg = 'rgba(255, 255, 255, 0.16)';
            itemActiveBg = 'rgba(255, 255, 255, 0.26)';
            itemSelectedBg = 'rgba(255, 255, 255, 0.20)';
            itemHoverColor = '#ffffff';
            separatorColor = 'rgba(255, 255, 255, 0.12)';
            borderStrokeColor = `rgba(255, 255, 255, ${borderOpacity.toFixed(2)})`;
            topSpecularColor = `rgba(255, 255, 255, ${Math.min(1.0, borderOpacity + 0.18).toFixed(2)})`;
            pillBodyBg = `rgba(10, 10, 12, ${bgOpacity.toFixed(2)})`;
            btHeaderBorder = 'rgba(255, 255, 255, 0.14)';
            btEmptyText = 'rgba(255, 255, 255, 0.5)';
            btHoverBg = 'rgba(255, 255, 255, 0.14)';
            btBarBg = 'rgba(255, 255, 255, 0.22)';
            btText = 'rgba(255, 255, 255, 0.8)';
        }

        const borderCss = borderWidth > 0
            ? `${borderWidth}px solid ${borderStrokeColor}`
            : 'none';

        const topHighlight = specular
            ? `border-top: 1px solid ${topSpecularColor} !important;`
            : '';

        const css = `/* Generated by Mak Appearance Controller */
/* ── Unified macOS Popup Menus, Context Menus & Kiwi Menu ─────────────────── */
.popup-menu-boxpointer,
.candidate-popup-boxpointer {
    -arrow-rise: 0px !important;
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
    ${topHighlight}
    background-color: rgba(${bgR}, ${bgG}, ${bgB}, ${bgOpacity.toFixed(2)}) !important;
    box-shadow: none !important;
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

.popup-menu-item:hover,
.popup-menu-item:focus {
    background-color: ${itemHoverBg} !important;
    color: ${itemHoverColor} !important;
}

.popup-menu-item:active {
    background-color: ${itemActiveBg} !important;
    color: ${itemHoverColor} !important;
}

.popup-menu-item.selected {
    background-color: ${itemSelectedBg} !important;
    color: ${itemHoverColor} !important;
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

/* ── Quick Settings Control Center ────────────────────────────────────────── */
.quick-settings,
.quick-toggle-menu {
    border-radius: ${qsRadius}px !important;
    border: ${borderCss} !important;
    ${topHighlight}
    background-color: rgba(${bgR}, ${bgG}, ${bgB}, ${bgOpacity.toFixed(2)}) !important;
    box-shadow: none !important;
}

/* ── Notification Banners ─────────────────────────────────────────────────── */
.notification-banner {
    border-radius: ${notifRadius}px !important;
    border: ${borderCss} !important;
    ${topHighlight}
    background-color: rgba(${bgR}, ${bgG}, ${bgB}, ${bgOpacity.toFixed(2)}) !important;
    box-shadow: none !important;
}

/* ── Modal Dialogs ────────────────────────────────────────────────────────── */
.modal-dialog {
    border-radius: ${Math.max(16, radius + 4)}px !important;
    border: ${borderCss} !important;
    ${topHighlight}
    background-color: rgba(${bgR}, ${bgG}, ${bgB}, ${bgOpacity.toFixed(2)}) !important;
    box-shadow: none !important;
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
    ${topHighlight}
    box-shadow: none !important;
    transition: width 0.3s ease, height 0.3s ease, border-radius 0.3s ease, transform 0.3s ease;
}
.pill-body:hover {
    transform: translateY(-1px) scale(1.02);
}
.music-pill-expanded {
    background-color: rgba(${bgR}, ${bgG}, ${bgB}, ${bgOpacity.toFixed(2)}) !important;
    border: ${borderCss} !important;
    border-radius: ${radius}px !important;
    ${topHighlight}
    padding: 16px;
    box-shadow: none !important;
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
