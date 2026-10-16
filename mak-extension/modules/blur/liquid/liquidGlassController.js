// SPDX-License-Identifier: GPL-3.0-or-later
// Mak Liquid Glass Controller
// Coordinates hardware-accelerated dynamic liquid glass refraction across
// Application Windows, Dock, Top Bar, Popups, Menus, Quick Settings, and OSDs.

import GLib from 'gi://GLib';
import Gio from 'gi://Gio';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';

import { ApplicationManager } from './applicationManager.js';
import { DashManager } from './dockManager.js';
import { TopBarManager } from './topBarManager.js';
import { PanelMenuManager } from './panelMenuManager.js';
import { QuickSettingsManager } from './quickSettingsManager.js';
import { NotificationManager } from './notificationManager.js';
import { OsdManager } from './osdManager.js';
import { UIManager } from './uiManager.js';
import { Logger } from './logger.js';
import { installGlassDiagnostics, removeGlassDiagnostics } from './diagnostics/glass.js';
import { setUtilsLogger } from './diagnostics/logging.js';

export class LiquidGlassController {
    constructor(extension) {
        this._extension = extension;
        this._makSettings = extension.getSettings('org.gnome.shell.extensions.mak');
        this._liquidSettings = null;
        this._logger = null;
        this._applicationManager = null;
        this._topBarManager = null;
        this._panelMenuManager = null;
        this._calendarMenuManager = null;
        this._quickSettingsManager = null;
        this._notificationManager = null;
        this._osdManager = null;
        this._dashDocks = [];
        this._dashSearchId = 0;
        this._uiChildAddedId = 0;
        this._monitorsChangedId = 0;
        this._makSettingsIds = [];
        this._interfaceSettings = null;
        this._ifaceChangedId = 0;
        this._enabled = false;
    }

    enable() {
        if (this._enabled) return;
        this._enabled = true;

        try {
            this._interfaceSettings = new Gio.Settings({ schema_id: 'org.gnome.desktop.interface' });
            this._ifaceChangedId = this._interfaceSettings.connect('changed::gtk-theme', () => this._syncMakPreferences());
        } catch (e) {
            console.warn('[Mak LiquidGlass] Failed to initialize desktop interface settings:', e);
        }

        try {
            this._liquidSettings = new Gio.Settings({ schema_id: 'org.gnome.shell.extensions.liquid-glass@thinkingcoding1231.gmail.com' });
        } catch (e) {
            console.error('[Mak LiquidGlass] Failed to initialize liquid glass schema:', e);
            return;
        }

        this._logger = new Logger(this._liquidSettings);
        setUtilsLogger(this._logger);
        installGlassDiagnostics();

        // Sync initial parameters from Mak into Liquid Glass
        this._syncMakPreferences();
        this._bindMakSettings();

        const path = this._extension.path + '/modules/blur/liquid';

        try {
            this._applicationManager = new ApplicationManager(path, this._liquidSettings, this._logger);
            this._applicationManager.setup();
        } catch (err) {
            console.error('[Mak LiquidGlass] ApplicationManager error:', err);
        }

        try {
            this._topBarManager = new TopBarManager(path, this._liquidSettings, this._logger);
            this._topBarManager.setup();
        } catch (err) {
            console.error('[Mak LiquidGlass] TopBarManager error:', err);
        }

        try {
            this._panelMenuManager = new PanelMenuManager(path, this._liquidSettings, this._logger);
            this._panelMenuManager.setup();
        } catch (err) {
            console.error('[Mak LiquidGlass] PanelMenuManager error:', err);
        }

        try {
            if (Main.panel?.statusArea?.dateMenu) {
                this._calendarMenuManager = new UIManager(
                    path,
                    this._liquidSettings,
                    this._logger,
                    Main.panel.statusArea.dateMenu,
                    false,
                    'enable-menu-glass',
                    'menu',
                    'calendar',
                    true
                );
                this._calendarMenuManager.setup();
            }
        } catch (err) {
            console.error('[Mak LiquidGlass] Calendar UIManager error:', err);
        }

        try {
            this._quickSettingsManager = new QuickSettingsManager(path, this._liquidSettings, this._logger);
            this._quickSettingsManager.setup();
        } catch (err) {
            console.error('[Mak LiquidGlass] QuickSettingsManager error:', err);
        }

        try {
            this._notificationManager = new NotificationManager(path, this._liquidSettings, this._logger);
            this._notificationManager.setup();
        } catch (err) {
            console.error('[Mak LiquidGlass] NotificationManager error:', err);
        }

        try {
            this._osdManager = new OsdManager(path, this._liquidSettings, this._logger);
            this._osdManager.setup();
        } catch (err) {
            console.error('[Mak LiquidGlass] OsdManager error:', err);
        }

        // Dock detection & hook
        this._monitorsChangedId = Main.layoutManager.connect('monitors-changed', () => this._rescanDock());
        this._uiChildAddedId = Main.layoutManager.uiGroup.connect('child-added', (_group, child) => {
            const name = child.get_name();
            if (name === 'makDockContainer' || name === 'dashtodockDashContainer' || name === 'dashtodockContainer') {
                this._rescanDock();
            }
        });

        // Search immediately, and check with short retries in case dock is initializing
        this._findDocks();
        this._dashSearchId = GLib.timeout_add(GLib.PRIORITY_DEFAULT, 400, () => {
            this._findDocks();
            return GLib.SOURCE_REMOVE;
        });
        GLib.timeout_add(GLib.PRIORITY_DEFAULT, 1200, () => {
            this._findDocks();
            return GLib.SOURCE_REMOVE;
        });

        console.log('[Mak LiquidGlass] Master dynamic liquid glass engine enabled.');
    }

