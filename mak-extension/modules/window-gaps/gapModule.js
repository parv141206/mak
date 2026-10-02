// SPDX-License-Identifier: GPL-3.0-or-later
// Mak Window Gaps Module: Outer margins around windows, even in maximized view

import Clutter from 'gi://Clutter';
import GLib from 'gi://GLib';
import Meta from 'gi://Meta';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';

export class GapManager {
    constructor(settings, extension = null) {
        this._settings = settings;
        this._extension = extension;
        this._actors = [];
    }

    rebuild() {
        this._destroyActors();

        if (!this._settings || !this._settings.get_boolean('gaps-enabled'))
            return;

        if (!this._settings.get_boolean('gaps-maximized'))
            return;

        const margins = this._getMargins();

        for (const monitor of Main.layoutManager.monitors) {
            // Panel offset: panel is on primary monitor at the top
            const panelHeight = (monitor === Main.layoutManager.primaryMonitor && Main.panel && Main.panel.visible)
                ? Main.panel.height
                : 0;

            // Dock offsets per side if present on this monitor
            let dockReserve = { top: 0, bottom: 0, left: 0, right: 0 };
            if (this._extension?._dock?._manager?._docks) {
                for (const dock of this._extension._dock._manager._docks) {
                    if (dock.monitorIndex === monitor.index || dock._monitor === monitor) {
                        const strut = dock._geom?.strut;
                        const side = dock._geom?.side;
                        if (strut && side) {
                            if (side === 'bottom') dockReserve.bottom = strut.h;
                            else if (side === 'top') dockReserve.top = strut.h;
                            else if (side === 'left') dockReserve.left = strut.w;
                            else if (side === 'right') dockReserve.right = strut.w;
                        }
                    }
                }
            }

            if (margins.top > 0) {
                const totalTop = panelHeight + dockReserve.top + margins.top;
                this._addEdge(monitor.x, monitor.y, monitor.width, totalTop);
            }

            if (margins.bottom > 0) {
                const totalBottom = dockReserve.bottom + margins.bottom;
                this._addEdge(
                    monitor.x,
                    monitor.y + monitor.height - totalBottom,
                    monitor.width,
                    totalBottom
                );
            }

            if (margins.left > 0) {
                const totalLeft = dockReserve.left + margins.left;
                this._addEdge(monitor.x, monitor.y, totalLeft, monitor.height);
            }

            if (margins.right > 0) {
                const totalRight = dockReserve.right + margins.right;
                this._addEdge(
                    monitor.x + monitor.width - totalRight,
                    monitor.y,
                    totalRight,
                    monitor.height
                );
            }
        }

        // Notify Mutter layout manager of strut updates and refresh running maximized windows
        try {
            Main.layoutManager._queueUpdateRegions();
            GLib.timeout_add(GLib.PRIORITY_DEFAULT, 50, () => {
                try {
                    for (const actor of global.get_window_actors()) {
                        const win = actor.metaWindow;
                        if (win && (win.maximized_horizontally || win.maximized_vertically)) {
                            win.unmaximize();
                            win.maximize();
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
        this._extension = null;
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
        this._gapManager = new GapManager(this._settings, this._extension);

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

