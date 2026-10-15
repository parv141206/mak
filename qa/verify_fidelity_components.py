#!/usr/bin/env python3
"""
Apple macOS 27 Finder Fidelity Verification Gallery
Renders the complete macOS Finder window with authentic HIG components:
- Traffic Lights (14px radial gradient circles with hairline border)
- Navigation Capsule (< | >)
- Clean Window Title
- View Mode Switcher Capsule ([ ⊞ | ☷ | 𝌕 | 𝌗 ] with active inset pill)
- Action Dropdown Splitbutton ([ ☶ ˅ ])
- Combined Actions Capsule ([ 📤  🏷️  ⋯ ])
- Search Button ([ 🔍 ])
- Anchored Sidebar (Favourites heading, active Downloads pill)
- Continuous Column Headers & File List with active selection row
- Bottom Breadcrumbs Pathbar
- Content Dialog Buttons & Chrome High-Contrast Popover Card
"""

import sys
import os
import argparse
import subprocess
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gdk, GLib, Gio

def build_qa_window():
    root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

    # 1. Authentic HeaderBar with Traffic Lights & Navigation
    hb = Adw.HeaderBar()
    hb.set_show_start_title_buttons(False)
    hb.set_show_end_title_buttons(False)

    # Traffic Lights (Close, Minimize, Maximize)
    wc = Gtk.WindowControls.new(Gtk.PackType.START)
    wc.set_decoration_layout("close,minimize,maximize:")
    hb.pack_start(wc)

    # Back/Forward Navigation Controls (< | >) - Single Capsule Pill
    hist_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, css_classes=["linked", "navigation-controls"])
    hist_box.set_name("NautilusHistoryControls")
    btn_back = Gtk.Button(icon_name="go-previous-symbolic")
    btn_back.set_name("back_button")
    btn_fwd = Gtk.Button(icon_name="go-next-symbolic")
    btn_fwd.set_name("forward_button")
    hist_box.append(btn_back)
    hist_box.append(btn_fwd)
    hb.pack_start(hist_box)

    # Window Title: Downloads
    title_label = Gtk.Label(label="Downloads", css_classes=["title"])
    title_label.set_margin_start(8)
    hb.set_title_widget(title_label)

    # Pack end widgets in reverse order so left-to-right matches Apple HIG (Image 2):
    # View Switcher -> Sort Splitbutton -> Combined Actions -> Search

    # Search Button ([ 🔍 ]) - Far right
    btn_search = Gtk.Button(icon_name="system-search-symbolic", css_classes=["flat"])
    hb.pack_end(btn_search)

    # Combined Actions Capsule ([ 📤  🏷️  ⋯ ])
    actions_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, css_classes=["linked"])
    btn_share = Gtk.Button(icon_name="document-send-symbolic")
    btn_tag = Gtk.Button(icon_name="tag-symbolic")
    btn_more = Gtk.Button(icon_name="view-more-symbolic")
    actions_box.append(btn_share)
    actions_box.append(btn_tag)
    actions_box.append(btn_more)
    hb.pack_end(actions_box)

    # Standalone Splitbutton ([ ☶ ˅ ]) - Capsule Pill
    sort_sb = Adw.SplitButton(icon_name="view-sort-descending-symbolic")
    sort_menu = Gio.Menu()
    sort_menu.append("Name", "win.sort_name")
    sort_menu.append("Date Modified", "win.sort_date")
    sort_sb.set_menu_model(sort_menu)
    hb.pack_end(sort_sb)

    # View Mode Switcher Capsule ([ ⊞ | ☷ | 𝌕 | 𝌗 ])
    view_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, css_classes=["linked", "viewswitcher"])
    btn_grid = Gtk.ToggleButton(icon_name="view-grid-symbolic")
    btn_grid.set_active(True)
    btn_list = Gtk.ToggleButton(icon_name="view-list-symbolic")
    btn_list.set_active(False)
    btn_cols = Gtk.ToggleButton(icon_name="view-column-symbolic")
    btn_cols.set_active(False)
    btn_page = Gtk.ToggleButton(icon_name="view-paged-symbolic")
    btn_page.set_active(False)
    view_box.append(btn_grid)
    view_box.append(btn_list)
    view_box.append(btn_cols)
    view_box.append(btn_page)
    hb.pack_end(view_box)

    # 2. Main Window Body: Sidebar on Left, Content on Right
    body_paned = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    body_paned.set_vexpand(True)

    # Sidebar Pane
    sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2, css_classes=["sidebar-pane", "navigation-sidebar"])
    sidebar.set_size_request(200, -1)
    sidebar.set_margin_top(8)
    sidebar.set_margin_start(8)
    sidebar.set_margin_end(8)

    lbl_fav = Gtk.Label(label="Favourites", css_classes=["heading"], halign=Gtk.Align.START)
    lbl_fav.set_margin_start(8)
    sidebar.append(lbl_fav)

    sidebar_items = [
        ("AirDrop", "preferences-system-network-symbolic", False),
        ("Recents", "document-open-recent-symbolic", False),
        ("Applications", "system-run-symbolic", False),
        ("Desktop", "user-desktop-symbolic", False),
        ("Documents", "folder-documents-symbolic", False),
        ("Downloads", "folder-download-symbolic", True),
        ("Personal", "folder-symbolic", False),
    ]

    for name, icon, is_selected in sidebar_items:
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8, css_classes=["sidebar-row", "activatable"])
        if is_selected:
            row.add_css_class("selected")
        img = Gtk.Image(icon_name=icon)
        lbl = Gtk.Label(label=name, halign=Gtk.Align.START)
        row.append(img)
        row.append(lbl)
        sidebar.append(row)

    body_paned.append(sidebar)

    # Vertical Divider Line
    v_sep = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
    body_paned.append(v_sep)

    # Content Pane
    content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0, css_classes=["content-pane"])
    content.set_hexpand(True)

    # Column Headers Strip
    col_hdr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, css_classes=["columnview", "header"])
    col_name = Gtk.Button(label="Name ▲", css_classes=["flat"])
    col_name.set_hexpand(True)
    col_size = Gtk.Button(label="Size", css_classes=["flat"])
    col_size.set_size_request(100, -1)
    col_kind = Gtk.Button(label="Kind", css_classes=["flat"])
    col_kind.set_size_request(120, -1)
    col_date = Gtk.Button(label="Date Modified", css_classes=["flat"])
    col_date.set_size_request(150, -1)

    col_hdr.append(col_name)
    col_hdr.append(col_size)
    col_hdr.append(col_kind)
    col_hdr.append(col_date)
    content.append(col_hdr)

    # File List Rows
    file_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)
    file_list.set_margin_top(4)

    files_data = [
        ("Recover deleted note.jpg", "28 KB", "JPEG image", "Today, 4:27 PM", True),
        ("Recover deleted note.png", "320 KB", "PNG image", "Today, 4:27 PM", False),
        ("Drag deleted note to a folder on Mac.jpg", "206 KB", "JPEG image", "Today, 4:27 PM", False),
        ("Add attachments button to Notes toolbar.jpg", "81 KB", "JPEG image", "Today, 4:27 PM", False),
        ("Attachments in Mac Notes.jpg", "91 KB", "JPEG image", "Today, 4:27 PM", False),
        ("iPad connected to external display.jpg", "180 KB", "JPEG image", "Today, 2:37 PM", False),
    ]

    for fname, fsize, fkind, fdate, is_sel in files_data:
        file_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8, css_classes=["columnview", "row", "activatable"])
        if is_sel:
            file_row.add_css_class("selected")

        c_name = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        c_name.set_hexpand(True)
        f_icon = Gtk.Image(icon_name="image-x-generic-symbolic")
        f_lbl = Gtk.Label(label=fname, halign=Gtk.Align.START)
        c_name.append(f_icon)
        c_name.append(f_lbl)

        c_size = Gtk.Label(label=fsize, halign=Gtk.Align.END)
        c_size.set_size_request(100, -1)

        c_kind = Gtk.Label(label=fkind, halign=Gtk.Align.START)
        c_kind.set_size_request(120, -1)

        c_date = Gtk.Label(label=fdate, halign=Gtk.Align.START)
        c_date.set_size_request(150, -1)

        file_row.append(c_name)
        file_row.append(c_size)
        file_row.append(c_kind)
        file_row.append(c_date)
        file_list.append(file_row)

    content.append(file_list)

    # Bottom Breadcrumb Pathbar
    h_sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    content.append(h_sep)

    path_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4, css_classes=["nautilus-pathbar", "path-bar"])
    path_box.set_margin_start(12)
    path_box.set_margin_top(6)
    path_box.set_margin_bottom(6)

    crumbs = ["Ankur", "Users", "ankur", "Downloads", "Recover deleted note.jpg"]
    for i, crumb in enumerate(crumbs):
        pb = Gtk.Button(label=crumb, css_classes=["nautilus-path-button", "flat"])
        path_box.append(pb)
        if i < len(crumbs) - 1:
            sep = Gtk.Label(label="›", css_classes=["dim-label"])
            path_box.append(sep)

    content.append(path_box)
    body_paned.append(content)
    root.append(body_paned)

    # 3. Universal Dialog & Push Buttons Gallery (Content verification)
    btn_section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    btn_section.set_margin_top(12)
    btn_section.set_margin_bottom(12)
    btn_section.set_margin_start(16)
    btn_section.set_margin_end(16)

    btn_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
    btn_row.append(Gtk.Button(label="Standard Push"))
    btn_row.append(Gtk.Button(label="Suggested Action", css_classes=["suggested-action"]))
    btn_row.append(Gtk.Button(label="Destructive Action", css_classes=["destructive-action"]))
    btn_row.append(Gtk.Button(label="Flat Button", css_classes=["flat"]))

    # In-Window Segmented Capsule
    seg_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, css_classes=["linked"])
    seg_box.append(Gtk.ToggleButton(label="Icons", active=False))
    seg_box.append(Gtk.ToggleButton(label="List", active=True))
    seg_box.append(Gtk.ToggleButton(label="Columns", active=False))
    btn_row.append(seg_box)

    btn_section.append(btn_row)

    # 4. Chrome-like Bubble Card Representation (High Contrast Popover QA)
    bubble_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8, css_classes=["bubble", "card"])
    bubble_card.set_margin_top(4)

    bubble_title = Gtk.Label(label="Restore pages? Chrome didn't shut down correctly.", css_classes=["heading"])
    bubble_title.set_halign(Gtk.Align.START)
    bubble_card.append(bubble_title)

    bubble_btns = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10, halign=Gtk.Align.END)
    bubble_btns.append(Gtk.Button(label="Close", css_classes=["flat"]))
    bubble_btns.append(Gtk.Button(label="Restore", css_classes=["suggested-action"]))
    bubble_card.append(bubble_btns)

    btn_section.append(bubble_card)
    root.append(btn_section)

    return hb, root

