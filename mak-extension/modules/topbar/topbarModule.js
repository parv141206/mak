// SPDX-License-Identifier: GPL-3.0-or-later
// Mak Top Bar Module: Authentic macOS Menu Bar Experience
// Apple Menu, Bold App Title, Media Pill, User Switcher, Status Extras, Spotlight, Control Center, Far-Right Clock

import Clutter from 'gi://Clutter';
import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import GObject from 'gi://GObject';
import Shell from 'gi://Shell';
import St from 'gi://St';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import * as PanelMenu from 'resource:///org/gnome/shell/ui/panelMenu.js';

import { MusicController } from './dynamic-music-pill/controller.js';

const _uid = Math.floor(Math.random() * 10000000);
const { KiwiMenu } = await import(`./kiwimenu.js?v=${_uid}`);
const { BluetoothBatteryButton } = await import(`./bluetoothBattery.js?v=${_uid}`);
const { UserSwitcherController } = await import(`./userSwitcher.js?v=${_uid}`);

const AppTitleButton = GObject.registerClass(
    { GTypeName: `MakAppTitleButton_${_uid}` },
    class AppTitleButton extends PanelMenu.Button {
        _init() {
            super._init(0.0, 'MakAppTitle', false);
            this.reactive = false;

            this._label = new St.Label({
                text: 'Finder',
                style_class: 'mak-app-title-label',
                y_align: Clutter.ActorAlign.CENTER,
            });
            this.add_child(this._label);

            this._tracker = Shell.WindowTracker.get_default();
            this._notifyId = this._tracker.connect('notify::focus-app', () => this._updateTitle());
            this._updateTitle();
        }

        _updateTitle() {
            const app = this._tracker.focus_app;
            if (app) {
                this._label.set_text(app.get_name());
            } else {
                this._label.set_text('Finder');
            }
        }

        destroy() {
            if (this._notifyId) {
                try { this._tracker.disconnect(this._notifyId); } catch (e) {}
                this._notifyId = 0;
            }
            super.destroy();
        }
    }
);

const SpotlightButton = GObject.registerClass(
    { GTypeName: `MakSpotlightButton_${_uid}` },
    class SpotlightButton extends PanelMenu.Button {
        _init(extension) {
            super._init(0.5, 'MakSpotlight', true);
            this._extension = extension;
            this.add_style_class_name('mak-spotlight-button');

            const icon = new St.Icon({
                icon_name: 'edit-find-symbolic',
                style_class: 'system-status-icon',
                y_align: Clutter.ActorAlign.CENTER,
            });
            this.add_child(icon);

            const toggle = () => {
                if (this._extension?._spotlight) {
                    this._extension._spotlight.toggle();
                } else {
                    Main.overview.show();
                }
            };

            const clickGesture = new Clutter.ClickGesture();
            clickGesture.connect('recognize', () => toggle());
            this.add_action(clickGesture);
        }
    }
);

const ControlCenterButton = GObject.registerClass(
    { GTypeName: `MakControlCenterButton_${_uid}` },
    class ControlCenterButton extends PanelMenu.Button {
        _init(extension) {
            super._init(0.5, 'MakControlCenter', true);
            this._extension = extension;
            this.add_style_class_name('mak-control-center-button');

            const iconPath = extension.path + '/icons/control-center-symbolic.svg';
            const gicon = Gio.icon_new_for_string(iconPath);
            const icon = new St.Icon({
                gicon: gicon,
                style_class: 'system-status-icon',
                y_align: Clutter.ActorAlign.CENTER,
            });
            this.add_child(icon);

            const toggle = () => {
                Main.panel.statusArea.quickSettings?.menu?.toggle();
            };

            const clickGesture = new Clutter.ClickGesture();
            clickGesture.connect('recognize', () => toggle());
            this.add_action(clickGesture);
        }
    }
);

export class TopBarModule {
    constructor(extension) {
        this._extension = extension;
        this._settings = extension.getSettings('org.gnome.shell.extensions.mak');
        this._interfaceSettings = new Gio.Settings({ schema_id: 'org.gnome.desktop.interface' });
        this._appleMenu = null;
        this._appTitle = null;
        this._userSwitcher = null;
        this._btBattery = null;
        this._musicController = null;
        this._spotlightBtn = null;
        this._controlCenterBtn = null;
        this._panelBlurEffect = null;
        this._clockMoved = false;
        this._origBannerAlignment = null;
        this._activitiesHidden = false;
        this._settingsChangedId = 0;
        this._interfaceChangedId = 0;
    }

