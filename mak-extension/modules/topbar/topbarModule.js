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
const { MenuStyleController } = await import(`../appearance/menuStyleController.js?v=${_uid}`);
const { WindowCornersModule } = await import(`../window-corners/cornersModule.js?v=${_uid}`);
const { BlurModule } = await import(`../blur/blurModule.js?v=${_uid}`);
const { ClipboardButton } = await import(`./clipboardButton.js?v=${_uid}`);
const { CaffeineButton } = await import(`./caffeineButton.js?v=${_uid}`);
const { NotesButton } = await import(`./notesButton.js?v=${_uid}`);
const { DynamicIsland } = await import(`./dynamicIsland.js?v=${_uid}`);
const { MacBatteryController } = await import(`./macBattery.js?v=${_uid}`);
const { PowerSaverButton } = await import(`./powerSaverButton.js?v=${_uid}`);

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
        this._makQuickSettingsBtn = null;
        this._clipboardBtn = null;
        this._caffeineBtn = null;
        this._notesBtn = null;
        this._dynamicIsland = null;
        this._macBattery = null;
        this._panelBlurEffect = null;
        this._clockMoved = false;
        this._origBannerAlignment = null;
        this._activitiesHidden = false;
        this._settingsChangedId = 0;
        this._interfaceChangedId = 0;
    }

    enable() {
        // Hot-reload dynamic styling, corners, and blur modules to ensure latest codebase runs
        if (this._extension) {
            try {
                if (this._extension._menuStyle) this._extension._menuStyle.disable();
                this._extension._menuStyle = new MenuStyleController(this._extension);
                this._extension._menuStyle.enable();
            } catch (err) {
                console.warn('[Mak TopBar] Could not hot-reload MenuStyleController:', err);
            }

            try {
                if (this._extension._windowCorners) this._extension._windowCorners.disable();
                this._extension._windowCorners = new WindowCornersModule(this._extension);
                this._extension._windowCorners.enable();
            } catch (err) {
                console.warn('[Mak TopBar] Could not hot-reload WindowCornersModule:', err);
            }

            try {
                if (this._extension._blur) this._extension._blur.disable();
                this._extension._blur = new BlurModule(this._extension);
                this._extension._blur.enable();
            } catch (err) {
                console.warn('[Mak TopBar] Could not hot-reload BlurModule:', err);
            }
        }

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

        // 6a. macOS System Battery (Colored + Inside/Side Percentage)
        this._enableMacBattery();

        // 6b. Caffeine Button (☕)
        if (this._settings.get_boolean('topbar-caffeine')) {
            this._enableCaffeineButton();
        }

        // 6b2. Eco Power Saver Button (🌿 / ⚡)
        if (this._settings.get_boolean('topbar-power-saver')) {
            this._enablePowerSaverButton();
        }

        // 6c. Notes Scratchpad Button (📝)
        if (this._settings.get_boolean('topbar-scratchpad')) {
            this._enableNotesButton();
        }

        // 7. Spotlight Button (Magnifying Glass)
        if (this._settings.get_boolean('topbar-spotlight-button')) {
            this._enableSpotlightButton();
        }

        // 7b. Clipboard Button (📋)
        if (this._settings.get_boolean('topbar-clipboard')) {
            this._enableClipboardButton();
        }

        // 7c. Dynamic Island
        if (this._settings.get_boolean('dynamic-island-enabled')) {
            this._enableDynamicIsland();
        }

        // 8. Control Center Button (Dual Sliders ⚎)
        if (this._settings.get_boolean('topbar-control-center')) {
            this._enableControlCenterButton();
        }

        // 8b. Mak Quick Settings Widget
        if (this._settings.get_boolean('topbar-mak-menu')) {
            this._enableMakQuickSettingsButton();
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

        // Re-apply panel transparency / opaqueness when returning from overview
        this._overviewHidingId = Main.overview.connect('hiding', () => {
            this._applyPanelTransparency();
        });
        this._overviewHiddenId = Main.overview.connect('hidden', () => {
            this._applyPanelTransparency();
        });

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
            } else if (key === 'topbar-caffeine') {
                if (this._settings.get_boolean('topbar-caffeine')) this._enableCaffeineButton();
                else this._disableCaffeineButton();
                this._applyRightBoxOrder();
            } else if (key === 'topbar-power-saver') {
                if (this._settings.get_boolean('topbar-power-saver')) this._enablePowerSaverButton();
                else this._disablePowerSaverButton();
                this._applyRightBoxOrder();
            } else if (key === 'topbar-scratchpad') {
                if (this._settings.get_boolean('topbar-scratchpad')) this._enableNotesButton();
                else this._disableNotesButton();
                this._applyRightBoxOrder();
            } else if (key === 'topbar-spotlight-button') {
                if (this._settings.get_boolean('topbar-spotlight-button')) this._enableSpotlightButton();
                else this._disableSpotlightButton();
                this._applyRightBoxOrder();
            } else if (key === 'topbar-clipboard') {
                if (this._settings.get_boolean('topbar-clipboard')) this._enableClipboardButton();
                else this._disableClipboardButton();
                this._applyRightBoxOrder();
            } else if (key === 'dynamic-island-enabled') {
                if (this._settings.get_boolean('dynamic-island-enabled')) this._enableDynamicIsland();
                else this._disableDynamicIsland();
            } else if (key === 'topbar-control-center') {
                if (this._settings.get_boolean('topbar-control-center')) this._enableControlCenterButton();
                else this._disableControlCenterButton();
                this._applyRightBoxOrder();
            } else if (key === 'topbar-mak-menu') {
                if (this._settings.get_boolean('topbar-mak-menu')) this._enableMakQuickSettingsButton();
                else this._disableMakQuickSettingsButton();
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
            } else if (key === 'topbar-transparency' || key === 'topbar-opaque' ||
                       key === 'topbar-transparent' || key === 'topbar-style-mode' ||
                       key === 'global-opacity' || key === 'topbar-blur' ||
                       key === 'topbar-blur-radius' || key === 'blur-panel') {
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

    async _enableCaffeineButton() {
        if (this._caffeineBtn) return;
        try {
            let Cls = CaffeineButton;
            try {
                const mod = await import(`./caffeineButton.js?v=${Date.now()}`);
                if (mod && mod.CaffeineButton) Cls = mod.CaffeineButton;
            } catch (e) {}
            this._caffeineBtn = new Cls(this._extension);
            Main.panel.addToStatusArea('MakCaffeine', this._caffeineBtn, 3, 'right');
            this._applyRightBoxOrder();
        } catch (err) {
            console.warn('[Mak TopBar] Could not add Caffeine button:', err);
        }
    }

    _disableCaffeineButton() {
        if (this._caffeineBtn) {
            try { this._caffeineBtn.destroy(); } catch (e) {}
            this._caffeineBtn = null;
        }
    }

    async _enablePowerSaverButton() {
        if (this._powerSaverBtn) return;
        try {
            let Cls = PowerSaverButton;
            try {
                const mod = await import(`./powerSaverButton.js?v=${Date.now()}`);
                if (mod && mod.PowerSaverButton) Cls = mod.PowerSaverButton;
            } catch (e) {}
            this._powerSaverBtn = new Cls(this._extension);
            Main.panel.addToStatusArea('MakPowerSaver', this._powerSaverBtn, 3, 'right');
            this._applyRightBoxOrder();
        } catch (err) {
            console.warn('[Mak TopBar] Could not add PowerSaver button:', err);
        }
    }

    _disablePowerSaverButton() {
        if (this._powerSaverBtn) {
            try { this._powerSaverBtn.destroy(); } catch (e) {}
            this._powerSaverBtn = null;
        }
    }

    async _enableNotesButton() {
        if (this._notesBtn) return;
        try {
            let Cls = NotesButton;
            try {
                const mod = await import(`./notesButton.js?v=${Date.now()}`);
                if (mod && mod.NotesButton) Cls = mod.NotesButton;
            } catch (e) {}
            this._notesBtn = new Cls(this._extension);
            Main.panel.addToStatusArea('MakNotes', this._notesBtn, 4, 'right');
            this._applyRightBoxOrder();
        } catch (err) {
            console.warn('[Mak TopBar] Could not add Notes button:', err);
        }
    }

    _disableNotesButton() {
        if (this._notesBtn) {
            try { this._notesBtn.destroy(); } catch (e) {}
            this._notesBtn = null;
        }
    }

    async _enableDynamicIsland() {
        if (this._dynamicIsland) return;
        try {
            let Cls = DynamicIsland;
            try {
                const mod = await import(`./dynamicIsland.js?v=${Date.now()}`);
                if (mod && mod.DynamicIsland) Cls = mod.DynamicIsland;
            } catch (e) {}
            this._dynamicIsland = new Cls(this._extension);
        } catch (err) {
            console.warn('[Mak TopBar] Could not add Dynamic Island:', err);
        }
    }

    _disableDynamicIsland() {
        if (this._dynamicIsland) {
            try { this._dynamicIsland.destroy(); } catch (e) {}
            this._dynamicIsland = null;
        }
    }

    async _enableClipboardButton() {
        if (this._clipboardBtn) return;
        try {
            let Cls = ClipboardButton;
            try {
                const mod = await import(`./clipboardButton.js?v=${Date.now()}`);
                if (mod && mod.ClipboardButton) Cls = mod.ClipboardButton;
            } catch (err) {
                // fallback to static import
            }
            this._clipboardBtn = new Cls(this._extension);
            Main.panel.addToStatusArea('MakClipboard', this._clipboardBtn, 4, 'right');
            this._applyRightBoxOrder();
        } catch (err) {
            console.warn('[Mak TopBar] Could not add Clipboard button:', err);
        }
    }

    _disableClipboardButton() {
        if (this._clipboardBtn) {
            try { this._clipboardBtn.destroy(); } catch (e) {}
            this._clipboardBtn = null;
        }
    }

    async _enableMacBattery() {
        if (this._macBattery) return;
        try {
            let Cls = MacBatteryController;
            try {
                const mod = await import(`./macBattery.js?v=${Date.now()}`);
                if (mod && mod.MacBatteryController) Cls = mod.MacBatteryController;
            } catch (e) {}
            this._macBattery = new Cls(this._extension);
            this._macBattery.enable();
        } catch (err) {
            console.warn('[Mak TopBar] Could not enable MacBattery:', err);
        }
    }

    _disableMacBattery() {
        if (this._macBattery) {
            try { this._macBattery.disable(); } catch (e) {}
            this._macBattery = null;
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

    async _enableMakQuickSettingsButton() {
        if (this._makQuickSettingsBtn) return;
        try {
            const v = Date.now();
            const { MakQuickSettingsButton } = await import(`./makQuickSettings.js?v=${v}`);
            this._makQuickSettingsBtn = new MakQuickSettingsButton(this._extension);
            Main.panel.addToStatusArea('MakQuickSettings', this._makQuickSettingsBtn, 7, 'right');
            this._applyRightBoxOrder();
        } catch (err) {
            console.warn('[Mak TopBar] Could not add Mak Quick Settings button:', err);
        }
    }

    _disableMakQuickSettingsButton() {
        if (this._makQuickSettingsBtn) {
            try { this._makQuickSettingsBtn.destroy(); } catch (e) {}
            this._makQuickSettingsBtn = null;
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
        // 7. Mak Quick Settings (⌘)
        // 8. Date & Time (Far Right Corner)
        const order = [
            'MakUserSwitcher',
            'keyboard',
            'MakBluetoothBattery',
            'quickSettings',
            'MakCaffeine',
            'MakPowerSaver',
            'MakNotes',
            'MakClipboard',
            'MakSpotlight',
            'MakControlCenter',
            'MakQuickSettings',
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
            const isOpaque = this._settings.get_boolean('topbar-opaque');
            const isTransparent = this._settings.settings_schema?.has_key('topbar-transparent')
                ? this._settings.get_boolean('topbar-transparent')
                : false;
            let styleMode = this._settings.settings_schema?.has_key('topbar-style-mode')
                ? this._settings.get_string('topbar-style-mode')
                : '';

            if (!styleMode) {
                if (isTransparent) styleMode = 'transparent';
                else if (isOpaque) styleMode = 'opaque';
                else styleMode = 'frosted';
            }

            const colorScheme = this._interfaceSettings ? this._interfaceSettings.get_string('color-scheme') : '';
            const gtkTheme = this._interfaceSettings ? this._interfaceSettings.get_string('gtk-theme') : '';
            const isLight = (colorScheme === 'prefer-light') || gtkTheme.toLowerCase().includes('light');
            const isAmoled = gtkTheme.toLowerCase().includes('amoled');

            if (isAmoled) {
                Main.panel.add_style_class_name('amoled-mode');
            } else {
                Main.panel.remove_style_class_name('amoled-mode');
            }

            if (isLight) {
                Main.panel.add_style_class_name('light-mode');
            } else {
                Main.panel.remove_style_class_name('light-mode');
            }

            if (styleMode === 'transparent' || (isTransparent && !isOpaque)) {
                Main.panel.add_style_class_name('transparent-panel');
                Main.panel.remove_style_class_name('opaque-panel');
                Main.panel.set_style('background-color: transparent !important; box-shadow: none !important; border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;');
            } else if (styleMode === 'opaque' || isOpaque) {
                Main.panel.add_style_class_name('opaque-panel');
                Main.panel.remove_style_class_name('transparent-panel');
                const r = isLight ? 246 : (isAmoled ? 0 : 32);
                const g = isLight ? 246 : (isAmoled ? 0 : 32);
                const b = isLight ? 248 : (isAmoled ? 0 : 36);
                Main.panel.set_style(`background-color: rgb(${r}, ${g}, ${b}) !important; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.22) !important; border-bottom: 1px solid rgba(255, 255, 255, 0.12) !important;`);
            } else {
                // Frosted Glass mode
                Main.panel.remove_style_class_name('opaque-panel');
                Main.panel.remove_style_class_name('transparent-panel');
                let rawAlpha = this._settings.get_double('topbar-transparency');
                // If previous opaque setting left rawAlpha at 1.0, use frosted default 0.35
                let alpha = (rawAlpha >= 0.98) ? 0.35 : Math.max(0.0, rawAlpha);
                const r = isLight ? 246 : (isAmoled ? 18 : 32);
                const g = isLight ? 246 : (isAmoled ? 18 : 32);
                const b = isLight ? 248 : (isAmoled ? 22 : 36);
                Main.panel.set_style(`background-color: rgba(${r}, ${g}, ${b}, ${alpha.toFixed(3)}) !important; border-bottom: 1px solid rgba(255, 255, 255, 0.12) !important; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15) !important;`);
            }
        } catch (e) {
            console.warn('[Mak TopBar] Could not apply panel transparency:', e.message);
        }
    }

    _removePanelTransparency() {
        try { Main.panel.set_style(''); } catch (e) {}
    }

    disable() {
        if (this._overviewHidingId) {
            try { Main.overview.disconnect(this._overviewHidingId); } catch (e) {}
            this._overviewHidingId = 0;
        }

        if (this._overviewHiddenId) {
            try { Main.overview.disconnect(this._overviewHiddenId); } catch (e) {}
            this._overviewHiddenId = 0;
        }

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

        this._disableDynamicIsland();
        this._disableNotesButton();
        this._disableCaffeineButton();
        this._disablePowerSaverButton();
        this._disableMacBattery();
        this._disableControlCenterButton();
        this._disableMakQuickSettingsButton();
        this._disableClipboardButton();
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
        Main.panel.remove_style_class_name('opaque-panel');
        Main.panel.remove_style_class_name('amoled-mode');
    }
}
