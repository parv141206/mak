// SPDX-License-Identifier: GPL-3.0-or-later
// Mak macOS Battery Indicator: Authentic Apple battery capsule with color-coding and inside/side percentage

import Cairo from 'cairo';
import Clutter from 'gi://Clutter';
import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import GObject from 'gi://GObject';
import Pango from 'gi://Pango';
import PangoCairo from 'gi://PangoCairo';
import St from 'gi://St';
import UPower from 'gi://UPowerGlib';

import * as Main from 'resource:///org/gnome/shell/ui/main.js';

const UPOWER_BUS_NAME = 'org.freedesktop.UPower';
const UPOWER_OBJECT_PATH = '/org/freedesktop/UPower/devices/DisplayDevice';

const DisplayDeviceInterface = `
<node>
  <interface name="org.freedesktop.UPower.Device">
    <property name="Percentage" type="d" access="read"/>
    <property name="State" type="u" access="read"/>
    <property name="IsPresent" type="b" access="read"/>
    <property name="IconName" type="s" access="read"/>
  </interface>
</node>`;

const PowerManagerProxy = Gio.DBusProxy.makeProxyWrapper(DisplayDeviceInterface);

const _uid = Math.floor(Math.random() * 10000000);

export const MacBatteryWidget = GObject.registerClass(
    { GTypeName: `MakMacBatteryWidget_${_uid}` },
    class MacBatteryWidget extends St.BoxLayout {
        _init(extension) {
            super._init({
                vertical: false,
                style_class: 'mak-mac-battery-box',
                y_align: Clutter.ActorAlign.CENTER,
                reactive: true,
            });

            this._extension = extension;
            this._settings = extension.getSettings('org.gnome.shell.extensions.mak');

            this._percentage = 100;
            this._state = UPower.DeviceState.DISCHARGING;
            this._isPresent = true;
            this._mode = 'inside'; // 'inside', 'side', 'hidden'
            this._colored = true;

            this._loadSettings();

            // 1. Side percentage label (visible in 'side' mode)
            this._sideLabel = new St.Label({
                text: '100%',
                style_class: 'mak-mac-battery-side-label',
                y_align: Clutter.ActorAlign.CENTER,
                visible: this._mode === 'side',
            });
            this.add_child(this._sideLabel);

            // 2. Battery Canvas (Custom Cairo Drawing)
            this._canvas = new St.DrawingArea({
                style_class: 'mak-mac-battery-canvas',
                y_align: Clutter.ActorAlign.CENTER,
            });
            this._updateCanvasSize();

            this._canvas.connect('repaint', (area) => this._onRepaint(area));
            this.add_child(this._canvas);

            // 3. Connect to UPower DBus
            this._proxy = new PowerManagerProxy(
                Gio.DBus.system,
                UPOWER_BUS_NAME,
                UPOWER_OBJECT_PATH,
                (proxy, error) => {
                    if (error) {
                        console.warn('[Mak Battery] UPower proxy error:', error);
                    } else {
                        this._proxy.connect('g-properties-changed', () => this._syncPower());
                        this._syncPower();
                    }
                }
            );

            // 4. Connect to settings changes
            this._settingsChangedId = this._settings.connect('changed', (s, key) => {
                if (key === 'battery-percentage-mode' || key === 'battery-colored') {
                    this._loadSettings();
                    this._updateCanvasSize();
                    this._syncPower();
                }
            });
        }

        _loadSettings() {
            if (this._settings) {
                this._mode = this._settings.get_string('battery-percentage-mode') || 'inside';
                this._colored = this._settings.get_boolean('battery-colored');
            }
        }

        _updateCanvasSize() {
            if (this._mode === 'inside') {
                this._canvas.set_size(36, 16);
            } else {
                this._canvas.set_size(26, 14);
            }
            if (this._sideLabel) {
                this._sideLabel.visible = this._mode === 'side';
            }
            this._canvas.queue_repaint();
        }

        _syncPower() {
            if (!this._proxy) return;

            this._isPresent = this._proxy.IsPresent !== undefined ? this._proxy.IsPresent : true;
            this._percentage = this._proxy.Percentage !== undefined ? this._proxy.Percentage : 100;
            this._state = this._proxy.State !== undefined ? this._proxy.State : UPower.DeviceState.DISCHARGING;

            this.visible = this._isPresent;

            if (this._sideLabel) {
                const isCharging = this._isCharging();
                const prefix = isCharging ? '⚡ ' : '';
                this._sideLabel.set_text(`${prefix}${Math.round(this._percentage)}%`);
            }

            this._canvas.queue_repaint();
        }

        _isCharging() {
            return (
                this._state === UPower.DeviceState.CHARGING ||
                this._state === UPower.DeviceState.FULLY_CHARGED ||
                this._state === UPower.DeviceState.PENDING_CHARGE
            );
        }

        _drawRoundedRect(cr, x, y, width, height, radius) {
            const r = Math.min(radius, width / 2, height / 2);
            cr.newSubPath();
            cr.arc(x + width - r, y + r, r, -Math.PI / 2, 0);
            cr.arc(x + width - r, y + height - r, r, 0, Math.PI / 2);
            cr.arc(x + r, y + height - r, r, Math.PI / 2, Math.PI);
            cr.arc(x + r, y + r, r, Math.PI, 3 * Math.PI / 2);
            cr.closePath();
        }

        _onRepaint(area) {
            const cr = area.get_context();
            const [w, h] = area.get_surface_size();

            // Clear
            cr.save();
            cr.setOperator(Cairo.Operator.CLEAR);
            cr.paint();
            cr.restore();

            const isInside = this._mode === 'inside';
            const isCharging = this._isCharging();
            const pct = Math.max(0, Math.min(100, this._percentage));

            // Geometry
            const bodyW = isInside ? 30 : 21;
            const bodyH = isInside ? 14 : 12;
            const bodyX = 1;
            const bodyY = Math.round((h - bodyH) / 2);
            const cornerRadius = isInside ? 4.0 : 3.5;

            const tipW = 2;
            const tipH = isInside ? 6 : 5;
            const tipX = bodyX + bodyW + 1.2;
            const tipY = Math.round((h - tipH) / 2);

            // Determine Fill Color
            let fillR = 1.0, fillG = 1.0, fillB = 1.0; // Default White

            if (this._colored) {
                if (isCharging) {
                    // Apple Green (#30d158)
                    fillR = 48 / 255;
                    fillG = 209 / 255;
                    fillB = 88 / 255;
                } else if (pct <= 20) {
                    // Apple Red (#ff453a)
                    fillR = 255 / 255;
                    fillG = 69 / 255;
                    fillB = 58 / 255;
                } else if (pct <= 30) {
                    // Apple Orange/Yellow (#ff9f0a)
                    fillR = 255 / 255;
                    fillG = 159 / 255;
                    fillB = 10 / 255;
                } else {
                    // Normal Solid White
                    fillR = 1.0;
                    fillG = 1.0;
                    fillB = 1.0;
                }
            }

            // 1. Terminal Nipple (Right Tip)
            this._drawRoundedRect(cr, tipX, tipY, tipW, tipH, 1.0);
            cr.setSourceRGBA(1.0, 1.0, 1.0, 0.45);
            cr.fill();

            // 2. Battery Body Unfilled Background (Translucent Grey)
            this._drawRoundedRect(cr, bodyX, bodyY, bodyW, bodyH, cornerRadius);
            cr.setSourceRGBA(1.0, 1.0, 1.0, 0.22);
            cr.fill();

            // 3. Proportional Fill Level
            const fillWidth = Math.max(isInside ? 4 : 2, Math.round(bodyW * (pct / 100)));
            cr.save();
            this._drawRoundedRect(cr, bodyX, bodyY, bodyW, bodyH, cornerRadius);
            cr.clip();

            cr.rectangle(bodyX, bodyY, fillWidth, bodyH);
            cr.setSourceRGBA(fillR, fillG, fillB, 0.95);
            cr.fill();
            cr.restore();

            // 4. Outer Shell Stroke Border
            this._drawRoundedRect(cr, bodyX + 0.5, bodyY + 0.5, bodyW - 1, bodyH - 1, cornerRadius);
            cr.setSourceRGBA(1.0, 1.0, 1.0, 0.38);
            cr.setLineWidth(1.0);
            cr.stroke();

            // 5. Draw Percentage Text INSIDE the Battery Capsule (Image 2 style)
            if (isInside) {
                const textStr = String(Math.round(pct));
                const layout = PangoCairo.create_layout(cr);
                const fontDesc = Pango.FontDescription.from_string('sans-serif bold 8.5');
                layout.set_font_description(fontDesc);
                layout.set_text(textStr, -1);

                const [textW, textH] = layout.get_pixel_size();
                const textX = bodyX + (bodyW - textW) / 2;
                const textY = bodyY + (bodyH - textH) / 2;

                // Contrast: If fill is full/bright white and covers text, use black; otherwise white
                const isUnderFill = fillWidth >= (textX + textW / 2);
                let textR = 1.0, textG = 1.0, textB = 1.0; // White text

                if (isUnderFill && !this._colored) {
                    textR = 0.0; textG = 0.0; textB = 0.0; // Black text on white fill
                } else if (isUnderFill && isCharging) {
                    textR = 0.0; textG = 0.0; textB = 0.0; // Black text on bright green fill
                }

                // Draw subtle shadow for crisp readability across gradients
                cr.save();
                cr.moveTo(textX + 0.5, textY + 0.5);
                cr.setSourceRGBA(0, 0, 0, 0.5);
                PangoCairo.show_layout(cr, layout);
                cr.restore();

                cr.moveTo(textX, textY);
                cr.setSourceRGBA(textR, textG, textB, 1.0);
                PangoCairo.show_layout(cr, layout);
            }
        }

        destroy() {
            if (this._settingsChangedId) {
                this._settings.disconnect(this._settingsChangedId);
                this._settingsChangedId = 0;
            }
            if (this._proxy) {
                this._proxy = null;
            }
            super.destroy();
        }
    }
);