    enable() {
        // 1. Hide default GNOME Activities / Workspace Indicator
        this._hideActivities(true);

        // 2. Add Apple Menu
        if (this._settings.get_boolean('topbar-apple-menu')) {
            this._enableAppleMenu();
        }

        // 3. Add Active App Title in bold
        if (this._settings.get_boolean('topbar-app-title')) {
            this._enableAppTitle();
        }

        // 4. Dynamic Media Pill in Center
        if (this._settings.get_boolean('topbar-media-pill')) {
            this._enableMediaPill();
        }

        // 5. User Switcher Button ("parv@arch")
        if (this._settings.get_boolean('topbar-user-switcher')) {
            this._enableUserSwitcher();
        }

        // 6. Bluetooth Battery Indicator
        if (this._settings.get_boolean('topbar-bluetooth-battery')) {
            this._enableBluetoothBattery();
        }

        // 7. Spotlight Button (Magnifying Glass)
        if (this._settings.get_boolean('topbar-spotlight-button')) {
            this._enableSpotlightButton();
        }

        // 8. Control Center Button (Dual Sliders ⚎)
        if (this._settings.get_boolean('topbar-control-center')) {
            this._enableControlCenterButton();
        }

        // 9. Move Clock to Far Right (macOS position)
        if (this._settings.get_boolean('topbar-clock-right')) {
            this._moveClockToRight();
        }

        // 10. Apply exact macOS Right Box sequence
        this._applyRightBoxOrder();

        // 11. Apply Glass Blur & Styling to Top Bar
        if (this._settings.get_boolean('topbar-blur')) {
            this._applyPanelBlur();
        }

        // 12. Apply panel transparency
        this._applyPanelTransparency();

        Main.panel.add_style_class_name('mak-panel');

        // Settings Listeners
        this._settingsChangedId = this._settings.connect('changed', (s, key) => {
            if (key === 'topbar-apple-menu') {
                if (this._settings.get_boolean('topbar-apple-menu')) this._enableAppleMenu();
                else this._disableAppleMenu();
            } else if (key === 'topbar-app-title') {
                if (this._settings.get_boolean('topbar-app-title')) this._enableAppTitle();
                else this._disableAppTitle();
            } else if (key === 'topbar-user-switcher') {
                if (this._settings.get_boolean('topbar-user-switcher')) this._enableUserSwitcher();
                else this._disableUserSwitcher();
                this._applyRightBoxOrder();
            } else if (key === 'topbar-bluetooth-battery') {
                if (this._settings.get_boolean('topbar-bluetooth-battery')) this._enableBluetoothBattery();
                else this._disableBluetoothBattery();
                this._applyRightBoxOrder();
            } else if (key === 'topbar-spotlight-button') {
                if (this._settings.get_boolean('topbar-spotlight-button')) this._enableSpotlightButton();
                else this._disableSpotlightButton();
                this._applyRightBoxOrder();
            } else if (key === 'topbar-control-center') {
                if (this._settings.get_boolean('topbar-control-center')) this._enableControlCenterButton();
                else this._disableControlCenterButton();
                this._applyRightBoxOrder();
            } else if (key === 'topbar-clock-right') {
                if (this._settings.get_boolean('topbar-clock-right')) this._moveClockToRight();
                else this._restoreClock();
                this._applyRightBoxOrder();
            } else if (key === 'topbar-hide-activities') {
                this._hideActivities(this._settings.get_boolean('topbar-hide-activities'));
            } else if (key === 'topbar-media-pill') {
                if (this._settings.get_boolean('topbar-media-pill')) this._enableMediaPill();
                else this._disableMediaPill();
            } else if (key === 'topbar-transparency' || key === 'global-opacity') {
                this._applyPanelTransparency();
            }
        });

        this._interfaceChangedId = this._interfaceSettings.connect('changed', (s, key) => {
            if (key === 'gtk-theme' || key === 'color-scheme') {
                this._applyPanelTransparency();
            }
        });
    }

    _hideActivities(hide) {
        const activities = Main.panel.statusArea.activities;
        if (activities) {
            if (hide) {
                activities.hide();
                activities.container?.hide();
                this._activitiesHidden = true;
            } else {
                activities.show();
                activities.container?.show();
                this._activitiesHidden = false;
            }
        }
    }

