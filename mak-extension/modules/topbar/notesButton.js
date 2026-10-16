// SPDX-License-Identifier: GPL-3.0-or-later
// Mak Topbar Quick Scratchpad & Notes Popover
// Elegant macOS Notes style popover card with autosave, word count, and quick copy

import Clutter from 'gi://Clutter';
import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import GObject from 'gi://GObject';
import Pango from 'gi://Pango';
import St from 'gi://St';

import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import * as PanelMenu from 'resource:///org/gnome/shell/ui/panelMenu.js';
import * as PopupMenu from 'resource:///org/gnome/shell/ui/popupMenu.js';

const _uid = Math.floor(Math.random() * 10000000);

export const NotesButton = GObject.registerClass(
    { GTypeName: `MakNotesButton_${_uid}` },
    class NotesButton extends PanelMenu.Button {
        _init(extension) {
            super._init(0.5, 'MakNotes', false);
            this._extension = extension;
            this._settings = extension.getSettings('org.gnome.shell.extensions.mak');
            this.add_style_class_name('mak-notes-button');

            this._clipboard = St.Clipboard.get_default();
            this._saveTimeoutId = 0;
            this._currentText = '';

            // Panel Icon
            this._icon = new St.Icon({
                icon_name: 'document-edit-symbolic',
                style_class: 'system-status-icon mak-notes-panel-icon',
                y_align: Clutter.ActorAlign.CENTER,
            });
            this.add_child(this._icon);

            // Configure Popup Menu Container
            this.menu.box.add_style_class_name('mak-notes-menu');

            // Load saved note content
            this._loadNote();

            // Build UI
            this._buildPopup();

            // Menu open listener to auto-focus and update stats
            this._openStateId = this.menu.connect('open-state-changed', (menu, isOpen) => {
                if (isOpen) {
                    this._updateStats();
                    GLib.timeout_add(GLib.PRIORITY_DEFAULT, 80, () => {
                        if (this._textView) {
                            this._textView.grab_key_focus();
                        }
                        return GLib.SOURCE_REMOVE;
                    });
                } else {
                    this._saveNoteImmediate();
                }
            });
        }

        _getNotesFilePath() {
            const configDir = GLib.build_filenamev([GLib.get_user_config_dir(), 'mak']);
            GLib.mkdir_with_parents(configDir, 0o755);
            return GLib.build_filenamev([configDir, 'scratchpad.json']);
        }

        _loadNote() {
            const path = this._getNotesFilePath();
            if (!GLib.file_test(path, GLib.FileTest.EXISTS)) {
                this._currentText = '';
                return;
            }
            try {
                const [ok, bytes] = GLib.file_get_contents(path);
                if (ok && bytes) {
                    const decoder = new TextDecoder();
                    const text = decoder.decode(bytes);
                    const parsed = JSON.parse(text);
                    this._currentText = parsed.text || '';
                }
            } catch (err) {
                console.warn('[Mak Notes] Could not read scratchpad:', err);
                this._currentText = '';
            }
        }

        _scheduleSave() {
            if (this._saveTimeoutId) {
                GLib.Source.remove(this._saveTimeoutId);
            }
            this._saveTimeoutId = GLib.timeout_add(GLib.PRIORITY_DEFAULT, 400, () => {
                this._saveTimeoutId = 0;
                this._saveNoteImmediate();
                return GLib.SOURCE_REMOVE;
            });
        }

        _saveNoteImmediate() {
            const path = this._getNotesFilePath();
            try {
                const data = JSON.stringify({
                    text: this._currentText,
                    modified: Date.now(),
                }, null, 2);
                GLib.file_set_contents(path, data);
            } catch (err) {
                console.warn('[Mak Notes] Could not write scratchpad:', err);
            }
        }

        _buildPopup() {
            this.menu.removeAll();

            const container = new St.BoxLayout({
                vertical: true,
                style_class: 'mak-notes-container',
            });
            this.menu.box.add_child(container);

            // ── 1. HEADER ROW ──
            const headerBox = new St.BoxLayout({
                vertical: false,
                style_class: 'mak-notes-header',
                y_align: Clutter.ActorAlign.CENTER,
            });

            const titleBox = new St.BoxLayout({
                vertical: false,
                style_class: 'mak-notes-title-box',
                y_align: Clutter.ActorAlign.CENTER,
                x_expand: true,
            });

            const headerIcon = new St.Icon({
                icon_name: 'document-edit-symbolic',
                style_class: 'mak-notes-header-icon',
                y_align: Clutter.ActorAlign.CENTER,
            });
            titleBox.add_child(headerIcon);

            const titleLabel = new St.Label({
                text: 'Quick Notes',
                style_class: 'mak-notes-header-title',
                y_align: Clutter.ActorAlign.CENTER,
            });
            titleBox.add_child(titleLabel);

            this._statsBadge = new St.Label({
                text: '0 words',
                style_class: 'mak-notes-stats-badge',
                y_align: Clutter.ActorAlign.CENTER,
            });
            titleBox.add_child(this._statsBadge);
            headerBox.add_child(titleBox);

            // Action Buttons
            const actionsBox = new St.BoxLayout({
                vertical: false,
                style_class: 'mak-notes-actions-box',
                y_align: Clutter.ActorAlign.CENTER,
            });

            // Copy Button
            const copyBtn = new St.Button({
                style_class: 'mak-notes-action-btn',
                can_focus: true,
                y_align: Clutter.ActorAlign.CENTER,
            });
            const copyIcon = new St.Icon({
                icon_name: 'edit-copy-symbolic',
                style_class: 'mak-notes-action-icon',
            });
            this._copyIcon = copyIcon;
            copyBtn.set_child(copyIcon);
            copyBtn.connect('clicked', () => {
                this._copyAll();
            });
            actionsBox.add_child(copyBtn);

            // Clear Button
            const clearBtn = new St.Button({
                style_class: 'mak-notes-action-btn',
                can_focus: true,
                y_align: Clutter.ActorAlign.CENTER,
            });
            const clearIcon = new St.Icon({
                icon_name: 'edit-clear-symbolic',
                style_class: 'mak-notes-action-icon',
            });
            clearBtn.set_child(clearIcon);
            clearBtn.connect('clicked', () => {
                this._clearNote();
            });
            actionsBox.add_child(clearBtn);

            headerBox.add_child(actionsBox);
            container.add_child(headerBox);

            // ── 2. MULTILINE TEXT VIEW ──
            this._scrollView = new St.ScrollView({
                style_class: 'mak-notes-scroll-view',
                hscrollbar_policy: St.PolicyType.NEVER,
                vscrollbar_policy: St.PolicyType.AUTOMATIC,
                enable_mouse_scrolling: true,
                x_expand: true,
                y_expand: true,
            });

            const textWrapBox = new St.BoxLayout({
                vertical: true,
                style_class: 'mak-notes-text-wrap',
                x_expand: true,
                y_expand: true,
            });

            this._textView = new Clutter.Text({
                text: this._currentText,
                editable: true,
                selectable: true,
                line_wrap: true,
                line_wrap_mode: Pango.WrapMode.WORD_CHAR,
                activatable: false,
                single_line_mode: false,
                cursor_visible: true,
            });
            this._textView.set_style('color: #f5f5f5;');

            this._textView.connect('text-changed', () => {
                this._currentText = this._textView.get_text();
                this._updateStats();
                this._scheduleSave();
            });

            textWrapBox.add_child(this._textView);
            this._scrollView.add_child(textWrapBox);
            container.add_child(this._scrollView);

            this._updateStats();
        }

        _updateStats() {
            if (!this._statsBadge) return;
            const text = this._currentText.trim();
            if (!text) {
                this._statsBadge.set_text('Empty');
                return;
            }
            const words = text.split(/\s+/).filter(w => w.length > 0).length;
            const chars = text.length;
            this._statsBadge.set_text(`${words} words · ${chars} chars`);
        }

        _copyAll() {
            if (!this._currentText) return;
            this._clipboard.set_text(St.ClipboardType.CLIPBOARD, this._currentText);

            if (this._copyIcon) {
                this._copyIcon.icon_name = 'emblem-ok-symbolic';
                GLib.timeout_add(GLib.PRIORITY_DEFAULT, 1000, () => {
                    if (this._copyIcon) {
                        this._copyIcon.icon_name = 'edit-copy-symbolic';
                    }
                    return GLib.SOURCE_REMOVE;
                });
            }
        }

        _clearNote() {
            this._currentText = '';
            if (this._textView) {
                this._textView.set_text('');
            }
            this._updateStats();
            this._saveNoteImmediate();
        }

        destroy() {
            if (this._saveTimeoutId) {
                GLib.Source.remove(this._saveTimeoutId);
                this._saveTimeoutId = 0;
            }
            this._saveNoteImmediate();

            if (this._openStateId) {
                try { this.menu.disconnect(this._openStateId); } catch (e) {}
                this._openStateId = 0;
            }

            super.destroy();
        }
    }
);
