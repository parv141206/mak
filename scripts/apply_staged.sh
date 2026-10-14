#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Mak macOS Suite: Apply Staged Apple-Fidelity Themes to Live User Session
# Idempotent deployment script.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STAGE_DIR="${REPO_ROOT}/build/stage/themes"
DEST_THEMES="${HOME}/.themes"
DEST_GTK4="${HOME}/.config/gtk-4.0"
DEST_GTK3="${HOME}/.config/gtk-3.0"
DEST_GTK2="${HOME}/.gtkrc-2.0"

echo "============================================================"
echo "    MAK macOS Suite — Apply Staged Fidelity Themes          "
echo "============================================================"
echo ""
echo "Source Staging Directory: ${STAGE_DIR}"
echo ""
echo "Target Directories & Configurations that will be updated:"
echo "  1. User Themes Directory : ${DEST_THEMES}/"
echo "  2. GTK 4 Configuration   : ${DEST_GTK4}/gtk.css"
echo "  3. GTK 3 Configuration   : ${DEST_GTK3}/gtk.css"
echo "  4. GTK 2 Runtime RC      : ${DEST_GTK2}"
echo ""

if [[ ! -d "${STAGE_DIR}" ]]; then
    echo "ERROR: Staging directory '${STAGE_DIR}' not found!"
    echo "Please run: python3 mak-app/theme_manager.py --stage"
    exit 1
fi

# List themes found in stage
echo "Staged Themes Ready to Deploy:"
for t in "${STAGE_DIR}"/*; do
    if [[ -d "$t" ]]; then
        echo "  • $(basename "$t")"
    fi
done
echo ""

# Dry-run support
if [[ "${1:-}" == "--dry-run" ]]; then
    echo "[DRY-RUN] No changes made to system configuration."
    exit 0
fi

# Confirmation prompt unless --force or -y is provided
if [[ "${1:-}" != "-y" && "${1:-}" != "--force" ]]; then
    read -rp "Proceed with copying staged themes into live user session? [y/N] " confirm
    if [[ "${confirm}" != [yY] && "${confirm}" != [yY][eE][sS] ]]; then
        echo "Aborted by user."
        exit 0
    fi
fi

echo ""
echo "Applying staged themes..."

# 1. Ensure destination themes directory exists
mkdir -p "${DEST_THEMES}"

# 2. Deploy each staged theme idempotently
for t in "${STAGE_DIR}"/*; do
    if [[ -d "$t" ]]; then
        tname="$(basename "$t")"
        echo "  -> Installing theme: ${tname}..."
        mkdir -p "${DEST_THEMES}/${tname}"
        rsync -a --delete "${STAGE_DIR}/${tname}/" "${DEST_THEMES}/${tname}/"
    fi
done

# 3. Synchronize current active theme into user gtk-4.0 and gtk-3.0 configs
CURRENT_THEME="$(gsettings get org.gnome.desktop.interface gtk-theme 2>/dev/null | tr -d \"\'\" || echo '>>>Mac-Dark-solid-purple')"
if [[ -z "${CURRENT_THEME}" || "${CURRENT_THEME}" == "Adwaita" ]]; then
    CURRENT_THEME=">>>Mac-Dark-solid-purple"
fi

echo ""
echo "Active GTK Theme: ${CURRENT_THEME}"

if [[ -d "${DEST_THEMES}/${CURRENT_THEME}" ]]; then
    # GTK 4.0
    mkdir -p "${DEST_GTK4}"
    if [[ -f "${DEST_THEMES}/${CURRENT_THEME}/gtk-4.0/gtk.css" ]]; then
        echo "  -> Updating ${DEST_GTK4}/gtk.css"
        cp -f "${DEST_THEMES}/${CURRENT_THEME}/gtk-4.0/gtk.css" "${DEST_GTK4}/gtk.css"
    fi
    if [[ -f "${DEST_THEMES}/${CURRENT_THEME}/gtk-4.0/gtk-dark.css" ]]; then
        cp -f "${DEST_THEMES}/${CURRENT_THEME}/gtk-4.0/gtk-dark.css" "${DEST_GTK4}/gtk-dark.css"
    fi

    # GTK 3.0
    mkdir -p "${DEST_GTK3}"
    if [[ -f "${DEST_THEMES}/${CURRENT_THEME}/gtk-3.0/gtk.css" ]]; then
        echo "  -> Updating ${DEST_GTK3}/gtk.css"
        cp -f "${DEST_THEMES}/${CURRENT_THEME}/gtk-3.0/gtk.css" "${DEST_GTK3}/gtk.css"
    fi
    if [[ -f "${DEST_THEMES}/${CURRENT_THEME}/gtk-3.0/gtk-dark.css" ]]; then
        cp -f "${DEST_THEMES}/${CURRENT_THEME}/gtk-3.0/gtk-dark.css" "${DEST_GTK3}/gtk-dark.css"
    fi

    # GTK 2.0
    if [[ -f "${DEST_THEMES}/${CURRENT_THEME}/gtk-2.0/gtkrc" ]]; then
        echo "  -> Updating ${DEST_GTK2}"
        echo "include \"${DEST_THEMES}/${CURRENT_THEME}/gtk-2.0/gtkrc\"" > "${DEST_GTK2}"
    fi
fi

# 4. Flatpak override sync if flatpak command exists
if command -v flatpak &>/dev/null; then
    echo "  -> Ensuring Flatpak filesystem permissions for ~/.themes..."
    flatpak override --user --filesystem="${DEST_THEMES}:ro" 2>/dev/null || true
fi

echo ""
echo "============================================================"
echo "✔ All staged Apple-fidelity themes successfully applied!"
echo "============================================================"
