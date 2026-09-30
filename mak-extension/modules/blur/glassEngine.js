// SPDX-License-Identifier: GPL-3.0-or-later
// Mak Blur & Glassmorphism Shader Engine
// Provides zero-artifact liquid frosted glass background blur with perfect corner clipping.

import Cogl from 'gi://Cogl';
import Clutter from 'gi://Clutter';
import GObject from 'gi://GObject';
import Meta from 'gi://Meta';
import Shell from 'gi://Shell';
import St from 'gi://St';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import * as Background from 'resource:///org/gnome/shell/ui/background.js';

import { NativeStaticBlurEffect } from './bms/effects/native_static_gaussian_blur.js';
import { NativeDynamicBlurEffect } from './bms/effects/native_dynamic_gaussian_blur.js';
import { CornerEffect } from './bms/effects/corner.js';

export class GlassBlurPipeline {
    constructor(actor, containerOrOptions = {}, maybeOptions = {}) {
        this._actor = actor;
        let container = null;
        let options = {};
        if (containerOrOptions && containerOrOptions instanceof Clutter.Actor) {
            container = containerOrOptions;
            options = maybeOptions || {};
        } else {
            options = containerOrOptions || {};
        }
        this._container = container;
        this._radius = options.radius ?? 32;
        this._brightness = options.brightness ?? 0.75;
        this._cornerRadius = options.cornerRadius ?? 24;
        this._enabled = options.enabled ?? true;

        this._bgGroup = null;
        this._blurActor = null;
        this._bgManager = null;
        this._blurEffect = null;
        this._cornerEffect = null;
        this._pendingUpdateId = 0;
        this._isDynamic = Boolean(NativeDynamicBlurEffect.supports_corner_radius);

        this._signalIds = [];

        this._build();
    }

    get isDynamic() {
        return this._isDynamic;
    }

    _build() {
        if (!this._actor) return;
        const container = this._container || this._actor.get_parent();
        if (!container) return;
        this._container = container;

        try {
            const monitor = this._getMonitor();
            this._bgGroup = new Meta.BackgroundGroup({
                name: 'aqua-dock-bg-group',
                reactive: false,
            });

            // Insert background group directly into the container at index 0 (behind all items & pill)
            this._container.insert_child_at_index(this._bgGroup, 0);

            if (this._isDynamic) {
                // ── 1. DYNAMIC BLUR (gnome-rounded-blur available) ──
                console.log('[Mak GlassBlur] Using dynamic stage blur with native corner radius:', this._cornerRadius);
                this._blurActor = new St.Widget({
                    name: 'aqua-dock-blurred-widget',
                    reactive: false,
                });
                this._bgGroup.add_child(this._blurActor);

                this._blurEffect = new NativeDynamicBlurEffect({
                    unscaled_radius: this._radius,
                    brightness: this._brightness,
                    unscaled_corner_radius: this._cornerRadius,
                });
                this._blurActor.add_effect(this._blurEffect);
            } else {
                // ── 2. ZERO-KORNERS STATIC BLUR (wallpaper blit + corner.glsl) ──
                console.log('[Mak GlassBlur] Using zero-korner static wallpaper blur pipeline.');
                const monW = monitor ? Math.max(100, monitor.width) : 1920;
                const monH = monitor ? Math.max(100, monitor.height) : 1080;

                this._blurActor = new St.Widget({
                    name: 'aqua-dock-blurred-widget',
                    reactive: false,
                    z_position: 1,
                    width: monW,
                    height: monH,
                });
                this._bgGroup.add_child(this._blurActor);

                if (monitor) {
                    this._bgManager = new Background.BackgroundManager({
                        container: this._blurActor,
                        monitorIndex: monitor.index,
                        controlPosition: false,
                    });
                    this._bgManager.connect('changed', () => this.syncClip());
                }

                this._blurEffect = new NativeStaticBlurEffect({
                    unscaled_radius: this._radius,
                    brightness: this._brightness,
                });
                this._blurActor.add_effect(this._blurEffect);

                this._cornerEffect = new CornerEffect({
                    radius: this._cornerRadius,
                });
                this._blurActor.add_effect(this._cornerEffect);
            }

            // Connect tracking signals
            const themeContext = St.ThemeContext.get_for_stage(global.stage);
            this._signalIds.push({
                obj: themeContext,
                id: themeContext.connect('notify::scale-factor', () => this._syncScale()),
            });

            this._signalIds.push({
                obj: this._actor,
                id: this._actor.connect('notify::x', () => this.syncClip()),
            });
            this._signalIds.push({
                obj: this._actor,
                id: this._actor.connect('notify::y', () => this.syncClip()),
            });
            this._signalIds.push({
                obj: this._actor,
                id: this._actor.connect('notify::width', () => this.syncClip()),
            });
            this._signalIds.push({
                obj: this._actor,
                id: this._actor.connect('notify::height', () => this.syncClip()),
            });
            this._signalIds.push({
                obj: this._actor,
                id: this._actor.connect('notify::opacity', () => this._syncVisibility()),
            });
            this._signalIds.push({
                obj: this._actor,
                id: this._actor.connect('notify::visible', () => this._syncVisibility()),
            });

            if (container) {
                this._signalIds.push({
                    obj: container,
                    id: container.connect('notify::x', () => this.syncClip()),
                });
                this._signalIds.push({
                    obj: container,
                    id: container.connect('notify::y', () => this.syncClip()),
                });
                this._signalIds.push({
                    obj: container,
                    id: container.connect('notify::allocation', () => this.syncClip()),
                });
                this._signalIds.push({
                    obj: container,
                    id: container.connect('notify::visible', () => this._syncVisibility()),
                });
            }

            this._scheduleUpdate();
        } catch (err) {
            console.warn('[Mak GlassBlur] Error building GlassBlurPipeline:', err);
        }
    }

