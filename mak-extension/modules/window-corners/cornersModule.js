// SPDX-License-Identifier: GPL-3.0-or-later
// Mak Window Corners Module Adapter

import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import RoundedCornersExtension from './extension.js';

export class WindowCornersModule {
    constructor(extension) {
        this._extension = extension;
        this._runner = null;
    }

    enable() {
        if (this._runner) return;
        try {
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

            // Ensure essential defaults: do not skip libadwaita apps, ensure border width >= 1
            try {
                const s = this._runner.getSettings();
                if (s.get_boolean('skip-libadwaita-app')) {
                    s.set_boolean('skip-libadwaita-app', false);
                }
                if (s.get_int('border-width') === 0) {
                    s.set_int('border-width', 1);
                }
            } catch (e) {}

            this._runner.enable();
            console.log('[Mak WindowCorners] Rounded window corners & borders enabled successfully.');
        } catch (err) {
            console.warn('[Mak WindowCorners] Failed to enable rounded window corners:', err);
        }
    }

    disable() {
        if (!this._runner) return;
        try {
            this._runner.disable();
        } catch (err) {
            console.warn('[Mak WindowCorners] Failed to disable rounded window corners:', err);
        }
        this._runner = null;
    }
}
