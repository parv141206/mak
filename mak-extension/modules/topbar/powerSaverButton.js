// SPDX-License-Identifier: GPL-3.0-or-later
// Mak Topbar Custom Managed Eco Power Saving Mode
// Ultra-optimized battery saver for distraction-free reading, documents, and maximum endurance

import Clutter from 'gi://Clutter';
import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import GObject from 'gi://GObject';
import St from 'gi://St';
import UPower from 'gi://UPowerGlib';

import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import * as PanelMenu from 'resource:///org/gnome/shell/ui/panelMenu.js';
import * as PopupMenu from 'resource:///org/gnome/shell/ui/popupMenu.js';

const _uid = Math.floor(Math.random() * 10000000);

export const PowerSaverButton = GObject.registerClass(
    { GTypeName: `MakPowerSaverButton_${_uid}` },
    class PowerSaverButton extends PanelMenu.Button {
        _init(extension) {
            super._init(0.5, 'MakPowerSaver', false);
            this._extension = extension;
            this._settings = extension.getSettings('org.gnome.shell.extensions.mak');
            this._liquidSettings = null;
            try {
                this._liquidSettings = extension.getSettings('org.gnome.shell.extensions.liquid-glass@thinkingcoding1231.gmail.com');
            } catch (e) {}

            this._desktopSettings = new Gio.Settings({ schema_id: 'org.gnome.desktop.interface' });
            this._sessionSettings = new Gio.Settings({ schema_id: 'org.gnome.desktop.session' });

            this.add_style_class_name('mak-power-saver-button');

            this._isActive = false;
            this._savedState = null;
            this._telemetryTimerId = 0;

            // Load Eco Leaf Icon
            const iconPath = `${extension.path}/icons/eco-saver-symbolic.svg`;
            if (GLib.file_test(iconPath, GLib.FileTest.EXISTS)) {
                this._iconGicon = Gio.icon_new_for_string(iconPath);
            } else {
                this._iconGicon = Gio.ThemedIcon.new('power-profile-power-saver-symbolic');
            }

            // Panel Button Layout: Icon + Optional "ECO" Badge
            const btnBox = new St.BoxLayout({
                vertical: false,
                style_class: 'mak-power-saver-panel-box',
                y_align: Clutter.ActorAlign.CENTER,
            });

            this._icon = new St.Icon({
                gicon: this._iconGicon,
                style_class: 'system-status-icon mak-power-saver-panel-icon',
                y_align: Clutter.ActorAlign.CENTER,
            });
            btnBox.add_child(this._icon);

            this._badge = new St.Label({
                text: 'ECO',
                style_class: 'mak-power-saver-panel-badge',
                y_align: Clutter.ActorAlign.CENTER,
                visible: false,
            });
            btnBox.add_child(this._badge);

            this.add_child(btnBox);

            // Configure Popup Menu Container
            this.menu.box.add_style_class_name('mak-power-saver-menu');

            // Build Popup Menu UI
            this._buildPopup();

            // Connect menu open to refresh telemetry
            this.menu.connect('open-state-changed', (_menu, isOpen) => {
                if (isOpen) {
                    this._updateTelemetry();
                    if (!this._telemetryTimerId) {
                        this._telemetryTimerId = GLib.timeout_add_seconds(GLib.PRIORITY_LOW, 3, () => {
                            this._updateTelemetry();
                            return GLib.SOURCE_CONTINUE;
                        });
                    }
                } else if (this._telemetryTimerId) {
                    GLib.source_remove(this._telemetryTimerId);
                    this._telemetryTimerId = 0;
                }
            });

            // Restore active state from settings
            if (this._settings && this._settings.get_boolean('power-saver-active')) {
                this.activate(false);
            }
        }

        _buildPopup() {
            this.menu.removeAll();

            const container = new St.BoxLayout({
                vertical: true,
                style_class: 'mak-power-saver-container',
            });
            this.menu.box.add_child(container);

            // ── 1. HEADER ──
            const headerBox = new St.BoxLayout({
                vertical: false,
                style_class: 'mak-power-saver-header',
                y_align: Clutter.ActorAlign.CENTER,
            });

            const titleBox = new St.BoxLayout({
                vertical: true,
                style_class: 'mak-power-saver-title-box',
                x_expand: true,
            });

            const title = new St.Label({
                text: 'Eco Power Saver',
                style_class: 'mak-power-saver-header-title',
            });
            titleBox.add_child(title);

            const subtitle = new St.Label({
                text: 'Extreme battery optimization for reading & tasks',
                style_class: 'mak-power-saver-header-sub',
            });
            titleBox.add_child(subtitle);
            headerBox.add_child(titleBox);

            this._statusBadge = new St.Label({
                text: this._isActive ? 'ACTIVE' : 'OFF',
                style_class: `mak-power-saver-status-badge ${this._isActive ? 'active' : ''}`,
                y_align: Clutter.ActorAlign.CENTER,
            });
            headerBox.add_child(this._statusBadge);
            container.add_child(headerBox);

            // ── 2. MASTER TOGGLE BUTTON ──
            this._toggleBtn = new St.Button({
                style_class: `mak-power-saver-toggle-btn ${this._isActive ? 'active' : ''}`,
                x_expand: true,
                reactive: true,
                can_focus: true,
            });

            const toggleBox = new St.BoxLayout({
                vertical: false,
                style_class: 'mak-power-saver-toggle-content',
                x_align: Clutter.ActorAlign.CENTER,
                y_align: Clutter.ActorAlign.CENTER,
            });

            this._toggleIcon = new St.Icon({
                gicon: this._iconGicon,
                style_class: 'mak-power-saver-toggle-icon',
            });
            toggleBox.add_child(this._toggleIcon);

            this._toggleLabel = new St.Label({
                text: this._isActive ? 'Turn Off Eco Mode' : 'Turn On Extreme Power Saver',
                style_class: 'mak-power-saver-toggle-label',
            });
            toggleBox.add_child(this._toggleLabel);
            this._toggleBtn.set_child(toggleBox);

            this._toggleBtn.connect('clicked', () => {
                if (this._isActive) this.deactivate();
                else this.activate(true);
            });
            container.add_child(this._toggleBtn);

            // Separator
            container.add_child(new St.Widget({ style_class: 'mak-power-saver-separator' }));

            // ── 3. TELEMETRY & BATTERY CARD ──
            const telemetryCard = new St.BoxLayout({
                vertical: true,
                style_class: 'mak-power-saver-card',
            });

            const batteryRow = new St.BoxLayout({
                vertical: false,
                style_class: 'mak-power-saver-telemetry-row',
                y_align: Clutter.ActorAlign.CENTER,
            });

            this._telemetryBatLabel = new St.Label({
                text: 'Battery: --%',
                style_class: 'mak-power-saver-telemetry-title',
                x_expand: true,
            });
            batteryRow.add_child(this._telemetryBatLabel);

            this._telemetryRateLabel = new St.Label({
                text: '-- W',
                style_class: 'mak-power-saver-telemetry-val',
            });
            batteryRow.add_child(this._telemetryRateLabel);
            telemetryCard.add_child(batteryRow);

            this._telemetrySubLabel = new St.Label({
                text: 'Hardware profile & services monitor',
                style_class: 'mak-power-saver-telemetry-sub',
            });
            telemetryCard.add_child(this._telemetrySubLabel);
            container.add_child(telemetryCard);

            // Separator
            container.add_child(new St.Widget({ style_class: 'mak-power-saver-separator' }));

            // ── 4. ACTIVE OPTIMIZATIONS CHECKLIST ──
            const listTitle = new St.Label({
                text: 'OPTIMIZATIONS ACTIVE',
                style_class: 'mak-power-saver-section-title',
            });
            container.add_child(listTitle);

            const checklistBox = new St.BoxLayout({
                vertical: true,
                style_class: 'mak-power-saver-checklist',
            });

            this._chkItems = [
                { id: 'cpu', label: 'CPU Eco Power-Saver Profile', icon: '⚡' },
                { id: 'glass', label: 'Pause Live Window Glass & Blur Shaders', icon: '🪟' },
                { id: 'anim', label: 'Disable UI Animations (Zero Framedrops)', icon: '🎬' },
                { id: 'kbd', label: 'Turn Off Keyboard Backlight', icon: '💡' },
                { id: 'dim', label: 'Dim Display for Extended Reading', icon: '🔅' },
                { id: 'sleep', label: 'Aggressive Display Sleep (3 min)', icon: '💤' },
                { id: 'index', label: 'Pause Background Indexer (localsearch)', icon: '🔍' },
                { id: 'bt', label: 'Disable Idle Bluetooth Radio', icon: '📶' },
            ];

            this._chkWidgets = [];
            for (const item of this._chkItems) {
                const row = new St.BoxLayout({
                    vertical: false,
                    style_class: 'mak-power-saver-check-row',
                    y_align: Clutter.ActorAlign.CENTER,
                });

                const iconLabel = new St.Label({
                    text: item.icon,
                    style_class: 'mak-power-saver-check-icon',
                });
                row.add_child(iconLabel);

                const textLabel = new St.Label({
                    text: item.label,
                    style_class: 'mak-power-saver-check-label',
                    x_expand: true,
                });
                row.add_child(textLabel);

                const statusLabel = new St.Label({
                    text: this._isActive ? '✓ Active' : 'Off',
                    style_class: `mak-power-saver-check-status ${this._isActive ? 'active' : ''}`,
                });
                row.add_child(statusLabel);

                checklistBox.add_child(row);
                this._chkWidgets.push(statusLabel);
            }
            container.add_child(checklistBox);

            this._updateTelemetry();
        }

        _updateTelemetry() {
            try {
                let capacity = 100;
                let status = 'Discharging';
                let wattsStr = '';

                // Read capacity
                if (GLib.file_test('/sys/class/power_supply/BAT0/capacity', GLib.FileTest.EXISTS)) {
                    const [, capBytes] = GLib.file_get_contents('/sys/class/power_supply/BAT0/capacity');
                    capacity = parseInt(new TextDecoder().decode(capBytes).trim(), 10) || 100;
                }
                if (GLib.file_test('/sys/class/power_supply/BAT0/status', GLib.FileTest.EXISTS)) {
                    const [, stBytes] = GLib.file_get_contents('/sys/class/power_supply/BAT0/status');
                    status = new TextDecoder().decode(stBytes).trim();
                }

                // Read voltage and current
                let volts = 0;
                let amps = 0;
                if (GLib.file_test('/sys/class/power_supply/BAT0/voltage_now', GLib.FileTest.EXISTS)) {
                    const [, vBytes] = GLib.file_get_contents('/sys/class/power_supply/BAT0/voltage_now');
                    volts = parseInt(new TextDecoder().decode(vBytes).trim(), 10) / 1000000.0;
                }
                if (GLib.file_test('/sys/class/power_supply/BAT0/current_now', GLib.FileTest.EXISTS)) {
                    const [, aBytes] = GLib.file_get_contents('/sys/class/power_supply/BAT0/current_now');
                    amps = parseInt(new TextDecoder().decode(aBytes).trim(), 10) / 1000000.0;
                }

                if (volts > 0 && amps > 0) {
                    const watts = volts * amps;
                    wattsStr = `${watts.toFixed(1)} W`;
                }

                if (this._telemetryBatLabel) {
                    this._telemetryBatLabel.set_text(`Battery: ${capacity}% (${status})`);
                }
                if (this._telemetryRateLabel && wattsStr) {
                    this._telemetryRateLabel.set_text(wattsStr);
                }
                if (this._telemetrySubLabel) {
                    if (this._isActive) {
                        this._telemetrySubLabel.set_text(`Eco Mode Active · Maximum energy savings engaged`);
                    } else {
                        this._telemetrySubLabel.set_text(`Normal Mode · Click above to engage Eco Saver`);
                    }
                }
            } catch (e) {
                console.warn('[Mak PowerSaver] Telemetry update error:', e.message);
            }
        }

        activate(saveToSettings = true) {
            this._isActive = true;
            this._icon.add_style_class_name('active');
            this._badge.set_visible(true);

            if (this._statusBadge) {
                this._statusBadge.set_text('ACTIVE');
                this._statusBadge.add_style_class_name('active');
            }
            if (this._toggleBtn) {
                this._toggleBtn.add_style_class_name('active');
            }
            if (this._toggleLabel) {
                this._toggleLabel.set_text('Turn Off Eco Mode');
            }
            if (this._chkWidgets) {
                this._chkWidgets.forEach(w => {
                    w.set_text('✓ Active');
                    w.add_style_class_name('active');
                });
            }

            // Capture initial state before applying changes
            this._savedState = {
                powerProfile: 'balanced',
                animations: this._desktopSettings.get_boolean('enable-animations'),
                idleDelay: this._sessionSettings.get_uint('idle-delay'),
                appGlass: true,
                topbarStyle: 'off',
                screenBrightness: '',
                kbdBacklight: '',
                bluetoothBlocked: false,
            };

            // 1. Get current power profile & switch to power-saver
            try {
                const [, stdout] = GLib.spawn_command_line_sync('powerprofilesctl get');
                if (stdout) {
                    this._savedState.powerProfile = new TextDecoder().decode(stdout).trim();
                }
                GLib.spawn_command_line_async('powerprofilesctl set power-saver');
            } catch (e) {
                console.warn('[Mak PowerSaver] Could not set powerprofilesctl:', e.message);
            }

            // 2. Pause live window glass shaders & blur
            try {
                if (this._liquidSettings) {
                    this._savedState.appGlass = this._liquidSettings.get_boolean('enable-application-glass');
                    this._savedState.topbarStyle = this._liquidSettings.get_string('top-bar-style');
                    this._liquidSettings.set_boolean('enable-application-glass', false);
                    this._liquidSettings.set_string('top-bar-style', 'off');
                }
            } catch (e) {
                console.warn('[Mak PowerSaver] Could not pause liquid glass:', e.message);
            }

            // 3. Disable GNOME animations
            try {
                this._desktopSettings.set_boolean('enable-animations', false);
            } catch (e) {}

            // 4. Set Aggressive Screen Sleep (3 minutes = 180 seconds)
            try {
                this._sessionSettings.set_uint('idle-delay', 180);
            } catch (e) {}

            // 5. Turn off keyboard backlight
            try {
                const [, kbdOut] = GLib.spawn_command_line_sync("brightnessctl --device='dell::kbd_backlight' get");
                if (kbdOut) {
                    this._savedState.kbdBacklight = new TextDecoder().decode(kbdOut).trim();
                    GLib.spawn_command_line_async("brightnessctl --device='dell::kbd_backlight' set 0");
                }
            } catch (e) {}

            // 6. Dim screen brightness for reading (25%)
            try {
                const [, briOut] = GLib.spawn_command_line_sync('brightnessctl get');
                if (briOut) {
                    this._savedState.screenBrightness = new TextDecoder().decode(briOut).trim();
                    GLib.spawn_command_line_async('brightnessctl set 25%');
                }
            } catch (e) {}

            // 7. Pause background search indexing
            try {
                GLib.spawn_command_line_async('localsearch pause');
            } catch (e) {}

            // 8. Turn off Bluetooth if not connected to any device
            try {
                const [, btOut] = GLib.spawn_command_line_sync("bluetoothctl info");
                const btText = btOut ? new TextDecoder().decode(btOut) : '';
                if (!btText.includes('Connected: yes')) {
                    GLib.spawn_command_line_async('rfkill block bluetooth');
                    this._savedState.bluetoothBlocked = true;
                }
            } catch (e) {}

            if (saveToSettings && this._settings) {
                this._settings.set_boolean('power-saver-active', true);
            }

            this._updateTelemetry();
            Main.notify('Eco Power Saver Engaged', 'CPU profile locked to power-saver, glass shaders paused, screen dimmed for extended battery life.');
        }

        deactivate(saveToSettings = true) {
            this._isActive = false;
            this._icon.remove_style_class_name('active');
            this._badge.set_visible(false);

            if (this._statusBadge) {
                this._statusBadge.set_text('OFF');
                this._statusBadge.remove_style_class_name('active');
            }
            if (this._toggleBtn) {
                this._toggleBtn.remove_style_class_name('active');
            }
            if (this._toggleLabel) {
                this._toggleLabel.set_text('Turn On Extreme Power Saver');
            }
            if (this._chkWidgets) {
                this._chkWidgets.forEach(w => {
                    w.set_text('Off');
                    w.remove_style_class_name('active');
                });
            }

            // Restore all states cleanly
            const s = this._savedState || {};

            // 1. Restore power profile
            try {
                const prof = s.powerProfile || 'balanced';
                GLib.spawn_command_line_async(`powerprofilesctl set ${prof}`);
            } catch (e) {}

            // 2. Restore liquid glass
            try {
                if (this._liquidSettings) {
                    const prevGlass = (s.appGlass !== undefined) ? s.appGlass : true;
                    this._liquidSettings.set_boolean('enable-application-glass', prevGlass);
                    if (s.topbarStyle) {
                        this._liquidSettings.set_string('top-bar-style', s.topbarStyle);
                    }
                }
            } catch (e) {}

            // 3. Restore animations
            try {
                const prevAnim = (s.animations !== undefined) ? s.animations : true;
                this._desktopSettings.set_boolean('enable-animations', prevAnim);
            } catch (e) {}

            // 4. Restore idle delay
            try {
                const prevDelay = (s.idleDelay !== undefined) ? s.idleDelay : 0;
                this._sessionSettings.set_uint('idle-delay', prevDelay);
            } catch (e) {}

            // 5. Restore keyboard backlight
            try {
                if (s.kbdBacklight) {
                    GLib.spawn_command_line_async(`brightnessctl --device='dell::kbd_backlight' set ${s.kbdBacklight}`);
                }
            } catch (e) {}

            // 6. Restore screen brightness
            try {
                if (s.screenBrightness) {
                    GLib.spawn_command_line_async(`brightnessctl set ${s.screenBrightness}`);
                }
            } catch (e) {}

            // 7. Resume search indexing
            try {
                GLib.spawn_command_line_async('localsearch resume');
            } catch (e) {}

            // 8. Restore Bluetooth
            try {
                if (s.bluetoothBlocked) {
                    GLib.spawn_command_line_async('rfkill unblock bluetooth');
                }
            } catch (e) {}

            this._savedState = null;

            if (saveToSettings && this._settings) {
                this._settings.set_boolean('power-saver-active', false);
            }

            this._updateTelemetry();
            Main.notify('Eco Power Saver Restored', 'Standard performance profile, UI animations, and glass effects restored.');
        }

        destroy() {
            if (this._telemetryTimerId) {
                GLib.source_remove(this._telemetryTimerId);
                this._telemetryTimerId = 0;
            }
            super.destroy();
        }
    }
);
