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

## 🔬 Deep Dive: Engine Architecture & Shenanigans

Achieving authentic macOS aesthetics on Wayland and GNOME Shell required solving deep compositor-level challenges involving Mutter actor hierarchies, Cogl GLSL shaders, and GTK 4/3 styling. Here is how each system works:

### 1. Hardware-Accelerated Glass Blur Engine (`blur/`)
- **BMS Application Pipeline**: Built upon Blur My Shell's applications component (`mak-extension/modules/blur/bms/components/applications.js`), the engine attaches Cogl pipeline effects directly to window actor container surfaces.
- **Mutter Culling Bypass (`hacks-level: 2`)**: Modern Mutter/Clutter culls background rendering beneath opaque window actors. Setting `hacks-level` to `2` forces GNOME Shell to preserve compositor layers behind targeted windows, enabling real-time translucent frosted glass across native and third-party apps.
- **Adaptive Opacity & Liquid Glass**: Dynamically modulates window background alpha while maintaining legible font contrast and hardware-accelerated Gaussian blur sigma (10–80).

### 2. Chromium & Electron Shader Gutter Masking Fix (`window-corners/`)
- **The Problem**: On Wayland, Chromium-based browsers, Electron apps (VS Code, Discord, Spotify), and certain XWayland clients allocate an invisible transparent gutter around the window for client-side resize handles and drop-shadow buffers. Standard corner shaders drew the rounded border around the outer boundary of this transparent buffer, creating an unsightly "floating outer border" or double border box separated from the actual web page content.
- **The Shader Mask Solution**: In `mak-extension/modules/window-corners/effect/shader/rounded_corners.frag`:
  ```glsl
  // Mask border by window content alpha to prevent drawing borders around
  // transparent resize gutters in Chromium, Electron, and Wayland apps
  borderAlpha *= clamp(cogl_color_out.a * 10.0, 0.0, 1.0);
  ```
  By modulating `borderAlpha` with the sampled window pixel alpha (`cogl_color_out.a`), the shader only renders the 16px squircle border where actual window content exists, completely eliminating phantom borders while keeping pixel-perfect squircle anti-aliasing.
- **Apple Squircle Formula**: Uses super-ellipse curvature exponent `n = 0.8` with smoothstep transitions, matching authentic macOS macOS Sonoma/Sequoia window geometry.

### 3. Maximized Window Gaps & Corner Retention (`window-gaps/`)
- **Built-in Struts Hook**: GNOME Mutter natively forces maximized windows to fill the entire monitor geometry minus top panel. `gapModule.js` hooks `Workspace.set_builtin_struts()` and `Main.layoutManager._queueUpdateRegions()`.
- **Maximized Padding Mechanics**: When a window maximizes, Mak injects strut margins (top, bottom, left, right) directly into the workspace layout manager. The maximized window is constrained within the gap bounds, showing the desktop background around all sides.
- **Uniform 16px Corner Radius**: By default GNOME and GTK themes unround corners (`border-radius: 0px`) when a window reaches maximized state (`:maximized` / `MetaWindow.maximized`). Mak overrides this:
  - `unround-maximized: false` in `cornersModule.js` preserves the squircle shader on maximized actors.
  - GTK 4/3 CSS overrides enforce `border-radius: 16px;` even with `window.maximized`, `window.tiled`, or `.maximized` classes.
  - Floating and maximized windows share identical curvature and visual hierarchy.

### 4. Notification & Menu Frosted Glass Persistence (`appearance/`)
- **The Problem**: Default GNOME Shell themes re-apply opaque solid background colors on `:hover` and `:focus` states for notification banners and popup menus, stripping blur transparency and causing sudden jarring color shifts.
- **The Fix**: `menuStyleController.js` injects high-priority CSS rules enforcing semi-translucent RGBA backgrounds (`rgba(255, 255, 255, 0.15)` for light, `rgba(20, 20, 20, 0.55)` for dark) and `backdrop-filter: blur(30px)` across default, `:hover`, and `:active` states.

### 5. Unified 16px Radii & Traffic Light Styling Across All Themes
- All 6 curated themes in `themes/` have been audited to strictly enforce 16px radii across GTK 3 (`gtk-3.0/gtk.css`), GTK 4 (`gtk-4.0/gtk.css`), and GNOME Shell:
  - `>>>Mac-Light-solid-purple`, `>>>Mac-Dark-solid-purple`, `>>>Mac-Dark-Amoled-purple`
  - `>>>Mac-Light-glassy-purple`, `>>>Mac-Dark-glassy-purple`, `>>>Mac-Dark-Amoled-glassy-purple`
- `theme_manager.py` dynamically injects CSS overrides into `~/.config/gtk-4.0/gtk.css` and `gtk-dark.css` on theme switch to guarantee traffic lights and window corners stay pixel-perfect regardless of GTK application theme overrides.

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

