#!/usr/bin/env bash
# ==============================================================================
# Mak Suite Installer
# Unified macOS Experience Suite: Glass Dock, Top Bar, Spotlight, Gaps, Corners
# ==============================================================================

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXT_UUID="mak@local"
EXT_DEST="$HOME/.local/share/gnome-shell/extensions/$EXT_UUID"
BIN_DEST="$HOME/.local/bin"
APP_DEST="$HOME/.local/share/applications"

echo "🍎 Installing Mak: Unified macOS Experience Suite..."

# 1. Compile schemas
echo "📦 Compiling schemas..."
glib-compile-schemas "$DIR/mak-extension/schemas"
mkdir -p "$HOME/.local/share/glib-2.0/schemas"
cp "$DIR/mak-extension/schemas/"*.gschema.xml "$HOME/.local/share/glib-2.0/schemas/"
glib-compile-schemas "$HOME/.local/share/glib-2.0/schemas"

# 2. Install GNOME Shell Extension
echo "🧩 Installing GNOME Shell Extension to $EXT_DEST..."
rm -rf "$EXT_DEST"
mkdir -p "$EXT_DEST"
cp -r "$DIR/mak-extension/"* "$EXT_DEST/"

# 3. Ensure GTK 3 & GTK 4 asset symlinks for macOS window controls
echo "🎨 Ensuring GTK window control asset symlinks..."
THEME_DIR="$HOME/.themes/>>>Mac-Dark-solid-purple"
if [ -d "$THEME_DIR" ]; then
    mkdir -p "$HOME/.config/gtk-3.0" "$HOME/.config/gtk-4.0"
    [ -d "$THEME_DIR/gtk-3.0/windows-assets" ] && ln -sfn "$THEME_DIR/gtk-3.0/windows-assets" "$HOME/.config/gtk-3.0/windows-assets"
    [ -d "$THEME_DIR/gtk-3.0/assets" ] && ln -sfn "$THEME_DIR/gtk-3.0/assets" "$HOME/.config/gtk-3.0/assets"
    [ -d "$THEME_DIR/gtk-4.0/windows-assets" ] && ln -sfn "$THEME_DIR/gtk-4.0/windows-assets" "$HOME/.config/gtk-4.0/windows-assets"
    [ -d "$THEME_DIR/gtk-4.0/assets" ] && ln -sfn "$THEME_DIR/gtk-4.0/assets" "$HOME/.config/gtk-4.0/assets"
fi

# 4. Install Mak Control Center Binary
echo "🚀 Installing Mak Control Center launcher..."
mkdir -p "$BIN_DEST"
cat << EOF > "$BIN_DEST/mak-app"
#!/usr/bin/env bash
exec python3 "$DIR/mak-app/main.py" "\$@"
EOF
chmod +x "$BIN_DEST/mak-app"

# 5. Install Desktop Entry
echo "🖥️  Installing Desktop entry..."
mkdir -p "$APP_DEST"
cp "$DIR/mak-app/mak-app.desktop" "$APP_DEST/"
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$APP_DEST" || true
fi

echo "✅ Mak installed successfully!"
echo ""
echo "To resolve conflicts with old extensions and activate Mak, run:"
echo "    python3 $DIR/mak-app/main.py"
echo "Or launch 'Mak' from your application menu!"