export class MacBatteryController {
    constructor(extension) {
        this._extension = extension;
        this._settings = extension.getSettings('org.gnome.shell.extensions.mak');
        this._widget = null;
        this._origIndicatorVisible = null;
        this._origLabelVisible = null;
    }

    enable() {
        if (this._widget) return;

        try {
            this._widget = new MacBatteryWidget(this._extension);

            const quickSettings = Main.panel.statusArea.quickSettings;
            const systemIndicator = quickSettings?._system;

            if (systemIndicator) {
                // Hide default GNOME battery icon & label
                if (systemIndicator._indicator) {
                    this._origIndicatorVisible = systemIndicator._indicator.visible;
                    systemIndicator._indicator.set_style('width: 0px; height: 0px; opacity: 0;');
                    systemIndicator._indicator.visible = false;
                }
                if (systemIndicator._percentageLabel) {
                    this._origLabelVisible = systemIndicator._percentageLabel.visible;
                    systemIndicator._percentageLabel.set_style('width: 0px; height: 0px; opacity: 0;');
                    systemIndicator._percentageLabel.visible = false;
                }

                // Add macOS battery widget directly into system status indicator
                systemIndicator.add_child(this._widget);
            } else {
                // Fallback: Add as panel button
                Main.panel.addToStatusArea('MakBattery', this._widget, 2, 'right');
            }
        } catch (err) {
            console.warn('[Mak Battery] Could not enable MacBattery:', err);
        }
    }

    disable() {
        if (this._widget) {
            const parent = this._widget.get_parent();
            if (parent) {
                parent.remove_child(this._widget);
            }
            try { this._widget.destroy(); } catch (e) {}
            this._widget = null;
        }

        // Restore default GNOME indicators
        const quickSettings = Main.panel.statusArea.quickSettings;
        const systemIndicator = quickSettings?._system;
        if (systemIndicator) {
            if (systemIndicator._indicator) {
                systemIndicator._indicator.set_style('');
                systemIndicator._indicator.visible = true;
            }
            if (systemIndicator._percentageLabel) {
                systemIndicator._percentageLabel.set_style('');
                systemIndicator._percentageLabel.visible = true;
            }
        }
    }
}
