/** @file Binds the actual corner rounding shader to the windows. */
var _a;
import Cogl from 'gi://Cogl';
import Gio from 'gi://Gio';
import GObject from 'gi://GObject';
import Shell from 'gi://Shell';
import { readShader } from '../utils/file.js';
import { getPref } from '../utils/settings.js';
const [declarations, code] = await readShader(import.meta.url, 'shader/rounded_corners.frag');
class Uniforms {
    bounds = 0;
    clipRadius = 0;
    borderWidth = 0;
    borderColor = 0;
    borderedAreaBounds = 0;
    borderedAreaClipRadius = 0;
    exponent = 0;
    pixelStep = 0;
    topbarOpacity = 0;
}
export const RoundedCornersEffect = GObject.registerClass({
    GTypeName: 'MakRoundedCornersEffect',
}, class Effect extends Shell.GLSLEffect {
    /**
     * To store a uniform value, we need to know its location in the shader,
     * which is done by calling `this.get_uniform_location()`. This is
     * expensive, so we cache the location of uniforms when the shader is
     * created.
     */
    static uniforms = new Uniforms();
    constructor() {
        super();
        for (const k in Effect.uniforms) {
            Effect.uniforms[k] =
                this.get_uniform_location(k);
        }
    }
    vfunc_build_pipeline() {
        this.add_glsl_snippet(Cogl.SnippetHook.FRAGMENT, declarations, code, false);
    }
    /**
     * Update uniforms of the shader.
     * For more information, see the comments in the shader file.
     *
     * @param config - Rounded corners configuration
     * @param windowBounds - Bounds of the window without padding
     */
    updateUniforms(config, windowBounds, win = null) {
        const borderWidth = getPref('border-width');
        const borderColor = config.borderColor;
        const outerRadius = config.borderRadius;
        const { padding, smoothing } = config;
        const bounds = [
            windowBounds.x1 + padding.left,
            windowBounds.y1 + padding.top,
            windowBounds.x2 - padding.right,
            windowBounds.y2 - padding.bottom,
        ];
        const borderedAreaBounds = [
            bounds[0] + borderWidth,
            bounds[1] + borderWidth,
            bounds[2] - borderWidth,
            bounds[3] - borderWidth,
        ];
        let borderedAreaRadius = outerRadius - borderWidth;
        if (borderedAreaRadius < 0.001) {
            borderedAreaRadius = 0.0;
        }
        const pixelStep = [
            1 / this.actor.get_width(),
            1 / this.actor.get_height(),
        ];
        // This is needed for squircle corners
        let exponent = smoothing * 10 + 2;
        let radius = outerRadius * 0.5 * exponent;
        const width = bounds[2] - bounds[0];
        const height = bounds[3] - bounds[1];
        const maxRadius = Math.min(width, height) * 0.5;
        if (radius > maxRadius) {
            exponent *= maxRadius / radius;
            radius = maxRadius;
        }
        borderedAreaRadius *= radius / outerRadius;

        // Chrome/Chromium glassy topbar + opaque web page support
        let topbarParam = [0.0, 1.0];
        const wmClass = (win?.wmClass || win?.get_wm_class?.() || '').toLowerCase();
        const gtkAppId = (win?.gtkApplicationId || win?.get_gtk_application_id?.() || '').toLowerCase();
        const isChrome = wmClass.includes('google-chrome') ||
                         wmClass.includes('chromium') ||
                         wmClass.includes('brave') ||
                         gtkAppId.includes('google-chrome') ||
                         gtkAppId.includes('chromium') ||
                         gtkAppId.includes('brave');

        if (isChrome) {
            let blurOpacity = 215;
            try {
                const bmsAppSettings = new Gio.Settings({ schema_id: 'org.gnome.shell.extensions.blur-my-shell.applications' });
                if (bmsAppSettings.get_boolean('blur')) {
                    blurOpacity = bmsAppSettings.get_int('opacity') || 215;
                }
            } catch (e) {}

            const alphaMultiplier = Math.max(0.1, Math.min(1.0, blurOpacity / 255.0));
            // Chrome header height: ~86px
            const topbarH = 86.0;
            topbarParam = [topbarH, alphaMultiplier];
        }

        this.#setUniforms(bounds, radius, borderWidth, borderColor, borderedAreaBounds, borderedAreaRadius, pixelStep, exponent, topbarParam);
    }
    #setUniforms(bounds, radius, borderWidth, borderColor, borderedAreaBounds, borderedAreaRadius, pixelStep, exponent, topbarParam) {
        const uniforms = Effect.uniforms;
        this.set_uniform_float(uniforms.bounds, 4, bounds);
        this.set_uniform_float(uniforms.clipRadius, 1, [radius]);
        this.set_uniform_float(uniforms.borderWidth, 1, [borderWidth]);
        this.set_uniform_float(uniforms.borderColor, 4, borderColor);
        this.set_uniform_float(uniforms.borderedAreaBounds, 4, borderedAreaBounds);
        this.set_uniform_float(uniforms.borderedAreaClipRadius, 1, [
            borderedAreaRadius,
        ]);
        this.set_uniform_float(uniforms.pixelStep, 2, pixelStep);
        this.set_uniform_float(uniforms.exponent, 1, [exponent]);
        this.set_uniform_float(uniforms.topbarOpacity, 2, topbarParam);
        this.queue_repaint();
    }
});
