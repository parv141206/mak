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

### Family 3: Text Fields / Search / Steppers (PASSED)
- **Tokens & Metrics Applied**:
  - Standard Entry Radius: **5px** (measured from `apple/text fields/1_text_field.png`).
  - Standard Entry Height: **22px** regular, padding **2px 8px**.
  - Focus Ring: **3px** outer glow (`rgba(0, 128, 247, 0.50)` light, `rgba(10, 132, 255, 0.60)` dark).
  - Search Fields: **9999px** capsule radius, **22px** height, internal clear/search icons (from `apple/search fields/2_search_field.png`).
  - Steppers / SpinButtons: **5px** container radius, **22px** height, **4px** inner button radius with chevron symbols (from `apple/steppers/1_stepper_no_field.png`).
  - Password Entry: Inherits **22px** height and **5px** radius.
- **Verification**:
  - Rendered `qa/report/family_3_entries_dark_gtk4.png`, `family_3_entries_light_gtk4.png`, `family_3_entries_dark_gtk3.png`, `family_3_entries_light_gtk3.png`.
  - Visual side-by-side comparison verified at `qa/report/family_3_comparison.png`.
  - Isolated regression diff confirmed zero diff outside entries family widgets at `qa/report/family_3_entries_isolated_diff.png`.
  - Numeric token assertions passed via `qa/verify_tokens.py`.

### Family 4: Pop-ups / Pull-downs / Combos (PASSED)
- **Tokens & Metrics Applied**:
  - Pop-up / Dropdown Button Radius: **5px** (was previously 9999px capsule in forms).
  - Height: **24px** regular, padding **3px 10px** (measured from `apple/pop ups and pull down buttons/1_pop_up_button.png` and `apple/combo boxes/1_combo_box.png`).
  - Dropdown Arrow: 12px chevron symbol with muted alpha label color.
  - Universal Selector Coverage: Extended to all `dropdown > button`, `combobox button`, and `menubutton:not(.flat):not(.titlebutton) > button`.
  - Focus Ring: **3px** outer glow ring.
- **Verification**:
  - Rendered `qa/report/family_4_combos_dark_gtk4.png`, `family_4_combos_light_gtk4.png`, `family_4_combos_dark_gtk3.png`, `family_4_combos_light_gtk3.png`.
  - Visual side-by-side comparison verified at `qa/report/family_4_comparison.png`.
  - Isolated regression diff confirmed zero diff outside combos family widgets at `qa/report/family_4_combos_isolated_diff.png`.
  - Numeric token assertions passed via `qa/verify_tokens.py`.

### Family 5: Menus & Popovers (PASSED)
- **Tokens & Metrics Applied**:
  - Popover Radius: **10px** corner radius, **6px** padding (measured from `apple/popovers/1_popover.png`, `5_mode_dark.png`).
  - Popover Shadow: `0 8px 20px rgba(0, 0, 0, 0.22), 0 2px 6px rgba(0, 0, 0, 0.12)` (dark), `0 6px 18px rgba(0, 0, 0, 0.10)` (light), `0 8px 22px rgba(0, 0, 0, 0.45)` (AMOLED).
  - Popover Menu Radius: **8px** container radius, **4px** padding (from `apple/menus/2_mode_light.png`, `5_mode_dark.png`).
  - Menu Item Row Height: **24px** (measured from `apple/menus/106_*`, `111_*`).
  - Item Selection Radius: **4px** pill radius.
  - Item Selection Fill: `@accent_bg_color` (`#0069f9` dark / `#0165e2` light), text `#ffffff`.
  - Menu Separators: **1px** min-height, **4px 6px** margin, subtle translucent border color.
  - Universal Unification: Synchronized `popover`, `.popover`, `popover.menu`, `menu`, `.menu`, and `modelbutton` / `menuitem.button.flat` across GTK 4 and GTK 3.
- **Verification**:
  - Rendered `qa/report/family_5_menus_gtk4_dark.png`, `family_5_menus_gtk4_light.png`, `family_5_menus_gtk3_dark.png`, `family_5_menus_gtk3_light.png`.
  - Visual side-by-side comparison verified at `qa/report/family_5_comparison.png`.
  - Token assertion tests passed across all 6 themes (Light/Dark/Amoled x solid/glassy).

