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
import { RefractionEffect } from './bms/effects/refraction.js';

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
        this._refractionStrength = options.refractionStrength ?? 0.42;
        this._chromaticDispersion = options.chromaticDispersion ?? 0.08;
        this._liquidGlass = options.liquidGlass ?? false;

        this._bgGroup = null;
        this._blurActor = null;
        this._bgManager = null;
        this._blurEffect = null;
        this._cornerEffect = null;
        this._refractionEffect = null;
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
            if (this._isDynamic) {
                // ── 1. DYNAMIC BLUR (gnome-rounded-blur available) ──
                // Apply blur effect DIRECTLY to the pill actor (_bg).
                // BlurMode.BACKGROUND blurs compositor content behind the actor;
                // the actor's own semi-transparent CSS background-color tints on top.
                // Avoids the z-order bug where a separate blur widget (index 0)
                // was fully occluded by _bg (index 1) with its solid background.
                console.log('[Mak GlassBlur] Using dynamic stage blur with native corner radius:', this._cornerRadius);
                this._blurEffect = new NativeDynamicBlurEffect({
                    unscaled_radius: this._radius,
                    brightness: this._brightness,
                    unscaled_corner_radius: this._cornerRadius,
                });
                this._actor.add_effect(this._blurEffect);
                // _blurActor kept null — effect is on _actor which is owned externally
                this._blurActor = null;
            } else {
                // ── 2. ZERO-KORNERS STATIC BLUR (wallpaper blit + corner.glsl) ──
                console.log('[Mak GlassBlur] Using zero-korner static wallpaper blur pipeline.');
                const monW = monitor ? Math.max(100, monitor.width) : 1920;
                const monH = monitor ? Math.max(100, monitor.height) : 1080;

                this._bgGroup = new Meta.BackgroundGroup({
                    name: 'aqua-dock-bg-group',
                    reactive: false,
                });
                this._container.insert_child_at_index(this._bgGroup, 0);

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
        if (this._isDynamic) {
            // In dynamic mode the blur effect is on _actor, which the dock manages.
            // Just toggle effect enabled state to match.
            if (this._blurEffect) {
                const on = Boolean((this._enabled ?? true) && this._actor?.visible);
                this._blurEffect.enabled = on;
            }
            return;
        }
        const targetActor = this._blurActor || this._bgGroup;
        if (!targetActor || !this._actor) return;
        const visible = Boolean((this._enabled ?? true) && this._actor.visible && (this._container ? this._container.visible : true));
        targetActor.visible = visible;
        targetActor.opacity = this._actor.opacity;
        if (this._bgGroup && this._bgGroup !== targetActor) {
            this._bgGroup.visible = visible;
            this._bgGroup.opacity = this._actor.opacity;
        }
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
        if (!this._container || !this._actor) return;
        // Static mode also needs _blurActor; early-out only if static and no blurActor
        if (!this._isDynamic && !this._blurActor) return;

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
            // Blur effect is applied directly to _actor — no separate actor to position.
            // Just ensure effect parameters are current.
            if (this._blurEffect) {
                this._blurEffect.unscaled_corner_radius = this._cornerRadius;
                this._blurEffect.unscaled_radius = this._radius;
                this._blurEffect.brightness = this._brightness;
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

    setParameters({ radius, brightness, cornerRadius, enabled, refractionStrength, chromaticDispersion, liquidGlass }) {
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
        if (refractionStrength !== undefined) this._refractionStrength = refractionStrength;
        if (chromaticDispersion !== undefined) this._chromaticDispersion = chromaticDispersion;
        if (liquidGlass !== undefined) this.setLiquidGlass(liquidGlass);

        if (this._refractionEffect) {
            this._refractionEffect.strength = this._refractionStrength;
            this._refractionEffect.rgb_fringing = this._chromaticDispersion;
            this._refractionEffect.corner_radius = this._cornerRadius;
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

    setLiquidGlass(enabled) {
        this._liquidGlass = Boolean(enabled);
        if (!this._actor) return;

        if (this._liquidGlass) {
            if (!this._refractionEffect) {
                try {
                    this._refractionEffect = new RefractionEffect({
                        strength: this._refractionStrength,
                        blur_radius: Math.max(3, Math.min(20, this._radius * 0.35)),
                        edge_size: 24,
                        falloff: 2.2,
                        corner_radius: this._cornerRadius,
                        rim_width: 4.8,
                        rgb_fringing: this._chromaticDispersion,
                        gloss: 0.60,
                        tint: 0.14,
                    });
                    this._actor.add_effect(this._refractionEffect);
                } catch (e) {
                    console.warn('[Mak GlassBlur] Could not add RefractionEffect:', e.message);
                    this._refractionEffect = null;
                }
            }
        } else {
            if (this._refractionEffect) {
                try { this._actor.remove_effect(this._refractionEffect); } catch (e) {}
                this._refractionEffect = null;
            }
        }
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

        if (this._isDynamic) {
            // Dynamic: effects applied directly to _actor — just remove them.
            // Do NOT destroy _actor; it is _bg, owned by the dock.
            if (this._refractionEffect && this._actor) {
                try { this._actor.remove_effect(this._refractionEffect); } catch (e) {}
            }
            this._refractionEffect = null;
            if (this._blurEffect && this._actor) {
                try { this._actor.remove_effect(this._blurEffect); } catch (e) {}
            }
            this._blurEffect = null;
            this._blurActor = null;
        } else {
            // Static: effects are on a separate _blurActor widget we created.
            if (this._blurEffect && this._blurActor) {
                try { this._blurActor.remove_effect(this._blurEffect); } catch (e) {}
                this._blurEffect = null;
            }
            if (this._cornerEffect && this._blurActor) {
                try { this._blurActor.remove_effect(this._cornerEffect); } catch (e) {}
                this._cornerEffect = null;
            }

            if (this._blurActor) {
                try {
                    if (this._container && this._container.contains(this._blurActor)) {
                        this._container.remove_child(this._blurActor);
                    }
                    this._blurActor.destroy();
                } catch (e) {}
                this._blurActor = null;
            }
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
