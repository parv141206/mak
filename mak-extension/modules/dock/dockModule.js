// SPDX-License-Identifier: GPL-3.0-or-later
// Mak Dock Module Adapter

import { ExtensionManager } from './core/extensionManager.js';

export class DockModule {
    constructor(extension) {
        this._extension = extension;
        this._manager = null;
    }

    enable() {
        if (this._manager) return;
        try {
            this._manager = new ExtensionManager(this._extension);
            this._manager.enable();
        } catch (err) {
            console.warn('[Mak] Failed to enable Dock module:', err);
        }
    }

    disable() {
        if (!this._manager) return;
        try {
            this._manager.disable();
        } catch (err) {
            console.warn('[Mak] Failed to cleanly disable Dock module:', err);
        }
        this._manager = null;
    }
}
