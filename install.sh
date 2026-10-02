#!/usr/bin/env bash
# ==============================================================================
# Mak Suite Installer
# Unified macOS Desktop Experience for GNOME
# Glass Dock, Top Bar & Apple Menu, Spotlight Search, Window Gaps, Squircles & Blur
# ==============================================================================

set -eo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXT_UUID="mak@local"
EXT_DEST="$HOME/.local/share/gnome-shell/extensions/$EXT_UUID"
BIN_DEST="$HOME/.local/bin"
APP_DEST="$HOME/.local/share/applications"
THEMES_DEST="$HOME/.themes"
SCHEMAS_DEST="$HOME/.local/share/glib-2.0/schemas"

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Conflicting extensions that Mak completely replaces and must be disabled
# Format: UUID|Feature Name|Mak Replacement
CONFLICTING_EXTENSIONS=(
    "blur-my-shell@aunetx|Blur My Shell|Built-in Hardware-Accelerated Glass Blur Engine"
    "aqua-dock-pro@shaque|Aqua Dock Pro|Built-in macOS Floating Glass Dock"
    "dash-to-dock@micxgx.gmail.com|Dash to Dock|Built-in macOS Floating Glass Dock"
    "dash2dock-lite@icedman.github.com|Dash2Dock Lite|Built-in macOS Floating Glass Dock"
    "rounded-window-corners@fxgn|Rounded Window Corners|Built-in Squircle Window Corner & Shader Engine"
    "rounded-window-corners-reborn@firox242|Rounded Window Corners Reborn|Built-in Squircle Window Corner & Shader Engine"
    "window-gap@amirhosseinkarimi.github.io|Window Gap|Built-in Window Gaps Engine"
    "gnome-maximized-window-gap@local|GNOME Maximized Window Gap|Built-in Window Gaps Engine"
    "search-light@icedman.github.com|Search Light|Built-in Spotlight Search Modal (Super+Space)"
    "bar-enhanced@mrvanguardia|Bar Enhanced|Built-in macOS Top Bar & Apple Menu"
    "superbar@Furkan-rgb.github.io|Superbar|Built-in macOS Top Bar & Apple Menu"
    "kiwimenu@kemma|Kiwi Menu|Built-in macOS Apple Menu"
    "kiwi@kemma|Kiwi Menu|Built-in macOS Apple Menu"
    "transparent-top-bar@ftpix.com|Transparent Top Bar|Built-in Dynamic Top Bar Frosted Glass Engine"
    "vibe-panel@pakovm|Vibe Panel|Built-in Dynamic Top Bar & Panel Styling"
    "compiz-alike-magic-lamp-effect@hermes83.github.com|Magic Lamp Effect|Built-in Dock Genie Minimize Animation"
)