    _syncMakPreferences() {
        if (!this._liquidSettings || !this._makSettings) return;

        try {
            const getStr = (key, fallback) => {
                try {
                    if (this._makSettings?.settings_schema?.has_key(key)) {
                        const val = this._makSettings.get_string(key);
                        return val || fallback;
                    }
                } catch (e) {}
                return fallback;
            };

            const getDbl = (key, fallback) => {
                try {
                    if (this._makSettings?.settings_schema?.has_key(key)) {
                        return this._makSettings.get_double(key);
                    }
                } catch (e) {}
                return fallback;
            };

            const getInt = (key, fallback) => {
                try {
                    if (this._makSettings?.settings_schema?.has_key(key)) {
                        return this._makSettings.get_int(key);
                    }
                } catch (e) {}
                return fallback;
            };

            const getBool = (key, fallback) => {
                try {
                    if (this._makSettings?.settings_schema?.has_key(key)) {
                        return this._makSettings.get_boolean(key);
                    }
                } catch (e) {}
                return fallback;
            };

            const refr = getDbl('blur-refraction-strength', 0.42);
            const disp = getDbl('blur-chromatic-dispersion', 0.08);
            const globalOp = getDbl('global-opacity', 0.85);
            const cornerRad = getInt('corner-radius', 16);
            const dockRad = getInt('dock-radius', 24);
            const edgeBending = getDbl('dock-edge-bending', refr);
            const glassLevel = getDbl('dock-glass-level', 0.60);

            // Optics & Dock Refraction Bending
            const dockDisp = Math.max(2.0, edgeBending * 28.0);
            const dockMaxZ = Math.max(10.0, glassLevel * 120.0);
            const dockIor = 1.4 + glassLevel * 1.0;

            this._liquidSettings.set_double('glass-displacement-scale', dockDisp);
            this._liquidSettings.set_double('glass-chroma-strength', disp);
            this._liquidSettings.set_double('glass-max-z', dockMaxZ);
            this._liquidSettings.set_double('glass-ior', dockIor);
            this._liquidSettings.set_double('glass-corner-smoothing', 0.6);

            const gtkTheme = this._interfaceSettings ? this._interfaceSettings.get_string('gtk-theme') : '';
            const isGlassyTheme = gtkTheme.toLowerCase().includes('glassy') || gtkTheme.toLowerCase().includes('glass');

            // Windows: Enable liquid glass refraction only when a glassy theme is selected and blur-applications is true.
            const appBlur = getBool('blur-applications', true);
            const appBlurRad = getInt('app-blur-radius', 14);
            const appOpacity = getDbl('app-opacity', isGlassyTheme ? Math.max(0.70, Math.min(0.96, globalOp)) : 1.0);
            const appTintColor = getStr('app-tint-color', '#ffffff');
            const appTintStrength = getDbl('app-tint-strength', 0.05);
            const appCornerRad = cornerRad > 0 ? cornerRad : getInt('corner-radius', 16);

            this._liquidSettings.set_boolean('enable-application-glass', isGlassyTheme && appBlur);
            this._liquidSettings.set_boolean('application-glass-all-windows', isGlassyTheme && appBlur);
            this._liquidSettings.set_double('application-content-opacity', (isGlassyTheme && appBlur) ? appOpacity : 1.0);
            this._liquidSettings.set_double('application-corner-radius', appCornerRad > 0 ? appCornerRad : 16.0);
            this._liquidSettings.set_int('application-blur-radius', (isGlassyTheme && appBlur) ? Math.max(1, appBlurRad) : 0);
            this._liquidSettings.set_string('application-tint-color', appTintColor);
            this._liquidSettings.set_double('application-tint-strength', Math.max(0.0, Math.min(1.0, appTintStrength)));

            // Blacklist Chrome, Brave, VS Code, Electron to preserve solid web rendering & authentic traffic lights
            const targetBlacklist = [
                'google-chrome*',
                'chromium*',
                'brave*',
                'code*',
                'Code*',
                'electron*',
                'Plank',
                'com.desktop.ding',
                'Conky',
            ];
            this._liquidSettings.set_strv('application-window-blacklist', targetBlacklist);

            // Dock
            const dockBlur = getBool('dock-blur', true);
            const dockBlurRad = getInt('dock-blur-radius', Math.max(1, Math.round(glassLevel * 28.0)));
            const dockTintColor = getStr('dock-tint-color', '#ffffff');
            const dockTintStrength = getDbl('dock-tint-strength', Math.max(0.04, Math.min(0.20, glassLevel * 0.16)));
            const dockEffectiveRadius = dockRad > 0 ? dockRad : getInt('dock-corner-radius', 24);

            this._liquidSettings.set_boolean('enable-dock-glass', dockBlur);
            this._liquidSettings.set_double('dock-corner-radius', dockEffectiveRadius > 0 ? dockEffectiveRadius : 24.0);
            this._liquidSettings.set_int('dock-blur-radius', dockBlur ? Math.max(1, dockBlurRad) : 0);
            this._liquidSettings.set_string('dock-tint-color', dockTintColor);
            this._liquidSettings.set_double('dock-tint-strength', Math.max(0.0, Math.min(1.0, dockTintStrength)));

            // Top Bar
            const topbarBlur = this._makSettings.get_boolean('topbar-blur');
            const blurPanel = this._makSettings.get_boolean('blur-panel');
            const topbarOpaque = this._makSettings.get_boolean('topbar-opaque');
            const topbarPill = this._makSettings.get_boolean('topbar-pill-style');
            const topbarBlurRad = this._makSettings.get_int('topbar-blur-radius');
            const topbarTrans = this._makSettings.get_double('topbar-transparency');
            const blurBright = this._makSettings.get_double('blur-brightness');
            const topbarTintColor = getStr('topbar-tint-color', '#ffffff');
            const topbarTintStrength = getDbl('topbar-tint-strength', 0.08);

            if (!topbarBlur || !blurPanel || topbarOpaque) {
                this._liquidSettings.set_string('top-bar-style', 'off');
            } else {
                this._liquidSettings.set_string('top-bar-style', 'pill');
                this._liquidSettings.set_string('top-bar-tint-color', topbarTintColor);
                // Calculate tint strength from panel transparency or explicit setting:
                const calcTintStr = Math.max(0.02, Math.min(0.40, (1.0 - topbarTrans) * 0.22));
                const finalTopbarTint = topbarTintStrength > 0.08 ? topbarTintStrength : calcTintStr;
                this._liquidSettings.set_double('top-bar-tint-strength', finalTopbarTint);
                this._liquidSettings.set_int('top-bar-blur-radius', topbarBlurRad > 0 ? topbarBlurRad : 24);
                this._liquidSettings.set_double('top-bar-brightness', blurBright > 0 ? blurBright : 1.0);

                if (topbarPill) {
                    this._liquidSettings.set_double('top-bar-corner-radius', 14.0);
                    this._liquidSettings.set_int('top-bar-margin-top', 6);
                    this._liquidSettings.set_int('top-bar-margin-bottom', 0);
                    this._liquidSettings.set_int('top-bar-margin-left', 12);
                    this._liquidSettings.set_int('top-bar-margin-right', 12);
                } else {
                    this._liquidSettings.set_double('top-bar-corner-radius', 0.0);
                    this._liquidSettings.set_int('top-bar-margin-top', 0);
                    this._liquidSettings.set_int('top-bar-margin-bottom', 0);
                    this._liquidSettings.set_int('top-bar-margin-left', 0);
                    this._liquidSettings.set_int('top-bar-margin-right', 0);
                }
            }

            this._liquidSettings.set_int('top-bar-padding-top', 0);
            this._liquidSettings.set_int('top-bar-padding-bottom', 0);
            this._liquidSettings.set_int('top-bar-padding-left', 0);
            this._liquidSettings.set_int('top-bar-padding-right', 0);
            this._liquidSettings.set_boolean('top-bar-enable-adaptive-text-color', false);

            // Re-apply topbar module transparency styling
            try { this._extension?._topbar?._applyPanelTransparency?.(); } catch (e) {}

            // Menus (Kiwi menu, app menus, calendar)
            const menuBlur = getBool('menu-blur', true);
            const menuBlurRad = getInt('menu-blur-radius', 16);
            const menuGlassLevel = getDbl('menu-glass-level', 0.60);
            const menuTintColor = getStr('menu-tint-color', '#ffffff');
            const menuTintStrength = getDbl('menu-tint-strength', 0.08);
            const menuCornerRad = getInt('menu-corner-radius', 14);

            // Calendar & Date Menu
            this._liquidSettings.set_boolean('enable-menu-glass', menuBlur);
            this._liquidSettings.set_boolean('enable-menu-animation', false);
            this._liquidSettings.set_double('menu-corner-radius', menuCornerRad > 0 ? menuCornerRad : 14.0);
            this._liquidSettings.set_int('menu-glass-expand', 0);
            this._liquidSettings.set_int('menu-blur-radius', menuBlur ? Math.max(1, menuBlurRad) : 0);
            this._liquidSettings.set_string('menu-tint-color', menuTintColor);
            this._liquidSettings.set_double('menu-tint-strength', Math.max(0.0, Math.min(1.0, menuTintStrength)));
            this._liquidSettings.set_boolean('menu-enable-adaptive-text-color', false);

            // Extra Panel Menus (Kiwi Apple menu, system indicators)
            this._liquidSettings.set_boolean('enable-extra-menu-glass', menuBlur);
            this._liquidSettings.set_boolean('enable-panel-menu-animation', false);
            this._liquidSettings.set_double('panel-menu-corner-radius', menuCornerRad > 0 ? menuCornerRad : 14.0);
            this._liquidSettings.set_int('panel-menu-glass-expand', 0);
            this._liquidSettings.set_int('panel-menu-blur-radius', menuBlur ? Math.max(1, menuBlurRad) : 0);
            this._liquidSettings.set_string('panel-menu-tint-color', menuTintColor);
            this._liquidSettings.set_double('panel-menu-tint-strength', Math.max(0.0, Math.min(1.0, menuTintStrength)));
            this._liquidSettings.set_boolean('panel-menu-enable-adaptive-text-color', false);

            // Desktop Context Menus
            const desktopMenuBlur = getBool('desktop-menu-blur', true);
            const desktopMenuBlurRad = getInt('desktop-menu-blur-radius', 16);
            const desktopMenuTintColor = getStr('desktop-menu-tint-color', '#ffffff');
            const desktopMenuTintStrength = getDbl('desktop-menu-tint-strength', 0.08);

            this._liquidSettings.set_boolean('enable-desktop-menu-glass', desktopMenuBlur);
            this._liquidSettings.set_double('desktop-menu-corner-radius', menuCornerRad > 0 ? menuCornerRad : 14.0);
            this._liquidSettings.set_int('desktop-menu-blur-radius', desktopMenuBlur ? Math.max(1, desktopMenuBlurRad) : 0);
            this._liquidSettings.set_string('desktop-menu-tint-color', desktopMenuTintColor);
            this._liquidSettings.set_double('desktop-menu-tint-strength', Math.max(0.0, Math.min(1.0, desktopMenuTintStrength)));
            this._liquidSettings.set_double('desktop-menu-content-opacity', 0.88);

            // Quick Settings: Unified background card mode (0), native toggle styling
            const ccBlur = getBool('control-center-blur', true);
            const ccBlurRad = getInt('control-center-blur-radius', 18);
            const ccGlassLevel = getDbl('control-center-glass-level', 0.60);
            const ccTintColor = getStr('control-center-tint-color', '#ffffff');
            const ccTintStrength = getDbl('control-center-tint-strength', 0.08);
            const ccCornerRad = getInt('quick-settings-radius', 20);

            this._liquidSettings.set_boolean('enable-quick-settings-glass', ccBlur);
            this._liquidSettings.set_boolean('enable-quick-settings-animation', false);
            this._liquidSettings.set_int('quick-settings-apply-to', 0);
            this._liquidSettings.set_double('quick-settings-corner-radius', ccCornerRad > 0 ? ccCornerRad : 20.0);
            this._liquidSettings.set_int('quick-settings-blur-radius', ccBlur ? Math.max(1, ccBlurRad) : 0);
            this._liquidSettings.set_string('quick-settings-tint-color', ccTintColor);
            this._liquidSettings.set_double('quick-settings-tint-strength', Math.max(0.0, Math.min(1.0, ccTintStrength)));
            this._liquidSettings.set_double('quick-settings-toggle-tint-strength', Math.max(0.0, Math.min(1.0, ccTintStrength)));
            this._liquidSettings.set_boolean('quick-settings-enable-adaptive-text-color', false);

            // Notifications
            this._liquidSettings.set_boolean('enable-notification-glass', true);
            this._liquidSettings.set_int('notification-glass-expand', 0);
            this._liquidSettings.set_double('notification-corner-radius', 16.0);
            this._liquidSettings.set_int('notification-blur-radius', 16);
            this._liquidSettings.set_string('notification-tint-color', '#ffffff');
            this._liquidSettings.set_double('notification-tint-strength', 0.08);
            this._liquidSettings.set_boolean('notification-enable-adaptive-text-color', false);

            // OSDs
            this._liquidSettings.set_boolean('enable-osd-glass', true);
            this._liquidSettings.set_double('osd-corner-radius', 16.0);
            this._liquidSettings.set_int('osd-blur-radius', 16);
            this._liquidSettings.set_string('osd-tint-color', '#ffffff');
            this._liquidSettings.set_double('osd-tint-strength', 0.08);
        } catch (e) {
            console.warn('[Mak LiquidGlass] Error syncing preferences:', e.message);
        }
    }

