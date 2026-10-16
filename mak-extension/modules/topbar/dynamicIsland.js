// SPDX-License-Identifier: GPL-3.0-or-later
// Mak Dynamic Island: macOS-inspired intelligent live capsule for flat screens with attached topbar
// Supports live MPRIS Media playback, animated waveform, expandable player card, and volume/brightness HUD

import Clutter from 'gi://Clutter';
import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import GObject from 'gi://GObject';
import Pango from 'gi://Pango';
import St from 'gi://St';

import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import * as Mpris from 'resource:///org/gnome/shell/ui/mpris.js';

const COMPACT_WIDTH = 220;
const COMPACT_HEIGHT = 32;
const HUD_WIDTH = 260;
const HUD_HEIGHT = 34;
const EXPANDED_WIDTH = 380;
const EXPANDED_HEIGHT = 86;

const _uid = Math.floor(Math.random() * 10000000);

export const DynamicIsland = GObject.registerClass(
    { GTypeName: `MakDynamicIsland_${_uid}` },
    class DynamicIsland extends St.Widget {
        _init(extension) {
            super._init({
                style_class: 'mak-island-container',
                reactive: true,
                track_hover: true,
                can_focus: true,
            });

            this._extension = extension;
            this._settings = extension.getSettings('org.gnome.shell.extensions.mak');

            this._state = 'compact'; // 'compact', 'hud', 'expanded'
            this._hudTimeoutId = 0;
            this._waveTimerId = 0;
            this._waveStep = 0;
            this._mprisSource = null;
            this._activePlayer = null;
            this._origOsdShow = null;
            this._monitorsChangedId = 0;

            // Build layout
            this._buildUI();

            // Setup MPRIS media listener
            this._setupMpris();

            // Setup OSD hook for Volume/Brightness
            this._setupOsdHook();

            // Position and add to UI via layoutManager Chrome
            this._reposition();
            Main.layoutManager.addChrome(this, {
                affectsStruts: false,
                trackFullscreen: true,
            });
            this._monitorsChangedId = Main.layoutManager.connect('monitors-changed', () => this._reposition());

            // Hover interactions
            this.connect('notify::hover', () => {
                if (this.hover) {
                    if (this._activePlayer && this._state !== 'expanded') {
                        this._expand();
                    }
                } else {
                    if (this._state === 'expanded') {
                        this._collapse();
                    }
                }
            });

            // Click interaction (toggle expanded)
            this.connect('button-press-event', (actor, event) => {
                const btn = event.get_button();
                if (btn === 1) { // Left click
                    if (this._state === 'expanded') {
                        this._collapse();
                    } else if (this._activePlayer) {
                        this._expand();
                    }
                    return Clutter.EVENT_STOP;
                }
                return Clutter.EVENT_PROPAGATE;
            });
        }

        _buildUI() {
            // Main Pill Background Frame
            this._pill = new St.BoxLayout({
                vertical: true,
                style_class: 'mak-island-pill',
                x_expand: true,
                y_expand: true,
            });
            this.add_child(this._pill);

            // ── 1. COMPACT ROW (Always present, toggles visibility when expanded) ──
            this._compactBox = new St.BoxLayout({
                vertical: false,
                style_class: 'mak-island-compact-box',
                y_align: Clutter.ActorAlign.CENTER,
                x_expand: true,
            });

            // Mini App / Music Icon
            this._miniIcon = new St.Icon({
                icon_name: 'audio-x-generic-symbolic',
                style_class: 'mak-island-mini-icon',
                y_align: Clutter.ActorAlign.CENTER,
            });
            this._compactBox.add_child(this._miniIcon);

            // Center scrolling / ellipsized track info
            this._compactTitle = new St.Label({
                text: 'Mak Desktop',
                style_class: 'mak-island-compact-title',
                x_expand: true,
                y_align: Clutter.ActorAlign.CENTER,
            });
            this._compactTitle.clutter_text.ellipsize = Pango.EllipsizeMode.END;
            this._compactBox.add_child(this._compactTitle);

            // Animated Equalizer Soundwave Bars
            this._waveBox = new St.BoxLayout({
                vertical: false,
                style_class: 'mak-island-wave-box',
                y_align: Clutter.ActorAlign.CENTER,
            });
            this._waveBars = [];
            for (let i = 0; i < 4; i++) {
                const bar = new St.Widget({
                    style_class: `mak-island-wave-bar bar-${i}`,
                    y_align: Clutter.ActorAlign.CENTER,
                });
                this._waveBars.push(bar);
                this._waveBox.add_child(bar);
            }
            this._compactBox.add_child(this._waveBox);
            this._pill.add_child(this._compactBox);

            // ── 2. HUD ROW (Volume / Brightness) ──
            this._hudBox = new St.BoxLayout({
                vertical: false,
                style_class: 'mak-island-hud-box',
                y_align: Clutter.ActorAlign.CENTER,
                x_expand: true,
                visible: false,
            });

            this._hudIcon = new St.Icon({
                icon_name: 'audio-volume-high-symbolic',
                style_class: 'mak-island-hud-icon',
                y_align: Clutter.ActorAlign.CENTER,
            });
            this._hudBox.add_child(this._hudIcon);

            // Progress Bar Track & Fill
            const progressTrack = new St.BoxLayout({
                vertical: false,
                style_class: 'mak-island-hud-track',
                x_expand: true,
                y_align: Clutter.ActorAlign.CENTER,
            });
            this._hudFill = new St.Widget({
                style_class: 'mak-island-hud-fill',
                y_align: Clutter.ActorAlign.CENTER,
            });
            progressTrack.add_child(this._hudFill);
            this._hudBox.add_child(progressTrack);

            this._hudPercentLabel = new St.Label({
                text: '50%',
                style_class: 'mak-island-hud-percent',
                y_align: Clutter.ActorAlign.CENTER,
            });
            this._hudBox.add_child(this._hudPercentLabel);
            this._pill.add_child(this._hudBox);

            // ── 3. EXPANDED CARD VIEW ──
            this._expandedBox = new St.BoxLayout({
                vertical: true,
                style_class: 'mak-island-expanded-box',
                x_expand: true,
                visible: false,
            });

            const topRow = new St.BoxLayout({
                vertical: false,
                style_class: 'mak-island-expanded-top',
                y_align: Clutter.ActorAlign.CENTER,
                x_expand: true,
            });

            // Album Artwork Image
            this._coverImage = new St.Icon({
                icon_name: 'audio-x-generic-symbolic',
                style_class: 'mak-island-cover-art',
                y_align: Clutter.ActorAlign.CENTER,
            });
            topRow.add_child(this._coverImage);

            // Track & Artist Meta
            const metaBox = new St.BoxLayout({
                vertical: true,
                style_class: 'mak-island-expanded-meta',
                x_expand: true,
                y_align: Clutter.ActorAlign.CENTER,
            });
            this._expandedTitle = new St.Label({
                text: 'Song Title',
                style_class: 'mak-island-expanded-title',
            });
            this._expandedTitle.clutter_text.ellipsize = Pango.EllipsizeMode.END;
            metaBox.add_child(this._expandedTitle);

            this._expandedArtist = new St.Label({
                text: 'Artist Name',
                style_class: 'mak-island-expanded-artist',
            });
            this._expandedArtist.clutter_text.ellipsize = Pango.EllipsizeMode.END;
            metaBox.add_child(this._expandedArtist);
            topRow.add_child(metaBox);

            // Playback Controls Row
            const controlsBox = new St.BoxLayout({
                vertical: false,
                style_class: 'mak-island-controls-box',
                y_align: Clutter.ActorAlign.CENTER,
            });

            // Previous Button
            const prevBtn = new St.Button({
                style_class: 'mak-island-ctrl-btn',
                can_focus: true,
                y_align: Clutter.ActorAlign.CENTER,
            });
            prevBtn.set_child(new St.Icon({
                icon_name: 'media-skip-backward-symbolic',
                style_class: 'mak-island-ctrl-icon',
            }));
            prevBtn.connect('clicked', () => {
                if (this._activePlayer) this._activePlayer._playerProxy?.PreviousAsync?.();
            });
            controlsBox.add_child(prevBtn);

            // Play/Pause Button
            this._playPauseBtn = new St.Button({
                style_class: 'mak-island-ctrl-btn play-pause',
                can_focus: true,
                y_align: Clutter.ActorAlign.CENTER,
            });
            this._playPauseIcon = new St.Icon({
                icon_name: 'media-playback-pause-symbolic',
                style_class: 'mak-island-ctrl-icon play',
            });
            this._playPauseBtn.set_child(this._playPauseIcon);
            this._playPauseBtn.connect('clicked', () => {
                if (this._activePlayer) this._activePlayer._playerProxy?.PlayPauseAsync?.();
            });
            controlsBox.add_child(this._playPauseBtn);

            // Next Button
            const nextBtn = new St.Button({
                style_class: 'mak-island-ctrl-btn',
                can_focus: true,
                y_align: Clutter.ActorAlign.CENTER,
            });
            nextBtn.set_child(new St.Icon({
                icon_name: 'media-skip-forward-symbolic',
                style_class: 'mak-island-ctrl-icon',
            }));
            nextBtn.connect('clicked', () => {
                if (this._activePlayer) this._activePlayer._playerProxy?.NextAsync?.();
            });
            controlsBox.add_child(nextBtn);

            topRow.add_child(controlsBox);
            this._expandedBox.add_child(topRow);
            this._pill.add_child(this._expandedBox);
        }

        _setupMpris() {
            try {
                this._mprisSource = new Mpris.MprisSource();
                this._mprisSource.connectObject(
                    'player-added', (source, player) => this._onPlayerAdded(player),
                    'player-removed', (source, player) => this._onPlayerRemoved(player),
                    this
                );

                // Initial players check
                const players = this._mprisSource.players || [];
                if (players.length > 0) {
                    this._setActivePlayer(players[0]);
                }
            } catch (err) {
                console.warn('[Mak Island] Could not init MprisSource:', err);
            }
        }

        _onPlayerAdded(player) {
            if (!this._activePlayer) {
                this._setActivePlayer(player);
            }
        }

        _onPlayerRemoved(player) {
            if (this._activePlayer === player) {
                this._activePlayer.disconnectObject(this);
                this._activePlayer = null;
                const players = this._mprisSource?.players || [];
                if (players.length > 0) {
                    this._setActivePlayer(players[0]);
                } else {
                    this._updateIdleState();
                }
            }
        }

        _setActivePlayer(player) {
            if (this._activePlayer) {
                this._activePlayer.disconnectObject(this);
            }
            this._activePlayer = player;
            player.connectObject('changed', () => this._updateMediaInfo(), this);
            this._updateMediaInfo();
        }

        _updateMediaInfo() {
            if (!this._activePlayer) {
                this._updateIdleState();
                return;
            }

            const title = this._activePlayer.trackTitle || 'Unknown Title';
            const artists = this._activePlayer.trackArtists?.join(', ') || 'Unknown Artist';
            const isPlaying = this._activePlayer.status === 'Playing';

            this._compactTitle.set_text(`${title} · ${artists}`);
            this._expandedTitle.set_text(title);
            this._expandedArtist.set_text(artists);

            // Update cover art
            if (this._activePlayer.trackCoverUrl) {
                try {
                    const gfile = Gio.File.new_for_uri(this._activePlayer.trackCoverUrl);
                    const gicon = new Gio.FileIcon({ file: gfile });
                    this._coverImage.set_gicon(gicon);
                } catch (e) {
                    this._coverImage.set_icon_name('audio-x-generic-symbolic');
                }
            } else {
                this._coverImage.set_icon_name('audio-x-generic-symbolic');
            }

            // Update Play/Pause Icon
            if (this._playPauseIcon) {
                this._playPauseIcon.icon_name = isPlaying
                    ? 'media-playback-pause-symbolic'
                    : 'media-playback-start-symbolic';
            }

            // Animated waveform bars when playing
            if (isPlaying) {
                this._startWaveAnimation();
            } else {
                this._stopWaveAnimation();
            }

            this.visible = true;
        }

        _updateIdleState() {
            this._stopWaveAnimation();
            this._compactTitle.set_text('Mak Desktop');
            this._coverImage.set_icon_name('audio-x-generic-symbolic');
            if (this._state === 'expanded') {
                this._collapse();
            }
        }

        _startWaveAnimation() {
            if (this._waveTimerId) return;
            const heights = [
                [6, 12, 8, 14],
                [10, 6, 14, 8],
                [14, 10, 6, 12],
                [8, 14, 10, 6],
            ];
            this._waveTimerId = GLib.timeout_add(GLib.PRIORITY_LOW, 140, () => {
                this._waveStep = (this._waveStep + 1) % heights.length;
                const pattern = heights[this._waveStep];
                this._waveBars.forEach((bar, idx) => {
                    bar.style = `height: ${pattern[idx]}px;`;
                });
                return GLib.SOURCE_CONTINUE;
            });
        }

        _stopWaveAnimation() {
            if (this._waveTimerId) {
                GLib.Source.remove(this._waveTimerId);
                this._waveTimerId = 0;
            }
            this._waveBars.forEach(bar => {
                bar.style = 'height: 4px;';
            });
        }

        _setupOsdHook() {
            if (!Main.osdWindowManager) return;
            this._origOsdShow = Main.osdWindowManager.show;
            const self = this;

            Main.osdWindowManager.show = function(icon, label, levels) {
                try {
                    if (levels && levels.length > 0) {
                        const pIdx = Main.layoutManager.primaryIndex;
                        const lvl = levels[pIdx] || levels[0];
                        if (lvl && typeof lvl.level === 'number') {
                            const frac = lvl.maxLevel > 0 ? (lvl.level / lvl.maxLevel) : lvl.level;
                            self._showHUD(icon, Math.round(frac * 100));
                        }
                    }
                } catch (e) {
                    console.warn('[Mak Island] OSD hook error:', e);
                }
                return self._origOsdShow.apply(this, arguments);
            };
        }

        _showHUD(icon, percent) {
            if (this._hudTimeoutId) {
                GLib.Source.remove(this._hudTimeoutId);
                this._hudTimeoutId = 0;
            }

            // Set HUD icon and values
            if (typeof icon === 'string') {
                this._hudIcon.icon_name = icon;
            } else if (icon instanceof Gio.Icon) {
                this._hudIcon.gicon = icon;
            } else {
                this._hudIcon.icon_name = 'audio-volume-high-symbolic';
            }

            this._hudPercentLabel.set_text(`${percent}%`);
            const trackWidth = 140;
            const fillWidth = Math.max(4, Math.round((percent / 100) * trackWidth));
            this._hudFill.style = `width: ${fillWidth}px;`;

            // Switch to HUD state
            this._compactBox.visible = false;
            this._expandedBox.visible = false;
            this._hudBox.visible = true;
            this._state = 'hud';

            this._animateTo(HUD_WIDTH, HUD_HEIGHT);

            // Revert after 1.8s
            this._hudTimeoutId = GLib.timeout_add(GLib.PRIORITY_DEFAULT, 1800, () => {
                this._hudTimeoutId = 0;
                this._hudBox.visible = false;
                this._compactBox.visible = true;
                this._state = 'compact';
                this._animateTo(COMPACT_WIDTH, COMPACT_HEIGHT);
                return GLib.SOURCE_REMOVE;
            });
        }

        _expand() {
            if (this._state === 'expanded') return;
            if (this._hudTimeoutId) {
                GLib.Source.remove(this._hudTimeoutId);
                this._hudTimeoutId = 0;
            }

            this._state = 'expanded';
            this._compactBox.visible = false;
            this._hudBox.visible = false;
            this._expandedBox.visible = true;

            this._animateTo(EXPANDED_WIDTH, EXPANDED_HEIGHT);
        }

        _collapse() {
            if (this._state === 'compact') return;
            this._state = 'compact';
            this._expandedBox.visible = false;
            this._hudBox.visible = false;
            this._compactBox.visible = true;

            this._animateTo(COMPACT_WIDTH, COMPACT_HEIGHT);
        }

        _animateTo(targetW, targetH) {
            const monitor = Main.layoutManager.primaryMonitor;
            if (!monitor) return;

            const targetX = monitor.x + Math.round((monitor.width - targetW) / 2);
            const targetY = monitor.y;

            this.ease({
                x: targetX,
                y: targetY,
                width: targetW,
                height: targetH,
                duration: 220,
                mode: Clutter.AnimationMode.EASE_OUT_CUBIC,
            });
        }

        _reposition() {
            const monitor = Main.layoutManager.primaryMonitor;
            if (!monitor) return;

            const w = this._state === 'expanded' ? EXPANDED_WIDTH : (this._state === 'hud' ? HUD_WIDTH : COMPACT_WIDTH);
            const h = this._state === 'expanded' ? EXPANDED_HEIGHT : (this._state === 'hud' ? HUD_HEIGHT : COMPACT_HEIGHT);

            this.set_size(w, h);
            this.set_position(
                monitor.x + Math.round((monitor.width - w) / 2),
                monitor.y
            );
        }

        destroy() {
            if (this._waveTimerId) {
                GLib.Source.remove(this._waveTimerId);
                this._waveTimerId = 0;
            }
            if (this._hudTimeoutId) {
                GLib.Source.remove(this._hudTimeoutId);
                this._hudTimeoutId = 0;
            }
            if (this._monitorsChangedId) {
                Main.layoutManager.disconnect(this._monitorsChangedId);
                this._monitorsChangedId = 0;
            }
            if (this._origOsdShow && Main.osdWindowManager) {
                Main.osdWindowManager.show = this._origOsdShow;
                this._origOsdShow = null;
            }
            if (this._activePlayer) {
                this._activePlayer.disconnectObject(this);
                this._activePlayer = null;
            }
            if (this._mprisSource) {
                this._mprisSource.disconnectObject(this);
                this._mprisSource = null;
            }

            try {
                Main.layoutManager.removeChrome(this);
            } catch (e) {}

            super.destroy();
        }
    }
);
