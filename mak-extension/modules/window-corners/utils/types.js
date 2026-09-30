/** @file Provides types used throughout the codebase, mostly for storing settings. */
/**
 * Type guard to check if a WindowActor has a metaWindow
 *
 * @param actor - The actor to guard.
 * @returns Whether the actor has a `metaWindow`.
 */
export function hasMetaWindow(actor) {
    return actor.metaWindow !== null;
}
