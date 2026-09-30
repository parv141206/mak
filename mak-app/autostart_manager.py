# SPDX-License-Identifier: GPL-3.0-or-later
# Mak Autostart Manager: Handles login startup desktop file

import os

HOME = os.path.expanduser("~")
AUTOSTART_DIR = os.path.join(HOME, ".config", "autostart")
AUTOSTART_FILE = os.path.join(AUTOSTART_DIR, "mak-app.desktop")

DESKTOP_CONTENT = """[Desktop Entry]
Type=Application
Name=Mak
Comment=Mak macOS Experience Sentinel & Control Center
Exec=mak-app --daemon
Icon=preferences-desktop-display
Terminal=false
Categories=Utility;Settings;
X-GNOME-Autostart-enabled=true
"""

def is_autostart_enabled():
    return os.path.exists(AUTOSTART_FILE)

def set_autostart_enabled(enabled):
    os.makedirs(AUTOSTART_DIR, exist_ok=True)
    if enabled:
        with open(AUTOSTART_FILE, "w", encoding="utf-8") as f:
            f.write(DESKTOP_CONTENT)
    else:
        if os.path.exists(AUTOSTART_FILE):
            try:
                os.remove(AUTOSTART_FILE)
            except:
                pass
    return is_autostart_enabled()
