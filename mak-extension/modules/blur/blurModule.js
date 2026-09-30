// SPDX-License-Identifier: GPL-3.0-or-later
// Mak Unified Shell Blur Module
// Applies authentic macOS frosted glass blur across Top Bar, Overview, Popups/Quick Settings, Folders, and Lock Screen.
// Supports Liquid Glass refraction shader with chromatic dispersion and Snell-law light bending.

import Gio from 'gi://Gio';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import BlurMyShell from './bms/extension.js';
import { NativeDynamicBlurEffect } from './bms/effects/native_dynamic_gaussian_blur.js';
import { unpack_pipelines, pack_pipelines } from './bms/conveniences/pipeline_settings.js';

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
            panelSettings.set_boolean('static-blur', false);
            panelSettings.set_boolean('override-background', true);
            panelSettings.set_int('style-panel', 0);
            panelSettings.set_boolean('unblur-in-overview', false);

            popupSettings.set_boolean('blur', true);
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
            const popupSettings = new Gio.Settings({ schema_id: 'org.gnome.shell.extensions.blur-my-shell.popup' });
            const overviewSettings = new Gio.Settings({ schema_id: 'org.gnome.shell.extensions.blur-my-shell.overview' });
            const appfolderSettings = new Gio.Settings({ schema_id: 'org.gnome.shell.extensions.blur-my-shell.appfolder' });
            const bmsSettings = new Gio.Settings({ schema_id: 'org.gnome.shell.extensions.blur-my-shell' });

            const topbarBlur = this._makSettings.get_boolean('topbar-blur') || this._makSettings.get_boolean('blur-panel');
            panelSettings.set_boolean('blur', topbarBlur);
            overviewSettings.set_boolean('blur', this._makSettings.get_boolean('blur-overview'));
            appfolderSettings.set_boolean('blur', this._makSettings.get_boolean('blur-appfolder'));

            // Toggle Liquid Glass refraction pipeline vs default Gaussian pipeline
            const liquidGlass = this._makSettings.get_boolean('blur-liquid-glass');
            if (liquidGlass) {
                panelSettings.set_string('pipeline', 'pipeline_liquid_glass');
                popupSettings.set_string('pipeline', 'pipeline_liquid_glass');
            } else {
                panelSettings.set_string('pipeline', 'pipeline_default');
                popupSettings.set_string('pipeline', 'pipeline_default_rounded');
            }

            // Sync global parameters
            const sigma = this._makSettings.get_int('blur-sigma');
            const brightness = this._makSettings.get_double('blur-brightness');
            const noise = this._makSettings.get_double('blur-noise-amount');
            const refractionStrength = this._makSettings.get_double('blur-refraction-strength');
            const chromaticDispersion = this._makSettings.get_double('blur-chromatic-dispersion');

            bmsSettings.set_int('sigma', sigma);
            bmsSettings.set_double('brightness', brightness);
            bmsSettings.set_double('noise-amount', noise);

            // Update live pipeline parameters so shader updates instantly
            try {
                const pipelinesVal = bmsSettings.get_value('pipelines');
                if (pipelinesVal) {
                    const pipelines = unpack_pipelines(pipelinesVal);
                    let changed = false;

                    if (pipelines['pipeline_default']) {
                        for (const eff of pipelines['pipeline_default'].effects) {
                            if (eff.type.includes('blur')) {
                                eff.params.radius = sigma;
                                eff.params.brightness = brightness;
                                changed = true;
                            }
                        }
                    }
                    if (pipelines['pipeline_default_rounded']) {
                        for (const eff of pipelines['pipeline_default_rounded'].effects) {
                            if (eff.type.includes('blur')) {
                                eff.params.radius = sigma;
                                eff.params.brightness = brightness;
                                changed = true;
                            }
                        }
                    }
                    if (pipelines['pipeline_liquid_glass']) {
                        for (const eff of pipelines['pipeline_liquid_glass'].effects) {
                            if (eff.type === 'refraction') {
                                eff.params.strength = refractionStrength;
                                eff.params.rgb_fringing = chromaticDispersion;
                                eff.params.blur_radius = Math.max(2.0, sigma / 2.5);
                                changed = true;
                            }
                        }
                    }

                    if (changed) {
                        bmsSettings.set_value('pipelines', pack_pipelines(pipelines));
                    }
                }
            } catch (pErr) {
                console.warn('[Mak Blur] Error updating pipelines parameters:', pErr.message);
            }
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
