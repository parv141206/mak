/*
 * SPDX-License-Identifier: GPL-3.0-or-later
 * forceQuitService.js - D-Bus service backing the Force Quit Applications
 * window. Provides the list of running applications (with their PIDs) and
 * performs the actual force quit, both on behalf of the GTK helper
 * (app/forceQuitWindow.js) which runs outside the shell process.
 */

import Gio from 'gi://Gio';
import Shell from 'gi://Shell';

const OBJECT_PATH = '/org/gnome/Shell/Extensions/KiwiMenu';

const FORCE_QUIT_IFACE = `
<node>
  <interface name="org.gnome.Shell.Extensions.KiwiMenu.ForceQuit">
    <method name="ListApps">
      <arg type="s" direction="out" name="apps"/>
    </method>
    <method name="ForceQuit">
      <arg type="s" direction="in" name="appId"/>
    </method>
  </interface>
</node>`;

const NON_KILLABLE_WM_CLASSES = new Set([
  'gnome-shell',
]);

// Kiwi Menu's own helper windows (Force Quit, About) must never list or kill themselves.
const SELF_ID_FRAGMENT = 'com.github.kemma.kiwimenu';

function getAppPids(app) {
  const pids = new Set();
  for (const window of app.get_windows()) {
    const pid = window.get_pid();
    if (pid > 0) {
      pids.add(pid);
    }
  }
  return [...pids];
}

function isKillableApp(app) {
  if (app.get_id()?.toLowerCase().includes(SELF_ID_FRAGMENT)) {
    return false;
  }

  const windows = app.get_windows();
  if (windows.length === 0) {
    return false;
  }

  return !windows.some((window) => {
    const wmClass = window.get_wm_class()?.toLowerCase() ?? '';
    return NON_KILLABLE_WM_CLASSES.has(wmClass) || wmClass.includes(SELF_ID_FRAGMENT);
  });
}

export class ForceQuitService {
  constructor() {
    this._dbusImpl = Gio.DBusExportedObject.wrapJSObject(FORCE_QUIT_IFACE, this);
    this._dbusImpl.export(Gio.DBus.session, OBJECT_PATH);
  }

  destroy() {
    if (this._dbusImpl) {
      this._dbusImpl.unexport();
      this._dbusImpl = null;
    }
  }

  ListApps() {
    const apps = Shell.AppSystem.get_default()
      .get_running()
      .filter(isKillableApp)
      .map((app) => ({
        id: app.get_id(),
        name: app.get_name() ?? '',
        icon: app.get_app_info()?.get_icon()?.to_string() ?? '',
        pids: getAppPids(app),
      }));

    return JSON.stringify(apps);
  }

  ForceQuit(appId) {
    const app = Shell.AppSystem.get_default()
      .get_running()
      .find((candidate) => candidate.get_id() === appId);

    if (!app || !isKillableApp(app)) {
      return;
    }

    const killedPids = new Set();
    for (const window of app.get_windows()) {
      const pid = window.get_pid();
      if (killedPids.has(pid)) {
        continue;
      }
      killedPids.add(pid);

      try {
        window.kill();
      } catch (error) {
        logError(error, `Failed to force quit ${app.get_name()}`);
      }
    }
  }
}
