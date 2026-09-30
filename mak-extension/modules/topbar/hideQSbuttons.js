/*
 * SPDX-License-Identifier: GPL-3.0-or-later
 * hideQSbuttons.js - Manages hiding quick settings action buttons.
 */

import GLib from 'gi://GLib';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';

const QUICK_ACTIONS = [
  {
    id: 'lock',
    settingKey: 'hide-lock-button',
  },
  {
    id: 'power',
    settingKey: 'hide-power-button',
  },
  {
    id: 'settings',
    settingKey: 'hide-settings-button',
  },
];

// Keeps the quick settings action buttons aligned with the user preferences.
export class QuickSettingsActionsController {
  constructor(settings) {
    this._settings = settings;
    this._tracked = new Map();
    this._settingsChangedIds = [];
    if (this._settings) {
      for (const { settingKey } of QUICK_ACTIONS) {
        this._settingsChangedIds.push(
          this._settings.connect(`changed::${settingKey}`, () => this._applyPreference())
        );
      }
    }

    this._sessionSignalId = Main.sessionMode?.connect('updated', () => this._sync()) ?? 0;
    this._menu = null;
    this._menuSignalId = 0;
    this._rescanSourceId = 0;

    this._sync();
  }

  destroy() {
    this._cancelRescan();
    this._disconnectMenu();

    for (const id of Array.from(this._tracked.keys())) {
      this._unregister(id);
    }

    if (this._settings) {
      for (const connectionId of this._settingsChangedIds) {
        if (connectionId) {
          this._settings.disconnect(connectionId);
        }
      }
    }
    this._settingsChangedIds = [];

    if (this._sessionSignalId) {
      try {
        Main.sessionMode.disconnect(this._sessionSignalId);
      } catch (_error) {
        // Session mode may already be gone during shutdown.
      }
    }
    this._sessionSignalId = 0;

    this._settings = null;
  }

  _sync() {
    this._ensureMenuHook();
    this._ensureTracked();
    this._applyPreference();
  }

  _ensureMenuHook() {
    const menu = Main.panel?.statusArea?.quickSettings?.menu ?? null;
    if (menu === this._menu) {
      return;
    }

    this._disconnectMenu();
    this._menu = menu;

    if (this._menu) {
      this._menuSignalId = this._menu.connect('open-state-changed', () => this._scheduleRescan());
    }
  }

  _disconnectMenu() {
    if (this._menu && this._menuSignalId) {
      try {
        this._menu.disconnect(this._menuSignalId);
      } catch (_error) {
        // Ignore disconnection errors when menu has already been disposed.
      }
    }
    this._menuSignalId = 0;
    this._menu = null;
  }

  _scheduleRescan() {
    if (this._rescanSourceId) {
      return;
    }

    this._rescanSourceId = GLib.idle_add(GLib.PRIORITY_DEFAULT, () => {
      this._rescanSourceId = 0;
      this._sync();
      return GLib.SOURCE_REMOVE;
    });
  }

  _cancelRescan() {
    if (!this._rescanSourceId) {
      return;
    }

    GLib.source_remove(this._rescanSourceId);
    this._rescanSourceId = 0;
  }

  _ensureTracked() {
    // Reaches into Shell-private layout: quickSettings._system._systemItem.child.
    // Path verified on GNOME Shell 45–50; revisit if either node is renamed upstream.
    const container =
      Main.panel?.statusArea?.quickSettings?._system?._systemItem?.child ?? null;

    if (!container) {
      this._dropTracked();
      return;
    }

    const matched = new Set();
    const children = container.get_children();

    for (const action of QUICK_ACTIONS) {
      const actor = children.find((child) => this._matchesQuickAction(action.id, child));
      if (actor) {
        matched.add(action.id);
        this._register(action.id, action.settingKey, actor);
      }
    }

    for (const id of Array.from(this._tracked.keys())) {
      if (!matched.has(id)) {
        this._unregister(id);
      }
    }
  }

  _dropTracked() {
    for (const id of Array.from(this._tracked.keys())) {
      this._unregister(id);
    }
  }

  _register(id, settingKey, actor) {
    const record = this._tracked.get(id);
    if (record?.actor === actor) {
      return;
    }

    if (record) {
      this._unregister(id);
    }

    const notifyId = actor.connect('notify::visible', () => this._onActorVisibility(id));
    const destroyId = actor.connect('destroy', () => this._onActorDestroyed(id));

    this._tracked.set(id, {
      actor,
      notifyId,
      destroyId,
      systemVisible: actor.visible,
      settingKey,
    });
  }

  _unregister(id) {
    const record = this._tracked.get(id);
    if (!record) {
      return;
    }

    const { actor, notifyId, destroyId, systemVisible } = record;

    // Disconnect signals FIRST so the visibility handler does not
    // re-hide the button when we restore its original state below.
    if (actor && notifyId) {
      try {
        actor.disconnect(notifyId);
      } catch (_error) {
        // Actor may already be disposed when tearing down.
      }
    }

    if (actor && destroyId) {
      try {
        actor.disconnect(destroyId);
      } catch (_error) {
        // Actor may already be disposed when tearing down.
      }
    }

    // Restore original visibility so buttons reappear when the extension is disabled.
    if (actor && systemVisible !== undefined) {
      try {
        actor.visible = systemVisible;
      } catch (_error) {
        // Actor may already be disposed.
      }
    }

    this._tracked.delete(id);
  }

  _applyPreference() {
    for (const record of this._tracked.values()) {
      const actor = record.actor;
      if (!actor) {
        continue;
      }

      const hide = this._settings?.get_boolean(record.settingKey) ?? false;
      if (hide) {
        if (actor.visible) {
          actor.visible = false;
        }
      } else if (actor.visible !== record.systemVisible) {
        actor.visible = record.systemVisible;
      }
    }
  }

  _onActorVisibility(id) {
    const record = this._tracked.get(id);
    if (!record?.actor) {
      return;
    }

    if (this._settings?.get_boolean(record.settingKey)) {
      if (record.actor.visible) {
        record.actor.visible = false;
      }
      return;
    }

    record.systemVisible = record.actor.visible;
  }

  _onActorDestroyed(id) {
    this._unregister(id);
    this._scheduleRescan();
  }

  _matchesQuickAction(id, actor) {
    if (!actor) {
      return false;
    }

    switch (id) {
      case 'lock':
        return actor.icon_name === 'system-lock-screen-symbolic';
      case 'power':
        return actor.icon_name === 'system-shutdown-symbolic';
      case 'settings':
        return this._isSettingsActor(actor);
      default:
        return false;
    }
  }

  _isSettingsActor(actor) {
    if (!actor) {
      return false;
    }

    if (actor._settingsApp?.get_id() === 'org.gnome.Settings.desktop') {
      return true;
    }

    const child = actor.child ?? null;
    const gicon = child?.gicon ?? null;
    if (gicon?.get_names) {
      const names = gicon.get_names();
      if (Array.isArray(names) && names.some((name) => name.includes('org.gnome.Settings'))) {
        return true;
      }
    }

    return false;
  }
}
