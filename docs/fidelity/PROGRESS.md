# Apple-Fidelity Pass Progress Log

## Phase 0: Recon (Completed)

- **System Environment**:
  - OS: Arch Linux (rolling)
  - GNOME Shell: 50.4
  - GTK 4: 4.22.4
  - GTK 3: 3.24.52
  - libadwaita-1: 1.9.3
  - GTK 2: `gtk+-2.0` package / engines (murrine, pixmap) are not installed on this modern rolling system. (Marking GTK2 output UNVERIFIED for rendering per Phase 7 instructions).
  - Fonts: Apple SF Pro (`SF Pro`, `SF Pro Display`, `SF Pro Text`, `SF Pro Rounded`) and `Inter` are fully installed.
  - Shell DevKit / Nested: `gnome-shell --devkit`, `--headless`, `--virtual-monitor` are present. Standalone `mutter-devkit` is not installed (`/usr/bin/mutter` is present).
  - Image viewing: Checked and confirmed functional (`apple/alerts/10_alert.png` rendered and inspected).

- **Architecture Mapping**:
  - `mak-app/theme_manager.py`: Master compiler (~4,300 lines) that merges upstream base CSS with:
    - Palette overrides (`GRAPHITE_PALETTE_OVERRIDE`, `AMOLED_PALETTE_OVERRIDE`, `LIGHT_PALETTE_OVERRIDE` and glassy variants)
    - Dynamic desktop accent color synchronization
    - `generate_widgets_override()` (controls, buttons, entries, inputs, lists)
    - `generate_traffic_lights_override()` (window controls, anti-repeat)
    - `generate_popover_override()` (popovers, menus, context popups)
    - `generate_nautilus_override()` (Nautilus sidebar, pathbar, columnview, lists)
    - `generate_window_corners_override()` (CSD corners and shadows)
    - `GLASSY_CONTAINER_RULES` (translucency)
  - Base theme repository: `themes/>>>Mac-*` (6 themes: Dark solid, Dark glassy, Amoled solid, Amoled glassy, Light solid, Light glassy).
  - Live target locations (Rule 2: MUST NOT touch during dev): `~/.config/gtk-4.0/`, `~/.config/gtk-3.0/`, `~/.themes/`, `~/.gtkrc-2.0`.
  - Development staging target: `build/stage/` with sandboxed `XDG_CONFIG_HOME` and `XDG_DATA_HOME`.

- **Current Inconsistencies & Drift**:
  - AMOLED: The architecture guide claimed AMOLED was `#000000`, but `theme_manager.py` defines it as `#1e1e21` / `#131315`. Geometry and tokens must be unified, with AMOLED strictly derived by overriding background-layer tokens of Dark.
  - Light mode: Guide claimed `#f6f6f8` / `#ececf0`, but code uses `#ebebef`. Reference PNGs in `apple/` will be the definitive source of truth.
  - Widget radii and metrics: Handcoded scattered magic numbers (e.g. 5px, 6px, 9999px) across multiple 1000-line generator functions without single token source.
  - Lack of sandbox: Generator previously wrote directly to home config and ran `nautilus -q` and `gsettings`.

## Phase 1: Reference Extraction (Completed)

- **Reference Scale**: Verified at **1x (logical CSS pixels)**.
- **Reference Index**: Generated `apple/INDEX.md` covering all 21 folders, file counts, states, modes, dimensions, and links to contact sheets.
- **Visual Contact Sheets**: Generated 21 composite contact sheets in `docs/fidelity/contact/` visualizing all variants.
- **Specification & Tokens**:
  - Created `docs/fidelity/tokens.json`: Unified design tokens for geometry, colors (light, dark, amoled, glassy), and component metrics.
  - Created `docs/fidelity/SPEC.md`: Full specification mapping 21 reference folders to GTK 4, GTK 3, GTK 2, and GNOME Shell selectors, documenting exact measured numbers, and cataloging every conflict between the old guide/code and the reference PNGs.
- **Conflicts Documented**:
  - Window Corner Radius: measured at **14px** (vs 16px/12px).
  - Dialog/Alert Radius: measured at **20px** (vs 12px/16px).
  - Button Radius: standard push button is **5px** (capsule is 9999px), height **24px** (small 20px, large 28px).
  - Traffic Lights: Diameter 14px, spacing 8px, margin 13px/12px. Close: `#ff5c60`, Min: `#fac800`, Zoom: `#35c759`, Inactive: 13% alpha (light) / 17% alpha (dark).
  - Sidebar row height: **32px** (pill radius 5px); list row height: **24px** (compact 20px); column header: **28px**.

