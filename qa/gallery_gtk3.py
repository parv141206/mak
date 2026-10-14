#!/usr/bin/env python3
"""
Mak Apple-Fidelity QA Gallery: GTK 3
Renders an exhaustive component gallery to PNG offscreen via Gtk.OffscreenWindow.
"""

import sys
import os
import argparse
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

def build_gallery_gtk3(family_filter=None):
    root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
    root.set_margin_top(16)
    root.set_margin_bottom(16)
    root.set_margin_start(16)
    root.set_margin_end(16)

    # 1. Headerbar & Window controls
    if not family_filter or family_filter in ["windows", "headerbars", "traffic_lights"]:
        hb = Gtk.HeaderBar()
        hb.set_title("Unified Window Headerbar")
        hb.set_show_close_button(True)
        root.pack_start(hb, False, False, 0)

    # 2. Buttons
    if not family_filter or family_filter in ["buttons"]:
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        btn_box.pack_start(Gtk.Button(label="Standard"), False, False, 0)
        
        sug = Gtk.Button(label="Suggested")
        sug.get_style_context().add_class("suggested-action")
        btn_box.pack_start(sug, False, False, 0)

        dest = Gtk.Button(label="Destructive")
        dest.get_style_context().add_class("destructive-action")
        btn_box.pack_start(dest, False, False, 0)

        flat = Gtk.Button(label="Flat")
        flat.get_style_context().add_class("flat")
        btn_box.pack_start(flat, False, False, 0)

        circ = Gtk.Button(label="+")
        circ.get_style_context().add_class("circular")
        btn_box.pack_start(circ, False, False, 0)

        dis = Gtk.Button(label="Disabled")
        dis.set_sensitive(False)
        btn_box.pack_start(dis, False, False, 0)

        root.pack_start(btn_box, False, False, 0)

    # 3. Linked / Segmented Buttons
    if not family_filter or family_filter in ["buttons", "segmented", "splitbutton"]:
        l_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        l_box.get_style_context().add_class("linked")
        l_box.pack_start(Gtk.Button(label="Segment A"), False, False, 0)
        
        sug_seg = Gtk.Button(label="Segment B")
        sug_seg.get_style_context().add_class("suggested-action")
        l_box.pack_start(sug_seg, False, False, 0)

        l_box.pack_start(Gtk.Button(label="Segment C"), False, False, 0)
        root.pack_start(l_box, False, False, 0)

    # 4. Text Entries, Search, Stepper
    if not family_filter or family_filter in ["entries", "search", "steppers"]:
        entry_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        entry = Gtk.Entry()
        entry.set_text("Standard Entry")
        entry_box.pack_start(entry, False, False, 0)

        search = Gtk.SearchEntry()
        search.set_text("Search files...")
        entry_box.pack_start(search, False, False, 0)

        adj = Gtk.Adjustment(value=50, lower=0, upper=100, step_increment=1, page_increment=10)
        spin = Gtk.SpinButton(adjustment=adj)
        entry_box.pack_start(spin, False, False, 0)

        root.pack_start(entry_box, False, False, 0)

    # 5. Dropdowns / Combos
    if not family_filter or family_filter in ["combos", "dropdowns", "popups"]:
        cb_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        cb = Gtk.ComboBoxText()
        cb.append_text("Combo Choice 1")
        cb.append_text("Choice 2")
        cb.append_text("Choice 3")
        cb.set_active(0)
        cb_box.pack_start(cb, False, False, 0)

        mb = Gtk.MenuButton(label="Menu Button")
        cb_box.pack_start(mb, False, False, 0)
        root.pack_start(cb_box, False, False, 0)

    # 5b. Menus & Popovers
    if not family_filter or family_filter in ["menus", "popovers"]:
        pop_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        m_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        m_box.get_style_context().add_class("menu")
        
        mi1 = Gtk.ModelButton()
        mi1.set_property("text", "New Window")
        m_box.pack_start(mi1, False, False, 0)
        
        mi2 = Gtk.ModelButton()
        mi2.set_property("text", "Open Recent…")
        m_box.pack_start(mi2, False, False, 0)
        
        sep = Gtk.Separator()
        m_box.pack_start(sep, False, False, 0)
        
        mi3 = Gtk.ModelButton()
        mi3.set_property("text", "Close Tab")
        m_box.pack_start(mi3, False, False, 0)
        
        pop_box.pack_start(m_box, False, False, 0)
        root.pack_start(pop_box, False, False, 0)

    # 6. Lists & Tables
    if not family_filter or family_filter in ["lists", "tables", "sidebars"]:
        lists_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)

        # Sidebar emulation
        sb_list = Gtk.ListBox()
        sb_list.get_style_context().add_class("sidebar")
        for title in ["Recents", "Documents", "Downloads", "Pictures"]:
            r = Gtk.ListBoxRow()
            b = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            b.pack_start(Gtk.Label(label=title), False, False, 0)
            r.add(b)
            sb_list.add(r)
        sb_list.select_row(sb_list.get_row_at_index(1))
        lists_box.pack_start(sb_list, True, True, 0)

        # Table emulation
        std_list = Gtk.ListBox()
        for i in range(4):
            r = Gtk.ListBoxRow()
            if i % 2 == 1:
                r.get_style_context().add_class("alt-row")
            b = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            b.pack_start(Gtk.Label(label=f"Table Item {i+1}"), False, False, 0)
            r.add(b)
            std_list.add(r)
        std_list.select_row(std_list.get_row_at_index(0))
        lists_box.pack_start(std_list, True, True, 0)

        root.pack_start(lists_box, False, False, 0)

    # 7. Frame
    if not family_filter or family_filter in ["group_boxes", "forms"]:
        frame = Gtk.Frame(label="Frame Container")
        fb = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        fb.set_margin_top(8)
        fb.set_margin_bottom(8)
        fb.set_margin_start(8)
        fb.set_margin_end(8)
        fb.pack_start(Gtk.Label(label="Content inside group box frame"), False, False, 0)
        frame.add(fb)
        root.pack_start(frame, False, False, 0)

        exp = Gtk.Expander(label="Advanced Settings")
        exp.add(Gtk.Label(label="Expanded disclosure content inside group box"))
        root.pack_start(exp, False, False, 0)

    # 8. Alert Card Representation
    if not family_filter or family_filter in ["alerts", "dialogs"]:
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        card.get_style_context().add_class("dialog")
        card.get_style_context().add_class("card")
        card.set_margin_top(8)
        card.set_margin_bottom(8)
        title_lbl = Gtk.Label(label="Save changes to document?")
        title_lbl.get_style_context().add_class("heading")
        card.pack_start(title_lbl, False, False, 0)
        desc_lbl = Gtk.Label(label="Your changes will be lost if you don't save them.")
        card.pack_start(desc_lbl, False, False, 0)
        btn_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        btn_row.set_halign(Gtk.Align.END)
        dest = Gtk.Button(label="Don't Save")
        dest.get_style_context().add_class("destructive-action")
        btn_row.pack_start(dest, False, False, 0)
        btn_row.pack_start(Gtk.Button(label="Cancel"), False, False, 0)
        sug = Gtk.Button(label="Save")
        sug.get_style_context().add_class("suggested-action")
        btn_row.pack_start(sug, False, False, 0)
        card.pack_start(btn_row, False, False, 0)
        root.pack_start(card, False, False, 0)

    # 9. Toolbars & Actionbars
    if not family_filter or family_filter in ["toolbars", "actionbars"]:
        tb_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        tb = Gtk.Toolbar()
        ti1 = Gtk.ToolButton.new_from_stock("gtk-new")
        ti2 = Gtk.ToolButton.new_from_stock("gtk-open")
        sep = Gtk.SeparatorToolItem()
        ti3 = Gtk.ToolButton.new_from_stock("gtk-save")
        tb.insert(ti1, -1)
        tb.insert(ti2, -1)
        tb.insert(sep, -1)
        tb.insert(ti3, -1)
        tb_box.pack_start(tb, False, False, 0)

        ab = Gtk.ActionBar()
        dis_btn = Gtk.Button(label="Discard")
        dis_btn.get_style_context().add_class("destructive-action")
        ab.pack_start(dis_btn)
        app_btn = Gtk.Button(label="Apply")
        app_btn.get_style_context().add_class("suggested-action")
        ab.pack_end(app_btn)
        tb_box.pack_start(ab, False, False, 0)

        root.pack_start(tb_box, False, False, 0)

    return root

