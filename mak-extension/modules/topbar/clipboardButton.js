// SPDX-License-Identifier: GPL-3.0-or-later
// Mak Topbar Clipboard History Indicator & Searchable Popup Card

import Clutter from 'gi://Clutter';
import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import GObject from 'gi://GObject';
import Meta from 'gi://Meta';
import Pango from 'gi://Pango';
import St from 'gi://St';

import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import * as PanelMenu from 'resource:///org/gnome/shell/ui/panelMenu.js';
import * as PopupMenu from 'resource:///org/gnome/shell/ui/popupMenu.js';

const _uid = Math.floor(Math.random() * 10000000);

export const ClipboardButton = GObject.registerClass(
    { GTypeName: `MakClipboardButton_${_uid}` },
    class ClipboardButton extends PanelMenu.Button {
        _init(extension) {
            super._init(0.5, 'MakClipboard', false);
            this._extension = extension;
            this._settings = extension.getSettings('org.gnome.shell.extensions.mak');
            this.add_style_class_name('mak-clipboard-button');

            this._clipboard = St.Clipboard.get_default();
            this._history = [];
            this._lastCopiedText = '';
            this._filterText = '';
            this._pollTimeoutId = 0;
            this._selectionId = 0;
            this._settingsChangedId = 0;

            // Topbar Icon
            this._icon = new St.Icon({
                icon_name: 'edit-paste-symbolic',
                style_class: 'system-status-icon mak-clipboard-panel-icon',
                y_align: Clutter.ActorAlign.CENTER,
            });
            this.add_child(this._icon);

            // Configure Popup Menu Container
            this.menu.box.add_style_class_name('mak-clipboard-menu');

            // Load saved history
            this._loadHistory();

            // Build UI
            this._buildPopup();

            // Monitor clipboard
            this._startMonitoring();

            // Menu open listener to refresh list and poll current content
            this._openStateId = this.menu.connect('open-state-changed', (menu, isOpen) => {
                if (isOpen) {
                    this._checkClipboard();
                    if (this._searchEntry) {
                        this._searchEntry.set_text('');
                        this._filterText = '';
                    }
                    this._renderItems();
                    GLib.timeout_add(GLib.PRIORITY_DEFAULT, 50, () => {
                        this._searchEntry?.grab_key_focus();
                        return GLib.SOURCE_REMOVE;
                    });
                }
            });

            // Listen for settings changes
            this._settingsChangedId = this._settings.connect('changed', (s, key) => {
                if (key === 'clipboard-history-size') {
                    this._trimHistory();
                    this._renderItems();
                }
            });
        }

        _getHistoryFilePath() {
            const configDir = GLib.build_filenamev([GLib.get_user_config_dir(), 'mak']);
            GLib.mkdir_with_parents(configDir, 0o755);
            return GLib.build_filenamev([configDir, 'clipboard_history.json']);
        }

        _loadHistory() {
            const path = this._getHistoryFilePath();
            if (!GLib.file_test(path, GLib.FileTest.EXISTS)) {
                this._history = [];
                return;
            }
            try {
                const [ok, bytes] = GLib.file_get_contents(path);
                if (ok && bytes) {
                    const decoder = new TextDecoder();
                    const text = decoder.decode(bytes);
                    const parsed = JSON.parse(text);
                    if (Array.isArray(parsed)) {
                        this._history = parsed;
                        this._trimHistory();
                    }
                }
            } catch (err) {
                console.warn('[Mak Clipboard] Error loading history:', err);
                this._history = [];
            }
        }

        _saveHistory() {
            if (!this._settings || !this._settings.get_boolean('clipboard-save-history'))
                return;
            const path = this._getHistoryFilePath();
            try {
                const data = JSON.stringify(this._history, null, 2);
                GLib.file_set_contents(path, data);
            } catch (err) {
                console.warn('[Mak Clipboard] Error saving history:', err);
            }
        }

        _trimHistory() {
            const max = this._settings ? this._settings.get_int('clipboard-history-size') : 30;
            if (this._history.length > max) {
                this._history = this._history.slice(0, max);
            }
        }

        _startMonitoring() {
            // 1. Selection owner-changed signal
            try {
                const selection = global.display.get_selection();
                if (selection) {
                    this._selectionId = selection.connect('owner-changed', (sel, type) => {
                        if (type === Meta.SelectionType.SELECTION_CLIPBOARD) {
                            this._checkClipboard();
                        }
                    });
                }
            } catch (err) {
                console.warn('[Mak Clipboard] Could not connect to display selection:', err);
            }

            // 2. Periodic background check (polls every 1.5 seconds)
            this._pollTimeoutId = GLib.timeout_add_seconds(GLib.PRIORITY_LOW, 2, () => {
                this._checkClipboard();
                return GLib.SOURCE_CONTINUE;
            });

            // Initial check
            this._checkClipboard();
        }

        _checkClipboard() {
            try {
                this._clipboard.get_text(St.ClipboardType.CLIPBOARD, (clip, text) => {
                    if (!text || typeof text !== 'string') return;
                    const trimmed = text.trim();
                    if (!trimmed || trimmed.length === 0) return;
                    if (this._lastCopiedText === text) return;

                    this._lastCopiedText = text;
                    this._addHistoryItem(text);
                });
            } catch (err) {
                // Ignore transient errors
            }
        }

        _addHistoryItem(text) {
            // If already present in history, move it to the top
            const existingIdx = this._history.findIndex(item => item.text === text);
            if (existingIdx !== -1) {
                const [existing] = this._history.splice(existingIdx, 1);
                existing.time = Date.now();
                this._history.unshift(existing);
            } else {
                this._history.unshift({
                    id: String(Date.now()),
                    text: text,
                    time: Date.now(),
                });
            }

            this._trimHistory();
            this._saveHistory();

            // Refresh UI if popup is currently open
            if (this.menu && this.menu.isOpen) {
                this._renderItems();
            }
        }

        _buildPopup() {
            this.menu.removeAll();

            const mainBox = new St.BoxLayout({
                vertical: true,
                style_class: 'mak-clipboard-container',
            });
            this.menu.box.add_child(mainBox);

            // ── 1. HEADER ROW ──
            const headerBox = new St.BoxLayout({
                vertical: false,
                style_class: 'mak-clipboard-header',
                y_align: Clutter.ActorAlign.CENTER,
            });

            const headerTitleBox = new St.BoxLayout({
                vertical: false,
                style_class: 'mak-clipboard-header-title-box',
                y_align: Clutter.ActorAlign.CENTER,
                x_expand: true,
            });

            const headerIcon = new St.Icon({
                icon_name: 'edit-paste-symbolic',
                style_class: 'mak-clipboard-header-icon',
                y_align: Clutter.ActorAlign.CENTER,
            });
            headerTitleBox.add_child(headerIcon);

            const titleLabel = new St.Label({
                text: 'Clipboard',
                style_class: 'mak-clipboard-header-title',
                y_align: Clutter.ActorAlign.CENTER,
            });
            headerTitleBox.add_child(titleLabel);

            this._countBadge = new St.Label({
                text: `${this._history.length}`,
                style_class: 'mak-clipboard-count-badge',
                y_align: Clutter.ActorAlign.CENTER,
            });
            headerTitleBox.add_child(this._countBadge);

            headerBox.add_child(headerTitleBox);

            // Clear All Button
            const clearBtn = new St.Button({
                style_class: 'mak-clipboard-clear-btn',
                can_focus: true,
                y_align: Clutter.ActorAlign.CENTER,
            });
            const clearBox = new St.BoxLayout({
                style_class: 'mak-clipboard-clear-box',
                y_align: Clutter.ActorAlign.CENTER,
            });
            const clearIcon = new St.Icon({
                icon_name: 'edit-clear-all-symbolic',
                style_class: 'mak-clipboard-clear-icon',
                y_align: Clutter.ActorAlign.CENTER,
            });
            const clearLabel = new St.Label({
                text: 'Clear',
                style_class: 'mak-clipboard-clear-text',
                y_align: Clutter.ActorAlign.CENTER,
            });
            clearBox.add_child(clearIcon);
            clearBox.add_child(clearLabel);
            clearBtn.set_child(clearBox);
            clearBtn.connect('clicked', () => {
                this._clearAll();
            });
            headerBox.add_child(clearBtn);

            mainBox.add_child(headerBox);

            // ── 2. SEARCH ENTRY ──
            const searchBox = new St.BoxLayout({
                style_class: 'mak-clipboard-search-box',
                x_expand: true,
            });
            this._searchEntry = new St.Entry({
                hint_text: 'Search clipboard...',
                style_class: 'mak-clipboard-search-entry',
                can_focus: true,
                x_expand: true,
            });
            this._searchEntry.set_secondary_icon(new St.Icon({
                icon_name: 'edit-find-symbolic',
                style_class: 'mak-clipboard-search-icon',
            }));
            this._searchEntry.clutter_text.connect('text-changed', () => {
                this._filterText = this._searchEntry.get_text().toLowerCase().trim();
                this._renderItems();
            });
            searchBox.add_child(this._searchEntry);
            mainBox.add_child(searchBox);

            // ── 3. SCROLLABLE ITEMS LIST ──
            this._scrollView = new St.ScrollView({
                style_class: 'mak-clipboard-scroll-view',
                hscrollbar_policy: St.PolicyType.NEVER,
                vscrollbar_policy: St.PolicyType.AUTOMATIC,
                enable_mouse_scrolling: true,
                x_expand: true,
                y_expand: true,
            });

            this._itemsBox = new St.BoxLayout({
                vertical: true,
                style_class: 'mak-clipboard-items-box',
                x_expand: true,
            });
            this._scrollView.add_child(this._itemsBox);
            mainBox.add_child(this._scrollView);

            // Initial render
            this._renderItems();
        }

        _renderItems() {
            if (!this._itemsBox) return;
            this._itemsBox.destroy_all_children();

            if (this._countBadge) {
                this._countBadge.set_text(`${this._history.length}`);
            }

            const filtered = this._filterText
                ? this._history.filter(item => item.text.toLowerCase().includes(this._filterText))
                : this._history;

            if (filtered.length === 0) {
                const emptyBox = new St.BoxLayout({
                    vertical: true,
                    style_class: 'mak-clipboard-empty-box',
                    x_align: Clutter.ActorAlign.CENTER,
                    y_align: Clutter.ActorAlign.CENTER,
                });
                const emptyIcon = new St.Icon({
                    icon_name: this._filterText ? 'edit-find-symbolic' : 'edit-paste-symbolic',
                    style_class: 'mak-clipboard-empty-icon',
                    x_align: Clutter.ActorAlign.CENTER,
                });
                const emptyLabel = new St.Label({
                    text: this._filterText ? 'No matching snippets found' : 'Clipboard is empty',
                    style_class: 'mak-clipboard-empty-label',
                    x_align: Clutter.ActorAlign.CENTER,
                });
                const emptySub = new St.Label({
                    text: this._filterText ? 'Try a different search query' : 'Copied text and snippets will appear here',
                    style_class: 'mak-clipboard-empty-sub',
                    x_align: Clutter.ActorAlign.CENTER,
                });
                emptyBox.add_child(emptyIcon);
                emptyBox.add_child(emptyLabel);
                emptyBox.add_child(emptySub);
                this._itemsBox.add_child(emptyBox);
                return;
            }

            filtered.forEach((item, index) => {
                const row = this._createItemRow(item, index + 1);
                this._itemsBox.add_child(row);
            });
        }

        _createItemRow(item, index) {
            const rowBtn = new St.Button({
                style_class: 'mak-clipboard-item-row',
                can_focus: true,
                reactive: true,
                track_hover: true,
                x_expand: true,
            });

            const rowContent = new St.BoxLayout({
                vertical: false,
                style_class: 'mak-clipboard-item-content',
                y_align: Clutter.ActorAlign.CENTER,
                x_expand: true,
            });

            // Index / Type Icon
            const indexLabel = new St.Label({
                text: `${index}`,
                style_class: 'mak-clipboard-item-index',
                y_align: Clutter.ActorAlign.CENTER,
            });
            rowContent.add_child(indexLabel);

            // Text Info Box
            const textInfoBox = new St.BoxLayout({
                vertical: true,
                style_class: 'mak-clipboard-item-text-box',
                x_expand: true,
            });

            // Single line preview (replace newlines with return symbols)
            const lines = item.text.split('\n');
            const previewText = lines[0].trim() + (lines.length > 1 ? ` ↵ (${lines.length} lines)` : '');

            const previewLabel = new St.Label({
                text: previewText,
                style_class: 'mak-clipboard-item-text',
                x_align: Clutter.ActorAlign.START,
            });
            previewLabel.clutter_text.ellipsize = Pango.EllipsizeMode.END;
            textInfoBox.add_child(previewLabel);

            // Metadata: chars and time
            const charCount = item.text.length;
            const timeAgo = this._formatTimeAgo(item.time);
            const metaLabel = new St.Label({
                text: `${charCount} chars · ${timeAgo}`,
                style_class: 'mak-clipboard-item-meta',
                x_align: Clutter.ActorAlign.START,
            });
            textInfoBox.add_child(metaLabel);

            rowContent.add_child(textInfoBox);

            // Delete action button
            const delBtn = new St.Button({
                style_class: 'mak-clipboard-item-del-btn',
                can_focus: true,
                y_align: Clutter.ActorAlign.CENTER,
            });
            const delIcon = new St.Icon({
                icon_name: 'window-close-symbolic',
                style_class: 'mak-clipboard-item-del-icon',
            });
            delBtn.set_child(delIcon);
            delBtn.connect('clicked', () => {
                this._deleteItem(item);
            });
            rowContent.add_child(delBtn);

            rowBtn.set_child(rowContent);

            // Click to copy and close
            rowBtn.connect('clicked', () => {
                this._copyItem(item);
            });

            return rowBtn;
        }

        _formatTimeAgo(timestamp) {
            if (!timestamp) return 'Recently';
            const diffMs = Date.now() - timestamp;
            const diffSec = Math.floor(diffMs / 1000);
            if (diffSec < 60) return 'Just now';
            const diffMin = Math.floor(diffSec / 60);
            if (diffMin < 60) return `${diffMin}m ago`;
            const diffHr = Math.floor(diffMin / 60);
            if (diffHr < 24) return `${diffHr}h ago`;
            const diffDays = Math.floor(diffHr / 24);
            return `${diffDays}d ago`;
        }

        _copyItem(item) {
            this._lastCopiedText = item.text;
            this._clipboard.set_text(St.ClipboardType.CLIPBOARD, item.text);

            // Re-order to top
            const idx = this._history.findIndex(i => i.id === item.id);
            if (idx !== -1) {
                const [moved] = this._history.splice(idx, 1);
                moved.time = Date.now();
                this._history.unshift(moved);
                this._saveHistory();
            }

            // Close popup
            this.menu.close();

            // Temporary visual feedback on panel icon
            this._showCopyFeedback();
        }

        _showCopyFeedback() {
            if (!this._icon) return;
            this._icon.icon_name = 'emblem-ok-symbolic';
            GLib.timeout_add(GLib.PRIORITY_DEFAULT, 1200, () => {
                if (this._icon) {
                    this._icon.icon_name = 'edit-paste-symbolic';
                }
                return GLib.SOURCE_REMOVE;
            });
        }

        _deleteItem(item) {
            const idx = this._history.findIndex(i => i.id === item.id);
            if (idx !== -1) {
                this._history.splice(idx, 1);
                this._saveHistory();
                this._renderItems();
            }
        }

        _clearAll() {
            this._history = [];
            this._saveHistory();
            this._renderItems();
        }

        destroy() {
            if (this._pollTimeoutId) {
                GLib.Source.remove(this._pollTimeoutId);
                this._pollTimeoutId = 0;
            }

            if (this._selectionId) {
                try {
                    const selection = global.display.get_selection();
                    if (selection) selection.disconnect(this._selectionId);
                } catch (e) {}
                this._selectionId = 0;
            }

            if (this._settingsChangedId) {
                try {
                    this._settings.disconnect(this._settingsChangedId);
                } catch (e) {}
                this._settingsChangedId = 0;
            }

            if (this._openStateId) {
                try {
                    this.menu.disconnect(this._openStateId);
                } catch (e) {}
                this._openStateId = 0;
            }

            super.destroy();
        }
    }
);
