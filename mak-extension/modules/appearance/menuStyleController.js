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
                key.startsWith('notification-') || key === 'global-opacity' ||
                key === 'blur-liquid-glass' || key.startsWith('topbar-') ||
                key.startsWith('control-center-') || key.startsWith('desktop-menu-') ||
                key.startsWith('dock-')) {
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

        const getStr = (key, fallback) => {
            try {
                if (this._settings?.settings_schema?.has_key(key)) {
                    const val = this._settings.get_string(key);
                    return val || fallback;
                }
            } catch (e) {}
            return fallback;
        };

        const getDbl = (key, fallback) => {
            try {
                if (this._settings?.settings_schema?.has_key(key)) {
                    return this._settings.get_double(key);
                }
            } catch (e) {}
            return fallback;
        };

        const hexToRgb = (hex, fallback = [255, 255, 255]) => {
            if (!hex || typeof hex !== 'string') return fallback;
            const h = hex.trim().replace(/^#/, '');
            if (h.length === 3) {
                return [
                    parseInt(h[0] + h[0], 16),
                    parseInt(h[1] + h[1], 16),
                    parseInt(h[2] + h[2], 16)
                ];
            }
            if (h.length === 6) {
                return [
                    parseInt(h.substring(0, 2), 16),
                    parseInt(h.substring(2, 4), 16),
                    parseInt(h.substring(4, 6), 16)
                ];
            }
            return fallback;
        };

        const topbarTextColor = getStr('topbar-text-color', '#ffffff');
        const topbarIconColor = getStr('topbar-icon-color', '#ffffff');
        const controlCenterTextColor = getStr('control-center-text-color', '#ffffff');
        const controlCenterIconColor = getStr('control-center-icon-color', '#ffffff');
        const customMenuTextColor = getStr('menu-text-color', '#ffffff');

        const controlCenterTintColor = getStr('control-center-tint-color', '#ffffff');
        const controlCenterTintStrength = getDbl('control-center-tint-strength', 0.08);
        const [ccTintR, ccTintG, ccTintB] = hexToRgb(controlCenterTintColor);

        const menuTintColor = getStr('menu-tint-color', '#ffffff');
        const menuTintStrength = getDbl('menu-tint-strength', 0.08);
        const [mTintR, mTintG, mTintB] = hexToRgb(menuTintColor);

        let bgR = 32, bgG = 32, bgB = 36;
        let menuOpacity = 0.65;
        let textColor = '#f5f5f7';
        let secondaryTextColor = 'rgba(255, 255, 255, 0.55)';
        let itemHoverBg = '#007aff';
        let itemActiveBg = '#0062cc';
        let itemSelectedBg = '#007aff';
        let itemHoverColor = '#ffffff';
        let separatorColor = 'rgba(255, 255, 255, 0.10)';
        let borderStrokeColor = 'rgba(255, 255, 255, 0.14)';
        let boxShadow = '0 10px 24px rgba(0, 0, 0, 0.25), 0 2px 6px rgba(0, 0, 0, 0.12)';
        let qsBoxShadow = '0 12px 28px rgba(0, 0, 0, 0.28), 0 2px 8px rgba(0, 0, 0, 0.14)';
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
            itemHoverBg = '#007aff';
            itemActiveBg = '#0062cc';
            itemSelectedBg = '#007aff';
            itemHoverColor = '#ffffff';
            separatorColor = 'rgba(0, 0, 0, 0.08)';
            borderStrokeColor = 'rgba(0, 0, 0, 0.12)';
            boxShadow = '0 8px 20px rgba(0, 0, 0, 0.12), 0 2px 6px rgba(0, 0, 0, 0.06)';
            qsBoxShadow = '0 10px 24px rgba(0, 0, 0, 0.14), 0 2px 6px rgba(0, 0, 0, 0.06)';
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
            itemHoverBg = '#007aff';
            itemActiveBg = '#0062cc';
            itemSelectedBg = '#007aff';
            itemHoverColor = '#ffffff';
            separatorColor = 'rgba(255, 255, 255, 0.12)';
            borderStrokeColor = 'rgba(255, 255, 255, 0.18)';
            boxShadow = '0 10px 28px rgba(0, 0, 0, 0.50), 0 2px 6px rgba(0, 0, 0, 0.25)';
            qsBoxShadow = '0 12px 32px rgba(0, 0, 0, 0.55), 0 2px 8px rgba(0, 0, 0, 0.28)';
            pillBodyBg = `rgba(10, 10, 12, ${menuOpacity})`;
            qsTileBg = 'rgba(255, 255, 255, 0.12)';
            qsTileHoverBg = 'rgba(255, 255, 255, 0.18)';
            btHeaderBorder = 'rgba(255, 255, 255, 0.14)';
            btEmptyText = 'rgba(255, 255, 255, 0.5)';
            btHoverBg = 'rgba(255, 255, 255, 0.14)';
            btBarBg = 'rgba(255, 255, 255, 0.22)';
            btText = 'rgba(255, 255, 255, 0.8)';
        }
        const finalTopbarText = (topbarTextColor && topbarTextColor !== 'default') ? topbarTextColor : (isLight ? '#1d1d1f' : '#f5f5f7');
        const finalTopbarIcon = (topbarIconColor && topbarIconColor !== 'default') ? topbarIconColor : (isLight ? '#1d1d1f' : '#f2f2f7');

        const isCCWhite = controlCenterTextColor === '#ffffff' || controlCenterTextColor === 'rgb(255,255,255)';
        const finalCCText = (controlCenterTextColor && controlCenterTextColor !== 'default' && !(isLight && isCCWhite))
            ? controlCenterTextColor 
            : (isLight ? '#1d1d1f' : '#f5f5f7');
        const isCCIconWhite = controlCenterIconColor === '#ffffff' || controlCenterIconColor === 'rgb(255,255,255)';
        const finalCCIcon = (controlCenterIconColor && controlCenterIconColor !== 'default' && !(isLight && isCCIconWhite))
            ? controlCenterIconColor 
            : (isLight ? '#1d1d1f' : '#f2f2f7');
        const isMenuWhite = customMenuTextColor === '#ffffff' || customMenuTextColor === 'rgb(255,255,255)';
        const finalMenuText = (customMenuTextColor && customMenuTextColor !== 'default' && !(isLight && isMenuWhite))
            ? customMenuTextColor 
            : textColor;

        const isLiquidGlass = this._settings.get_boolean('blur-liquid-glass');
        if (isLiquidGlass) {
            menuOpacity = isLight ? 0.30 : (isAmoled ? 0.38 : 0.34);
            borderStrokeColor = isLight ? 'rgba(0, 0, 0, 0.10)' : 'rgba(255, 255, 255, 0.15)';
            boxShadow = isLight
                ? '0 10px 28px rgba(0, 0, 0, 0.12), 0 2px 6px rgba(0, 0, 0, 0.05)'
                : '0 12px 32px rgba(0, 0, 0, 0.35), 0 2px 8px rgba(0, 0, 0, 0.15)';
            qsBoxShadow = isLight
                ? '0 12px 30px rgba(0, 0, 0, 0.14), 0 2px 6px rgba(0, 0, 0, 0.06)'
                : '0 14px 36px rgba(0, 0, 0, 0.40), 0 2px 10px rgba(0, 0, 0, 0.18)';
        }

        // Quick Settings capsule/pill tinting
        const ccPillAlpha = isLight
            ? (0.20 + controlCenterTintStrength * 0.12).toFixed(2)
            : (0.08 + controlCenterTintStrength * 0.14).toFixed(2);
        const ccPillHoverAlpha = isLight
            ? (0.32 + controlCenterTintStrength * 0.14).toFixed(2)
            : (0.16 + controlCenterTintStrength * 0.16).toFixed(2);
        const qsPillBg = isLiquidGlass
            ? `rgba(${ccTintR}, ${ccTintG}, ${ccTintB}, ${ccPillAlpha})`
            : qsTileBg;
        const qsPillHoverBg = isLiquidGlass
            ? `rgba(${ccTintR}, ${ccTintG}, ${ccTintB}, ${ccPillHoverAlpha})`
            : qsTileHoverBg;

        // Submenu background inside Quick Settings
        const qsSubmenuBgR = (controlCenterTintColor !== '#ffffff' && controlCenterTintStrength > 0)
            ? Math.round(bgR * (1 - controlCenterTintStrength) + ccTintR * controlCenterTintStrength)
            : bgR;
        const qsSubmenuBgG = (controlCenterTintColor !== '#ffffff' && controlCenterTintStrength > 0)
            ? Math.round(bgG * (1 - controlCenterTintStrength) + ccTintG * controlCenterTintStrength)
            : bgG;
        const qsSubmenuBgB = (controlCenterTintColor !== '#ffffff' && controlCenterTintStrength > 0)
            ? Math.round(bgB * (1 - controlCenterTintStrength) + ccTintB * controlCenterTintStrength)
            : bgB;

        // Menu background tinted with menu-tint-color
        if (menuTintColor !== '#ffffff' && menuTintStrength > 0) {
            bgR = Math.round(bgR * (1 - menuTintStrength) + mTintR * menuTintStrength);
            bgG = Math.round(bgG * (1 - menuTintStrength) + mTintG * menuTintStrength);
            bgB = Math.round(bgB * (1 - menuTintStrength) + mTintB * menuTintStrength);
        }

        const frostedGlassBg = (menuTintColor !== '#ffffff' && menuTintStrength > 0)
            ? `rgba(${mTintR}, ${mTintG}, ${mTintB}, ${isLight ? 0.32 : 0.28})`
            : (isLight
                ? 'rgba(255, 255, 255, 0.28)'
                : (isAmoled ? 'rgba(18, 18, 22, 0.36)' : 'rgba(30, 30, 34, 0.32)'));

        const borderCss = `${borderWidth > 0 ? borderWidth : 1}px solid ${borderStrokeColor}`;

        const css = `/* Generated by Mak Appearance Controller */
/* ── Explicit Top Bar Item Colors ────────────────────────────────────────── */
#panel.mak-panel .panel-button,
#panel.mak-panel .panel-button StLabel,
#panel.mak-panel .mak-app-title-label,
#panel.mak-panel .clock-display,
#panel.mak-panel .clock,
#panel.mak-panel .clock-display-box .clock,
#panel.mak-panel .mak-user-switcher-label,
#panel.mak-panel .mak-bt-panel-label {
    color: ${finalTopbarText} !important;
}

#panel.mak-panel .menu-button,
#panel.mak-panel .system-status-icon,
#panel.mak-panel .panel-button StIcon,
#panel.mak-panel .panel-button .system-status-icon,
#panel.mak-panel .mak-spotlight-button StIcon,
#panel.mak-panel .mak-control-center-button StIcon,
#panel.mak-panel .mak-quick-settings-button StIcon,
#panel.mak-panel .mak-bt-panel-box StIcon {
    color: ${finalTopbarIcon} !important;
}

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
    color: ${finalMenuText} !important;
}

.popup-menu-item StLabel {
    color: ${finalMenuText} !important;
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

.calendar-day-base,
.calendar-day,
.calendar .calendar-day {
    color: ${textColor} !important;
    border-radius: 9999px !important;
    font-weight: normal !important;
    text-align: center;
    margin: 2px !important;
}

.calendar-day-base:hover,
.calendar-day-base:focus,
.calendar-day:hover,
.calendar-day:focus,
.calendar .calendar-day:hover {
    background-color: ${itemHoverBg} !important;
    color: ${itemHoverColor} !important;
}

.calendar-day-base:active,
.calendar-day:active,
.calendar .calendar-day:active {
    background-color: ${itemActiveBg} !important;
    color: ${itemHoverColor} !important;
}

.calendar-day-base:selected,
.calendar-day:selected,
.calendar-day:checked,
.calendar .calendar-day:selected,
.calendar .calendar-day:checked {
    background-color: -st-accent-color !important;
    color: #ffffff !important;
    font-weight: bold !important;
}

/* Today circle */
.calendar-day-base.calendar-today,
.calendar-day.calendar-today,
.calendar .calendar-day.calendar-today {
    background-color: -st-accent-color !important;
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

.message-list .message {
    background-color: ${qsTileBg} !important;
    border-radius: 14px !important;
    color: ${textColor} !important;
    padding: 8px 12px !important;
}

.message-list .message:hover {
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
    color: -st-accent-color !important;
}

.mak-user-menu-item:hover .mak-user-name-label {
    color: ${itemHoverColor} !important;
}

/* ── Quick Settings Control Center Floating Individual Liquid Glass Pills ─── */
/* Outer background is completely transparent so each pod floats as an independent pill */
.quick-settings-menu,
.quick-settings-menu .popup-menu-content,
.quick-settings-menu .popup-menu-boxpointer,
.popup-menu-boxpointer:has(.quick-settings),
.popup-menu-content:has(.quick-settings),
.popup-menu:has(.quick-settings),
.liquid-glass-qs-root,
.liquid-glass-qs-root .popup-menu-content,
.liquid-glass-qs-root .popup-menu-boxpointer,
.liquid-glass-transparent:has(.quick-settings),
.liquid-glass-transparent.popup-menu:has(.quick-settings),
.liquid-glass-transparent.quick-settings,
.liquid-glass-qs-root.quick-settings {
    border: none !important;
    background: transparent !important;
    background-color: transparent !important;
    background-image: none !important;
    box-shadow: none !important;
    margin: 0 !important;
    padding: 0 !important;
}

.quick-settings {
    border: none !important;
    background: transparent !important;
    background-color: transparent !important;
    background-image: none !important;
    box-shadow: none !important;
    margin: 0 !important;
    padding: 8px !important;
}

/* Unified structured grid gaps between pills */
.quick-settings-grid {
    spacing-rows: 8px !important;
    spacing-columns: 8px !important;
}

/* Other popup menus (Kiwi menu, date/calendar) preserve their frosted glass card */
.popup-menu:not(.liquid-glass-qs-root) .popup-menu-content,
.popup-menu.liquid-glass-transparent:not(.liquid-glass-qs-root) .popup-menu-content {
    border: ${borderCss} !important;
    background-color: ${frostedGlassBg} !important;
    box-shadow: ${boxShadow} !important;
}

.liquid-glass-transparent.notification-banner,
.liquid-glass-transparent .notification-banner,
.notification-banner.liquid-glass-transparent,
.notification-banner.liquid-glass-transparent-keep-border {
    border: ${borderCss} !important;
    background-color: ${frostedGlassBg} !important;
    box-shadow: ${qsBoxShadow} !important;
    border-radius: ${notifRadius}px !important;
}

/* ── Top System Row: Battery pill + circular action icons ──────────────────── */
.quick-settings-system-item {
    margin-bottom: 4px !important;
}

.quick-settings-system-item > StBoxLayout {
    spacing: 6px !important;
}

/* Battery percentage pill: compact, elegant capsule pill */
.quick-settings-system-item .power-item,
.quick-settings-system-item .quick-toggle.power-item {
    min-width: 0 !important;
    max-width: none !important;
    min-height: 34px !important;
    height: 34px !important;
    padding: 0 12px !important;
    margin: 0 !important;
    border-radius: 9999px !important;
    background-color: ${qsPillBg} !important;
    border: 1px solid ${borderStrokeColor} !important;
    box-shadow: none !important;
    color: ${finalCCText} !important;
}

.quick-settings-system-item .power-item StIcon,
.quick-settings-system-item .quick-toggle.power-item StIcon {
    icon-size: 16px !important;
    color: ${finalCCIcon} !important;
    margin-right: 4px !important;
}

.quick-settings-system-item .power-item StLabel,
.quick-settings-system-item .quick-toggle.power-item StLabel {
    color: ${finalCCText} !important;
    font-size: 0.9em !important;
    font-weight: 600 !important;
}

/* Header Action Buttons (Screenshot, Settings, Lock, Power) - Sleek round pills */
.quick-settings-system-item .icon-button,
.quick-settings .icon-button,
.quick-settings .button {
    min-width: 34px !important;
    min-height: 34px !important;
    width: 34px !important;
    height: 34px !important;
    padding: 0 !important;
    margin: 0 !important;
    color: ${finalCCIcon} !important;
    background-color: ${qsPillBg} !important;
    border: 1px solid ${borderStrokeColor} !important;
    border-radius: 9999px !important;
    box-shadow: none !important;
}

.quick-settings-system-item .icon-button StIcon,
.quick-settings .icon-button StIcon,
.quick-settings .button StIcon {
    icon-size: 15px !important;
    color: ${finalCCIcon} !important;
}

.quick-settings-system-item .icon-button:hover,
.quick-settings .icon-button:hover,
.quick-settings .button:hover {
    background-color: ${qsPillHoverBg} !important;
    color: ${itemHoverColor} !important;
}

.quick-settings-system-item .icon-button:hover StIcon,
.quick-settings .icon-button:hover StIcon,
.quick-settings .button:hover StIcon {
    color: ${itemHoverColor} !important;
}

/* ── Sliders (Volume, Brightness) - Clean capsules ─────────────────────────── */
.quick-slider {
    min-height: 38px !important;
    height: 38px !important;
    padding: 0 12px !important;
    margin: 2px 0 !important;
    background-color: ${qsPillBg} !important;
    border: 1px solid ${borderStrokeColor} !important;
    border-radius: 9999px !important;
    box-shadow: none !important;
}

.quick-slider > StBoxLayout {
    spacing: 10px !important;
}

.quick-slider .icon-button {
    padding: 0 !important;
    margin: 0 !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

.quick-slider StIcon,
.quick-slider .icon-button StIcon {
    icon-size: 16px !important;
    color: ${finalCCIcon} !important;
}

.quick-slider .slider-bin {
    min-height: 16px !important;
    padding: 0 !important;
}

/* ── Quick Toggles (Wi-Fi, Bluetooth, Dark Style, Night Light, etc.) ───────── */
/* Outer pills: consistent capsule geometry and refined proportions */
.quick-settings-grid > .quick-toggle,
.quick-settings-grid .quick-toggle:not(.quick-toggle-has-menu .quick-toggle):not(.power-item),
.quick-toggle-has-menu {
    min-height: 44px !important;
    height: 44px !important;
    border-radius: 9999px !important;
    background-color: ${qsPillBg} !important;
    border: 1px solid ${borderStrokeColor} !important;
    box-shadow: none !important;
    margin: 0 !important;
    padding: 0 !important;
}

.quick-settings-grid > .quick-toggle,
.quick-settings-grid .quick-toggle:not(.quick-toggle-has-menu .quick-toggle):not(.power-item) {
    padding: 0 12px !important;
}

.quick-settings-grid > .quick-toggle:hover,
.quick-settings-grid .quick-toggle:hover:not(.quick-toggle-has-menu .quick-toggle):not(.power-item),
.quick-toggle-has-menu:hover {
    background-color: ${qsPillHoverBg} !important;
}

/* Reset inner buttons inside .quick-toggle-has-menu: prevent double boxes & weird borders */
.quick-toggle-has-menu .quick-toggle {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 0 0 12px !important;
    min-height: 44px !important;
    height: 44px !important;
    border-radius: 9999px 0 0 9999px !important;
}

.quick-toggle-has-menu .quick-toggle-menu-button {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 10px 0 4px !important;
    min-height: 44px !important;
    height: 44px !important;
    border-radius: 0 9999px 9999px 0 !important;
    color: ${finalCCIcon} !important;
}

.quick-toggle-has-menu .quick-toggle-menu-button:hover {
    background-color: rgba(255, 255, 255, 0.12) !important;
}

.quick-toggle-has-menu .quick-toggle-separator {
    width: 0 !important;
    border: none !important;
    background: transparent !important;
}

/* Dropdown Submenus inside Quick Settings */
.quick-toggle-menu,
.quick-settings .quick-toggle-menu,
.liquid-glass-qs-root .quick-toggle-menu,
.quick-settings .popup-sub-menu {
    border-radius: 18px !important;
    border: 1px solid ${borderStrokeColor} !important;
    background-color: rgba(${qsSubmenuBgR}, ${qsSubmenuBgG}, ${qsSubmenuBgB}, ${isLight ? '0.92' : '0.88'}) !important;
    box-shadow: ${qsBoxShadow} !important;
    padding: 10px 14px !important;
    margin: 8px 0 !important;
}

.quick-toggle-menu .header,
.quick-settings .quick-toggle-menu .header {
    margin-bottom: 8px !important;
    padding-bottom: 6px !important;
    border-bottom: 1px solid ${separatorColor} !important;
}

.quick-toggle-menu .header .title,
.quick-settings .quick-toggle-menu .header .title {
    color: ${textColor} !important;
    font-weight: bold !important;
    font-size: 1.1em !important;
}

.quick-toggle-menu .header .subtitle,
.quick-settings .quick-toggle-menu .header .subtitle {
    color: ${secondaryTextColor} !important;
    font-size: 0.88em !important;
}

.quick-toggle-menu .header .icon,
.quick-settings .quick-toggle-menu .header .icon {
    color: ${textColor} !important;
}

.quick-toggle-menu .popup-menu-item,
.quick-settings .quick-toggle-menu .popup-menu-item {
    border-radius: 10px !important;
    padding: 8px 12px !important;
    margin: 2px 0 !important;
    color: ${textColor} !important;
}

.quick-toggle-menu .popup-menu-item StLabel,
.quick-settings .quick-toggle-menu .popup-menu-item StLabel {
    color: ${textColor} !important;
}

.quick-toggle-menu .popup-menu-item StIcon,
.quick-settings .quick-toggle-menu .popup-menu-item StIcon {
    color: ${textColor} !important;
}

.quick-toggle-menu .popup-menu-item:hover,
.quick-toggle-menu .popup-menu-item:focus,
.quick-settings .quick-toggle-menu .popup-menu-item:hover,
.quick-settings .quick-toggle-menu .popup-menu-item:focus {
    background-color: ${itemHoverBg} !important;
    color: ${itemHoverColor} !important;
}

.quick-toggle-menu .popup-menu-item:hover StLabel,
.quick-toggle-menu .popup-menu-item:focus StLabel,
.quick-toggle-menu .popup-menu-item:hover StIcon,
.quick-toggle-menu .popup-menu-item:focus StIcon,
.quick-settings .quick-toggle-menu .popup-menu-item:hover StLabel,
.quick-settings .quick-toggle-menu .popup-menu-item:focus StLabel,
.quick-settings .quick-toggle-menu .popup-menu-item:hover StIcon,
.quick-settings .quick-toggle-menu .popup-menu-item:focus StIcon {
    color: ${itemHoverColor} !important;
}

.quick-toggle-menu .popup-menu-item:active,
.quick-settings .quick-toggle-menu .popup-menu-item:active {
    background-color: ${itemActiveBg} !important;
    color: ${itemHoverColor} !important;
}

.quick-toggle-menu .popup-menu-item.selected,
.quick-settings .quick-toggle-menu .popup-menu-item.selected {
    background-color: ${itemSelectedBg} !important;
    color: ${itemHoverColor} !important;
}

.quick-toggle-menu .popup-separator-menu-item,
.quick-settings .quick-toggle-menu .popup-separator-menu-item {
    margin: 4px 6px !important;
    padding: 0 !important;
}

.quick-toggle-menu .popup-separator-menu-item .popup-separator-menu-item-separator,
.quick-settings .quick-toggle-menu .popup-separator-menu-item .popup-separator-menu-item-separator {
    background-color: ${separatorColor} !important;
    height: 1px !important;
}

/* Unchecked Toggles & Dropdown items: explicit user-configured text and icons */
.quick-toggle:not(:checked) StIcon,
.quick-toggle:not(:checked) .quick-toggle-icon,
.quick-toggle-has-menu:not(:checked) StIcon,
.quick-toggle-has-menu:not(:checked) .quick-toggle-icon,
.quick-toggle-has-menu:not(:checked) .quick-toggle-menu-button StIcon,
.quick-toggle-menu StIcon {
    color: ${finalCCIcon} !important;
}

.quick-toggle:not(:checked) StLabel,
.quick-toggle-has-menu:not(:checked) StLabel,
.quick-toggle-has-menu:not(:checked) .quick-toggle-title,
.quick-settings StLabel,
.quick-toggle-menu StLabel {
    color: ${finalCCText} !important;
}

.quick-toggle-has-menu:not(:checked) .quick-toggle-subtitle {
    color: ${secondaryTextColor} !important;
}

.quick-toggle-has-menu:not(:checked) .quick-toggle-menu-button {
    color: ${secondaryTextColor} !important;
}

/* Checked / Active Toggles: dynamic shell accent with crisp WHITE text and icons */
.quick-settings-grid > .quick-toggle:checked,
.quick-settings-grid .quick-toggle:checked:not(.quick-toggle-has-menu .quick-toggle):not(.power-item),
.quick-toggle-has-menu:checked {
    background-color: -st-accent-color !important;
    color: #ffffff !important;
}

.quick-toggle:checked StIcon,
.quick-toggle:checked .quick-toggle-icon,
.quick-toggle-has-menu:checked StIcon,
.quick-toggle-has-menu:checked .quick-toggle-icon,
.quick-toggle-has-menu:checked .quick-toggle-menu-button StIcon {
    color: #ffffff !important;
}

.quick-toggle-has-menu:checked .quick-toggle,
.quick-toggle-has-menu:checked .quick-toggle StLabel,
.quick-toggle-has-menu:checked .quick-toggle-title,
.quick-toggle-has-menu:checked .quick-toggle-subtitle {
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
    color: ${finalCCText} !important;
}

/* ── Notification Banners ─────────────────────────────────────────────────── */
.notification-banner,
.notification-banner:hover,
.notification-banner:focus,
.notification-banner:active,
.notification-banner.message,
.notification-banner.message:hover,
.notification-banner.message:focus,
.notification-banner.message:active,
.message.notification-banner,
.message.notification-banner:hover,
.message.notification-banner:focus,
.message.notification-banner:active {
    border-radius: ${notifRadius}px !important;
    border: ${borderCss} !important;
    background-color: rgba(${bgR}, ${bgG}, ${bgB}, ${menuOpacity.toFixed(2)}) !important;
    box-shadow: ${qsBoxShadow} !important;
    color: ${textColor} !important;
}

.notification-banner StLabel,
.notification-banner:hover StLabel,
.notification-banner .message-title,
.notification-banner .message-body,
.notification-banner .message-header-content {
    color: ${textColor} !important;
}

.notification-banner .message,
.notification-banner .message-box,
.notification-banner .message-content,
.notification-banner .message-header,
.notification-banner .message-body,
.notification-banner .message-header-content,
.notification-banner StBoxLayout,
.notification-banner StBin,
.notification-banner .message-notification-group {
    background-color: transparent !important;
    background-image: none !important;
    border: none !important;
    box-shadow: none !important;
}

.notification-banner .message-close-button,
.notification-banner .message .message-header .message-close-button {
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    border-radius: 9999px !important;
    padding: 2px !important;
    min-height: 18px !important;
    min-width: 18px !important;
    color: ${textColor} !important;
    opacity: 0.65 !important;
}

.notification-banner .message-close-button:hover,
.notification-banner .message .message-header .message-close-button:hover {
    background-color: rgba(255, 255, 255, 0.15) !important;
    opacity: 1.0 !important;
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

/* ── Mak Quick Settings Dynamic Theming ─────────────────────────────────── */
.mak-qs-menu {
    border-radius: ${radius}px !important;
    border: ${borderCss} !important;
    background-color: rgba(${bgR}, ${bgG}, ${bgB}, ${menuOpacity.toFixed(2)}) !important;
    box-shadow: ${boxShadow} !important;
}

.mak-qs-title {
    color: ${textColor} !important;
}

.mak-qs-subtitle,
.mak-qs-section-title {
    color: ${secondaryTextColor} !important;
}

.mak-qs-toggle-label,
.mak-qs-step-val {
    color: ${textColor} !important;
}

.mak-qs-open-btn {
    background-color: ${itemHoverBg} !important;
    color: ${textColor} !important;
    border: 1px solid ${borderStrokeColor} !important;
}

.mak-qs-open-btn:hover {
    background-color: ${itemActiveBg} !important;
    color: ${itemHoverColor} !important;
}

.mak-qs-divider {
    background-color: ${separatorColor} !important;
}

.mak-qs-theme-btn {
    background-color: ${itemHoverBg} !important;
    color: ${textColor} !important;
    border: 1px solid ${borderStrokeColor} !important;
}

.mak-qs-theme-btn:hover {
    background-color: ${itemActiveBg} !important;
    color: ${itemHoverColor} !important;
}

.mak-qs-step-btn {
    background-color: ${itemHoverBg} !important;
    color: ${textColor} !important;
    border: 1px solid ${borderStrokeColor} !important;
}

.mak-qs-step-btn:hover {
    background-color: ${itemActiveBg} !important;
}

.mak-qs-switch-btn {
    background-color: ${itemHoverBg} !important;
    color: ${secondaryTextColor} !important;
    border: 1px solid ${borderStrokeColor} !important;
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