def main():
    parser = argparse.ArgumentParser(description="Render GTK 3 widget gallery to PNG")
    parser.add_argument("--css", help="Path to gtk.css to load")
    parser.add_argument("--mode", choices=["light", "dark"], default="dark")
    parser.add_argument("--out", required=True, help="Output PNG path")
    parser.add_argument("--family", help="Component family filter")
    args = parser.parse_args()

    # Load custom CSS if provided
    if args.css and os.path.exists(args.css):
        provider = Gtk.CssProvider()
        provider.load_from_path(args.css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_USER
        )

    # Force dark preference if requested
    settings = Gtk.Settings.get_default()
    if settings:
        settings.set_property("gtk-application-prefer-dark-theme", args.mode == "dark")

    win = Gtk.OffscreenWindow()
    win.set_default_size(800, 600)
    gallery = build_gallery_gtk3(args.family)
    win.add(gallery)
    win.show_all()

    # Settle GTK events
    for _ in range(10):
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)

    pixbuf = win.get_pixbuf()
    if pixbuf:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        pixbuf.savev(args.out, "png", [], [])
        print(f"[QA GTK3] Saved {pixbuf.get_width()}x{pixbuf.get_height()} gallery to {args.out}")
    else:
        print("[QA GTK3] Error: Pixbuf was None", file=sys.stderr)

if __name__ == "__main__":
    main()
