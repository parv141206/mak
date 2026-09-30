#!@GJS@ -m
/*
 * SPDX-License-Identifier: GPL-3.0-or-later
 * forceQuitWindow.js - Standalone GTK4 "Force Quit Applications" window.
 * Launched by Kiwi Menu with `gjs -m forceQuitWindow.js`. Gets the list of
 * running applications from the extension over D-Bus and asks it to perform
 * the actual force quit; CPU and memory usage are read from /proc locally.
 */

import Adw from 'gi://Adw?version=1';
import Gdk from 'gi://Gdk?version=4.0';
import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import Gtk from 'gi://Gtk?version=4.0';
import Pango from 'gi://Pango';
import Gettext from 'gettext';

const REFRESH_INTERVAL_MS = 2000;
const BUS_NAME = 'org.gnome.Shell';
const OBJECT_PATH = '/org/gnome/Shell/Extensions/KiwiMenu';
const IFACE = 'org.gnome.Shell.Extensions.KiwiMenu.ForceQuit';

const CSS = `
list.kiwi-fq-list > row {
  min-height: 0;
  padding: 2px 8px;
}
list.kiwi-fq-list > row:selected {
  background-color: @accent_bg_color;
  color: @accent_fg_color;
}
button.kiwi-fq-button {
  min-height: 0;
  padding: 4px 14px;
}
`;

const [scriptPath] = GLib.filename_from_uri(import.meta.url);
const extensionDir = GLib.path_get_dirname(GLib.path_get_dirname(scriptPath));
Gettext.bindtextdomain('kiwimenu@kemma', GLib.build_filenamev([extensionDir, 'locale']));
Gettext.textdomain('kiwimenu@kemma');
const _ = Gettext.gettext;

function callShell(method, params) {
  return new Promise((resolve, reject) => {
    Gio.DBus.session.call(
      BUS_NAME,
      OBJECT_PATH,
      IFACE,
      method,
      params,
      null,
      Gio.DBusCallFlags.NONE,
      -1,
      null,
      (connection, result) => {
        try {
          resolve(connection.call_finish(result));
        } catch (error) {
          reject(error);
        }
      }
    );
  });
}

function readProcFile(path) {
  try {
    const [ok, bytes] = GLib.file_get_contents(path);
    return ok ? new TextDecoder().decode(bytes) : null;
  } catch {
    // Process exited or /proc entry is unreadable.
    return null;
  }
}

function readTotalCpuTicks() {
  const contents = readProcFile('/proc/stat');
  const line = contents?.split('\n', 1)[0] ?? '';
  if (!line.startsWith('cpu')) {
    return 0;
  }

  return line
    .trim()
    .split(/\s+/)
    .slice(1, 9)
    .reduce((sum, field) => sum + (Number.parseInt(field, 10) || 0), 0);
}

function readProcessCpuTicks(pid) {
  const contents = readProcFile(`/proc/${pid}/stat`);
  const closeParen = contents?.lastIndexOf(')') ?? -1;
  if (closeParen < 0) {
    return 0;
  }

  // Fields after the parenthesised command name: state(0) ... utime(11) stime(12)
  const fields = contents.slice(closeParen + 1).trim().split(/\s+/);
  const utime = Number.parseInt(fields[11], 10) || 0;
  const stime = Number.parseInt(fields[12], 10) || 0;
  return utime + stime;
}

function readProcessRssKb(pid) {
  const contents = readProcFile(`/proc/${pid}/status`);
  const match = contents?.match(/^VmRSS:\s+(\d+)\s+kB/m);
  return match ? Number.parseInt(match[1], 10) : 0;
}

function formatMemory(rssKb) {
  const mb = rssKb / 1024;
  if (mb >= 1024) {
    return `${(mb / 1024).toFixed(1)} GB`;
  }
  return `${Math.round(mb)} MB`;
}

let listBox = null;
let forceQuitButton = null;

const rows = new Map();
let rowAppIds = '';
let previousTicks = new Map();
let previousTotalTicks = 0;

function rebuildRows(apps) {
  const selectedId = listBox.get_selected_row()?._appId ?? null;

  let child;
  while ((child = listBox.get_first_child()) !== null) {
    listBox.remove(child);
  }
  rows.clear();

  for (const app of apps) {
    const box = new Gtk.Box({ orientation: Gtk.Orientation.HORIZONTAL, spacing: 8 });

    if (app.icon) {
      try {
        box.append(new Gtk.Image({
          gicon: Gio.Icon.new_for_string(app.icon),
          pixel_size: 20,
        }));
      } catch {
        // Unresolvable icon string; row simply has no icon.
      }
    }

    const nameLabel = new Gtk.Label({
      label: app.name,
      xalign: 0,
      hexpand: true,
      ellipsize: Pango.EllipsizeMode.END,
    });
    const statsLabel = new Gtk.Label({ label: '—', xalign: 1 });
    statsLabel.add_css_class('dim-label');
    statsLabel.add_css_class('numeric');

    box.append(nameLabel);
    box.append(statsLabel);

    const row = new Gtk.ListBoxRow({ child: box });
    row._appId = app.id;
    row._statsLabel = statsLabel;

    listBox.append(row);
    rows.set(app.id, row);

    if (app.id === selectedId) {
      listBox.select_row(row);
    }
  }
}