    _bindMakSettings() {
        const sync = () => this._syncMakPreferences();
        for (const key of [
            'blur-refraction-strength',
            'blur-chromatic-dispersion',
            'dock-edge-bending',
            'dock-glass-level',
            'dock-blur',
            'dock-blur-radius',
            'dock-corner-radius',
            'dock-tint-color',
            'dock-tint-strength',
            'global-opacity',
            'corner-radius',
            'dock-radius',
            'topbar-blur',
            'topbar-blur-radius',
            'topbar-transparency',
            'topbar-opaque',
            'topbar-pill-style',
            'topbar-tint-color',
            'topbar-tint-strength',
            'blur-panel',
            'blur-brightness',
            'blur-sigma',
            'control-center-blur',
            'control-center-blur-radius',
            'control-center-glass-level',
            'control-center-tint-color',
            'control-center-tint-strength',
            'quick-settings-radius',
            'menu-blur',
            'menu-blur-radius',
            'menu-glass-level',
            'menu-tint-color',
            'menu-tint-strength',
            'menu-corner-radius',
            'desktop-menu-blur',
            'desktop-menu-blur-radius',
            'desktop-menu-glass-level',
            'desktop-menu-tint-color',
            'desktop-menu-tint-strength',
            'blur-applications',
            'app-blur-radius',
            'app-opacity',
            'app-tint-color',
            'app-tint-strength',
            'app-glass-level'
        ]) {
            const id = this._makSettings.connect(`changed::${key}`, sync);
            this._makSettingsIds.push(id);
        }

        for (const key of [
            'dock-position',
            'dock-alignment',
            'dock-size',
            'dock-enabled',
            'dock-autohide',
        ]) {
            const id = this._makSettings.connect(`changed::${key}`, () => {
                this._rescanDock();
            });
            this._makSettingsIds.push(id);
        }
    }

