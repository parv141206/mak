// SPDX-License-Identifier: GPL-3.0-or-later
// Mak Zen Module: Distraction-free full-screen experience
// Toggled via <Control><Shift><Alt>F11
// Hides top bar & dock, maximizes windows to literal full screen (0 struts)
// Automatically reveals top bar on touching top monitor edge, and dock on touching dock edge.

import Clutter from 'gi://Clutter';
import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import Meta from 'gi://Meta';
import Shell from 'gi://Shell';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';

export class ZenModule {
    constructor(extension) {
        this._extension = extension;
        this._settings = extension.getSettings('org.gnome.shell.extensions.mak');
        this._active = false;
        this._topbarRevealed = false;
        this._origPanelAffectsStruts = null;
        this._savedWindow = null;
        this._wasMaximized = false;
        this._stageEventId = 0;
        this._overviewShowingId = 0;
        this._overviewHiddenId = 0;
        this._hideTopBarTimeoutId = 0;
        this._keybindingAdded = false;
        this._transitioning = false;
        this._settingChangedId = 0;
    }

    enable() {
        this._registerKeybinding();

        // Listen for setting changes if toggled from Mak App GUI or CLI
        this._settingChangedId = this._settings.connect('changed::zen-mode-enabled', () => {
            const enabled = this._settings.get_boolean('zen-mode-enabled');
            if (enabled !== this._active) {
                if (enabled) this.activate();
                else this.deactivate();
            }
        });

        // If enabled in persistent settings on startup
        if (this._settings.get_boolean('zen-mode-enabled')) {
            GLib.idle_add(GLib.PRIORITY_DEFAULT_IDLE, () => {
                if (!this._active) this.activate();
                return GLib.SOURCE_REMOVE;
            });
        }
    }

    disable() {
        this._unregisterKeybinding();

        if (this._settingChangedId) {
            this._settings.disconnect(this._settingChangedId);
            this._settingChangedId = 0;
        }

        if (this._active) {
            this.deactivate(false);
        }
    }

    _registerKeybinding() {
        if (this._keybindingAdded) return;
        try {
            Main.wm.addKeybinding(
                'zen-mode-toggle',
                this._settings,
                Meta.KeyBindingFlags.IGNORE_AUTOREPEAT,
                Shell.ActionMode.NORMAL | Shell.ActionMode.OVERVIEW,
                () => this.toggle()
            );
            this._keybindingAdded = true;
        } catch (e) {
            console.warn('[Mak Zen] Could not register keybinding:', e);
        }
    }

    _unregisterKeybinding() {
        if (this._keybindingAdded) {
            try {
                Main.wm.removeKeybinding('zen-mode-toggle');
            } catch (e) {}
            this._keybindingAdded = false;
        }
    }

    toggle() {
        if (this._active) {
            this.deactivate();
        } else {
            this.activate();
        }
    }

    activate() {
        if (this._active || this._transitioning) return;
        this._transitioning = true;
        this._active = true;

        if (!this._settings.get_boolean('zen-mode-enabled')) {
            this._settings.set_boolean('zen-mode-enabled', true);
        }

        // Display sleek On-Screen HUD feedback
        try {
            Main.osdWindowManager?.show(
                -1,
                Gio.Icon.new_for_string('view-fullscreen-symbolic'),
                'Zen Mode Enabled'
            );
        } catch (e) {}

        // Capture current focused window state
        const focusWin = global.display.focus_window;
        if (focusWin && focusWin.window_type === Meta.WindowType.NORMAL) {
            this._savedWindow = focusWin;
            this._wasMaximized = (focusWin.maximized_horizontally && focusWin.maximized_vertically);
        } else {
            this._savedWindow = null;
            this._wasMaximized = false;
        }

        // 1. Remove panel strut from GNOME Shell LayoutManager
        try {
            const panelBox = Main.layoutManager.panelBox;
            const pIdx = Main.layoutManager._findActor(panelBox);
            if (pIdx !== -1) {
                this._origPanelAffectsStruts = Main.layoutManager._trackedActors[pIdx].affectsStruts;
                Main.layoutManager._trackedActors[pIdx].affectsStruts = false;
            }
        } catch (e) {
            console.warn('[Mak Zen] Error adjusting panel struts:', e);
        }

        // 2. Hide TopBar off-screen
        this._topbarRevealed = false;
        this._hideTopBar(true);

        // 3. Put Dock into Zen autohide mode (0 strut, forced hide)
        try {
            this._extension?._dock?.setZenMode(true);
        } catch (e) {
            console.warn('[Mak Zen] Error setting dock zen mode:', e);
        }

        // 4. Suspend window gaps
        try {
            this._extension?._windowGaps?.setZenMode(true);
        } catch (e) {}

        // 5. Update regions & maximize windows to full screen
        try {
            Main.layoutManager._queueUpdateRegions();
        } catch (e) {}

        GLib.timeout_add(GLib.PRIORITY_DEFAULT, 60, () => {
            this._maximizeWindowsToFullScreen();
            this._transitioning = false;
            return GLib.SOURCE_REMOVE;
        });

        // 6. Hook mouse pointer tracking for edge reveal
        this._connectPointerTracking();

        // 7. Hook overview signals
        this._connectOverview();
    }

