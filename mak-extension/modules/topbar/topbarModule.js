// SPDX-License-Identifier: GPL-3.0-or-later
// Mak Top Bar Module: Apple Menu, Active App Title, Media Pill, Bluetooth Battery, and Glass Panel Styling

import Clutter from 'gi://Clutter';
import Gio from 'gi://Gio';
import GObject from 'gi://GObject';
import Shell from 'gi://Shell';
import St from 'gi://St';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import * as PanelMenu from 'resource:///org/gnome/shell/ui/panelMenu.js';

import { KiwiMenu } from './kiwimenu.js';
import { BluetoothBatteryButton } from './bluetoothBattery.js';
import { MusicController } from './dynamic-music-pill/controller.js';

const AppTitleButton = GObject.registerClass(
    { GTypeName: 'MakAppTitleButton' },
    class AppTitleButton extends PanelMenu.Button {
        _init() {
            super._init(0.0, 'MakAppTitle', false);
            this.reactive = false;

            this._label = new St.Label({
                text: 'Finder',
                style_class: 'mak-app-title-label',
                y_align: Clutter.ActorAlign.CENTER,
            });
            this.add_child(this._label);

            this._tracker = Shell.WindowTracker.get_default();
            this._notifyId = this._tracker.connect('notify::focus-app', () => this._updateTitle());
            this._updateTitle();
        }

        _updateTitle() {
            const app = this._tracker.focus_app;
            if (app) {
                this._label.set_text(app.get_name());
            } else {
                this._label.set_text('Finder');
            }
        }

        destroy() {
            if (this._notifyId) {
                try { this._tracker.disconnect(this._notifyId); } catch (e) {}
                this._notifyId = 0;
            }
            super.destroy();
        }
    }
);

export class TopBarModule {
    constructor(extension) {
        this._extension = extension;
        this._settings = extension.getSettings('org.gnome.shell.extensions.mak');
        this._interfaceSettings = new Gio.Settings({ schema_id: 'org.gnome.desktop.interface' });
        this._appleMenu = null;
        this._appTitle = null;
        this._btBattery = null;
        this._musicController = null;
        this._panelBlurEffect = null;
        this._settingsChangedId = 0;
        this._interfaceChangedId = 0;
    }

    enable() {
        // 1. Add Apple Menu
        if (this._settings.get_boolean('topbar-apple-menu')) {
            this._enableAppleMenu();
        }

        // 2. Add Active App Title
        if (this._settings.get_boolean('topbar-app-title')) {
            this._enableAppTitle();
        }

        // 3. Add Bluetooth Battery Indicator
        if (this._settings.get_boolean('topbar-bluetooth-battery')) {
            this._enableBluetoothBattery();
        }

        // 4. Add Dynamic Media Pill
        if (this._settings.get_boolean('topbar-media-pill')) {
            this._enableMediaPill();
        }

        // 5. Apply Glass Blur & Styling to Top Bar
        if (this._settings.get_boolean('topbar-blur')) {
            this._applyPanelBlur();
        }

        // 6. Apply panel transparency from settings
        this._applyPanelTransparency();

        Main.panel.add_style_class_name('mak-panel');

        this._settingsChangedId = this._settings.connect('changed', (s, key) => {
            if (key === 'topbar-apple-menu') {
                if (this._settings.get_boolean('topbar-apple-menu')) this._enableAppleMenu();
                else this._disableAppleMenu();
            } else if (key === 'topbar-app-title') {
                if (this._settings.get_boolean('topbar-app-title')) this._enableAppTitle();
                else this._disableAppTitle();
            } else if (key === 'topbar-bluetooth-battery') {
                if (this._settings.get_boolean('topbar-bluetooth-battery')) this._enableBluetoothBattery();
                else this._disableBluetoothBattery();
            } else if (key === 'topbar-media-pill') {
                if (this._settings.get_boolean('topbar-media-pill')) this._enableMediaPill();
                else this._disableMediaPill();
            } else if (key === 'topbar-blur') {
                if (this._settings.get_boolean('topbar-blur')) this._applyPanelBlur();
                else this._removePanelBlur();
            } else if (key === 'topbar-transparency' || key === 'global-opacity') {
                this._applyPanelTransparency();
            }
        });

        this._interfaceChangedId = this._interfaceSettings.connect('changed', (s, key) => {
            if (key === 'gtk-theme' || key === 'color-scheme') {
                this._applyPanelTransparency();
            }
        });
    }

    _enableAppleMenu() {
        if (this._appleMenu) return;
        try {
            const kiwiSettings = this._extension.getSettings('org.gnome.shell.extensions.kiwimenu');
            this._appleMenu = new KiwiMenu(kiwiSettings, this._extension.path, this._extension);
            Main.panel.addToStatusArea('MakAppleMenu', this._appleMenu, 0, 'left');
        } catch (err) {
            console.warn('[Mak TopBar] Could not add Apple Menu:', err);
        }
    }