def render_single_gallery(css_path, mode, out_path):
    app = Adw.Application.new("org.mak.qa.fidelity", Gio.ApplicationFlags.NON_UNIQUE)

    def on_activate(app):
        sm = Adw.StyleManager.get_default()
        if mode == "dark":
            sm.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
        else:
            sm.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)

        # Force decoration layout to ensure window controls show on start
        settings = Gtk.Settings.get_default()
        if settings:
            settings.set_property("gtk-decoration-layout", "close,minimize,maximize:")

        if os.path.exists(css_path):
            provider = Gtk.CssProvider()
            provider.load_from_path(css_path)
            Gtk.StyleContext.add_provider_for_display(
                Gdk.Display.get_default(),
                provider,
                Gtk.STYLE_PROVIDER_PRIORITY_USER
            )

        win = Adw.ApplicationWindow(application=app)
        win.set_default_size(980, 620)
        win.set_decorated(True)
        
        hb, content_box = build_qa_window()
        tv = Adw.ToolbarView()
        tv.add_top_bar(hb)
        tv.set_content(content_box)
        win.set_content(tv)
        win.present()

        # Let GTK layout settle
        for _ in range(30):
            while GLib.MainContext.default().iteration(False): pass

        paintable = Gtk.WidgetPaintable.new(win)
        w = max(win.get_width(), 980)
        h = max(win.get_height(), 620)
        snapshot = Gtk.Snapshot()
        paintable.snapshot(snapshot, w, h)
        node = snapshot.to_node()
        renderer = win.get_renderer()
        if renderer and node:
            texture = renderer.render_texture(node, None)
            os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
            texture.save_to_png(out_path)
            print(f"[Fidelity QA] Saved {w}x{h} verification gallery to {out_path}")
        else:
            print("[Fidelity QA] Error: Failed to render texture", file=sys.stderr)

        win.close()
        app.quit()

    app.connect("activate", on_activate)
    app.run(None)

