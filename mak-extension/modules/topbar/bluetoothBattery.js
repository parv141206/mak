// SPDX-License-Identifier: GPL-3.0-or-later
// Mak Bluetooth Battery Indicator for Top Bar

import Clutter from 'gi://Clutter';
import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import GObject from 'gi://GObject';
import St from 'gi://St';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import * as PanelMenu from 'resource:///org/gnome/shell/ui/panelMenu.js';
import { gettext as _ } from 'resource:///org/gnome/shell/extensions/extension.js';

let GnomeBluetooth = null;
try {
    GnomeBluetooth = (await import('gi://GnomeBluetooth?version=3.0')).default;
} catch (e) {
    console.warn('[Mak BluetoothBattery] Could not import GnomeBluetooth 3.0:', e.message);
}

export const BluetoothBatteryButton = GObject.registerClass(
    { GTypeName: 'MakBluetoothBatteryButton' },
    class BluetoothBatteryButton extends PanelMenu.Button {
        _init(extension) {
            super._init(0.5, 'Mak Bluetooth Battery', false);
            this._extension = extension;
            this._settings = extension.getSettings();

            // Panel icon and mini battery indicator container
            this.panelBox = new St.BoxLayout({
                vertical: false,
                style_class: 'mak-bt-panel-box',
                x_align: Clutter.ActorAlign.CENTER,
                y_align: Clutter.ActorAlign.CENTER,
            });
            this.add_child(this.panelBox);

            this.icon = new St.Icon({
                icon_name: 'bluetooth-active-symbolic',
                style_class: 'system-status-icon mak-bt-icon',
                x_align: Clutter.ActorAlign.CENTER,
                y_align: Clutter.ActorAlign.CENTER,
            });
            this.panelBox.add_child(this.icon);

            this.batteryLabel = new St.Label({
                text: '',
                style_class: 'mak-bt-panel-label',
                y_align: Clutter.ActorAlign.CENTER,
                visible: false,
            });
            this.panelBox.add_child(this.batteryLabel);

            this.panelBatteryBarBg = new St.BoxLayout({
                style_class: 'mak-bt-panel-bar-bg',
                x_align: Clutter.ActorAlign.CENTER,
                y_align: Clutter.ActorAlign.CENTER,
                visible: false,
            });
            this.panelBatteryBarFill = new St.BoxLayout({
                style_class: 'mak-bt-panel-bar-fill',
            });
            this.panelBatteryBarBg.add_child(this.panelBatteryBarFill);
            this.panelBox.add_child(this.panelBatteryBarBg);

            // Dropdown menu styling
            this.menu.box.add_style_class_name('mak-bt-menu');

            this.mainBox = new St.BoxLayout({
                vertical: true,
                style_class: 'mak-bt-container',
            });
            this.menu.box.add_child(this.mainBox);

            // Header
            const headerBox = new St.BoxLayout({
                vertical: false,
                style_class: 'mak-bt-header',
            });
            const headerLabel = new St.Label({
                text: _('Bluetooth Devices'),
                x_expand: true,
                y_align: Clutter.ActorAlign.CENTER,
                style_class: 'mak-bt-header-label',
            });
            headerBox.add_child(headerLabel);
            this.mainBox.add_child(headerBox);

            // Devices list container
            this.devicesBox = new St.BoxLayout({
                vertical: true,
                style_class: 'mak-bt-devices',
            });
            this.mainBox.add_child(this.devicesBox);

            this._deviceSignals = [];
            this._destroyed = false;
            this._updateIdleId = null;
            this._visibilityIdleId = null;
            this._itemsChangedId = null;

            if (GnomeBluetooth) {
                try {
                    this._client = new GnomeBluetooth.Client();
                    this._devicesModel = this._client.get_devices();
                    if (this._devicesModel) {
                        this._itemsChangedId = this._devicesModel.connect('items-changed', () => {
                            this._queueDeviceUpdate();
                        });
                    }
                } catch (e) {
                    console.warn('[Mak BluetoothBattery] Error initializing GnomeBluetooth Client:', e.message);
                }
            }

            // Periodic backup check
            this._backupTimeoutId = GLib.timeout_add_seconds(GLib.PRIORITY_DEFAULT, 10, () => {
                this._updateDevices();
                return GLib.SOURCE_CONTINUE;
            });

            this._queueDeviceUpdate();
        }

        _queueDeviceUpdate() {
            if (this._destroyed || this._updateIdleId) return;
            this._updateIdleId = GLib.idle_add(GLib.PRIORITY_DEFAULT_IDLE, () => {
                this._updateIdleId = null;
                if (!this._destroyed) {
                    this._updateDevices();
                }
                return GLib.SOURCE_REMOVE;
            });
        }

        _updateDevices() {
            if (this._destroyed) return;

            // Disconnect old signals
            if (this._deviceSignals) {
                for (const sig of this._deviceSignals) {
                    try {
                        sig.obj.disconnect(sig.id);
                    } catch (e) {}
                }
            }
            this._deviceSignals = [];

            if (!this._devicesModel) {
                this._queueVisibility(false);
                return;
            }

            const connectedDevices = [];
            const nItems = this._devicesModel.get_n_items();

            for (let i = 0; i < nItems; i++) {
                const dev = this._devicesModel.get_item(i);
                if (!dev) continue;

                const watchedProps = ['connected', 'battery-percentage', 'battery-level', 'alias'];
                for (const prop of watchedProps) {
                    const id = dev.connect(`notify::${prop}`, () => this._queueDeviceUpdate());
                    this._deviceSignals.push({ obj: dev, id: id });
                }

                if (dev.connected) {
                    connectedDevices.push(dev);
                }
            }

            let lowestBattery = null;
            for (const dev of connectedDevices) {
                const battery = dev.battery_percentage !== undefined ? dev.battery_percentage : dev['battery-percentage'];
                if (battery !== undefined && battery !== null && battery >= 0) {
                    if (lowestBattery === null || battery < lowestBattery) {
                        lowestBattery = battery;
                    }
                }
            }

            if (lowestBattery !== null && lowestBattery >= 0) {
                this.batteryLabel.set_text(`${lowestBattery}%`);
                this.batteryLabel.visible = true;
                this.panelBatteryBarBg.visible = true;

                const fillWidth = Math.max(1, Math.round((lowestBattery / 100) * 16));
                this.panelBatteryBarFill.set_style(`width: ${fillWidth}px;`);

                this.panelBatteryBarFill.remove_style_class_name('mak-bt-fill-green');
                this.panelBatteryBarFill.remove_style_class_name('mak-bt-fill-orange');
                this.panelBatteryBarFill.remove_style_class_name('mak-bt-fill-red');

                if (lowestBattery > 50) {
                    this.panelBatteryBarFill.add_style_class_name('mak-bt-fill-green');
                } else if (lowestBattery > 20) {
                    this.panelBatteryBarFill.add_style_class_name('mak-bt-fill-orange');
                } else {
                    this.panelBatteryBarFill.add_style_class_name('mak-bt-fill-red');
                }
            } else {
                this.batteryLabel.visible = false;
                this.panelBatteryBarBg.visible = false;
            }

            this.devicesBox.destroy_all_children();

            if (connectedDevices.length === 0) {
                this._queueVisibility(false);
                const noDev = new St.Label({
                    text: _('No connected devices'),
                    style_class: 'mak-bt-empty',
                });
                this.devicesBox.add_child(noDev);
                return;
            }

            this._queueVisibility(true);

            for (const dev of connectedDevices) {
                const name = dev.alias || dev.name || _('Unknown Device');
                const iconName = dev.icon || 'bluetooth-active-symbolic';
                const battery = dev.battery_percentage !== undefined ? dev.battery_percentage : dev['battery-percentage'];

                const itemBox = new St.BoxLayout({
                    vertical: false,
                    style_class: 'mak-bt-device-item',
                });

                const icon = new St.Icon({
                    icon_name: iconName,
                    style_class: 'mak-bt-device-icon',
                });
                itemBox.add_child(icon);

                const label = new St.Label({
                    text: name,
                    x_expand: true,
                    y_align: Clutter.ActorAlign.CENTER,
                    style_class: 'mak-bt-device-label',
                });
                itemBox.add_child(label);

                if (battery !== undefined && battery >= 0) {
                    const batteryBox = new St.BoxLayout({
                        vertical: false,
                        style_class: 'mak-bt-battery-box',
                    });

                    const progressBarContainer = new St.BoxLayout({
                        style_class: 'mak-bt-progress-bg',
                        y_align: Clutter.ActorAlign.CENTER,
                        x_expand: false,
                    });

                    const progressBarFill = new St.BoxLayout({
                        style_class: 'mak-bt-progress-fill',
                    });
                    progressBarFill.set_style(`width: ${Math.max(1, (battery / 100) * 60)}px;`);

                    progressBarContainer.add_child(progressBarFill);
                    batteryBox.add_child(progressBarContainer);

                    const batteryLabel = new St.Label({
                        text: `${battery}%`,
                        y_align: Clutter.ActorAlign.CENTER,
                        style_class: 'mak-bt-battery-text',
                    });
                    batteryBox.add_child(batteryLabel);

                    itemBox.add_child(batteryBox);
                }

                this.devicesBox.add_child(itemBox);
            }
        }

        _queueVisibility(visible) {
            if (this._destroyed) return;
            if (this._visibilityIdleId) {
                GLib.Source.remove(this._visibilityIdleId);
                this._visibilityIdleId = null;
            }
            this._visibilityIdleId = GLib.idle_add(GLib.PRIORITY_DEFAULT_IDLE, () => {
                this._visibilityIdleId = null;
                if (!this._destroyed) {
                    if (visible) this.show();
                    else this.hide();
                }
                return GLib.SOURCE_REMOVE;
            });
        }

        destroy() {
            this._destroyed = true;
            if (this._updateIdleId) {
                GLib.Source.remove(this._updateIdleId);
                this._updateIdleId = null;
            }
            if (this._visibilityIdleId) {
                GLib.Source.remove(this._visibilityIdleId);
                this._visibilityIdleId = null;
            }
            if (this._backupTimeoutId) {
                GLib.Source.remove(this._backupTimeoutId);
                this._backupTimeoutId = null;
            }
            if (this._deviceSignals) {
                for (const sig of this._deviceSignals) {
                    try { sig.obj.disconnect(sig.id); } catch (e) {}
                }
                this._deviceSignals = [];
            }
            if (this._devicesModel && this._itemsChangedId) {
                try { this._devicesModel.disconnect(this._itemsChangedId); } catch (e) {}
                this._itemsChangedId = null;
            }
            super.destroy();
        }
    }
);
