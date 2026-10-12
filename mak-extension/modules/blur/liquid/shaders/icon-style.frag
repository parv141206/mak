// An icon redrawn from its style map (src/iconStyle/styleMap.ts) as glass
// plates under a symbol. A Cogl fragment snippet for
// src/iconStyle/iconEffect.ts; the contact sheet (tools/icon-sheet) runs it in
// WebGL too.
uniform sampler2D cogl_sampler0; // The icon as drawn, for the launch animation
uniform sampler2D cogl_sampler1; // The style map
uniform sampler2D cogl_sampler2; // The tones of the plates in it

// The icon's square in layer 0's texture coordinates.
uniform float box_x0;
uniform float box_y0;
uniform float box_x1;
uniform float box_y1;
// Map px per screen px, for the width of anti-aliased edges.
uniform float map_px;
// 1 while a clone draws the icon (the launch animation): its colours only.
uniform float clone;
uniform float plate_r;
uniform float plate_g;
uniform float plate_b;
uniform float plate_a;
uniform float inner_r;
uniform float inner_g;
uniform float inner_b;
uniform float inner_a;
uniform float symbol_r;
uniform float symbol_g;
uniform float symbol_b;
uniform float symbol_a;
uniform float symbol_inner_r;
uniform float symbol_inner_g;
uniform float symbol_inner_b;
uniform float symbol_inner_a;
// The lit rim: brightness, width (map px), and light on the sides away from the light.
uniform float rim_a;
uniform float rim_width;
uniform float rim_base;
// How much lighter the outer plate is at its top than at its bottom.
uniform float sheen;
// How far a plate's tone takes its colour towards white or black.
uniform float tone_spread;
uniform float tint_r;
uniform float tint_g;
uniform float tint_b;
uniform float opacity;

const float MAP_SIZE = 256.0;
const float MAP_RANGE = 16.0;

float field(float v) {
    return (0.5 - v) * 2.0 * MAP_RANGE;
}

vec4 over(vec4 dst, vec4 src) {
    return src + dst * (1.0 - src.a);
}

// A plate whose outline is at distance d (map px) with outward normal n: a
// sheet of colour whose rim catches light on the sides facing the top left
// and the bottom right, as glass does.
vec4 plate(float d, vec2 n, vec3 rgb, float alpha) {
    float cover = clamp(0.5 - d / max(map_px, 0.5), 0.0, 1.0);
    float rim = 1.0 - clamp(-d / max(rim_width, 0.5), 0.0, 1.0);
    rim *= rim;
    float facing = abs(dot(n, normalize(vec2(-0.55, -0.83))));
    float light = rim_a * rim * mix(rim_base, 1.0, facing);
    vec4 c = vec4(rgb * alpha, alpha);
    c = over(c, vec4(vec3(light), light));
    return c * cover;
}

// A plate's colour and opacity at a tone: 0.5 is the colour itself, 1 towards white and more opaque, 0 towards black
// and clearer. The opacity carries the difference where the colour is white already.
vec4 toned(vec3 rgb, float alpha, float tone) {
    float d = (tone - 0.5) * 2.0 * tone_spread;
    rgb = mix(mix(rgb, vec3(1.0), max(d, 0.0) * 0.55), vec3(0.0), max(-d, 0.0) * 0.45);
    return vec4(rgb, clamp(alpha * (1.0 + d * 0.6), 0.0, 1.0));
}

vec2 gradient(vec4 l, vec4 r, vec4 u, vec4 b, int channel) {
    vec2 g;
    if (channel == 0) g = vec2(l.r - r.r, u.r - b.r);
    else if (channel == 1) g = vec2(l.g - r.g, u.g - b.g);
    else g = vec2(l.b - r.b, u.b - b.b);
    float len = length(g);
    return len > 1e-5 ? g / len : vec2(0.0);
}

// No early return, and no texture read inside a branch: a mipmapped read in a
// branch that some neighbouring pixels skip picks a wrong level on real GPUs,
// which shows as dark lines along the square's edges. Cogl may add its own
// steps after this code.
void main() {
    vec2 st = cogl_tex_coord_in[0].st;
    vec2 uv = (st - vec2(box_x0, box_y0)) / vec2(box_x1 - box_x0, box_y1 - box_y0);
    vec2 at = clamp(uv, 0.0, 1.0);
    float t = 1.0 / MAP_SIZE;
    vec4 m = texture2D(cogl_sampler1, at);
    vec4 l = texture2D(cogl_sampler1, at - vec2(t, 0.0));
    vec4 r = texture2D(cogl_sampler1, at + vec2(t, 0.0));
    vec4 u = texture2D(cogl_sampler1, at - vec2(0.0, t));
    vec4 b = texture2D(cogl_sampler1, at + vec2(0.0, t));
    vec4 icon = texture2D(cogl_sampler0, st);
    vec4 tone = texture2D(cogl_sampler2, at);

    vec3 base = toned(vec3(plate_r, plate_g, plate_b), plate_a, tone.b).rgb * (1.0 + sheen * (0.5 - at.y));
    vec4 c = plate(field(m.r), gradient(l, r, u, b, 0), base, plate_a);
    vec3 inner = vec3(inner_r, inner_g, inner_b);
    vec4 firstTone = toned(inner, inner_a, tone.r);
    vec4 deeperTone = toned(inner, inner_a, tone.g);
    vec4 first = plate(field(m.g), gradient(l, r, u, b, 1), firstTone.rgb, firstTone.a);
    vec4 deeper = plate(field(m.b), gradient(l, r, u, b, 2), deeperTone.rgb, deeperTone.a);
    c = over(over(c, first), deeper);
    // Over a plate on the outer one the symbol takes its other colour, to stand apart from that plate.
    float onInner = max(first.a / max(firstTone.a, 0.01), deeper.a / max(deeperTone.a, 0.01));
    vec4 symbol = mix(vec4(symbol_r, symbol_g, symbol_b, symbol_a),
                      vec4(symbol_inner_r, symbol_inner_g, symbol_inner_b, symbol_inner_a), clamp(onInner, 0.0, 1.0));
    c = over(c, vec4(symbol.rgb, 1.0) * (symbol.a * m.a));
    float inside = step(0.0, uv.x) * step(0.0, uv.y) * step(uv.x, 1.0) * step(uv.y, 1.0);
    c *= inside;

    // The launch animation: lightness over the tint, from its dark to its light side.
    vec3 rgb = icon.a > 0.0 ? icon.rgb / icon.a : vec3(0.0);
    float lightness = smoothstep(0.08, 0.92, dot(rgb, vec3(0.2126, 0.7152, 0.0722)));
    vec3 tint = vec3(tint_r, tint_g, tint_b);
    vec4 launch = vec4(mix(tint * 0.3, mix(tint, vec3(1.0), 0.7), lightness) * icon.a, icon.a);

    cogl_color_out = mix(c, launch, step(0.5, clone)) * opacity;
}
