# `effect`

This directory contains the code for applying GLSL effects to windows.

## `clip_shadow_effect.ts`

Due to a bug in GNOME, window shadows are drawn behind window contents. This
effect loads a simple Fragment shader that clips the shadow behind the window.

## `linear_filter_effect.ts`

This effect applies linear interpolation to the window, which makes windows
in the overview look less blurry.

## `rounded_corners_effect.ts`

This effect loads the actual Fragment shader that rounds the corners and draws
custom borders for the window. The class applies the effect and provides a
function to change uniforms passed to the effect.

## `shader`

This is the directory where the Fragment shaders are stored.

If you're interested in implementation details of the shader, you can read the
`shader/rounded_corners.frag` file, which is well commented and explains how
it works in great detail.