    _collectDockContainers() {
        const found = [];
        // 1. Direct reference from Mak Dock module if available
        try {
            const docks = this._extension?._dock?._manager?._docks;
            if (Array.isArray(docks)) {
                for (const d of docks) {
                    const c = d?._chrome?.container;
                    if (c && !found.includes(c) && (!c.get_stage || c.get_stage())) {
                        found.push(c);
                    }
                }
            }
        } catch (e) {}

        // 2. Traversal of uiGroup & chrome
        const walk = actor => {
            if (!actor || actor === global.window_group) return;
            const name = actor.get_name();
            if (name === 'makDockContainer' || name === 'dashtodockDashContainer' || name === 'dashtodockContainer') {
                if (!found.includes(actor)) found.push(actor);
                return;
            }
            for (const child of actor.get_children()) {
                walk(child);
            }
        };
        walk(Main.layoutManager.uiGroup);
        return found;
    }

    _findDocks() {
        if (!this._enabled || !this._liquidSettings) return;

        // Clean up any stale or unmounted dock containers
        for (const entry of [...this._dashDocks]) {
            if (!entry.container || !entry.container.get_stage?.()) {
                this._releaseDock(entry);
            }
        }

        const path = this._extension.path + '/modules/blur/liquid';
        for (const container of this._collectDockContainers()) {
            if (this._dashDocks.some(entry => entry.container === container)) continue;

            try {
                const manager = new DashManager(path, container, this._liquidSettings, this._logger);
                manager.setup();
                const entry = { container, manager, destroyId: 0 };
                entry.destroyId = container.connect('destroy', () => {
                    entry.destroyId = 0;
                    this._releaseDock(entry);
                });
                this._dashDocks.push(entry);
            } catch (err) {
                console.warn('[Mak LiquidGlass] Could not attach to dock container:', err);
            }
        }
    }

