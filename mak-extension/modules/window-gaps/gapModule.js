// SPDX-License-Identifier: GPL-3.0-or-later
// Mak Window Gaps Module: Outer margins around windows, even in maximized view

import Clutter from 'gi://Clutter';
import GLib from 'gi://GLib';
import Meta from 'gi://Meta';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';

export class GapManager {
    constructor(settings) {
        this._settings = settings;
        this._actors = [];
    }

    rebuild() {
        this._destroyActors();

        if (!this._settings.get_boolean('gaps-enabled'))
            return;

        const margins = this._getMargins();

        for (const monitor of Main.layoutManager.monitors) {
            if (margins.top > 0)
                this._addEdge(monitor.x, monitor.y, monitor.width, margins.top);

            if (margins.bottom > 0) {
                this._addEdge(
                    monitor.x,
                    monitor.y + monitor.height - margins.bottom,
                    monitor.width,
                    margins.bottom
                );
            }

            if (margins.left > 0)
                this._addEdge(monitor.x, monitor.y, margins.left, monitor.height);

            if (margins.right > 0) {
                this._addEdge(
                    monitor.x + monitor.width - margins.right,
                    monitor.y,
                    margins.right,
                    monitor.height
                );
            }
        }

        // Notify Mutter layout manager of strut updates and refresh running maximized windows
        try {
            Main.layoutManager._queueUpdateRegions();
            GLib.idle_add(GLib.PRIORITY_DEFAULT_IDLE, () => {
                try {
                    for (const actor of global.get_window_actors()) {
                        const win = actor.metaWindow;
                        if (win && (win.maximized_horizontally || win.maximized_vertically)) {
                            win.unmaximize(Meta.MaximizeFlags.BOTH);
                            win.maximize(Meta.MaximizeFlags.BOTH);
                        }
                    }
                } catch (e) {}
                return GLib.SOURCE_REMOVE;
            });
        } catch (e) {}
    }

    destroy() {
        this._destroyActors();
        this._settings = null;
    }

    _getMargins() {
        if (!this._settings.get_boolean('gaps-enabled')) {
            return { top: 0, bottom: 0, left: 0, right: 0 };
        }

        if (this._settings.get_boolean('gap-uniform')) {
            const size = this._settings.get_int('gap-size');
            return { top: size, bottom: size, left: size, right: size };
        }

        return {
            top: this._settings.get_int('gap-top'),
            bottom: this._settings.get_int('gap-bottom'),
            left: this._settings.get_int('gap-left'),
            right: this._settings.get_int('gap-right'),
        };
    }

    _addEdge(x, y, width, height) {
        const actor = new Clutter.Actor({
            reactive: false,
            width,
            height,
            x,
            y,
            opacity: 0,
        });

        Main.layoutManager.addChrome(actor, {
            affectsStruts: true,
        });

        this._actors.push(actor);
    }

    _destroyActors() {
        for (const actor of this._actors) {
            Main.layoutManager.removeChrome(actor);
            actor.destroy();
        }
        this._actors = [];
        try {
            Main.layoutManager._queueUpdateRegions();
        } catch (e) {}
    }
}

export class WindowGapModule {
    constructor(extension) {
        this._extension = extension;
        this._settings = extension.getSettings();
        this._gapManager = null;
        this._monitorsId = 0;
        this._settingsId = 0;
    }

    enable() {
        this._gapManager = new GapManager(this._settings);

        this._settingsId = this._settings.connect('changed', (s, key) => {
            if (key.startsWith('gap') || key === 'gaps-enabled' || key === 'gaps-maximized')
                this._gapManager.rebuild();
        });

        this._monitorsId = Main.layoutManager.connect('monitors-changed', () => {
            this._gapManager.rebuild();
        });

        this._gapManager.rebuild();
    }

    rebuild() {
        this._gapManager?.rebuild();
    }

    disable() {
        if (this._settingsId) {
            this._settings.disconnect(this._settingsId);
            this._settingsId = 0;
        }

        if (this._monitorsId) {
            Main.layoutManager.disconnect(this._monitorsId);
            this._monitorsId = 0;
        }

        if (this._gapManager) {
            this._gapManager.destroy();
            this._gapManager = null;
        }
    }
}