def main():
    parser = argparse.ArgumentParser(description="Render GTK 4 Apple Fidelity Verification Gallery to PNG")
    parser.add_argument("--css", help="Path to gtk.css to load")
    parser.add_argument("--mode", choices=["light", "dark"], default="light")
    parser.add_argument("--out", help="Output PNG path")
    parser.add_argument("--all", action="store_true", help="Render all 6 themes from themes/ directory")
    args = parser.parse_args()

    if args.all:
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        themes_dir = os.path.join(repo_root, "themes")
        themes = sorted([d for d in os.listdir(themes_dir) if d.startswith(">>>Mac-")])
        out_dir = "/tmp/mak_qa_fidelity"
        os.makedirs(out_dir, exist_ok=True)
        for t in themes:
            mode = "light" if "Light" in t else "dark"
            css_path = os.path.join(themes_dir, t, "gtk-4.0", "gtk.css")
            out_file = os.path.join(out_dir, f"{t}.png")
            print(f"\n[Fidelity QA] Rendering theme: {t} ({mode})...")
            subprocess.run([sys.executable, __file__, "--css", css_path, "--mode", mode, "--out", out_file], check=True)
        print(f"\n[Fidelity QA] All {len(themes)} themes rendered into {out_dir}/")
        return

    if not args.css or not args.out:
        parser.error("--css and --out are required unless --all is specified.")

    render_single_gallery(args.css, args.mode, args.out)

if __name__ == "__main__":
    main()