    deactivate(updateSetting = true) {
        if (!this._active || this._transitioning) return;
        this._transitioning = true;
        this._active = false;

        if (updateSetting && this._settings.get_boolean('zen-mode-enabled')) {
            this._settings.set_boolean('zen-mode-enabled', false);
        }

        // Display sleek On-Screen HUD feedback
        try {
            Main.osdWindowManager?.show(
                -1,
                Gio.Icon.new_for_string('view-restore-symbolic'),
                'Zen Mode Disabled'
            );
        } catch (e) {}

        // Disconnect pointer tracking & overview
        this._disconnectPointerTracking();
        this._disconnectOverview();

        // 1. Restore TopBar position & struts
        this._cancelHideTopBar();
        try {
            const panelBox = Main.layoutManager.panelBox;
            panelBox.remove_transition('translation_y');
            panelBox.ease({
                translation_y: 0,
                duration: 250,
                mode: Clutter.AnimationMode.EASE_OUT_QUAD,
            });
            Main.panel.remove_style_class_name('mak-zen-revealed');
            this._topbarRevealed = true;

            const pIdx = Main.layoutManager._findActor(panelBox);
            if (pIdx !== -1) {
                Main.layoutManager._trackedActors[pIdx].affectsStruts = (this._origPanelAffectsStruts ?? true);
            }
        } catch (e) {
            console.warn('[Mak Zen] Error restoring panel:', e);
        }

        // 2. Restore Dock
        try {
            this._extension?._dock?.setZenMode(false);
        } catch (e) {
            console.warn('[Mak Zen] Error restoring dock zen mode:', e);
        }

        // 3. Restore WindowGaps
        try {
            this._extension?._windowGaps?.setZenMode(false);
        } catch (e) {}

        // 4. Update regions & restore window geometry
        try {
            Main.layoutManager._queueUpdateRegions();
        } catch (e) {}

        GLib.timeout_add(GLib.PRIORITY_DEFAULT, 60, () => {
            this._restoreWindowsGeometry();
            this._transitioning = false;
            return GLib.SOURCE_REMOVE;
        });
    }

    _maximizeWindowsToFullScreen() {
        try {
            if (this._savedWindow && this._savedWindow.get_workspace() === global.workspace_manager.get_active_workspace()) {
                if (!this._wasMaximized) {
                    this._savedWindow.maximize();
                } else {
                    this._savedWindow.unmaximize();
                    this._savedWindow.maximize();
                }
            }

            // Sync other maximized windows on current workspace
            for (const actor of global.get_window_actors()) {
                const w = actor.metaWindow;
                if (w && w !== this._savedWindow && w.window_type === Meta.WindowType.NORMAL) {
                    if (w.maximized_horizontally || w.maximized_vertically) {
                        w.unmaximize();
                        w.maximize();
                    }
                }
            }
        } catch (e) {
            console.warn('[Mak Zen] Error maximizing windows:', e);
        }
    }

    _restoreWindowsGeometry() {
        try {
            if (this._savedWindow && this._savedWindow.get_workspace() === global.workspace_manager.get_active_workspace()) {
                if (!this._wasMaximized) {
                    this._savedWindow.unmaximize();
                } else {
                    this._savedWindow.unmaximize();
                    this._savedWindow.maximize();
                }
            }

            for (const actor of global.get_window_actors()) {
                const w = actor.metaWindow;
                if (w && w !== this._savedWindow && w.window_type === Meta.WindowType.NORMAL) {
                    if (w.maximized_horizontally || w.maximized_vertically) {
                        w.unmaximize();
                        w.maximize();
                    }
                }
            }
        } catch (e) {
            console.warn('[Mak Zen] Error restoring window geometry:', e);
        }
    }

    _connectPointerTracking() {
        if (this._stageEventId) return;
        this._stageEventId = global.stage.connect('captured-event', (_stage, event) => {
            if (!this._active) return Clutter.EVENT_PROPAGATE;
            if (event.type() === Clutter.EventType.MOTION) {
                const [x, y] = event.get_coords();
                this._onPointerMotion(x, y);
            }
            return Clutter.EVENT_PROPAGATE;
        });
    }

    _disconnectPointerTracking() {
        if (this._stageEventId) {
            global.stage.disconnect(this._stageEventId);
            this._stageEventId = 0;
        }
        this._cancelHideTopBar();
    }

    _connectOverview() {
        if (!this._overviewShowingId) {
            this._overviewShowingId = Main.overview.connect('showing', () => {
                if (this._active) {
                    this._revealTopBar(true);
                    this._revealDock();
                }
            });
        }
        if (!this._overviewHiddenId) {
            this._overviewHiddenId = Main.overview.connect('hidden', () => {
                if (this._active) {
                    this._hideTopBar(false);
                    try {
                        this._extension?._dock?._manager?._docks?.forEach(d => d._autohide?._scheduleHide(null, true));
                    } catch (e) {}
                }
            });
        }
    }

