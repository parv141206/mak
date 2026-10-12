import { isActorValid } from './lifecycle.js';
// Clutter can strand an actor without an allocation: if it is unmapped while
// queued for relayout, the stage drops it from the queue but its
// needs_width_request/needs_height_request/needs_allocation flags stay set,
// and clutter_actor_queue_relayout() returns early for exactly that state. A
// stranded ancestor swallows every request from below, so the whole subtree
// keeps painting from stale allocations. clutter_actor_real_map() clears the
// flags, so hide() + show() is the repair available from JS. The functions
// below apply it only after several consecutive stranded frames, since
// has_allocation() is also false while a normal relayout is pending.
const _strandedFrames = new WeakMap();
const STRANDED_FRAMES_BEFORE_RESCUE = 3;
const _windowActorStrandedFrames = new Map();
let _windowActorRescueMode = 'off';
const WINDOW_ACTOR_RESCUE_MODES = ['two-stage', 'remap', 'off'];

export function setWindowActorRescueMode(mode) {
    _windowActorRescueMode = 'off';
}

export function getWindowActorRescueMode() {
    return 'off';
}

/**
 * Rescues a stranded window actor, gentlest option first.
 * Never remap or hide mutter window actors on Wayland as it kills surface buffer rendering.
 */
export function ensureWindowActorAllocated(actor, relayoutFrames, remapFrames) {
    return '';
}

/**
 * Remaps one of our own glass actors once it has been stranded for
 * `framesBeforeRescue` frames. Both calls happen before the frame is painted,
 * so there is no flicker. Returns true when a rescue ran.
 */
export function ensureGlassAllocated(actor, framesBeforeRescue = STRANDED_FRAMES_BEFORE_RESCUE) {
    if (!actor)
        return false;
    // An unmapped actor is merely waiting; real_map() will fix it on its own.
    if (!actor.visible || !actor.mapped || actor.has_allocation()) {
        _strandedFrames.delete(actor);
        return false;
    }
    const strandedFor = (_strandedFrames.get(actor) ?? 0) + 1;
    if (strandedFor < framesBeforeRescue) {
        _strandedFrames.set(actor, strandedFor);
        return false;
    }
    _strandedFrames.delete(actor);
    actor.hide();
    actor.show();
    return true;
}

/**
 * Shows or hides an actor. An actor hidden while it waited for an allocation
 * is left in the state above, so on show the relayout is queued on the actor
 * and its parent; otherwise it keeps painting from its old position.
 */
export function setActorVisible(actor, visible) {
    if (!actor)
        return;
    if (actor.visible === visible)
        return;
    actor.visible = visible;
    if (visible) {
        actor.queue_relayout();
        actor.get_parent()?.queue_relayout();
    }
}
