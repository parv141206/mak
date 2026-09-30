// SPDX-License-Identifier: GPL-3.0-or-later
// Mak Unified Shell Blur Module
// Applies authentic macOS frosted glass blur across Top Bar, Overview, Popups/Quick Settings, Folders, and Lock Screen.

import Gio from 'gi://Gio';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import BlurMyShell from './bms/extension.js';
import { NativeDynamicBlurEffect } from './bms/effects/native_dynamic_gaussian_blur.js';

export class BlurModule {
    constructor(extension) {
        this._extension = extension;
        this._makSettings = extension.getSettings('org.gnome.shell.extensions.mak');
        this._bms = null;
        this._settingsChangedId = 0;
    }

    enable() {
        this._initBmsSettings();

        try {
            this._bms = new BlurMyShell(this._extension);
            this._bms.enable();
            console.log('[Mak Blur] BMS Liquid Glass blur engine enabled.');
        } catch (err) {
            console.error('[Mak Blur] Failed to enable BMS engine:', err);
        }

        this._settingsChangedId = this._makSettings.connect('changed', (s, key) => {
            if (key.startsWith('blur-') || key.startsWith('topbar-blur')) {
                this._syncSettings();
            }
        });

        this._syncSettings();
        console.log('[Mak Blur] Shell-wide blur & glassmorphism enabled.');
    }

    _initBmsSettings() {
        try {
            const panelSettings = new Gio.Settings({ schema_id: 'org.gnome.shell.extensions.blur-my-shell.panel' });
            const popupSettings = new Gio.Settings({ schema_id: 'org.gnome.shell.extensions.blur-my-shell.popup' });
            const overviewSettings = new Gio.Settings({ schema_id: 'org.gnome.shell.extensions.blur-my-shell.overview' });
            const appfolderSettings = new Gio.Settings({ schema_id: 'org.gnome.shell.extensions.blur-my-shell.appfolder' });
            const lockscreenSettings = new Gio.Settings({ schema_id: 'org.gnome.shell.extensions.blur-my-shell.lockscreen' });

            const hasDynamicCornerSupport = Boolean(NativeDynamicBlurEffect.supports_corner_radius);
            console.log('[Mak Blur] Dynamic corner blur support:', hasDynamicCornerSupport);

            // Liquid glass blur across panel, popups, overview, app folders, and lockscreen
            panelSettings.set_boolean('blur', true);
            // Panel is full-screen rectangular bar; dynamic stage blur works with ZERO corner artifacts!
            panelSettings.set_boolean('static-blur', false);
            panelSettings.set_boolean('override-background', true);
            panelSettings.set_int('style-panel', 0); // Transparent panel so blurred windows shine through
            panelSettings.set_boolean('unblur-in-overview', false);

            popupSettings.set_boolean('blur', true); // Enables blur on Quick Settings / Control Center, Menus, Dialogs
            // If gnome-rounded-blur is installed, use true dynamic blur with corner-radius; otherwise use zero-korner static actor
            popupSettings.set_boolean('static-blur', !hasDynamicCornerSupport);
            popupSettings.set_int('style-popup', 3);
            popupSettings.set_int('quick-settings-corner-radius', 28);
            popupSettings.set_int('menu-corner-radius', 18);
            popupSettings.set_int('notification-corner-radius', 18);
            popupSettings.set_int('dialog-corner-radius', 18);

            overviewSettings.set_boolean('blur', true);
            appfolderSettings.set_boolean('blur', true);
            lockscreenSettings.set_boolean('blur', true);
        } catch (err) {
            console.warn('[Mak Blur] Could not initialize BMS settings:', err);
        }
    }

    _syncSettings() {
        const enabled = this._makSettings.get_boolean('blur-enabled');
        if (!enabled) {
            if (this._bms) {
                try { this._bms.disable(); } catch (e) {}
                this._bms = null;
            }
            return;
        }

        if (!this._bms) {
            try {
                this._bms = new BlurMyShell(this._extension);
                this._bms.enable();
            } catch (e) {}
        }

        try {
            const panelSettings = new Gio.Settings({ schema_id: 'org.gnome.shell.extensions.blur-my-shell.panel' });
            const topbarBlur = this._makSettings.get_boolean('topbar-blur') || this._makSettings.get_boolean('blur-panel');
            panelSettings.set_boolean('blur', topbarBlur);

            const overviewSettings = new Gio.Settings({ schema_id: 'org.gnome.shell.extensions.blur-my-shell.overview' });
            overviewSettings.set_boolean('blur', this._makSettings.get_boolean('blur-overview'));

            const appfolderSettings = new Gio.Settings({ schema_id: 'org.gnome.shell.extensions.blur-my-shell.appfolder' });
            appfolderSettings.set_boolean('blur', this._makSettings.get_boolean('blur-appfolder'));
        } catch (err) {
            console.warn('[Mak Blur] Error syncing settings to BMS:', err);
        }
    }

    disable() {
        if (this._settingsChangedId) {
            try { this._makSettings.disconnect(this._settingsChangedId); } catch (e) {}
            this._settingsChangedId = 0;
        }

        if (this._bms) {
            try {
                this._bms.disable();
            } catch (err) {
                console.warn('[Mak Blur] Error disabling BMS:', err);
            }
            this._bms = null;
        }

        console.log('[Mak Blur] Shell-wide blur disabled.');
    }
}
