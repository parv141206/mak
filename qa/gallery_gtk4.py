#!/usr/bin/env python3
"""
Mak Apple-Fidelity QA Gallery: GTK 4 + Libadwaita
Renders an exhaustive component gallery to PNG offscreen.
"""

import sys
import os
import argparse
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gdk, Gsk, GLib, Gio

def build_gallery(family_filter=None):
    root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
    root.set_margin_top(16)
    root.set_margin_bottom(16)
    root.set_margin_start(16)
    root.set_margin_end(16)
    root.add_css_class("view")

    # 1. Headerbar & Traffic lights
    if not family_filter or family_filter in ["windows", "headerbars", "traffic_lights"]:
        hb = Adw.HeaderBar()
        hb.set_title_widget(Gtk.Label(label="Unified Window Headerbar", css_classes=["title"]))
        root.append(hb)

    # 2. Buttons
    if not family_filter or family_filter in ["buttons"]:
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        btn_box.append(Gtk.Button(label="Standard"))
        btn_box.append(Gtk.Button(label="Suggested", css_classes=["suggested-action"]))
        btn_box.append(Gtk.Button(label="Destructive", css_classes=["destructive-action"]))
        btn_box.append(Gtk.Button(label="Flat", css_classes=["flat"]))
        circ = Gtk.Button(icon_name="go-next-symbolic", css_classes=["circular"])
        btn_box.append(circ)
        dis_btn = Gtk.Button(label="Disabled")
        dis_btn.set_sensitive(False)
        btn_box.append(dis_btn)
        root.append(btn_box)

    # 3. Linked & Segmented Controls & Split Buttons
    if not family_filter or family_filter in ["buttons", "segmented", "splitbutton"]:
        split_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        
        # Linked box
        l_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, css_classes=["linked"])
        l_box.append(Gtk.Button(label="Segment A"))
        l_box.append(Gtk.Button(label="Segment B", css_classes=["suggested-action"]))
        l_box.append(Gtk.Button(label="Segment C"))
        split_box.append(l_box)

        # Adw.SplitButton
        sb = Adw.SplitButton(label="Action")
        menu = Gio.Menu()
        menu.append("Option 1", "win.opt1")
        menu.append("Option 2", "win.opt2")
        sb.set_menu_model(menu)
        split_box.append(sb)

        root.append(split_box)

    # 4. Text Fields, Search, Spin Buttons
    if not family_filter or family_filter in ["entries", "search", "steppers"]:
        entry_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        entry = Gtk.Entry(text="Standard Entry")
        entry_box.append(entry)

        search = Gtk.SearchEntry()
        search.set_text("Search files...")
        entry_box.append(search)

        spin_adj = Gtk.Adjustment(value=50, lower=0, upper=100, step_increment=1, page_increment=10)
        spin = Gtk.SpinButton(adjustment=spin_adj)
        entry_box.append(spin)

        pwd = Gtk.PasswordEntry(text="secret")
        entry_box.append(pwd)
        root.append(entry_box)

    # 5. Pop-ups, Combos, Dropdowns
    if not family_filter or family_filter in ["combos", "dropdowns", "popups"]:
        combo_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        model = Gtk.StringList.new(["Dropdown Choice 1", "Choice 2", "Choice 3"])
        dd = Gtk.DropDown.new(model, None)
        combo_box.append(dd)

        mb = Gtk.MenuButton(label="Menu Button")
        m = Gio.Menu()
        m.append("Item 1", "win.item1")
        m.append("Item 2", "win.item2")
        mb.set_menu_model(m)
        combo_box.append(mb)
        root.append(combo_box)

    # 6. Lists, Sidebars & Tables
    if not family_filter or family_filter in ["lists", "tables", "sidebars"]:
        lists_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)

        # Sidebar emulation
        sb_list = Gtk.ListBox(css_classes=["navigation-sidebar"])
        for title in ["Recents", "Documents", "Downloads", "Pictures"]:
            r = Gtk.ListBoxRow()
            b = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            b.append(Gtk.Image.new_from_icon_name("folder-symbolic"))
            b.append(Gtk.Label(label=title))
            r.set_child(b)
            sb_list.append(r)
        sb_list.select_row(sb_list.get_row_at_index(1))
        lists_box.append(sb_list)

        # Standard list with alternating rows
        std_list = Gtk.ListBox(css_classes=["boxed-list"])
        for i in range(4):
            r = Gtk.ListBoxRow()
            if i % 2 == 1:
                r.add_css_class("alt-row")
            b = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            b.append(Gtk.Label(label=f"Table Item {i+1}"))
            r.set_child(b)
            std_list.append(r)
        std_list.select_row(std_list.get_row_at_index(0))
        lists_box.append(std_list)

        root.append(lists_box)

    # 7. Boxed list / Preferences Group
    if not family_filter or family_filter in ["group_boxes", "forms"]:
        pg = Adw.PreferencesGroup(title="Preferences Group", description="Apple-styled form card")
        row1 = Adw.ActionRow(title="Account Synchronization", subtitle="Connected as macOS user")
        row1.add_suffix(Gtk.Switch(active=True))
        pg.add(row1)
        root.append(pg)

    # 8. Alert Card Representation
    if not family_filter or family_filter in ["alerts", "dialogs"]:
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8, css_classes=["card"])
        card.set_margin_top(8)
        card.set_margin_bottom(8)
        title_lbl = Gtk.Label(label="Save changes to document?", css_classes=["heading"])
        card.append(title_lbl)
        desc_lbl = Gtk.Label(label="Your changes will be lost if you don't save them.")
        card.append(desc_lbl)
        btn_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10, halign=Gtk.Align.END)
        btn_row.append(Gtk.Button(label="Don't Save", css_classes=["destructive-action"]))
        btn_row.append(Gtk.Button(label="Cancel"))
        btn_row.append(Gtk.Button(label="Save", css_classes=["suggested-action"]))
        card.append(btn_row)
        root.append(card)

    return root