### Family 6: Lists, Tables & Sidebars (PASSED)
- **Tokens & Metrics Applied**:
  - Sidebar Row Height: **32px** regular, **28px** compact (measured from `apple/sidebars/82_size_medium_*`, `70_size_small_*`).
  - Sidebar Row Selection: **5px** floating pill radius, **1px 8px** margin, **4px 10px** padding.
  - Sidebar Glyphs: **16px** SF-Symbols accent icons.
  - List & Table Row Height: **24px** regular, **20px** compact/tree (measured from `apple/lists and tables/28_level_0_*`).
  - Column Header Height: **28px**, **3px 10px** padding (measured from `apple/lists and tables/23_column_header.png`).
  - Active Row Selection: `@accent_bg_color` (`#0165e2` / `#0069f9`), text `#ffffff`.
  - Inactive Window Selection: `rgba(0, 0, 0, 0.14)` (light) / `rgba(255, 255, 255, 0.14)` (dark/AMOLED) backdrop fill.
  - Alternating Zebra Rows: `rgba(0, 0, 0, 0.05)` (light) / `rgba(255, 255, 255, 0.04)` (dark/AMOLED) alternating row tint (from `apple/lists and tables/98_level_0_*`).
- **Verification**:
  - Rendered `qa/report/family_6_sidebars_gtk4_dark.png`, `family_6_sidebars_gtk4_light.png`, `family_6_sidebars_gtk3_dark.png`, `family_6_sidebars_gtk3_light.png`.
  - Visual side-by-side comparison verified at `qa/report/family_6_comparison.png`.
  - Token assertion tests passed across all 6 themes (Light/Dark/Amoled x solid/glassy).

### Family 7: Toolbars & Actionbars (PASSED)
- **Tokens & Metrics Applied**:
  - Unified Topbar Chrome: Toolbars, headerbars, and searchbars unified with `@headerbar_bg_color` and `@headerbar_fg_color`.
  - Separators: **1px** width, **16px** height vertical divider line (measured from `apple/toolbars/424_separator.png`, `430_separator.png`).
  - Actionbars: Bottom window and dialog action areas unified with 1px top border line and 6px 14px padding.
  - Toolbar Buttons: Flat default with 5px radius, 24px height, hover and active subtle states, `@accent_bg_color` when checked/toggled.
- **Verification**:
  - Rendered `qa/report/family_7_toolbars_gtk4_dark.png`, `family_7_toolbars_gtk4_light.png`, `family_7_toolbars_gtk3_dark.png`, `family_7_toolbars_gtk3_light.png`.
  - Visual side-by-side comparison verified at `qa/report/family_7_comparison.png`.
  - Token assertion tests passed across all 6 themes (Light/Dark/Amoled x solid/glassy).

### Family 8: Group boxes / Forms / Disclosure (PASSED)
- **Tokens & Metrics Applied**:
  - Group Box / Card Radius: **10px** corner radius (was previously 12px, measured strictly from `apple/group boxes/1_group_box.png`).
  - Card Border & Fill: **1px** solid subtle border, `@card_bg_color` background fill.
  - Boxed List Row Radii: First row 10px top radii, last row 10px bottom radii, 1px internal dividers.
  - Disclosure Controls: **16px** chevron symbol, 24px min-height, hover feedback, 90deg animation (from `apple/disclosure controls/4_state_idle_*`).
- **Verification**:
  - Rendered `qa/report/family_8_groupboxes_gtk4_dark.png`, `family_8_groupboxes_gtk4_light.png`, `family_8_groupboxes_gtk3_dark.png`, `family_8_groupboxes_gtk3_light.png`.
  - Visual side-by-side comparison verified at `qa/report/family_8_comparison.png`.
  - Token assertion tests passed across all 6 themes (Light/Dark/Amoled x solid/glassy).

### Family 9: Alerts & Dialogs (PASSED)
- **Tokens & Metrics Applied**:
  - Alert Card Radius: **20px** corner radius (measured strictly from `apple/alerts/12_bg.png`, was previously 18px / 12px).
  - Action Button Geometry: **9999px** full capsule radius, **26px** control height, **3px 16px** padding (measured from `apple/alerts/5_mode_light__type_primary.png` and `9_mode_dark__type_primary.png`).
  - Action Button Colors: Destructive `#ff453a` (dark) / `#ff383c` (light), Suggested `#0a84ff` (dark) / `#0080f7` (light), Secondary subtle border and fill.
  - Multi-toolkit Selectors: Modern `adwdialog`, `adwalertdialog`, `messagedialog`, `window.dialog`, `alertdialog` across GTK4 and GTK3.
- **Verification**:
  - Rendered `qa/report/family_9_alerts_gtk4_dark.png`, `family_9_alerts_gtk4_light.png`, `family_9_alerts_gtk3_dark.png`, `family_9_alerts_gtk3_light.png`.
  - Side-by-side comparison verified at `qa/report/family_9_comparison.png`.
  - Token assertion tests passed across all 6 themes.
