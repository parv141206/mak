// SPDX-License-Identifier: GPL-3.0-or-later
// Mak Window Corners Module Adapter: Real-Time Dynamic Sync with Mak Suite

import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import RoundedCornersExtension from './extension.js';
import { onSettingsChanged } from './manager/event_handlers.js';

export class WindowCornersModule {
    constructor(extension) {
        this._extension = extension;
        this._runner = null;
        this._settings = null;
        this._settingsChangedId = 0;
    }

    enable() {
        if (this._runner) return;
        try {
            this._settings = this._extension.getSettings('org.gnome.shell.extensions.mak');

            const dir = this._extension.dir ?? Gio.File.new_for_path(this._extension.path);
            this._runner = new RoundedCornersExtension({
                uuid: 'rounded-window-corners@local',
                path: this._extension.path,
                dir: dir,
                'settings-schema': 'org.gnome.shell.extensions.rounded-window-corners-reborn',
            });
            this._runner.getSettings = (schema) => {
                try {
                    return this._extension.getSettings(schema || 'org.gnome.shell.extensions.rounded-window-corners-reborn');
                } catch (e) {
                    return this._extension.getSettings();
                }
            };

            // Enable runner
            this._runner.enable();

            // Initial sync of settings from Mak Control Center
            this._syncSettings();

            // Connect to real-time changes in Mak settings
            this._settingsChangedId = this._settings.connect('changed', (settings, key) => {
                if (key.startsWith('corner-') ||
                    key === 'unround-maximized' ||
                    key === 'skip-libadwaita-app' ||
                    key === 'skip-libhandy-app' ||
                    key.startsWith('focused-shadow') ||
                    key.startsWith('unfocused-shadow') ||
                    key === 'shadow-enabled' ||
                    key === 'border-color') {
                    this._syncSettings();
                }
            });

            console.log('[Mak WindowCorners] Rounded window corners & borders enabled with live settings sync.');
        } catch (err) {
            console.warn('[Mak WindowCorners] Failed to enable rounded window corners:', err);
        }
    }

    sync() {
        this._syncSettings();
    }

    _syncSettings() {
        if (!this._runner || !this._settings) return;
        try {
            const s = this._runner.getSettings();
            if (!s) return;

            const radius = this._settings.get_int('corner-radius') || 16;
            const smoothing = this._settings.get_double('corner-smoothing') ?? 0.8;
            const borderWidth = this._settings.get_int('corner-border-width') ?? 1;
            const unroundMaximized = this._settings.get_boolean('unround-maximized');
            const skipLibadwaita = this._settings.get_boolean('skip-libadwaita-app');
            const skipLibhandy = this._settings.get_boolean('skip-libhandy-app');

            const shadowEnabled = this._settings.get_boolean('shadow-enabled');
            const fVOffset = this._settings.get_int('focused-shadow-v-offset') || 4;
            const fBlur = this._settings.get_int('focused-shadow-blur') || 28;
            const fOpacity = this._settings.get_int('focused-shadow-opacity') || 60;
            const uVOffset = this._settings.get_int('unfocused-shadow-v-offset') || 2;
            const uBlur = this._settings.get_int('unfocused-shadow-blur') || 12;
            const uOpacity = this._settings.get_int('unfocused-shadow-opacity') || 50;

            s.set_boolean('skip-libadwaita-app', skipLibadwaita);
            s.set_boolean('skip-libhandy-app', skipLibhandy);
            s.set_int('border-width', borderWidth);

            const currentVal = s.get_value('global-rounded-corner-settings');
            const curDict = currentVal ? currentVal.recursiveUnpack() : {};
            const variantDict = {
                padding: new GLib.Variant('a{su}', curDict.padding || { left: 0, right: 0, top: 0, bottom: 0 }),
                keepRoundedCorners: new GLib.Variant('a{sb}', { maximized: !unroundMaximized, fullscreen: false }),
                borderRadius: GLib.Variant.new_uint32(radius),
                smoothing: GLib.Variant.new_double(smoothing),
                borderColor: new GLib.Variant('(dddd)', curDict.borderColor || [1.0, 1.0, 1.0, 0.18]),
                enabled: GLib.Variant.new_boolean(true),
            };
            s.set_value('global-rounded-corner-settings', new GLib.Variant('a{sv}', variantDict));

            // Sync shadows
            s.set_value('focused-shadow', new GLib.Variant('a{si}', {
                verticalOffset: fVOffset,
                horizontalOffset: 0,
                blurOffset: fBlur,
                spreadRadius: 4,
                opacity: shadowEnabled ? fOpacity : 0,
            }));

            s.set_value('unfocused-shadow', new GLib.Variant('a{si}', {
                verticalOffset: uVOffset,
                horizontalOffset: 0,
                blurOffset: uBlur,
                spreadRadius: 2,
                opacity: shadowEnabled ? uOpacity : 0,
            }));

            // Force all windows on screen to re-read settings and redraw immediately
            onSettingsChanged();
        } catch (e) {
            console.warn('[Mak WindowCorners] Error syncing corner settings:', e);
        }
    }

    disable() {
        if (this._settingsChangedId) {
            this._settings?.disconnect(this._settingsChangedId);
            this._settingsChangedId = 0;
        }
        if (this._runner) {
            try {
                this._runner.disable();
            } catch (err) {
                console.warn('[Mak WindowCorners] Failed to disable rounded window corners:', err);
            }
            this._runner = null;
        }
        this._settings = null;
    }
}