async function refresh() {
  let apps;
  try {
    const result = await callShell('ListApps', null);
    apps = JSON.parse(result.deepUnpack()[0]);
  } catch (error) {
    logError(error, 'Failed to fetch running applications from Kiwi Menu');
    return;
  }

  const appIds = apps.map((app) => app.id).join('\n');
  if (appIds !== rowAppIds) {
    rebuildRows(apps);
    rowAppIds = appIds;
  }

  const totalTicks = readTotalCpuTicks();
  const totalDelta = totalTicks - previousTotalTicks;
  const cpuCount = GLib.get_num_processors();
  const nextTicks = new Map();

  for (const app of apps) {
    let ticks = 0;
    let rssKb = 0;
    for (const pid of app.pids) {
      ticks += readProcessCpuTicks(pid);
      rssKb += readProcessRssKb(pid);
    }
    nextTicks.set(app.id, ticks);

    const row = rows.get(app.id);
    if (!row) {
      continue;
    }

    let cpuText = '—';
    const previous = previousTicks.get(app.id);
    if (previous !== undefined && totalDelta > 0) {
      const percent = Math.max(0, ((ticks - previous) / totalDelta) * cpuCount * 100);
      cpuText = `${percent.toFixed(1)}%`;
    }
    row._statsLabel.label = `${cpuText} · ${formatMemory(rssKb)}`;
  }

  previousTicks = nextTicks;
  previousTotalTicks = totalTicks;
}

function buildWindow(application) {
  const window = new Adw.ApplicationWindow({
    application,
    title: _('Force Quit Applications'),
    default_width: 340,
    default_height: 400,
  });

  const provider = new Gtk.CssProvider();
  provider.load_from_string(CSS);
  Gtk.StyleContext.add_provider_for_display(
    Gdk.Display.get_default(),
    provider,
    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
  );

  const description = new Gtk.Label({
    label: _("If an app doesn't respond for a while, select its name and click Force Quit."),
    wrap: true,
    xalign: 0,
  });

  listBox = new Gtk.ListBox({ selection_mode: Gtk.SelectionMode.SINGLE });
  listBox.add_css_class('kiwi-fq-list');
  listBox.connect('row-selected', (_box, row) => {
    forceQuitButton.sensitive = row !== null;
  });

  const scrolled = new Gtk.ScrolledWindow({
    hscrollbar_policy: Gtk.PolicyType.NEVER,
    vexpand: true,
    child: listBox,
  });
  scrolled.add_css_class('frame');

  forceQuitButton = new Gtk.Button({
    label: _('Force Quit'),
    halign: Gtk.Align.END,
    sensitive: false,
  });
  forceQuitButton.add_css_class('pill');
  forceQuitButton.add_css_class('suggested-action');
  forceQuitButton.add_css_class('kiwi-fq-button');
  forceQuitButton.connect('clicked', () => {
    const appId = listBox.get_selected_row()?._appId;
    if (!appId) {
      return;
    }
    callShell('ForceQuit', new GLib.Variant('(s)', [appId])).catch(logError);
  });

  const content = new Gtk.Box({
    orientation: Gtk.Orientation.VERTICAL,
    spacing: 12,
    margin_top: 6,
    margin_bottom: 12,
    margin_start: 12,
    margin_end: 12,
  });
  content.append(description);
  content.append(scrolled);
  content.append(forceQuitButton);

  // GTK4 has no API to disable a single titlebar button, so drop minimize
  // from the system decoration layout while keeping close and maximize.
  const baseLayout = Gtk.Settings.get_default()?.gtk_decoration_layout ?? 'icon:close';
  const decorationLayout = baseLayout
    .split(':')
    .map((side) => side.split(',').filter((btn) => btn !== 'minimize').join(','))
    .join(':');

  const toolbarView = new Adw.ToolbarView({ content });
  toolbarView.add_top_bar(new Adw.HeaderBar({ decoration_layout: decorationLayout }));
  window.set_content(toolbarView);

  GLib.timeout_add(GLib.PRIORITY_DEFAULT, REFRESH_INTERVAL_MS, () => {
    refresh().catch(logError);
    return GLib.SOURCE_CONTINUE;
  });
  refresh().catch(logError);

  return window;
}

const application = new Adw.Application({
  application_id: 'com.github.kemma.KiwiMenu.ForceQuit',
});

let window = null;
application.connect('activate', () => {
  if (!window) {
    window = buildWindow(application);
  }
  window.present();
});

application.run(null);