print_banner() {
    echo -e "${PURPLE}${BOLD}"
    cat << "EOF"
  __  __       _    
 |  \/  |     | |   
 | \  / | __ _| | __
 | |\/| |/ _` | |/ /
 | |  | | (_| |   < 
 |_|  |_|\__,_|_|\_\
EOF
    echo -e "${NC}${CYAN}🍎 Unified macOS Desktop Suite for GNOME${NC}"
    echo -e "${CYAN}   Glass Dock • Top Bar & Apple Menu • Spotlight • Gaps • Squircles • Blur${NC}"
    echo ""
}

show_help() {
    print_banner
    echo -e "${BOLD}Usage:${NC} ./install.sh [OPTIONS]"
    echo ""
    echo -e "${BOLD}Options:${NC}"
    echo "  -y, --yes               Automatic yes to prompts; non-interactive mode"
    echo "  --disable-conflicts     Automatically detect and disable conflicting extensions"
    echo "  --uninstall             Uninstall Mak extension, binaries, and desktop entries"
    echo "  -h, --help              Show this help menu and exit"
    echo ""
    echo -e "${BOLD}Examples:${NC}"
    echo "  ./install.sh                    # Interactive standard installation"
    echo "  ./install.sh --disable-conflicts # Install and automatically disable conflicting extensions"
    echo "  ./install.sh -y                 # Non-interactive automated install"
    echo "  ./install.sh --uninstall       # Remove Mak suite"
    echo ""
}

AUTO_YES=false
DISABLE_CONFLICTS=false
DO_UNINSTALL=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        -y|--yes)
            AUTO_YES=true
            shift
            ;;
        --disable-conflicts)
            DISABLE_CONFLICTS=true
            shift
            ;;
        --uninstall)
            DO_UNINSTALL=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Run './install.sh --help' for usage."
            exit 1
            ;;
    esac
done

uninstall_mak() {
    echo -e "${YELLOW}🗑️  Uninstalling Mak Suite...${NC}"
    
    if command -v gnome-extensions >/dev/null 2>&1; then
        echo "Disabling Mak extension..."
        gnome-extensions disable "$EXT_UUID" 2>/dev/null || true
    fi
    
    echo "Removing extension directory: $EXT_DEST"
    rm -rf "$EXT_DEST"
    
    echo "Removing launcher: $BIN_DEST/mak-app"
    rm -f "$BIN_DEST/mak-app"
    
    echo "Removing desktop entry: $APP_DEST/mak-app.desktop"
    rm -f "$APP_DEST/mak-app.desktop"
    if command -v update-desktop-database >/dev/null 2>&1; then
        update-desktop-database "$APP_DEST" 2>/dev/null || true
    fi

    echo "Removing installed schemas..."
    rm -f "$SCHEMAS_DEST/org.gnome.shell.extensions.mak.gschema.xml"
    if command -v glib-compile-schemas >/dev/null 2>&1; then
        glib-compile-schemas "$SCHEMAS_DEST" 2>/dev/null || true
    fi

    echo -e "${GREEN}✅ Mak Suite uninstalled successfully.${NC}"
    exit 0
}

if [ "$DO_UNINSTALL" = true ]; then
    uninstall_mak
fi

print_banner

# ==============================================================================
# Step 1: Pre-flight checks and dependencies
# ==============================================================================
echo -e "${BOLD}${BLUE}==> [1/6] Checking system prerequisites and dependencies...${NC}"

MISSING_DEPS=()
for cmd in glib-compile-schemas gsettings gnome-extensions python3; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        MISSING_DEPS+=("$cmd")
    fi
done

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo -e "${RED}❌ Missing required system tools: ${MISSING_DEPS[*]}${NC}"
    echo "Please install them via your distribution package manager."
    exit 1
fi

# Check Python GObject and Libadwaita bindings
PY_CHECK=$(python3 -c "
try:
    import gi
    gi.require_version('Gtk', '4.0')
    gi.require_version('Adw', '1')
    gi.require_version('Gio', '2.0')
    from gi.repository import Gtk, Adw, Gio
    print('OK')
except Exception as e:
    print('FAIL: ' + str(e))
" 2>/dev/null || echo "FAIL")

if [[ "$PY_CHECK" != *"OK"* ]]; then
    echo -e "${YELLOW}⚠️  Python GTK 4 / Libadwaita bindings missing or incomplete (${PY_CHECK}).${NC}"
    echo -e "   The Mak Control Center (GUI) requires ${BOLD}python3-gobject${NC}, ${BOLD}gtk4${NC}, and ${BOLD}libadwaita${NC}."
    echo ""
    echo -e "   ${CYAN}To install required packages:${NC}"
    echo -e "     ${BOLD}Arch Linux:${NC}     sudo pacman -S python-gobject gtk4 libadwaita glib2 gnome-shell-extensions"
    echo -e "     ${BOLD}Fedora:${NC}         sudo dnf install python3-gobject gtk4 libadwaita glib2 gnome-shell-extension-user-theme"
    echo -e "     ${BOLD}Ubuntu/Debian:${NC}  sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 libglib2.0-bin gnome-shell-extension-manager"
    echo ""
    if [ "$AUTO_YES" = false ]; then
        read -rp "Continue installation anyway? [y/N]: " proceed
        if [[ ! "$proceed" =~ ^[Yy]$ ]]; then
            echo "Installation aborted."
            exit 1
        fi
    fi
else
    echo -e "  ${GREEN}✓${NC} Python 3, PyGObject, GTK 4, and Libadwaita detected."
fi

# ==============================================================================
# Step 2: Install Curated macOS Themes
# ==============================================================================
echo -e "${BOLD}${BLUE}==> [2/6] Installing curated macOS themes into ~/.themes/...${NC}"
mkdir -p "$THEMES_DEST"
if [ -d "$DIR/themes" ]; then
    cp -r "$DIR/themes/"* "$THEMES_DEST/"
    echo -e "  ${GREEN}✓${NC} Synchronized 6 curated macOS themes to $THEMES_DEST:"
    echo "    - >>>Mac-Dark-solid-purple      (macOS Sonoma graphite dark)"
    echo "    - >>>Mac-Light-solid-purple     (Crisp Apple light mode)"
    echo "    - >>>Mac-Dark-Amoled-purple     (Pitch Black OLED dark)"
    echo "    - >>>Mac-Dark-glassy-purple     (Frosted translucent graphite)"
    echo "    - >>>Mac-Light-glassy-purple    (Frosted translucent light)"
    echo "    - >>>Mac-Dark-Amoled-glassy-purple (Frosted translucent OLED)"
fi

# Ensure GTK 3 & GTK 4 asset symlinks exist
mkdir -p "$HOME/.config/gtk-3.0" "$HOME/.config/gtk-4.0"
THEME_PREF="$THEMES_DEST/>>>Mac-Light-solid-purple"
[ ! -d "$THEME_PREF" ] && THEME_PREF="$THEMES_DEST/>>>Mac-Dark-solid-purple"

if [ -d "$THEME_PREF" ]; then
    [ -d "$THEME_PREF/gtk-3.0/windows-assets" ] && ln -sfn "$THEME_PREF/gtk-3.0/windows-assets" "$HOME/.config/gtk-3.0/windows-assets"
    [ -d "$THEME_PREF/gtk-3.0/assets" ] && ln -sfn "$THEME_PREF/gtk-3.0/assets" "$HOME/.config/gtk-3.0/assets"
    [ -d "$THEME_PREF/gtk-4.0/windows-assets" ] && ln -sfn "$THEME_PREF/gtk-4.0/windows-assets" "$HOME/.config/gtk-4.0/windows-assets"
    [ -d "$THEME_PREF/gtk-4.0/assets" ] && ln -sfn "$THEME_PREF/gtk-4.0/assets" "$HOME/.config/gtk-4.0/assets"
    echo -e "  ${GREEN}✓${NC} GTK 3 and GTK 4 window control asset symlinks configured."
fi

# ==============================================================================
# Step 3: Compile schemas and install GNOME Shell extension
# ==============================================================================
echo -e "${BOLD}${BLUE}==> [3/6] Compiling GSettings schemas and installing Mak Extension...${NC}"
mkdir -p "$SCHEMAS_DEST"

# Compile local schemas directory
glib-compile-schemas "$DIR/mak-extension/schemas"

# Copy schema to user schemas and compile
cp "$DIR/mak-extension/schemas/"*.gschema.xml "$SCHEMAS_DEST/"
glib-compile-schemas "$SCHEMAS_DEST"
echo -e "  ${GREEN}✓${NC} GSettings schemas compiled and installed into $SCHEMAS_DEST."

# Install extension
rm -rf "$EXT_DEST"
mkdir -p "$EXT_DEST"
cp -r "$DIR/mak-extension/"* "$EXT_DEST/"
echo -e "  ${GREEN}✓${NC} Mak GNOME Shell extension installed into $EXT_DEST."

# ==============================================================================
# Step 4: Detect and resolve conflicting extensions
# ==============================================================================
echo -e "${BOLD}${BLUE}==> [4/6] Auditing and resolving conflicting GNOME extensions...${NC}"

ENABLED_EXTENSIONS=$(gnome-extensions list --enabled 2>/dev/null || true)
ACTIVE_CONFLICTS=()

for item in "${CONFLICTING_EXTENSIONS[@]}"; do
    IFS="|" read -r uuid name replaced_by <<< "$item"
    if echo "$ENABLED_EXTENSIONS" | grep -qx "$uuid"; then
        ACTIVE_CONFLICTS+=("$uuid|$name|$replaced_by")
    fi
done

if [ ${#ACTIVE_CONFLICTS[@]} -gt 0 ]; then
    echo -e "${YELLOW}${BOLD}⚠️  Detected ${#ACTIVE_CONFLICTS[@]} active extension(s) that conflict with Mak:${NC}"
    echo ""
    printf "  %-38s %-26s %s\n" "Extension ID" "Name" "Replaced By Mak Feature"
    echo "  -----------------------------------------------------------------------------------------------"
    for conflict in "${ACTIVE_CONFLICTS[@]}"; do
        IFS="|" read -r uuid name replaced_by <<< "$conflict"
        printf "  %-38s %-26s %s\n" "$uuid" "$name" "$replaced_by"
    done
    echo ""
    echo -e "${YELLOW}Running these alongside Mak causes compositor shader conflicts, broken window blur,${NC}"
    echo -e "${YELLOW}double dock/panel overlaps, and duplicate window borders.${NC}"
    echo ""

    DISABLE_NOW=false
    if [ "$DISABLE_CONFLICTS" = true ] || [ "$AUTO_YES" = true ]; then
        DISABLE_NOW=true
    else
        read -rp "Would you like Mak to automatically disable these conflicting extensions now? [Y/n]: " ans
        if [[ -z "$ans" || "$ans" =~ ^[Yy]$ ]]; then
            DISABLE_NOW=true
        fi
    fi

    if [ "$DISABLE_NOW" = true ]; then
        for conflict in "${ACTIVE_CONFLICTS[@]}"; do
            IFS="|" read -r uuid name replaced_by <<< "$conflict"
            echo -e "  Disabling ${CYAN}$uuid${NC} ($name)..."
            gnome-extensions disable "$uuid" 2>/dev/null || true
        done
        echo -e "  ${GREEN}✓${NC} All conflicting extensions have been disabled."
    else
        echo -e "  ${YELLOW}Note:${NC} Conflicting extensions were left active. If you encounter UI overlap, disable them manually."
    fi
else
    echo -e "  ${GREEN}✓${NC} No active conflicting extensions found. System is clean!"
fi

# Enable Mak extension
echo -e "  Enabling Mak extension (${CYAN}$EXT_UUID${NC})..."
gnome-extensions enable "$EXT_UUID" 2>/dev/null || true

# Check user-theme extension
if echo "$ENABLED_EXTENSIONS" | grep -q "user-theme"; then
    echo -e "  ${GREEN}✓${NC} 'User Themes' extension is enabled (required for GNOME Shell macOS theme)."
else
    if gnome-extensions list | grep -q "user-theme"; then
        echo -e "  Enabling 'User Themes' extension..."
        gnome-extensions enable user-theme@gnome-shell-extensions.gcampax.github.com 2>/dev/null || true
    else
        echo -e "  ${YELLOW}Tip:${NC} Install and enable the 'User Themes' extension to allow Mak to style GNOME Shell directly."
    fi
fi

# ==============================================================================
# Step 5: Install Mak Control Center Binary & Desktop Entry
# ==============================================================================
echo -e "${BOLD}${BLUE}==> [5/6] Installing Mak Control Center launcher and desktop entry...${NC}"
mkdir -p "$BIN_DEST"
cat << EOF > "$BIN_DEST/mak-app"
#!/usr/bin/env bash
exec python3 "$DIR/mak-app/main.py" "\$@"
EOF
chmod +x "$BIN_DEST/mak-app"
echo -e "  ${GREEN}✓${NC} Created launcher binary: $BIN_DEST/mak-app"

mkdir -p "$APP_DEST"
cat << EOF > "$APP_DEST/mak-app.desktop"
[Desktop Entry]
Type=Application
Name=Mak
GenericName=macOS Experience Control Center
Comment=Unified settings and sentinel for macOS Dock, Top Bar, Spotlight, and Themes
Exec=$BIN_DEST/mak-app
Icon=preferences-desktop-display
Terminal=false
Categories=Utility;Settings;DesktopSettings;
Keywords=mac;macos;dock;topbar;spotlight;theme;gaps;
StartupNotify=true
EOF
echo -e "  ${GREEN}✓${NC} Installed desktop entry: $APP_DEST/mak-app.desktop"

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$APP_DEST" 2>/dev/null || true
fi

# ==============================================================================
# Step 6: Initialize Theme Overrides & Traffic Lights
# ==============================================================================
echo -e "${BOLD}${BLUE}==> [6/6] Generating initial GTK 3 & GTK 4 window styling and traffic lights...${NC}"
python3 -c "
import sys, os
sys.path.insert(0, '$DIR/mak-app')
try:
    import theme_manager
    theme_manager.update_titlebar_buttons()
    print('  ✓ Initialized GTK stylesheets with anti-repeat traffic light rules and window corner geometry.')
except Exception as e:
    print(f'  Note on theme initialization: {e}')
"

echo ""
echo -e "${GREEN}${BOLD}══════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}${BOLD}             🎉 Mak Suite Installed Successfully!                    ${NC}"
echo -e "${GREEN}${BOLD}══════════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  ${BOLD}🚀 Quick Start:${NC}"
echo -e "    1. Open ${CYAN}Mak Control Center${NC} by typing ${BOLD}mak-app${NC} in terminal or"
echo -e "       selecting ${BOLD}Mak${NC} from your application menu."
echo -e "    2. Press ${BOLD}Super + Space${NC} anytime to trigger ${CYAN}Spotlight Search${NC}."
echo -e "    3. Customize Dock size, magnification physics, gap margins, squircle radii,"
echo -e "       and curated themes right from the Mak Control Center."
echo ""
echo -e "  ${BOLD}💡 Note for Wayland / GNOME Shell Users:${NC}"
echo -e "    If the extension does not appear immediately, log out and log back in, or run:"
echo -e "    ${BOLD}gnome-extensions enable mak@local${NC}"
echo ""