## Phase 2: Gap Analysis & Settings Audit (Completed)

- **Gap Matrix**: Created `docs/fidelity/GAP_ANALYSIS.md` cataloging all 19 component families across (GTK4, GTK3, GTK2, Shell) x (Light, Dark) with severity and reference mappings.
- **Settings Audit**:
  - Audited all 168 keys in `org.gnome.shell.extensions.mak.gschema.xml`.
  - Identified 13 dead keys with no consumers in code or UI (`sync-*`, `unround-fullscreen`, `topbar-siri-button`, etc.).
  - Identified disconnected keys (e.g. `corner-radius` only changed extension squircle, leaving GTK CSS hardcoded).
  - Formulated remediation for Phase 6 to expose all visual tunables (radii, heights, shadow, translucency) as true functional GSettings keys.

## Phase 3: QA Harness & Baseline (Completed)

- **Harness Implementation**:
  - `qa/gallery_gtk4.py`: Offscreen GTK 4 + Libadwaita gallery renderer using `Gtk.WidgetPaintable` and `Gsk.Renderer.render_texture` directly to PNG (no window flash or screen scraping).
  - `qa/gallery_gtk3.py`: Offscreen GTK 3 gallery renderer using `Gtk.OffscreenWindow`.
  - `qa/diff_pixel.py`: Visual and numeric pixel diff tool with highlight maps.
  - `qa/verify_tokens.py`: Numeric assertion suite measuring rendered widgets against tokens.
- **Baseline Capture**:
  - Captured complete pre-change visual baselines for all 6 themes x (GTK 4, GTK 3) in `qa/baseline/`.
  - Checkpoint committed.

## Phase 5: Component Family Passes

### Family 1: Windows, Headerbars & Traffic Lights (PASSED)
- **Tokens & Metrics Applied**:
  - Window Corner Radius: **14px** (from `apple/windows/110_*` and `1_window_bg.png`).
  - Traffic Light Size: **14px** circular button with 8px spacing and 13px left margin.
  - Traffic Light Colors: Close `#ff5c60`, Minimize `#fac800`, Maximize `#35c759`.
  - Inactive Window Controls: Light mode `rgba(0, 0, 0, 0.13)`, Dark/AMOLED mode `rgba(255, 255, 255, 0.17)`.
  - Chrome Palettes: Dark `#242426`, Light `#ececf0`, AMOLED `#000000` (window/view) & `#0a0a0c` (headerbar/sidebar).
- **Verification**:
  - Rendered `qa/report/family_1_windows_dark_gtk4.png` and `family_1_windows_light_gtk4.png`.
  - Side-by-side comparison generated and inspected at `qa/report/family_1_comparison.png`.
  - Numeric token assertions passed via `qa/verify_tokens.py`.

### Family 2: Buttons / Split / Segmented (PASSED)
- **Tokens & Metrics Applied**:
  - Push Button Radius: **5px** corner radius (was previously 9999px capsule!).
  - Push Button Height: **24px** regular (measured from `apple/buttons/58_*`).
  - Padding: **3px 12px** horizontal/vertical.
  - Action Button Colors: Suggested `#0a84ff` (dark) / `#0080f7` (light), Destructive `#ff453a` (dark) / `#ff383c` (light).
  - Segmented Controls / Linked Buttons: Container radius **6px**, padding **2px**, inner segment radius **5px**, height **22px** (from `apple/segmented controls/1_segmented_control.png`).
  - Split Buttons: Directional radii with LTR/RTL support (`border-top-left-radius` / `border-bottom-left-radius` 5px on lead button, 0 on trail; flipped for RTL).
  - Dialog / Alert Action Buttons: Preserved Apple UI kit **9999px** capsule radius and 26px height.
- **Verification**:
  - Rendered `qa/report/family_2_buttons_dark_gtk4.png`, `family_2_buttons_light_gtk4.png`, `family_2_buttons_dark_gtk3.png`, `family_2_buttons_light_gtk3.png`.
  - Visual side-by-side comparison verified at `qa/report/family_2_comparison.png`.
  - Isolated regression diff confirmed zero diff outside button family widgets at `qa/report/family_2_buttons_isolated_diff.png`.
  - Numeric token assertions passed via `qa/verify_tokens.py`.





