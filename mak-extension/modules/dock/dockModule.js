// SPDX-License-Identifier: GPL-3.0-or-later
// Mak Dock Module Adapter

import { ExtensionManager } from './core/extensionManager.js';

export class DockModule {
    constructor(extension) {
        this._extension = extension;
        this._manager = null;
    }

    async enable() {
        if (this._manager) return;
        try {
            const { ExtensionManager: DynamicExtMgr } = await import(`./core/extensionManager.js?v=${Date.now()}`);
            this._manager = new DynamicExtMgr(this._extension);
            this._manager.enable();
        } catch (err) {
            try {
                this._manager = new ExtensionManager(this._extension);
                this._manager.enable();
            } catch (fallbackErr) {
                console.warn('[Mak] Failed to enable Dock module:', fallbackErr);
            }
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
