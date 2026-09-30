# 🍎 Mak: Unified macOS Desktop Suite for GNOME

**Mak** integrates all macOS desktop features — floating glass dock, top menu bar with Apple menu, Spotlight search, squircle rounded corners, outer window gaps, drop shadows, and glass blur engine — into a **single, standalone codebase** with a dedicated **GTK 4 + Libadwaita Control Center** (`mak-app`) and unified **GNOME Shell Extension** (`mak@local`).

Zero external extension dependencies. All configuration options and subsettings are directly integrated and managed from one central place.

---

## 🌟 Architecture & Highlights

Previously, achieving a macOS experience required installing and managing 7 disparate extensions (`aqua-dock-pro`, `bar-enhanced`, `blur-my-shell`, `gnome-maximized-window-gap`, `kiwi-menu`, `rounded-window-corners`, `superbar`), leading to layout conflicts, competing stylesheets, broken blur shaders, and scattered settings.

**Mak replaces them with a single integrated system:**
- **Single Extension Codebase** (`mak-extension/`): Self-contained submodules (`dock/`, `topbar/`, `spotlight/`, `window-gaps/`, `window-corners/`, `blur/`) running synchronously under `org.gnome.shell.extensions.mak`.
- **Comprehensive Control Center** (`mak-app/`): Built with GTK 4 and Libadwaita. Exposes over 140 granular settings and subsettings across 8 dedicated sections.
- **Dual-Bus Settings Sync** (`settings_bridge.py`): Configures Mak's master schema while dynamically updating active desktop components in real-time.

---

## 🚀 Granular Feature & Subsettings Breakdown

### 1. ⛵ macOS Floating Glass Dock
- **Layout & Geometry**: Screen position (Bottom, Left, Right), alignment (Center, Start, End), resting icon size (24px–128px), icon spacing, floating edge margin, overall dock scale factor, auto-shrink to fit display, multi-monitor dock, isolate monitors, isolate workspaces.
- **Magnification & Physics Engine**: Peak magnification factor (1.0x–3.5x), spread range, curve sharpness falloff, follow animation smoothness, spring tension, spring damping, hover icon lift, launch bounce height, bounce decay factor.
- **Glass Pill & Appearance**: Pill corner radius, background translucency opacity, background tint, border stroke width, border color, pill thickness, automatic thickness scaling.
- **Autohide & Pressure**: Autohide behavior (Never / Always Visible, Intellihide / Dodge, Always Hide), hide delay, edge reveal pressure barrier, autohide handle indicator, pressure-sense dwell reveal, dwell sensitivity, lock layout.
- **Interactions & Clicks**: Click focused app to minimize, primary left-click action (smart, minimize, cycle, previews, nothing), middle-click action (new window, smart, nothing), scroll wheel action (minimize/restore, cycle, nothing), drag icon outside to launch.
- **Indicators & Badges**: Indicator styles (glow dots, glowing bar, single dot, multiple dots, solid line, pill), dot size, indicator color, multi-window count dots, notification counter badges, badge color.
- **Stacks & Special Items**: Applications launcher grid button, trash can with full/empty states, Downloads folder stack, opening view style (fan, grid, list), max files count, sort order (newest, name, type), mounted drives, removable media, network shares.
- **Live Window Previews & Tooltips**: Live window thumbnail previews on hover, preview delay, preview size, hidden vs all windows filter, close buttons, app tooltips, genie (magic lamp) minimize animation and duration.

### 2. 🍏 macOS Menu Bar & Apple Menu
- **System Branding & Logo**: Apple logo menu on panel left, custom logo icons (Apple, Arch Linux, Fedora, Debian, Ubuntu, Linux Tux), active application name in bold beside menu, hide default GNOME 'Activities' button, macOS keyboard accelerator symbols (⌘ ⌥ ^ ⎋), custom App Store launcher command, Force Quit keyboard shortcut.
- **Panel Styling & Frosted Glass**: Dynamic frosted glass blur effect, blur radius, panel transparency factor, smooth macOS pill button styling for status indicators.
- **Quick Settings Customization**: Toggle individual quick settings actions (hide lock screen button, hide power/shutdown button, hide settings button).

### 3. 🔍 Spotlight Search Modal (`Super + Space`)
- **Modal Geometry & Layout**: Trigger shortcut, search modal bar width (400px–1200px), vertical placement (center, top, bottom), glass surface opacity, max concurrent search results, adaptive ranking history for frequent applications.
- **Integrated Providers & Services**: Default web search engine (Google, DuckDuckGo, Bing, Brave, Ecosia, Kagi), installed applications search, open windows search across workspaces, local files and documents, clipboard history search, inline mathematical calculator evaluation, live weather forecast lookup, dictionary word definitions, foreign currency exchange rates, system commands (lock, sleep, restart, shutdown), GNOME search providers integration.

### 4. 🪟 Window Management: Gaps, Corners & Shadows
- **Outer Window Gaps**: Enable/disable outer padding, uniform mode, uniform gap size (0px–200px), independent per-edge margins (top, bottom, left, right), retain gaps for maximized windows.
- **Rounded Corners & Borders**: Anti-aliased squircle window shader, corner radius, Apple super-ellipse smoothing curvature exponent (0.8 = authentic Apple curvature), window border stroke width, border color, retain corners when maximized, retain corners in fullscreen, bypass for native Libadwaita / LibHandy apps.
- **macOS Window Drop Shadows**: Drop shadows with realistic depth, retain shadows for maximized windows, focused window vertical offset, blur radius, opacity percentage, background/unfocused window vertical offset, blur radius, and opacity.

### 5. 🔮 Hardware-Accelerated Glass Blur Engine
- **Gaussian Kernel Tuning**: Global blur master toggle, blur sigma radius (10–80), glass brightness luminance multiplier, film grain / noise amount.
- **Target Surfaces**: Independent toggles for top menu bar, dock pill background, activities overview wallpaper, and application folder popups.

### 6. 🎨 Curated macOS Themes & Global Synchronization
- **Curated Themes** (in `~/.themes/`):
  - `>>>Mac-Dark-Amoled-purple`: Pure OLED black (`#0c0d12`) with vibrant Apple purple accents.
  - `>>>Mac-Dark-solid-purple`: macOS Sonoma graphite dark mode.
  - `>>>Mac-Light-solid-purple`: Crisp, luminous Apple light mode.
- **One-Click Global Apply**: Synchronizes simultaneously across:
  - GNOME Shell User Theme
  - GTK 4 / Libadwaita (`~/.config/gtk-4.0/`)
  - GTK 3 (`~/.config/gtk-3.0/`)
  - GTK 2 (`~/.gtkrc-2.0`)
  - Flatpak sandbox overrides (`flatpak override --user`)

---

## 🛠️ Launching the Control Center

Launch from terminal:
```bash
mak-app
```
Or open **Mak** from your application launcher / App Grid.

---

## 📦 Installation & Schema Rebuild

```bash
cd /home/parv/projects/mak
./install.sh
```
