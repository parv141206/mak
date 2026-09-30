// SPDX-License-Identifier: GPL-3.0-or-later
// Mak Top Bar Module: Apple Menu, Active App Title, and Glass Panel Styling

import Clutter from 'gi://Clutter';
import GObject from 'gi://GObject';
import Shell from 'gi://Shell';
import St from 'gi://St';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import * as PanelMenu from 'resource:///org/gnome/shell/ui/panelMenu.js';

import { KiwiMenu } from './kiwimenu.js';

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
        this._settings = extension.getSettings();
        this._appleMenu = null;
        this._appTitle = null;
        this._panelBlurEffect = null;
    }

    enable() {
        // 1. Add Apple Menu
        if (this._settings.get_boolean('topbar-apple-menu')) {
            try {
                const kiwiSettings = this._extension.getSettings('org.gnome.shell.extensions.kiwimenu');
                this._appleMenu = new KiwiMenu(kiwiSettings, this._extension.path, this._extension);
                Main.panel.addToStatusArea('MakAppleMenu', this._appleMenu, 0, 'left');
            } catch (err) {
                console.warn('[Mak TopBar] Could not add Apple Menu:', err);
            }
        }

        // 2. Add Active App Title
        if (this._settings.get_boolean('topbar-app-title')) {
            try {
                this._appTitle = new AppTitleButton();
                Main.panel.addToStatusArea('MakAppTitle', this._appTitle, 1, 'left');
            } catch (err) {
                console.warn('[Mak TopBar] Could not add App Title:', err);
            }
        }

        // 3. Apply Glass Blur & Styling to Top Bar
        if (this._settings.get_boolean('topbar-blur')) {
            this._applyPanelBlur();
        }

        Main.panel.add_style_class_name('mak-panel');
    }

    _applyPanelBlur() {
        if (this._panelBlurEffect || Main.panel.get_effects().some(e => e instanceof Shell.BlurEffect)) return;
        try {
            const radius = this._settings.get_int('topbar-blur-radius') || 28;
            this._panelBlurEffect = new Shell.BlurEffect({
                mode: Shell.BlurMode.BACKGROUND,
                radius: radius,
                brightness: 0.85,
            });
            Main.panel.add_effect(this._panelBlurEffect);
        } catch (err) {
            console.warn('[Mak TopBar] Could not apply panel blur:', err);
        }
    }

    disable() {
        if (this._panelBlurEffect) {
            try { Main.panel.remove_effect(this._panelBlurEffect); } catch (e) {}
            this._panelBlurEffect = null;
        }

        Main.panel.remove_style_class_name('mak-panel');

        if (this._appTitle) {
            this._appTitle.destroy();
            this._appTitle = null;
        }

        if (this._appleMenu) {
            this._appleMenu.destroy();
            this._appleMenu = null;
        }
    }
}
