# Apple macOS UI Fidelity Specification & Measured Tokens

Extracted directly from Apple's official macOS UI kit (`apple/` PNG exports).
Scale: **1x logical CSS pixels** (1:1 with GTK CSS px values).

## 1. Component Family Mapping to GTK & Shell Selectors

| Component Family | Target GTK / Shell Selectors | Key Measured Metrics | Reference Provenance |
|---|---|---|---|
| **Windows** | `window.csd`, `window.csd > contents`, `.titlebar` | Radius: **14px**, Header: 52px (compact 38px) | `apple/windows/` (110_*, 895_*, 1_window_bg.png) |
| **Traffic Lights** | `headerbar windowcontrols > button`, `button.titlebutton` | Diameter: **14px** (12px dot), Spacing: **8px**, Left margin: **13px**, Close: `#ff5c60`, Min: `#fac800`, Max: `#35c759`, Inactive: 13-17% alpha | `apple/windows/897_close.png`, `898_minimize.png`, `899_zoom.png` |
| **Buttons** | `button`, `button.flat`, `button.suggested-action`, `button.destructive-action`, `button.circular` | Height: **24px** (small 20px, large 28px), Radius: **5px** (capsule: 9999px), Default fill: 8-10% alpha, Prominent: `#0080f7`, Destructive: `#ff383c` | `apple/buttons/` (102_*, 104_*, 106_*, 115_*) |
| **Segmented & Split Buttons** | `splitbutton`, `.linked`, `stackswitcher > button` | Height: **22px**, Container Radius: **6px**, Inner Segment Radius: **5px**, 1px border | `apple/segmented controls/` (12_*, 18_*) |
| **Text Fields & Search** | `entry`, `searchentry`, `passwordentry` | Height: **22px** (small 18px, large 38px), Radius: **5px**, Focus ring: 3px `#0080f7`/`#0a84ff` | `apple/text fields/`, `apple/search fields/` |
| **Steppers** | `spinbutton`, `spinbutton > button` | Height: **22px**, Split 1px separator, 5px radius | `apple/steppers/` |
| **Pop-ups & Combos** | `dropdown`, `combobox`, `menubutton` | Height: **24px**, Radius: **5px** | `apple/pop ups and pull down buttons/` |
| **Menus & Popovers** | `popover`, `popover.menu`, `menu`, `.context-menu`, `popover.menu modelbutton` | Popover Radius: **10px**, Menu row: **24px**, Item selection radius: **4px**, Active selection fill: `#0069f9` | `apple/popovers/`, `apple/menus/` |
| **Lists & Tables** | `listview`, `columnview`, `treeview`, `list > row` | Row: **24px** (compact 20px), Header: **28px**, Selection active: `#0165e2`, Inactive: 14% alpha, Zebra fill: 5% alpha | `apple/lists and tables/` (16_*, 14_*, 105_*, 23_*) |
| **Sidebars** | `.navigation-sidebar`, `.sidebar`, `placessidebar` | Row: **32px** (compact 28px), Selection Radius: **5px** | `apple/sidebars/` (100_*, 102_*) |
| **Toolbars & Actionbars** | `headerbar`, `actionbar`, `.toolbar` | Unified topbar & sidebar background, clean 1px separators | `apple/toolbars/` |
| **Group Boxes & Forms** | `frame`, `.boxed-list`, `preferencesgroup` | Radius: **10px**, 1px subtle border | `apple/group boxes/`, `apple/forms/` |
| **Disclosure Controls** | `expander`, `expander-widget` | Chevron size: 16px, 90deg animation | `apple/disclosure controls/` |
| **Alerts & Dialogs** | `AdwAlertDialog`, `GtkDialog`, `window.dialog` | Radius: **20px**, Buttons: **26px** capsule (9999px), side-by-side or stacked | `apple/alerts/10_alert.png`, `12_bg.png` |
| **Color Wells & Image Wells** | `colorbutton`, `image-well` | Height: **22px**, Radius: **4px** | `apple/color wells/`, `apple/image wells/` |
| **Notifications** | GNOME Shell notification banner & message list | Radius: **16px**, Padding: **14px** | `apple/notifications/` |

## 2. Conflicts Between Guide and Reference PNGs

The reference PNGs in `apple/` are the sole authority. The following discrepancies existed in the previous guide or code:

1. **Window Corner Radius**:
   - Guide: Claimed 16px or 12px.
   - Reference PNGs: Measured exactly **14px** arc extent on window frames.

2. **Dialog / Alert Corner Radius**:
   - Guide: Assumed standard window radius or 12px.
   - Reference PNGs: Measured exactly **20px** corner curvature on alert cards.

3. **Button Heights & Radii**:
   - Guide / Old Generator: Arbitrarily scattered 5px, 6px, and 9999px across different CSS blocks, and min-heights of 26-32px.
   - Reference PNGs: Standard button height is **24px**, radius is strictly **5px** (capsule is 9999px for dialogs/segmented controls).

4. **Traffic Light Colors & Geometry**:
   - Old Generator: Used generic SVG or CSS colors (#ff5f56, #ffbd2e, #27c93f).
   - Reference PNGs: Measured Close: `#ff5c60`, Minimize: `#fac800`, Zoom: `#35c759`, Inactive: `rgba(0, 0, 0, 0.13)` (light) / `rgba(255, 255, 255, 0.17)` (dark). Diameter: **14px**, spacing: **8px**.

5. **Sidebar & List View Heights**:
   - Old Generator: Handcoded padding resulting in varying row heights.
   - Reference PNGs: Sidebar row height is **32px** (selection pill radius 5px); list row height is **24px** (compact/tree 20px); column header is **28px**.

6. **AMOLED Derivation**:
   - Guide stated `#000000`, but previous generator code drifted to `#1e1e21`.
   - Reference Resolution: Amoled derives purely by overriding the background-layer tokens of Dark to `#000000` (view/window) and `#0a0a0c` (headerbar/sidebar), keeping geometry 100% identical.