    _getMonitor() {
        const container = this._container || this._actor?.get_parent();
        if (container) {
            const mon = Main.layoutManager.findMonitorForActor(container);
            if (mon) return mon;
        }
        return Main.layoutManager.primaryMonitor;
    }

    _syncVisibility() {
        if (!this._bgGroup || !this._actor) return;
        const visible = Boolean((this._enabled ?? true) && this._actor.visible && (this._container ? this._container.visible : true));
        this._bgGroup.visible = visible;
        this._bgGroup.opacity = this._actor.opacity;
    }

    _syncScale() {
        const stage = this._container?.get_stage() || global.stage;
        const scale = St.ThemeContext.get_for_stage(stage).scale_factor || 1;
        if (this._blurEffect) {
            this._blurEffect.unscaled_radius = this._radius;
            if (this._isDynamic) {
                this._blurEffect.unscaled_corner_radius = this._cornerRadius;
            }
        }
        if (this._cornerEffect) {
            this._cornerEffect.radius = this._cornerRadius * scale;
        }
        this.syncClip();
    }

    syncGeometry(width, height, x = null, y = null) {
        this.syncClip(width, height, x, y);
    }

    syncClip(overrideW = null, overrideH = null, overrideX = null, overrideY = null) {
        if (!this._blurActor || !this._container || !this._actor) return;

        const stage = this._container.get_stage();
        if (!stage || !this._container.has_allocation()) {
            this._scheduleUpdate();
            return;
        }

        const monitor = this._getMonitor();
        if (!monitor || monitor.width <= 0 || monitor.height <= 0) return;

        const scale = St.ThemeContext.get_for_stage(stage).scale_factor || 1;

        const pillX = Math.round(overrideX !== null ? overrideX : this._actor.x);
        const pillY = Math.round(overrideY !== null ? overrideY : this._actor.y);
        const pillW = Math.round(Math.max(1, overrideW !== null ? overrideW : this._actor.width));
        const pillH = Math.round(Math.max(1, overrideH !== null ? overrideH : this._actor.height));

        if (isNaN(pillX) || isNaN(pillY) || isNaN(pillW) || isNaN(pillH) || pillW <= 1 || pillH <= 1) {
            this._scheduleUpdate();
            return;
        }

        if (this._isDynamic) {
            // Dynamic blur actor directly matches pill rect
            this._blurActor.set_position(pillX, pillY);
            this._blurActor.set_size(pillW, pillH);
            if (this._blurEffect) {
                this._blurEffect.unscaled_corner_radius = this._cornerRadius;
            }
        } else {
            // Static wallpaper blur: calculate stage offsets for monitor alignment
            const [parent_stage_x, parent_stage_y] = this._container.get_transformed_position();
            const [bg_stage_x, bg_stage_y] = this._actor.get_transformed_position();

            if (isNaN(parent_stage_x) || isNaN(parent_stage_y) || isNaN(bg_stage_x) || isNaN(bg_stage_y)) {
                this._scheduleUpdate();
                return;
            }

            const background_x = monitor.x - parent_stage_x;
            const background_y = monitor.y - parent_stage_y;
            const clip_x = bg_stage_x - monitor.x;
            const clip_y = bg_stage_y - monitor.y;

            this._blurActor.set_position(background_x, background_y);
            this._blurActor.set_clip(clip_x, clip_y, pillW, pillH);

            if (this._cornerEffect) {
                this._cornerEffect.radius = this._cornerRadius * scale;
                this._cornerEffect.clip = [clip_x, clip_y, pillW, pillH];
            }
        }

        this._syncVisibility();
    }

