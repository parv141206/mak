// SPDX-License-Identifier: GPL-3.0-or-later
// Mak: Master GNOME Shell Extension Entrypoint

import { Extension } from 'resource:///org/gnome/shell/extensions/extension.js';

import { DockModule } from './modules/dock/dockModule.js';
import { TopBarModule } from './modules/topbar/topbarModule.js';
import { SpotlightModule } from './modules/spotlight/spotlightModule.js';
import { WindowGapModule } from './modules/window-gaps/gapModule.js';
import { WindowCornersModule } from './modules/window-corners/cornersModule.js';
import { BlurModule } from './modules/blur/blurModule.js';

export default class MakExtension extends Extension {
    enable() {
        this._settings = this.getSettings('org.gnome.shell.extensions.mak');

        // Submodules
        this._dock = new DockModule(this);
        this._topbar = new TopBarModule(this);
        this._spotlight = new SpotlightModule(this);
        this._windowGaps = new WindowGapModule(this);
        this._windowCorners = new WindowCornersModule(this);
        this._blur = new BlurModule(this);

        this._settingsChangedId = this._settings.connect('changed', (settings, key) => {
            this._onSettingChanged(key);
        });

        // Enable configured features
        if (this._settings.get_boolean('dock-enabled')) {
            this._dock.enable();
        }
        if (this._settings.get_boolean('topbar-enabled')) {
            this._topbar.enable();
        }
        if (this._settings.get_boolean('spotlight-enabled')) {
            this._spotlight.enable();
        }
        if (this._settings.get_boolean('gaps-enabled')) {
            this._windowGaps.enable();
        }
        if (this._settings.get_boolean('corners-enabled')) {
            this._windowCorners.enable();
        }
        if (this._settings.get_boolean('blur-enabled')) {
            this._blur.enable();
        }

        console.log('[Mak] Unified macOS Experience Suite Enabled successfully.');
    }

    _onSettingChanged(key) {
        if (key === 'dock-enabled') {
            if (this._settings.get_boolean('dock-enabled'))
                this._dock.enable();
            else
                this._dock.disable();
        } else if (key === 'topbar-enabled') {
            if (this._settings.get_boolean('topbar-enabled'))
                this._topbar.enable();
            else
                this._topbar.disable();
        } else if (key === 'spotlight-enabled') {
            if (this._settings.get_boolean('spotlight-enabled'))
                this._spotlight.enable();
            else
                this._spotlight.disable();
        } else if (key === 'gaps-enabled') {
            if (this._settings.get_boolean('gaps-enabled'))
                this._windowGaps.enable();
            else
                this._windowGaps.disable();
        } else if (key === 'corners-enabled') {
            if (this._settings.get_boolean('corners-enabled'))
                this._windowCorners.enable();
            else
                this._windowCorners.disable();
        } else if (key === 'blur-enabled') {
            if (this._settings.get_boolean('blur-enabled'))
                this._blur.enable();
            else
                this._blur.disable();
        }
    }

    disable() {
        if (this._settingsChangedId) {
            this._settings.disconnect(this._settingsChangedId);
            this._settingsChangedId = 0;
        }

        try { this._dock?.disable(); } catch (e) {}
        try { this._topbar?.disable(); } catch (e) {}
        try { this._spotlight?.disable(); } catch (e) {}
        try { this._windowGaps?.disable(); } catch (e) {}
        try { this._windowCorners?.disable(); } catch (e) {}
        try { this._blur?.disable(); } catch (e) {}

        this._dock = null;
        this._topbar = null;
        this._spotlight = null;
        this._windowGaps = null;
        this._windowCorners = null;
        this._blur = null;
        this._settings = null;

        console.log('[Mak] Unified macOS Experience Suite Disabled.');
    }
}