    _disconnectOverview() {
        if (this._overviewShowingId) {
            Main.overview.disconnect(this._overviewShowingId);
            this._overviewShowingId = 0;
        }
        if (this._overviewHiddenId) {
            Main.overview.disconnect(this._overviewHiddenId);
            this._overviewHiddenId = 0;
        }
    }

    _onPointerMotion(x, y) {
        const monitor = Main.layoutManager.findMonitorForPoint(x, y) || Main.layoutManager.primaryMonitor;
        if (!monitor) return;

        const panelBox = Main.layoutManager.panelBox;
        const panelHeight = panelBox?.height || 28;

        // Top edge: touching top edge of primary monitor reveals top bar
        if (y <= monitor.y + 2 && monitor === Main.layoutManager.primaryMonitor) {
            this._revealTopBar();
        } else if (this._topbarRevealed) {
            if (y <= monitor.y + panelHeight + 4 && monitor === Main.layoutManager.primaryMonitor) {
                // Pointer is hovering over revealed topbar
                this._cancelHideTopBar();
            } else {
                // Pointer moved below topbar: schedule hide
                this._scheduleHideTopBar();
            }
        }

        // Dock edge: touching dock edge of monitor reveals dock
        const dockSide = this._getDockSide();
        let nearDockEdge = false;
        if (dockSide === 'bottom') {
            nearDockEdge = (y >= monitor.y + monitor.height - 3);
        } else if (dockSide === 'left') {
            nearDockEdge = (x <= monitor.x + 3);
        } else if (dockSide === 'right') {
            nearDockEdge = (x >= monitor.x + monitor.width - 3);
        }

        if (nearDockEdge) {
            this._revealDock();
        }
    }

    _revealTopBar(immediate = false) {
        this._cancelHideTopBar();
        if (this._topbarRevealed) return;
        this._topbarRevealed = true;

        const panelBox = Main.layoutManager.panelBox;
        panelBox.remove_transition('translation_y');
        Main.panel.add_style_class_name('mak-zen-revealed');

        if (immediate) {
            panelBox.translation_y = 0;
        } else {
            panelBox.ease({
                translation_y: 0,
                duration: 200,
                mode: Clutter.AnimationMode.EASE_OUT_QUAD,
            });
        }
    }

    _hideTopBar(immediate = false) {
        this._cancelHideTopBar();
        if (!this._active) return;
        if (!immediate && this._isMenuOpen()) return;

        this._topbarRevealed = false;
        const panelBox = Main.layoutManager.panelBox;
        const panelHeight = panelBox?.height || 28;

        panelBox.remove_transition('translation_y');
        Main.panel.remove_style_class_name('mak-zen-revealed');

        if (immediate) {
            panelBox.translation_y = -panelHeight;
        } else {
            panelBox.ease({
                translation_y: -panelHeight,
                duration: 220,
                mode: Clutter.AnimationMode.EASE_IN_QUAD,
            });
        }
    }

    _scheduleHideTopBar() {
        if (this._hideTopBarTimeoutId || !this._topbarRevealed) return;
        this._hideTopBarTimeoutId = GLib.timeout_add(GLib.PRIORITY_DEFAULT, 350, () => {
            this._hideTopBarTimeoutId = 0;
            if (this._isMenuOpen()) return GLib.SOURCE_REMOVE;

            const [px, py] = global.get_pointer();
            const mon = Main.layoutManager.findMonitorForPoint(px, py) || Main.layoutManager.primaryMonitor;
            const panelHeight = Main.layoutManager.panelBox?.height || 28;
            if (mon === Main.layoutManager.primaryMonitor && py <= mon.y + panelHeight + 4) {
                return GLib.SOURCE_REMOVE;
            }

            this._hideTopBar();
            return GLib.SOURCE_REMOVE;
        });
    }

    _cancelHideTopBar() {
        if (this._hideTopBarTimeoutId) {
            GLib.source_remove(this._hideTopBarTimeoutId);
            this._hideTopBarTimeoutId = 0;
        }
    }

    _isMenuOpen() {
        if (Main.panel.menuManager?.activeMenu) return true;
        if (Main.overview.visible) return true;
        if (Main.panel.statusArea) {
            for (const key of Object.keys(Main.panel.statusArea)) {
                const item = Main.panel.statusArea[key];
                if (item?.menu?.isOpen) return true;
            }
        }
        return false;
    }

    _revealDock() {
        try {
            const docks = this._extension?._dock?._manager?._docks || [];
            for (const dock of docks) {
                if (dock._autohide) {
                    dock._autohide._reveal();
                }
            }
        } catch (e) {}
    }

    _getDockSide() {
        try {
            const dockSettings = this._extension.getSettings('org.gnome.shell.extensions.aqua-dock-pro');
            return dockSettings?.get_string('position') || 'bottom';
        } catch (e) {
            return 'bottom';
        }
    }
}