    _enableAppleMenu() {
        if (this._appleMenu) return;
        try {
            const kiwiSettings = this._extension.getSettings('org.gnome.shell.extensions.kiwimenu');
            this._appleMenu = new KiwiMenu(kiwiSettings, this._extension.path, this._extension);
            Main.panel.addToStatusArea('MakAppleMenu', this._appleMenu, 0, 'left');
        } catch (err) {
            console.warn('[Mak TopBar] Could not add Apple Menu:', err);
        }
    }

    _disableAppleMenu() {
        if (this._appleMenu) {
            try { this._appleMenu.destroy(); } catch (e) {}
            this._appleMenu = null;
        }
    }

    _enableAppTitle() {
        if (this._appTitle) return;
        try {
            this._appTitle = new AppTitleButton();
            Main.panel.addToStatusArea('MakAppTitle', this._appTitle, 1, 'left');
        } catch (err) {
            console.warn('[Mak TopBar] Could not add App Title:', err);
        }
    }

    _disableAppTitle() {
        if (this._appTitle) {
            try { this._appTitle.destroy(); } catch (e) {}
            this._appTitle = null;
        }
    }

    _enableUserSwitcher() {
        if (this._userSwitcher) return;
        try {
            this._userSwitcher = new UserSwitcherController(this._extension);
        } catch (err) {
            console.warn('[Mak TopBar] Could not enable User Switcher:', err);
        }
    }

    _disableUserSwitcher() {
        if (this._userSwitcher) {
            try { this._userSwitcher.destroy(); } catch (e) {}
            this._userSwitcher = null;
        }
    }

    _enableBluetoothBattery() {
        if (this._btBattery) return;
        try {
            this._btBattery = new BluetoothBatteryButton(this._extension);
            Main.panel.addToStatusArea('MakBluetoothBattery', this._btBattery, 3, 'right');
        } catch (err) {
            console.warn('[Mak TopBar] Could not add Bluetooth Battery indicator:', err);
        }
    }

    _disableBluetoothBattery() {
        if (this._btBattery) {
            try { this._btBattery.destroy(); } catch (e) {}
            this._btBattery = null;
        }
    }

    _enableSpotlightButton() {
        if (this._spotlightBtn) return;
        try {
            this._spotlightBtn = new SpotlightButton(this._extension);
            Main.panel.addToStatusArea('MakSpotlight', this._spotlightBtn, 5, 'right');
        } catch (err) {
            console.warn('[Mak TopBar] Could not add Spotlight button:', err);
        }
    }

    _disableSpotlightButton() {
        if (this._spotlightBtn) {
            try { this._spotlightBtn.destroy(); } catch (e) {}
            this._spotlightBtn = null;
        }
    }

    _enableControlCenterButton() {
        if (this._controlCenterBtn) return;
        try {
            this._controlCenterBtn = new ControlCenterButton(this._extension);
            Main.panel.addToStatusArea('MakControlCenter', this._controlCenterBtn, 6, 'right');
        } catch (err) {
            console.warn('[Mak TopBar] Could not add Control Center button:', err);
        }
    }

    _disableControlCenterButton() {
        if (this._controlCenterBtn) {
            try { this._controlCenterBtn.destroy(); } catch (e) {}
            this._controlCenterBtn = null;
        }
    }

    _moveClockToRight() {
        const dateMenu = Main.panel.statusArea.dateMenu;
        if (!dateMenu || !dateMenu.container) return;

        const currentParent = dateMenu.container.get_parent();
        if (currentParent === Main.panel._rightBox) {
            this._clockMoved = true;
            return;
        }

        if (currentParent) {
            currentParent.remove_child(dateMenu.container);
        }

        Main.panel._rightBox.add_child(dateMenu.container);
        dateMenu.container.add_style_class_name('mak-clock-button');
        if (typeof dateMenu.menu?.setSourceAlignment === 'function') {
            dateMenu.menu.setSourceAlignment(1.0);
        }

        this._origBannerAlignment = Main.messageTray?.bannerAlignment;
        if (Main.messageTray) {
            Main.messageTray.bannerAlignment = Clutter.ActorAlign.END;
        }
        this._clockMoved = true;
    }

    _restoreClock() {
        const dateMenu = Main.panel.statusArea.dateMenu;
        if (!dateMenu || !dateMenu.container || !this._clockMoved) return;

        const currentParent = dateMenu.container.get_parent();
        if (currentParent) {
            currentParent.remove_child(dateMenu.container);
        }

        Main.panel._centerBox.add_child(dateMenu.container);
        dateMenu.container.remove_style_class_name('mak-clock-button');
        if (typeof dateMenu.menu?.setSourceAlignment === 'function') {
            dateMenu.menu.setSourceAlignment(0.5);
        }

        if (Main.messageTray) {
            Main.messageTray.bannerAlignment = this._origBannerAlignment ?? Clutter.ActorAlign.CENTER;
        }
        this._clockMoved = false;
    }

