// SPDX-License-Identifier: GPL-3.0-or-later
// Mak Topbar Caffeine / Amphetamine (Keep-Awake) Indicator & Controller
// Isolated native GNOME SessionManager & ScreenSaver inhibitor with duration presets

import Clutter from 'gi://Clutter';
import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import GObject from 'gi://GObject';
import St from 'gi://St';

import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import * as PanelMenu from 'resource:///org/gnome/shell/ui/panelMenu.js';
import * as PopupMenu from 'resource:///org/gnome/shell/ui/popupMenu.js';

const _uid = Math.floor(Math.random() * 10000000);

export const CaffeineButton = GObject.registerClass(
    { GTypeName: `MakCaffeineButton_${_uid}` },
    class CaffeineButton extends PanelMenu.Button {
        _init(extension) {
            super._init(0.5, 'MakCaffeine', false);
            this._extension = extension;
            this._settings = extension.getSettings('org.gnome.shell.extensions.mak');
            this.add_style_class_name('mak-caffeine-button');

            this._isActive = false;
            this._durationMinutes = 0; // 0 = indefinite
            this._expireTimestamp = 0;
            this._timerId = 0;
            this._sessionCookie = 0;
            this._screenSaverCookie = 0;

            // Load icons
            this._iconOff = Gio.icon_new_for_string(`${extension.path}/icons/caffeine-off-symbolic.svg`);
            this._iconOn = Gio.icon_new_for_string(`${extension.path}/icons/caffeine-on-symbolic.svg`);

            // Panel Button Layout: Icon + Countdown Badge
            const btnBox = new St.BoxLayout({
                vertical: false,
                style_class: 'mak-caffeine-panel-box',
                y_align: Clutter.ActorAlign.CENTER,
            });

            this._icon = new St.Icon({
                gicon: this._iconOff,
                style_class: 'system-status-icon mak-caffeine-panel-icon',
                y_align: Clutter.ActorAlign.CENTER,
            });
            btnBox.add_child(this._icon);

            this._badge = new St.Label({
                text: '',
                style_class: 'mak-caffeine-panel-badge',
                y_align: Clutter.ActorAlign.CENTER,
                visible: false,
            });
            btnBox.add_child(this._badge);

            this.add_child(btnBox);

            // Configure Popup Menu Container
            this.menu.box.add_style_class_name('mak-caffeine-menu');

            // Build Popup Menu UI
            this._buildPopup();

            // Restore state if previously active
            if (this._settings && this._settings.get_boolean('caffeine-active')) {
                const dur = this._settings.get_int('caffeine-duration');
                this.activate(dur);
            }
        }

        _buildPopup() {
            this.menu.removeAll();

            const container = new St.BoxLayout({
                vertical: true,
                style_class: 'mak-caffeine-container',
            });
            this.menu.box.add_child(container);

            // ── 1. HEADER ──
            const headerBox = new St.BoxLayout({
                vertical: false,
                style_class: 'mak-caffeine-header',
                y_align: Clutter.ActorAlign.CENTER,
            });

            const titleBox = new St.BoxLayout({
                vertical: true,
                style_class: 'mak-caffeine-title-box',
                x_expand: true,
            });

            const title = new St.Label({
                text: 'Caffeine',
                style_class: 'mak-caffeine-header-title',
            });
            titleBox.add_child(title);

            const subtitle = new St.Label({
                text: this._isActive ? 'Screen & system keep-awake active' : 'Sleep and display dimming allowed',
                style_class: 'mak-caffeine-header-sub',
            });
            this._statusSubLabel = subtitle;
            titleBox.add_child(subtitle);
            headerBox.add_child(titleBox);

            // Status Badge
            this._headerBadge = new St.Label({
                text: this._isActive ? 'ON' : 'OFF',
                style_class: this._isActive ? 'mak-caffeine-status-badge active' : 'mak-caffeine-status-badge',
                y_align: Clutter.ActorAlign.CENTER,
            });
            headerBox.add_child(this._headerBadge);
            container.add_child(headerBox);

            // ── 2. SEPARATOR ──
            const sep = new St.Widget({ style_class: 'mak-caffeine-separator' });
            container.add_child(sep);

            // ── 3. DURATION PRESET OPTIONS ──
            const presetsBox = new St.BoxLayout({
                vertical: true,
                style_class: 'mak-caffeine-presets-box',
            });

            const presets = [
                { label: 'Indefinitely', minutes: 0, icon: 'media-playback-start-symbolic' },
                { label: '15 Minutes', minutes: 15, icon: 'alarm-symbolic' },
                { label: '30 Minutes', minutes: 30, icon: 'alarm-symbolic' },
                { label: '1 Hour', minutes: 60, icon: 'alarm-symbolic' },
                { label: '2 Hours', minutes: 120, icon: 'alarm-symbolic' },
                { label: '4 Hours', minutes: 240, icon: 'alarm-symbolic' },
            ];

            this._presetButtons = [];

            presets.forEach(preset => {
                const row = new St.Button({
                    style_class: 'mak-caffeine-preset-row',
                    can_focus: true,
                    reactive: true,
                    track_hover: true,
                    x_expand: true,
                });

                const rowContent = new St.BoxLayout({
                    vertical: false,
                    style_class: 'mak-caffeine-preset-content',
                    y_align: Clutter.ActorAlign.CENTER,
                });

                const rowIcon = new St.Icon({
                    icon_name: preset.icon,
                    style_class: 'mak-caffeine-preset-icon',
                    y_align: Clutter.ActorAlign.CENTER,
                });
                rowContent.add_child(rowIcon);

                const rowLabel = new St.Label({
                    text: preset.label,
                    style_class: 'mak-caffeine-preset-label',
                    x_expand: true,
                    y_align: Clutter.ActorAlign.CENTER,
                });
                rowContent.add_child(rowLabel);

                const checkIcon = new St.Icon({
                    icon_name: 'emblem-ok-symbolic',
                    style_class: 'mak-caffeine-preset-check',
                    y_align: Clutter.ActorAlign.CENTER,
                    visible: this._isActive && this._durationMinutes === preset.minutes,
                });
                rowContent.add_child(checkIcon);

                row.set_child(rowContent);

                row.connect('clicked', () => {
                    this.activate(preset.minutes);
                    this.menu.close();
                });

                this._presetButtons.push({ preset, row, checkIcon });
                presetsBox.add_child(row);
            });

            container.add_child(presetsBox);

            // ── 4. DEACTIVATE BUTTON ──
            const toggleBtn = new St.Button({
                style_class: this._isActive ? 'mak-caffeine-toggle-btn active' : 'mak-caffeine-toggle-btn',
                can_focus: true,
                x_expand: true,
            });
            const toggleLabel = new St.Label({
                text: this._isActive ? 'Deactivate Caffeine' : 'Activate (Indefinite)',
                style_class: 'mak-caffeine-toggle-label',
                x_align: Clutter.ActorAlign.CENTER,
                y_align: Clutter.ActorAlign.CENTER,
            });
            toggleBtn.set_child(toggleLabel);
            toggleBtn.connect('clicked', () => {
                if (this._isActive) {
                    this.deactivate();
                } else {
                    this.activate(0);
                }
                this.menu.close();
            });
            container.add_child(toggleBtn);
        }

        activate(durationMinutes = 0) {
            this._isActive = true;
            this._durationMinutes = durationMinutes;

            if (this._settings) {
                this._settings.set_boolean('caffeine-active', true);
                this._settings.set_int('caffeine-duration', durationMinutes);
            }

            // Inhibit GNOME Session Manager
            this._inhibitSession();

            // Set up timer if timed duration
            if (durationMinutes > 0) {
                this._expireTimestamp = Date.now() + durationMinutes * 60 * 1000;
                this._startCountdownTimer();
            } else {
                this._expireTimestamp = 0;
                this._stopCountdownTimer();
                this._badge.set_text('');
                this._badge.visible = false;
            }

            this._updateUI();
        }

        deactivate() {
            this._isActive = false;
            this._durationMinutes = 0;
            this._expireTimestamp = 0;

            if (this._settings) {
                this._settings.set_boolean('caffeine-active', false);
                this._settings.set_int('caffeine-duration', 0);
            }

            this._stopCountdownTimer();
            this._uninhibitSession();
            this._updateUI();
        }

        toggle() {
            if (this._isActive) {
                this.deactivate();
            } else {
                this.activate(0);
            }
        }

        _inhibitSession() {
            // 1. org.gnome.SessionManager Inhibit
            try {
                Gio.DBus.session.call(
                    'org.gnome.SessionManager',
                    '/org/gnome/SessionManager',
                    'org.gnome.SessionManager',
                    'Inhibit',
                    new GLib.Variant('(susu)', ['Mak Caffeine', 0, 'Mak Keep-Awake Active', 12 /* idle + suspend */]),
                    null,
                    Gio.DBusCallFlags.NONE,
                    -1,
                    null,
                    (conn, res) => {
                        try {
                            const reply = conn.call_finish(res);
                            const [cookie] = reply.deepUnpack();
                            this._sessionCookie = cookie;
                        } catch (e) {
                            console.warn('[Mak Caffeine] SessionManager Inhibit error:', e);
                        }
                    }
                );
            } catch (err) {
                console.warn('[Mak Caffeine] Could not call SessionManager.Inhibit:', err);
            }

            // 2. org.freedesktop.ScreenSaver Inhibit (backup for media/display players)
            try {
                Gio.DBus.session.call(
                    'org.freedesktop.ScreenSaver',
                    '/org/freedesktop/ScreenSaver',
                    'org.freedesktop.ScreenSaver',
                    'Inhibit',
                    new GLib.Variant('(ss)', ['Mak Caffeine', 'Keep Display Awake']),
                    null,
                    Gio.DBusCallFlags.NONE,
                    -1,
                    null,
                    (conn, res) => {
                        try {
                            const reply = conn.call_finish(res);
                            const [cookie] = reply.deepUnpack();
                            this._screenSaverCookie = cookie;
                        } catch (e) {
                            // Non-fatal
                        }
                    }
                );
            } catch (err) {}
        }

        _uninhibitSession() {
            if (this._sessionCookie) {
                const cookie = this._sessionCookie;
                this._sessionCookie = 0;
                try {
                    Gio.DBus.session.call(
                        'org.gnome.SessionManager',
                        '/org/gnome/SessionManager',
                        'org.gnome.SessionManager',
                        'Uninhibit',
                        new GLib.Variant('(u)', [cookie]),
                        null,
                        Gio.DBusCallFlags.NONE,
                        -1,
                        null,
                        null
                    );
                } catch (e) {}
            }

            if (this._screenSaverCookie) {
                const cookie = this._screenSaverCookie;
                this._screenSaverCookie = 0;
                try {
                    Gio.DBus.session.call(
                        'org.freedesktop.ScreenSaver',
                        '/org/freedesktop/ScreenSaver',
                        'org.freedesktop.ScreenSaver',
                        'UnInhibit',
                        new GLib.Variant('(u)', [cookie]),
                        null,
                        Gio.DBusCallFlags.NONE,
                        -1,
                        null,
                        null
                    );
                } catch (e) {}
            }
        }

        _startCountdownTimer() {
            this._stopCountdownTimer();
            this._updateCountdownBadge();

            this._timerId = GLib.timeout_add_seconds(GLib.PRIORITY_DEFAULT, 1, () => {
                if (!this._isActive || this._expireTimestamp === 0) {
                    this._timerId = 0;
                    return GLib.SOURCE_REMOVE;
                }

                const remainingMs = this._expireTimestamp - Date.now();
                if (remainingMs <= 0) {
                    this._timerId = 0;
                    this.deactivate();
                    Main.notify('Mak Caffeine', 'Keep-awake duration expired. Sleep mode restored.');
                    return GLib.SOURCE_REMOVE;
                }

                this._updateCountdownBadge();
                return GLib.SOURCE_CONTINUE;
            });
        }

        _stopCountdownTimer() {
            if (this._timerId) {
                GLib.Source.remove(this._timerId);
                this._timerId = 0;
            }
            if (this._badge) {
                this._badge.visible = false;
                this._badge.set_text('');
            }
        }

        _updateCountdownBadge() {
            if (!this._badge || !this._isActive || this._expireTimestamp === 0) return;
            const remainingSec = Math.max(0, Math.floor((this._expireTimestamp - Date.now()) / 1000));
            const min = Math.floor(remainingSec / 60);
            const sec = remainingSec % 60;
            const hr = Math.floor(min / 60);

            let txt = '';
            if (hr > 0) {
                txt = `${hr}h ${min % 60}m`;
            } else if (min > 0) {
                txt = `${min}m`;
            } else {
                txt = `${sec}s`;
            }

            this._badge.set_text(txt);
            this._badge.visible = true;
        }

        _updateUI() {
            if (!this._icon) return;

            if (this._isActive) {
                this._icon.gicon = this._iconOn;
                this._icon.add_style_class_name('active');
            } else {
                this._icon.gicon = this._iconOff;
                this._icon.remove_style_class_name('active');
                this._badge.visible = false;
            }

            // Rebuild popup contents to reflect checkmarks & labels
            if (this.menu && this.menu.isOpen) {
                this._buildPopup();
            }
        }

        destroy() {
            this._stopCountdownTimer();
            this._uninhibitSession();
            super.destroy();
        }
    }
);
