// SPDX-License-Identifier: GPL-3.0-or-later
// Mak Spotlight Search Module Adapter

import Gio from 'gi://Gio';
import SearchBar from './extension.js';

export class SpotlightModule {
    constructor(extension) {
        this._extension = extension;
        this._searchBar = null;
    }

    enable() {
        if (this._searchBar) return;
        try {
            const dir = this._extension.dir ?? Gio.File.new_for_path(this._extension.path);
            this._searchBar = new SearchBar({
                uuid: 'mak-spotlight@local',
                path: this._extension.path,
                dir: dir,
                'settings-schema': 'org.gnome.shell.extensions.superbar',
            });
            this._searchBar.getSettings = (schema) => this._extension.getSettings(schema || 'org.gnome.shell.extensions.superbar');
            this._searchBar.enable();
        } catch (err) {
            console.warn('[Mak Spotlight] Failed to enable Spotlight:', err);
        }
    }

    disable() {
        if (!this._searchBar) return;
        try {
            this._searchBar.disable();
        } catch (err) {
            console.warn('[Mak Spotlight] Failed to disable Spotlight:', err);
        }
        this._searchBar = null;
    }
}
