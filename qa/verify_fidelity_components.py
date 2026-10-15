#!/usr/bin/env python3
"""
Apple Fidelity Verification Gallery
Renders all macOS components (Traffic Lights, Nautilus Navigation, Pathbar,
Column Headers, Splitbuttons, Dropdowns, and Dialogs) offscreen to PNG for visual QA.
"""

import sys
import os
import argparse
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gdk, GLib, Gio

def build_qa_window():
    root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
    root.set_margin_top(16)
    root.set_margin_bottom(16)
    root.set_margin_start(16)
    root.set_margin_end(16)

    # 1. Authentic HeaderBar with Traffic Lights & Navigation
    hb = Adw.HeaderBar()
    hb.set_show_start_title_buttons(False)
    hb.set_show_end_title_buttons(False)
    hb.set_title_widget(Gtk.Label(label="macOS 27 Finder — Unified Titlebar", css_classes=["title"]))

    # Explicit Traffic Lights (Close, Minimize, Maximize)
    wc = Gtk.WindowControls.new(Gtk.PackType.START)
    wc.set_decoration_layout("close,minimize,maximize:")
    hb.pack_start(wc)

    # Back/Forward Navigation Controls (< >)
    hist_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, css_classes=["linked", "navigation-controls"])
    hist_box.set_name("NautilusHistoryControls")
    btn_back = Gtk.Button(icon_name="go-previous-symbolic")
    btn_back.set_name("back_button")
    btn_fwd = Gtk.Button(icon_name="go-next-symbolic")
    btn_fwd.set_name("forward_button")
    hist_box.append(btn_back)
    hist_box.append(btn_fwd)
    hb.pack_start(hist_box)

    # Pathbar breadcrumbs
    path_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2, css_classes=["path-bar"])
    for crumb in ["Home", "projects", "mak", "scratch"]:
        pb = Gtk.Button(label=crumb, css_classes=["nautilus-path-button", "flat"])
        path_box.append(pb)
        if crumb != "scratch":
            sep = Gtk.Label(label="/", css_classes=["dim-label"])
            path_box.append(sep)
    hb.pack_start(path_box)

    # View Mode Switcher / Menu Button
    view_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
    mb = Gtk.MenuButton(icon_name="view-grid-symbolic", css_classes=["flat"])
    view_box.append(mb)
    hb.pack_end(view_box)

    # 2. Column Headers Strip (apple/lists and tables/2__column_headers.png)
    col_hdr_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, css_classes=["columnview", "header"])
    col_hdr_box.set_name("NautilusColumnViewHeader")
    
    col1 = Gtk.Button(label="Name ▲", css_classes=["flat"])
    col1.set_hexpand(True)
    col2 = Gtk.Button(label="Size", css_classes=["flat"])
    col2.set_size_request(100, -1)
    col3 = Gtk.Button(label="Kind", css_classes=["flat"])
    col3.set_size_request(120, -1)
    col4 = Gtk.Button(label="Date Modified", css_classes=["flat"])
    col4.set_size_request(150, -1)

    col_hdr_box.append(col1)
    col_hdr_box.append(col2)
    col_hdr_box.append(col3)
    col_hdr_box.append(col4)
    root.append(col_hdr_box)

    # 3. Standard Buttons Row (Dialog / Content Push Buttons)
    btn_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
    btn_row.append(Gtk.Button(label="Standard Push"))
    btn_row.append(Gtk.Button(label="Suggested Action", css_classes=["suggested-action"]))
    btn_row.append(Gtk.Button(label="Destructive Action", css_classes=["destructive-action"]))
    btn_row.append(Gtk.Button(label="Flat Button", css_classes=["flat"]))
    
    # Segmented Control (Pill)
    seg_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, css_classes=["linked"])
    seg_a = Gtk.Button(label="Icons")
    seg_b = Gtk.Button(label="List", css_classes=["suggested-action"])
    seg_c = Gtk.Button(label="Columns")
    seg_box.append(seg_a)
    seg_box.append(seg_b)
    seg_box.append(seg_c)
    btn_row.append(seg_box)

    # Adw.SplitButton
    sb = Adw.SplitButton(label="Share")
    menu = Gio.Menu()
    menu.append("AirDrop", "win.airdrop")
    menu.append("Messages", "win.messages")
    sb.set_menu_model(menu)
    btn_row.append(sb)

    root.append(btn_row)

    # 4. Chrome-like Bubble Card Representation (High Contrast QA)
    bubble_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8, css_classes=["bubble", "card"])
    bubble_card.set_margin_top(8)
    bubble_card.set_margin_bottom(8)
    bubble_card.set_margin_start(20)
    bubble_card.set_margin_end(20)

    bubble_title = Gtk.Label(label="Restore pages? Chrome didn't shut down correctly.", css_classes=["heading"])
    bubble_title.set_halign(Gtk.Align.START)
    bubble_card.append(bubble_title)

    bubble_btns = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10, halign=Gtk.Align.END)
    bubble_btns.append(Gtk.Button(label="Close", css_classes=["flat"]))
    bubble_btns.append(Gtk.Button(label="Restore", css_classes=["suggested-action"]))
    bubble_card.append(bubble_btns)

    root.append(bubble_card)

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
        win.set_default_size(880, 480)
        win.set_decorated(True)
        
        hb, content_box = build_qa_window()
        tv = Adw.ToolbarView()
        tv.add_top_bar(hb)
        tv.set_content(content_box)
        win.set_content(tv)
        win.present()

        # Let GTK layout settle
        for _ in range(25):
            while GLib.MainContext.default().iteration(False): pass

        paintable = Gtk.WidgetPaintable.new(win)
        w = max(win.get_width(), 880)
        h = max(win.get_height(), 480)
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
            # Run in separate python process to ensure clean GTK style context per theme
            subprocess.run([sys.executable, __file__, "--css", css_path, "--mode", mode, "--out", out_file], check=True)
        print(f"\n[Fidelity QA] All {len(themes)} themes rendered into {out_dir}/")
        return

    if not args.css or not args.out:
        parser.error("--css and --out are required unless --all is specified.")

    render_single_gallery(args.css, args.mode, args.out)

if __name__ == "__main__":
    import subprocess
    main()
