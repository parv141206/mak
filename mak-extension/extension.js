// SPDX-License-Identifier: GPL-3.0-or-later
// Mak: Master GNOME Shell Extension Entrypoint

import { Extension } from 'resource:///org/gnome/shell/extensions/extension.js';

import { DockModule } from './modules/dock/dockModule.js';
import { TopBarModule } from './modules/topbar/topbarModule.js';
import { SpotlightModule } from './modules/spotlight/spotlightModule.js';
import { WindowGapModule } from './modules/window-gaps/gapModule.js';
import { WindowCornersModule } from './modules/window-corners/cornersModule.js';
import { BlurModule } from './modules/blur/blurModule.js';
import { MenuStyleController } from './modules/appearance/menuStyleController.js';

export default class MakExtension extends Extension {
    async enable() {
        this._settings = this.getSettings('org.gnome.shell.extensions.mak');

        // Submodules with cache-busting dynamic imports
        this._dock = new DockModule(this);
        try {
            const { TopBarModule: DynamicTopBar } = await import(`./modules/topbar/topbarModule.js?v=${Date.now()}`);
            this._topbar = new DynamicTopBar(this);
        } catch (err) {
            console.warn('[Mak] Dynamic TopBar import fallback:', err);
            this._topbar = new TopBarModule(this);
        }
        this._spotlight = new SpotlightModule(this);
        this._windowGaps = new WindowGapModule(this);

        try {
            const { WindowCornersModule: DynamicCorners } = await import(`./modules/window-corners/cornersModule.js?v=${Date.now()}`);
            this._windowCorners = new DynamicCorners(this);
        } catch (err) {
            this._windowCorners = new WindowCornersModule(this);
        }

        try {
            const { BlurModule: DynamicBlur } = await import(`./modules/blur/blurModule.js?v=${Date.now()}`);
            this._blur = new DynamicBlur(this);
        } catch (err) {
            this._blur = new BlurModule(this);
        }

        try {
            const { MenuStyleController: DynamicMenuStyle } = await import(`./modules/appearance/menuStyleController.js?v=${Date.now()}`);
            this._menuStyle = new DynamicMenuStyle(this);
        } catch (err) {
            this._menuStyle = new MenuStyleController(this);
        }

        this._settingsChangedId = this._settings.connect('changed', (settings, key) => {
            this._onSettingChanged(key);
        });

        // Always enable unified menu & shell appearance
        this._menuStyle.enable();

        // Enable configured features
        if (this._settings.get_boolean('dock-enabled')) {
            try { this._dock.enable(); } catch (e) { console.error('[Mak Dock] Enable error:', e); }
        }
        console.log('[Mak] topbar-enabled setting is:', this._settings.get_boolean('topbar-enabled'));
        if (this._settings.get_boolean('topbar-enabled')) {
            try { this._topbar.enable(); } catch (e) { console.error('[Mak TopBar] Enable error:', e); }
        }
        if (this._settings.get_boolean('spotlight-enabled')) {
            try { this._spotlight.enable(); } catch (e) { console.error('[Mak Spotlight] Enable error:', e); }
        }
        if (this._settings.get_boolean('gaps-enabled')) {
            try { this._windowGaps.enable(); } catch (e) { console.error('[Mak WindowGaps] Enable error:', e); }
        }
        if (this._settings.get_boolean('corners-enabled')) {
            try { this._windowCorners.enable(); } catch (e) { console.error('[Mak WindowCorners] Enable error:', e); }
        }
        if (this._settings.get_boolean('blur-enabled')) {
            try { this._blur.enable(); } catch (e) { console.error('[Mak Blur] Enable error:', e); }
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
        try { this._menuStyle?.disable(); } catch (e) {}

        this._dock = null;
        this._topbar = null;
        this._spotlight = null;
        this._windowGaps = null;
        this._windowCorners = null;
        this._blur = null;
        this._menuStyle = null;
        this._settings = null;

        console.log('[Mak] Unified macOS Experience Suite Disabled.');
    }
}