    _disableAppleMenu() {
        if (this._appleMenu) {
            this._appleMenu.destroy();
            this._appleMenu = null;
        }
    }

    _enableAppTitle() {
        if (this._appTitle) return;
        try {
            this._appTitle = new AppTitleButton();
            Main.panel.addToStatusArea('MakAppTitle', this._appTitle, 1, 'left');
        } catch (err) {
            console.warn('[Mak TopBar] Could not add App Title:', err);
        }
    }

    _disableAppTitle() {
        if (this._appTitle) {
            this._appTitle.destroy();
            this._appTitle = null;
        }
    }

    _enableBluetoothBattery() {
        if (this._btBattery) return;
        try {
            this._btBattery = new BluetoothBatteryButton(this._extension);
            Main.panel.addToStatusArea('MakBluetoothBattery', this._btBattery, 1, 'right');
        } catch (err) {
            console.warn('[Mak TopBar] Could not add Bluetooth Battery indicator:', err);
        }
    }

    _disableBluetoothBattery() {
        if (this._btBattery) {
            try { this._btBattery.destroy(); } catch (e) {}
            this._btBattery = null;
        }
    }

    _enableMediaPill() {
        if (this._musicController) return;
        try {
            this._musicController = new MusicController(this._extension);
            this._musicController.enable();
        } catch (err) {
            console.warn('[Mak TopBar] Could not enable Dynamic Music Pill:', err);
        }
    }

    _disableMediaPill() {
        if (this._musicController) {
            try { this._musicController.disable(); } catch (e) {}
            this._musicController = null;
        }
    }

    _applyPanelBlur() {
        // Panel blur is handled entirely by Blur-My-Shell (BlurModule) which uses
        // gnome-rounded-blur's dynamic background blur via DummyPipeline.
        // We do NOT add a second Shell.BlurEffect here — stacking two blur effects
        // causes double-blur, wrong brightness, and z-order artifacts.
        // BMS reads topbar-blur and blur-panel from mak settings and enables/disables
        // its own panel blur accordingly.
    }

    _removePanelBlur() {
        // Clean up any previously added direct effect (from older extension versions)
        if (this._panelBlurEffect) {
            try { Main.panel.remove_effect(this._panelBlurEffect); } catch (e) {}
            this._panelBlurEffect = null;
        }
    }

    _applyPanelTransparency() {
        // Read transparency from settings.
        // global-opacity acts as a master override when it differs from the default (0.5);
        // otherwise topbar-transparency is used.
        try {
            let alpha = this._settings.get_double('topbar-transparency');
            const colorScheme = this._interfaceSettings ? this._interfaceSettings.get_string('color-scheme') : '';
            const gtkTheme = this._interfaceSettings ? this._interfaceSettings.get_string('gtk-theme') : '';
            const isLight = (colorScheme === 'prefer-light') || gtkTheme.toLowerCase().includes('light');
            const isAmoled = gtkTheme.toLowerCase().includes('amoled');

            if (isLight) {
                Main.panel.add_style_class_name('light-mode');
                const r = 255, g = 255, b = 255;
                const style = `background-color: rgba(${r}, ${g}, ${b}, ${alpha.toFixed(3)});`;
                Main.panel.set_style(style);
            } else {
                Main.panel.remove_style_class_name('light-mode');
                const r = isAmoled ? 0 : 22;
                const g = isAmoled ? 0 : 22;
                const b = isAmoled ? 0 : 28;
                const style = `background-color: rgba(${r}, ${g}, ${b}, ${alpha.toFixed(3)});`;
                Main.panel.set_style(style);
            }
        } catch (e) {
            console.warn('[Mak TopBar] Could not apply panel transparency:', e.message);
        }
    }

    _removePanelTransparency() {
        try { Main.panel.set_style(''); } catch (e) {}
    }

    disable() {
        if (this._settingsChangedId) {
            try { this._settings.disconnect(this._settingsChangedId); } catch (e) {}
            this._settingsChangedId = 0;
        }

        if (this._interfaceChangedId) {
            try { this._interfaceSettings.disconnect(this._interfaceChangedId); } catch (e) {}
            this._interfaceChangedId = 0;
        }
        this._interfaceSettings = null;

        this._removePanelBlur();
        this._removePanelTransparency();
        Main.panel.remove_style_class_name('mak-panel');
        Main.panel.remove_style_class_name('light-mode');

        this._disableMediaPill();
        this._disableBluetoothBattery();
        this._disableAppTitle();
        this._disableAppleMenu();
    }
}