def main():
    parser = argparse.ArgumentParser(description="Render GTK 4 widget gallery to PNG")
    parser.add_argument("--css", help="Path to gtk.css to load")
    parser.add_argument("--mode", choices=["light", "dark"], default="dark")
    parser.add_argument("--out", required=True, help="Output PNG path")
    parser.add_argument("--family", help="Component family filter")
    args = parser.parse_args()

    # Load custom CSS if provided
    if args.css and os.path.exists(args.css):
        provider = Gtk.CssProvider()
        provider.load_from_path(args.css)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_USER
        )

    app = Adw.Application.new(f"org.mak.qa.gtk4.{os.getpid()}", 0)

    def on_activate(app):
        # Force color scheme
        sm = Adw.StyleManager.get_default()
        if args.mode == "dark":
            sm.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
        else:
            sm.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)

        win = Adw.ApplicationWindow(application=app)
        win.set_default_size(800, 600)
        gallery = build_gallery(args.family)
        win.set_content(gallery)
        win.present()

        # Let GTK layout and settle
        for _ in range(10):
            while GLib.MainContext.default().iteration(False): pass

        paintable = Gtk.WidgetPaintable.new(win)
        w = max(win.get_width(), 800)
        h = max(win.get_height(), 600)
        snapshot = Gtk.Snapshot()
        paintable.snapshot(snapshot, w, h)
        node = snapshot.to_node()
        renderer = win.get_renderer()
        if renderer and node:
            texture = renderer.render_texture(node, None)
            os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
            texture.save_to_png(args.out)
            print(f"[QA GTK4] Saved {w}x{h} gallery to {args.out}")
        else:
            print("[QA GTK4] Error: Failed to render texture", file=sys.stderr)

        win.close()
        app.quit()

    app.connect("activate", on_activate)
    app.run(None)

if __name__ == "__main__":
    main()
