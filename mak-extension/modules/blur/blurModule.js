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
            if (key.startsWith('blur-') || key.startsWith('topbar-blur') ||
                key === 'global-opacity' || key === 'background-opacity' ||
                key === 'topbar-transparency' || key === 'topbar-opaque') {
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

            // Liquid glass dynamic stage blur across panel, popups, overview, app folders, and lockscreen
            panelSettings.set_boolean('blur', true);
            panelSettings.set_boolean('static-blur', false);
            panelSettings.set_boolean('override-background', true);
            panelSettings.set_int('style-panel', 0);
            panelSettings.set_boolean('unblur-in-overview', true);

            popupSettings.set_boolean('blur', true);
            popupSettings.set_boolean('static-blur', false);
            popupSettings.set_int('style-popup', 0);
            popupSettings.set_int('quick-settings-corner-radius', 16);
            popupSettings.set_int('menu-corner-radius', 12);
            popupSettings.set_int('notification-corner-radius', 16);
            popupSettings.set_int('dialog-corner-radius', 16);

            overviewSettings.set_boolean('blur', true);
            appfolderSettings.set_boolean('blur', true);
            lockscreenSettings.set_boolean('blur', true);

            // Enable dynamic application window blur
            const appSettings = new Gio.Settings({ schema_id: 'org.gnome.shell.extensions.blur-my-shell.applications' });
            appSettings.set_boolean('blur', true);
            appSettings.set_boolean('static-blur', false);
            appSettings.set_boolean('enable-all', true);
            appSettings.set_boolean('dynamic-opacity', false);
            if (appSettings.get_int('opacity') >= 250) {
                appSettings.set_int('opacity', 215);
            }
            appSettings.set_int('corner-radius', 16);
            appSettings.set_boolean('corner-when-maximized', true);

            // Blacklist Chrome, Chromium, Brave from whole-window translucency
            // to keep web content completely solid, crisp, and bug-free
            const targetBlacklist = [
                'google-chrome*',
                'chromium*',
                'brave*',
                'Plank',
                'com.desktop.ding',
                'Conky',
            ];
            const currentBlacklist = appSettings.get_strv('blacklist');
            const mergedBlacklist = Array.from(new Set([...currentBlacklist, ...targetBlacklist]));
            appSettings.set_strv('blacklist', mergedBlacklist);

            // Whitelist apps for window translucency
            const targetWhitelist = [
                'antigravity*',
                'code*',
                'electron*',
                'org.gnome.*',
                'com.mattjakeman.ExtensionManager',
                'io.github.*',
                'com.github.*',
            ];
            const currentWhitelist = appSettings.get_strv('whitelist');
            const filteredWhitelist = currentWhitelist.filter(x => !x.includes('chrome') && !x.includes('brave') && !x.includes('chromium'));
            const mergedWhitelist = Array.from(new Set([...filteredWhitelist, ...targetWhitelist]));
            appSettings.set_strv('whitelist', mergedWhitelist);

            // Set hacks-level 2 to disable clipped redraws so blur updates behind all windows
            const bmsSettings = new Gio.Settings({ schema_id: 'org.gnome.shell.extensions.blur-my-shell' });
            bmsSettings.set_int('hacks-level', 2);
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

            const isTopBarOpaque = this._makSettings.get_boolean('topbar-opaque');
            const topbarBlur = !isTopBarOpaque && (this._makSettings.get_boolean('topbar-blur') || this._makSettings.get_boolean('blur-panel'));
            panelSettings.set_boolean('blur', topbarBlur);
            panelSettings.set_boolean('override-background', !isTopBarOpaque);
            overviewSettings.set_boolean('blur', this._makSettings.get_boolean('blur-overview'));
            appfolderSettings.set_boolean('blur', this._makSettings.get_boolean('blur-appfolder'));

            // Sync global parameters
            const sigma = this._makSettings.get_int('blur-sigma');
            const brightness = this._makSettings.get_double('blur-brightness');
            const noise = this._makSettings.get_double('blur-noise-amount');
            const refractionStrength = this._makSettings.get_double('blur-refraction-strength');
            const chromaticDispersion = this._makSettings.get_double('blur-chromatic-dispersion');
            const liquidGlass = this._makSettings.get_boolean('blur-liquid-glass');

            // Apply sigma and brightness directly to individual component settings
            panelSettings.set_int('sigma', sigma);
            panelSettings.set_double('brightness', brightness);
            popupSettings.set_int('sigma', sigma);
            popupSettings.set_double('brightness', brightness);
            appfolderSettings.set_int('sigma', sigma);
            appfolderSettings.set_double('brightness', brightness);

            try {
                const appSettings = new Gio.Settings({ schema_id: 'org.gnome.shell.extensions.blur-my-shell.applications' });
                appSettings.set_int('sigma', sigma);
                appSettings.set_double('brightness', brightness);
                appSettings.set_boolean('blur', true);
                appSettings.set_boolean('static-blur', false);
                appSettings.set_boolean('enable-all', true);
                appSettings.set_boolean('dynamic-opacity', false);
                appSettings.set_int('corner-radius', 16);
                appSettings.set_boolean('corner-when-maximized', true);
                if (appSettings.get_int('opacity') >= 250) {
                    appSettings.set_int('opacity', 215);
                }
            } catch (e) {}

            bmsSettings.set_int('sigma', sigma);
            bmsSettings.set_double('brightness', brightness);
            bmsSettings.set_double('noise-amount', noise);
            bmsSettings.set_int('hacks-level', 2);

            // Update live pipeline parameters so shader updates instantly
            try {
                const pipelinesVal = bmsSettings.get_value('pipelines');
                const pipelines = pipelinesVal ? unpack_pipelines(pipelinesVal) : {};
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

                // Calibrate blur radius behind refraction:
                // Moderate blur (8-16px) allows physical Snell-law light bending and chromatic dispersion
                // to be strikingly perceptible rather than washed out by excessive diffusion.
                const glassBlurRadius = Math.max(3.0, Math.min(20.0, sigma * 0.35));

                if (!pipelines['pipeline_liquid_glass']) {
                    pipelines['pipeline_liquid_glass'] = {
                        name: 'Liquid Glass',
                        effects: [
                            {
                                type: 'refraction',
                                id: 'effect_liquid_glass_01',
                                params: {
                                    strength: refractionStrength,
                                    blur_radius: glassBlurRadius,
                                    edge_size: 24.0,
                                    falloff: 2.2,
                                    corner_radius: 20.0,
                                    rim_width: 4.8,
                                    rgb_fringing: chromaticDispersion,
                                    gloss: 0.60,
                                    tint: 0.14,
                                }
                            }
                        ]
                    };
                    changed = true;
                } else {
                    for (const eff of pipelines['pipeline_liquid_glass'].effects) {
                        if (eff.type === 'refraction') {
                            eff.params.strength = refractionStrength;
                            eff.params.rgb_fringing = chromaticDispersion;
                            eff.params.blur_radius = glassBlurRadius;
                            eff.params.gloss = 0.60;
                            eff.params.tint = 0.14;
                            changed = true;
                        }
                    }
                }

                if (changed) {
                    bmsSettings.set_value('pipelines', pack_pipelines(pipelines));
                }
            } catch (pErr) {
                console.warn('[Mak Blur] Error updating pipelines parameters:', pErr.message);
            }

            // ── Pipeline assignment ──
            // DummyPipeline (dynamic, static-blur=false) ignores pipeline string.
            // RefractionEffect only activates via the static Pipeline path (static-blur=true).
            panelSettings.set_boolean('unblur-in-overview', true);

            if (liquidGlass) {
                panelSettings.set_boolean('static-blur', true);
                popupSettings.set_boolean('static-blur', true);
                panelSettings.set_string('pipeline', 'pipeline_liquid_glass');
                popupSettings.set_string('pipeline', 'pipeline_liquid_glass');
            } else {
                panelSettings.set_boolean('static-blur', false);
                popupSettings.set_boolean('static-blur', false);
                panelSettings.set_string('pipeline', 'pipeline_default');
                popupSettings.set_string('pipeline', 'pipeline_default_rounded');
            }

            if (this._bms) {
                try {
                    this._bms._panel_blur?.reset();
                    this._bms._popup?.reset();
                } catch (e) {}
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
