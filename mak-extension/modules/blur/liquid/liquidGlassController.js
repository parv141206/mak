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
        this._quickSettingsManager = null;
        this._notificationManager = null;
        this._osdManager = null;
        this._dashDocks = [];
        this._dashSearchId = 0;
        this._uiChildAddedId = 0;
        this._monitorsChangedId = 0;
        this._makSettingsIds = [];
        this._enabled = false;
    }

    enable() {
        if (this._enabled) return;
        this._enabled = true;

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
            const refr = this._makSettings.get_double('blur-refraction-strength');
            const disp = this._makSettings.get_double('blur-chromatic-dispersion');
            const globalOp = this._makSettings.get_double('global-opacity');
            const cornerRad = this._makSettings.get_int('corner-radius');
            const dockRad = this._makSettings.get_int('dock-radius');

            // Optics
            this._liquidSettings.set_double('glass-displacement-scale', Math.max(3.0, refr * 25.0));
            this._liquidSettings.set_double('glass-chroma-strength', disp);
            this._liquidSettings.set_double('glass-max-z', 88.0);
            this._liquidSettings.set_double('glass-ior', 2.40);
            this._liquidSettings.set_double('glass-corner-smoothing', 0.6);

            // Windows
            this._liquidSettings.set_boolean('enable-application-glass', true);
            this._liquidSettings.set_boolean('application-glass-all-windows', true);
            this._liquidSettings.set_double('application-content-opacity', Math.max(0.65, Math.min(0.98, globalOp)));
            this._liquidSettings.set_double('application-corner-radius', cornerRad > 0 ? cornerRad : 16.0);
            this._liquidSettings.set_int('application-blur-radius', 12);
            this._liquidSettings.set_double('application-tint-strength', 0.12);

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
            this._liquidSettings.set_boolean('enable-dock-glass', true);
            this._liquidSettings.set_double('dock-corner-radius', dockRad > 0 ? dockRad : 27.0);
            this._liquidSettings.set_int('dock-blur-radius', 16);
            this._liquidSettings.set_double('dock-tint-strength', 0.14);

            // Top Bar & Menus
            this._liquidSettings.set_string('top-bar-style', 'pill');
            this._liquidSettings.set_double('top-bar-corner-radius', 0.0);
            this._liquidSettings.set_int('top-bar-blur-radius', 18);
            this._liquidSettings.set_double('top-bar-tint-strength', 0.14);

            this._liquidSettings.set_boolean('enable-menu-glass', true);
            this._liquidSettings.set_boolean('enable-extra-menu-glass', true);
            this._liquidSettings.set_boolean('enable-quick-settings-glass', true);
            this._liquidSettings.set_boolean('enable-notification-glass', true);
            this._liquidSettings.set_boolean('enable-osd-glass', true);
        } catch (e) {
            console.warn('[Mak LiquidGlass] Error syncing preferences:', e.message);
        }
    }

    _bindMakSettings() {
        const sync = () => this._syncMakPreferences();
        for (const key of [
            'blur-refraction-strength',
            'blur-chromatic-dispersion',
            'global-opacity',
            'corner-radius',
            'dock-radius'
        ]) {
            const id = this._makSettings.connect(`changed::${key}`, sync);
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
                    if (c && !found.includes(c)) found.push(c);
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
        if (this._dashSearchId) return;
        this._dashSearchId = GLib.timeout_add(GLib.PRIORITY_DEFAULT, 250, () => {
            this._dashSearchId = 0;
            this._findDocks();
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
    }

    disable() {
        if (!this._enabled) return;
        this._enabled = false;

        for (const id of this._makSettingsIds) {
            try { this._makSettings.disconnect(id); } catch (e) {}
        }
        this._makSettingsIds = [];

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
