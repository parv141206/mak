/** @file Provides wrapper functions for printing out debug messages. */
import { getPref } from './settings.js';
/**
 * Log a message with a [Rounded Window Corners] prefix, but only
 * when debug mode is enabled.
 */
export function logDebug(...args) {
    if (getPref('debug-mode')) {
        console.log(`[Rounded Window Corners] ${args}`);
    }
}
/**
 * Log an error with a [Rounded Window Corners] prefix.
 */
export function logError(...args) {
    console.error(`[Rounded Window Corners] ${args}`);
}