    _scheduleUpdate() {
        if (this._pendingUpdateId) return;
        this._pendingUpdateId = global.compositor.get_laters().add(
            Meta.LaterType.IDLE,
            () => {
                this._pendingUpdateId = 0;
                this.syncClip();
                return false;
            }
        );
    }

    setParameters({ radius, brightness, cornerRadius, enabled }) {
        if (enabled !== undefined) {
            this._enabled = Boolean(enabled);
        }
        if (radius !== undefined) {
            this._radius = radius;
            if (this._blurEffect) this._blurEffect.unscaled_radius = radius;
        }
        if (brightness !== undefined) {
            this._brightness = brightness;
            if (this._blurEffect) this._blurEffect.brightness = brightness;
        }
        if (cornerRadius !== undefined) {
            this._cornerRadius = cornerRadius;
            const stage = this._container?.get_stage() || global.stage;
            const scale = St.ThemeContext.get_for_stage(stage).scale_factor || 1;
            if (this._cornerEffect) this._cornerEffect.radius = cornerRadius * scale;
            if (this._isDynamic && this._blurEffect) {
                this._blurEffect.unscaled_corner_radius = cornerRadius;
            }
        }
        if (this._blurEffect && typeof this._blurEffect.queue_repaint === 'function') {
            this._blurEffect.queue_repaint();
        }
        if (this._cornerEffect && typeof this._cornerEffect.queue_repaint === 'function') {
            this._cornerEffect.queue_repaint();
        }
        this._syncVisibility();
        this.syncClip();
    }

    destroy() {
        if (this._pendingUpdateId) {
            try {
                global.compositor.get_laters().remove(this._pendingUpdateId);
            } catch (e) {}
            this._pendingUpdateId = 0;
        }

        for (const sig of this._signalIds) {
            try {
                sig.obj.disconnect(sig.id);
            } catch (e) {}
        }
        this._signalIds = [];

        if (this._bgManager) {
            try { this._bgManager.destroy(); } catch (e) {}
            this._bgManager = null;
        }

        if (this._blurEffect && this._blurActor) {
            try { this._blurActor.remove_effect(this._blurEffect); } catch (e) {}
            this._blurEffect = null;
        }
        if (this._cornerEffect && this._blurActor) {
            try { this._blurActor.remove_effect(this._cornerEffect); } catch (e) {}
            this._cornerEffect = null;
        }

        if (this._blurActor) {
            try { this._blurActor.destroy(); } catch (e) {}
            this._blurActor = null;
        }

        if (this._bgGroup) {
            try {
                if (this._container && this._container.contains(this._bgGroup)) {
                    this._container.remove_child(this._bgGroup);
                }
                this._bgGroup.destroy();
            } catch (e) {}
            this._bgGroup = null;
        }

        this._actor = null;
        this._container = null;
    }
}