    _applyRightBoxOrder() {
        const rightBox = Main.panel._rightBox;
        if (!rightBox) return;

        // Visual order in macOS (from left to right):
        // 1. User Switcher ("parv@arch")
        // 2. Keyboard layout (Input Source)
        // 3. Bluetooth Battery indicator
        // 4. Quick Settings (Wi-Fi, Battery %, etc.)
        // 5. Spotlight Search (🔍)
        // 6. Control Center (⚎)
        // 7. Date & Time (Far Right Corner)
        const order = [
            'MakUserSwitcher',
            'keyboard',
            'MakBluetoothBattery',
            'quickSettings',
            'MakSpotlight',
            'MakControlCenter',
            'dateMenu',
        ];

        order.forEach(role => {
            const item = Main.panel.statusArea[role];
            const container = item?.container;
            if (container && container.get_parent() === rightBox) {
                const children = rightBox.get_children();
                if (children.length > 0 && children[children.length - 1] !== container) {
                    rightBox.remove_child(container);
                    rightBox.add_child(container);
                }
            }
        });
        console.log('[Mak TopBar] RightBox order applied cleanly. UserSwitcher label:', this._userSwitcher?._userSwitcher?._nameLabel?.get_text());
    }

    _enableMediaPill() {
        if (this._musicController) return;
        try {
            this._musicController = new MusicController(this._extension);
            this._musicController.enable();
        } catch (err) {
            console.warn('[Mak TopBar] Could not enable Dynamic Music Pill:', err);
        }
    }

    _disableMediaPill() {
        if (this._musicController) {
            try { this._musicController.disable(); } catch (e) {}
            this._musicController = null;
        }
    }

    _applyPanelBlur() {
        // Panel blur is handled by Blur-My-Shell (BlurModule) using gnome-rounded-blur
    }

    _removePanelBlur() {
        if (this._panelBlurEffect) {
            try { Main.panel.remove_effect(this._panelBlurEffect); } catch (e) {}
            this._panelBlurEffect = null;
        }
    }

    _applyPanelTransparency() {
        try {
            let alpha = this._settings.get_double('topbar-transparency');
            const colorScheme = this._interfaceSettings ? this._interfaceSettings.get_string('color-scheme') : '';
            const gtkTheme = this._interfaceSettings ? this._interfaceSettings.get_string('gtk-theme') : '';
            const isLight = (colorScheme === 'prefer-light') || gtkTheme.toLowerCase().includes('light');
            const isAmoled = gtkTheme.toLowerCase().includes('amoled');

            if (isLight) {
                Main.panel.add_style_class_name('light-mode');
                const r = 255, g = 255, b = 255;
                const style = `background-color: rgba(${r}, ${g}, ${b}, ${alpha.toFixed(3)});`;
                Main.panel.set_style(style);
            } else {
                Main.panel.remove_style_class_name('light-mode');
                const r = isAmoled ? 0 : 22;
                const g = isAmoled ? 0 : 22;
                const b = isAmoled ? 0 : 28;
                const style = `background-color: rgba(${r}, ${g}, ${b}, ${alpha.toFixed(3)});`;
                Main.panel.set_style(style);
            }
        } catch (e) {
            console.warn('[Mak TopBar] Could not apply panel transparency:', e.message);
        }
    }

    _removePanelTransparency() {
        try { Main.panel.set_style(''); } catch (e) {}
    }

    disable() {
        if (this._settingsChangedId) {
            try { this._settings.disconnect(this._settingsChangedId); } catch (e) {}
            this._settingsChangedId = 0;
        }

        if (this._interfaceChangedId) {
            try { this._interfaceSettings.disconnect(this._interfaceChangedId); } catch (e) {}
            this._interfaceChangedId = 0;
        }
        this._interfaceSettings = null;

        this._restoreClock();
        this._hideActivities(false);

        this._disableControlCenterButton();
        this._disableSpotlightButton();
        this._disableBluetoothBattery();
        this._disableUserSwitcher();
        this._disableMediaPill();
        this._disableAppTitle();
        this._disableAppleMenu();

        this._removePanelBlur();
        this._removePanelTransparency();
        Main.panel.remove_style_class_name('mak-panel');
        Main.panel.remove_style_class_name('light-mode');
    }
}