    _rescanDock() {
        if (!this._enabled) return;
        if (this._dashSearchId) {
            GLib.Source.remove(this._dashSearchId);
            this._dashSearchId = 0;
        }
        this._dashSearchId = GLib.timeout_add(GLib.PRIORITY_DEFAULT, 150, () => {
            this._dashSearchId = 0;
            this._findDocks();
            return GLib.SOURCE_REMOVE;
        });

        // Fallback scan to guarantee latching onto newly created docks after transition settles
        GLib.timeout_add(GLib.PRIORITY_DEFAULT, 500, () => {
            if (this._enabled) this._findDocks();
            return GLib.SOURCE_REMOVE;
        });
    }

    _releaseDock(entry) {
        if (entry.destroyId) {
            entry.container.disconnect(entry.destroyId);
            entry.destroyId = 0;
        }
        try {
            entry.manager?.cleanup();
        } catch (e) {}
        const idx = this._dashDocks.indexOf(entry);
        if (idx >= 0) this._dashDocks.splice(idx, 1);
        if (this._enabled) {
            this._rescanDock();
        }
    }

    disable() {
        if (!this._enabled) return;
        this._enabled = false;

        for (const id of this._makSettingsIds) {
            try { this._makSettings.disconnect(id); } catch (e) {}
        }
        this._makSettingsIds = [];

        if (this._ifaceChangedId && this._interfaceSettings) {
            try { this._interfaceSettings.disconnect(this._ifaceChangedId); } catch (e) {}
            this._ifaceChangedId = 0;
        }
        this._interfaceSettings = null;

        if (this._dashSearchId) {
            GLib.Source.remove(this._dashSearchId);
            this._dashSearchId = 0;
        }

        if (this._monitorsChangedId) {
            Main.layoutManager.disconnect(this._monitorsChangedId);
            this._monitorsChangedId = 0;
        }

        if (this._uiChildAddedId) {
            Main.layoutManager.uiGroup.disconnect(this._uiChildAddedId);
            this._uiChildAddedId = 0;
        }

        for (const entry of [...this._dashDocks]) {
            this._releaseDock(entry);
        }
        this._dashDocks = [];

        try { this._applicationManager?.cleanup(); } catch (e) {}
        this._applicationManager = null;

        try { this._topBarManager?.cleanup(); } catch (e) {}
        this._topBarManager = null;

        try { this._panelMenuManager?.cleanup(); } catch (e) {}
        this._panelMenuManager = null;

        try { this._calendarMenuManager?.cleanup(); } catch (e) {}
        this._calendarMenuManager = null;

        try { this._quickSettingsManager?.cleanup(); } catch (e) {}
        this._quickSettingsManager = null;

        try { this._notificationManager?.cleanup(); } catch (e) {}
        this._notificationManager = null;

        try { this._osdManager?.cleanup(); } catch (e) {}
        this._osdManager = null;

        removeGlassDiagnostics();
        setUtilsLogger(null);
        if (this._logger) {
            try { this._logger.cleanup(); } catch (e) {}
            this._logger = null;
        }
        this._liquidSettings = null;

        console.log('[Mak LiquidGlass] Master dynamic liquid glass engine disabled.');
    }
}
