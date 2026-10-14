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


