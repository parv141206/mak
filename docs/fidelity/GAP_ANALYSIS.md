# Apple Fidelity Gap Analysis & Settings Audit

## 1. Component Family Gap Matrix

| Component Family | Toolkit Targets | Light Mode Gap | Dark Mode Gap | Severity | Status / Reference |
|---|---|---|---|---|---|
| **Windows & CSD Chrome** | GTK4, GTK3, GTK2, Shell | Frame radius hardcoded, headerbar padding & button vertical alignment inconsistent | Active toolbar background alpha needs exact Sonoma tint | High | `apple/windows/` (14px radius, 52px/38px header, 14px buttons) |
| **Traffic Lights** | GTK4, GTK3, GTK2 | Spacing and left margin varied by app (Nautilus vs Terminal); colors were generic SVG | Colors were generic; inactive dots lacked exact macOS 13%/17% alpha | High | `apple/windows/` (`#ff5c60`, `#fac800`, `#35c759`, 14px size, 8px spacing, 13px margin) |
| **Buttons (Standard/Push)** | GTK4, GTK3, GTK2 | Min-height was 28-32px (Apple is 24px); radius mixed 5px/6px; idle bg lacked subtle 8% alpha | Dark idle bg lacked exact 10% white alpha; pressed state lacked contrast | High | `apple/buttons/` (24px height, 5px radius, 8%/10% alpha fill) |
| **Buttons (Prominent/Suggested)** | GTK4, GTK3, GTK2 | Used purple accent by default instead of system accent `#0080f7`; radius was mixed | Used purple accent instead of `#0a84ff`; radius was mixed | Medium | `apple/buttons/` (Prominent blue `#0080f7`/`#0a84ff`, 5px radius) |
| **Buttons (Destructive)** | GTK4, GTK3, GTK2 | Inconsistent red tones; lacked Apple tinted-destructive variant | Inconsistent red tones; lacked Apple tinted-destructive variant | Medium | `apple/buttons/` (`#ff383c`/`#ff453a`, tinted fill with colored text) |
| **Split & Segmented Buttons** | GTK4, GTK3, GTK2 | Capsule was 9999px in headers but 6px in body; inner buttons had double border artifacts | Capsule container radius should be 6px with 5px inner segments (or 9999px pill) | High | `apple/segmented controls/` (22px height, 6px container, 5px segments) |
| **Text Fields & Search** | GTK4, GTK3, GTK2 | Height was 28-32px; focus ring was generic outline; radius was inconsistent | Dark fill was too bright; focus ring lacked Apple soft glow (3px) | High | `apple/text fields/`, `apple/search fields/` (22px regular, 5px radius, 3px focus ring) |
| **Steppers / Spin Buttons** | GTK4, GTK3, GTK2 | Buttons were stacked vertically with low hitboxes | 1px separator and matching 22px entry height missing | Medium | `apple/steppers/` (22px height, clean 1px division) |
| **Pop-ups & Combos** | GTK4, GTK3, GTK2 | Generic dropdown arrow; height was 28px+ | Height and radius did not match standard push buttons (24px, 5px) | Medium | `apple/pop ups and pull down buttons/` (24px height, 5px radius) |
| **Menus & Popovers** | GTK4, GTK3, GTK2, Shell | Menu row height was 28-32px; selection hover lacked 4px pill radius | Popover radius was 14px+ instead of 10px; menu hover color lacked exact `#0069f9` | High | `apple/menus/`, `apple/popovers/` (10px popover radius, 24px menu row, 4px selection pill) |
| **Lists & Tables** | GTK4, GTK3, GTK2 | Row height was 28px+; zebra striping was missing or harsh; selected hover turned text white on white in Nautilus | Selection active lacked `#0165e2` Apple blue; inactive selection lacked 14% alpha | Critical | `apple/lists and tables/` (24px standard row, 20px compact, 28px header, `#0165e2` active selection) |
| **Sidebars** | GTK4, GTK3, GTK2 | Row height was variable; selection pill radius varied; background did not match headerbar | Row height should be 32px (28px compact); background must match headerbar unified chrome | High | `apple/sidebars/` (32px row, 5px selection radius, unified `#242426`/`#ececf0`) |
| **Toolbars & Headerbars** | GTK4, GTK3, GTK2 | Border separator between sidebar and headerbar was sometimes double or harsh | Unification with sidebar background was incomplete in non-Nautilus apps | High | `apple/toolbars/` (unified background, seamless 1px divider) |
| **Group Boxes & Forms** | GTK4, GTK3, GTK2 | Border radius was 6-8px; padding was inconsistent | Border radius was 12px; should be 10px with 1px subtle border | Medium | `apple/group boxes/`, `apple/forms/` (10px radius, 1px border) |
| **Disclosure Controls** | GTK4, GTK3, GTK2 | Standard GTK expander arrows; lack smooth rotation | Standard arrows | Low | `apple/disclosure controls/` (16px chevron) |
| **Alerts & Dialogs** | GTK4, GTK3, GTK2 | Dialog radius was 12-14px; buttons were square/low radius | Dialog radius should be 20px; buttons must be 26px capsule (9999px) pills | High | `apple/alerts/`, `apple/dialogs/` (20px radius, 26px capsule buttons) |
| **Color Wells & Image Wells** | GTK4, GTK3, GTK2 | Generic button styling | Missing 22px height with 4px inner swatch radius | Low | `apple/color wells/`, `apple/image wells/` (22px height, 4px radius) |
| **Notifications** | Shell | Banner radius was 12px | Banner radius should be 16px with 14px padding | Medium | `apple/notifications/` (16px radius, 14px padding) |
| **Shell Chrome (Dock, Topbar)**| Shell | Handcoded stylesheets without token integration | AMOLED mode was not true pitch black in all layers | High | Tokens unified across extension & themes |

---

## 2. GSettings Configuration Audit

Audit of `mak-extension/schemas/org.gnome.shell.extensions.mak.gschema.xml`:
- **Total Keys**: 168 keys defined.
- **Wired in SettingsBridge**: 147 keys active.
- **Dead / Unreferenced Keys in Extension & UI**:
  1. `topbar-force-quit-shortcut`
  2. `topbar-siri-button`
  3. `topbar-global-menu`
  4. `unround-fullscreen`
  5. `keep-shadow-maximized`
  6. `focused-shadow-h-offset`
  7. `focused-shadow-spread`
  8. `unfocused-shadow-h-offset`
  9. `unfocused-shadow-spread`
  10. `sync-flatpak`
  11. `sync-gtk2`
  12. `sync-gtk3`
  13. `sync-gtk4`
- **Misleading / Disconnected Settings**:
  - `corner-radius`: Changed window corners extension, but did NOT update the GTK CSS window or widget corner radii in generated themes.
  - `titlebar-button-size` and `titlebar-button-spacing`: Wired to `update_titlebar_buttons()`, but operated directly on live config instead of clean staging.
  - Geometry tunables: Control heights, entry heights, button radii, and sidebar translucency had no GSettings keys and were completely hardcoded in `theme_manager.py`.
- **Remediation for Phase 6**:
  - Introduce master GSettings keys for geometry parameters (`control-corner-radius`, `window-corner-radius`, `control-height`, `shadow-strength`, etc.) in `org.gnome.shell.extensions.mak`.
  - Wire them through `MakSettingsBridge` to interactive widgets on `mak-app` Window & Appearance pages.
  - Ensure the generator binds these keys directly into the single token set.
