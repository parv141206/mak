// Gio.Settings wrapper and derived configuration snapshot generator.

import { clamp, logError, TimeoutGroup } from './utils.js';
import {
    ICON_BOT,
    SETTINGS_DEBOUNCE_MS,
    STRUCTURAL_KEYS,
} from './constants.js';
import { migrateSettings } from './settingsMigration.js';
import { parseCustomItems } from '../services/customItems.js';

const SETTINGS_RETRY_DELAYS_MS = [250, 500, 1000, 2000];

// Pill thickness derived from icon size when auto mode is on: 25 px
// of vertical breathing room around the icon, clamped to the schema's range.
function autoPillThickness(iconSize) {
    return Math.max(36, Math.min(120, iconSize + 25));
}

// Derive the full runtime configuration from raw settings. Pure function of the
// settings object: same keys in, same snapshot out. Kept module-private so the
// only supported way to read config is the cached `config` getter.
function computeConfig(s, mak = null) {
    const scale = clamp(s.get_double('dock-scale'), 0.5, 2.0);
    const iconSize = Math.round((mak ? mak.get_int('icon-size') : s.get_int('icon-size')) * scale);
    const zoomMax = Math.max(1, s.get_double('magnification'));
    const renderSize = Math.round(iconSize * zoomMax);
    const pillThickness = s.get_boolean('pill-thickness-auto')
        ? autoPillThickness(iconSize)
        : s.get_int('pill-thickness');
    const dockH = Math.round(pillThickness * scale);
    const hoverLift = Math.round(s.get_int('hover-lift') * scale);
    const requestedSpacing = s.get_int('icon-spacing');
    // The original dock used two independently rounded 6px side paddings.
    // Preserve that exact geometry for the new 12px default at fractional
    // scales, while user-selected values retain exact single-pixel steps.
    const iconSpacing = requestedSpacing === 12
        ? Math.round(requestedSpacing * scale / 2) * 2
        : Math.round(requestedSpacing * scale);
    const cellPad = iconSpacing / 2;
    const iconTopAtRest = dockH - ICON_BOT - iconSize;
    const headroom = Math.max(0, renderSize - iconSize + hoverLift - iconTopAtRest) + 10;
    const position = mak ? mak.get_string('dock-position') : s.get_string('dock-position');
    const vertical = position === 'left' || position === 'right';
    const autoHideMode = s.get_string('auto-hide-mode');

    const blurRadius = mak ? mak.get_int('blur-sigma') : 30;
    const blurBrightness = mak ? mak.get_double('blur-brightness') : 0.75;
    const dockBlur = mak ? (mak.get_boolean('dock-blur') && mak.get_boolean('blur-dock') && mak.get_boolean('blur-enabled')) : true;
    const _dockOpacity = mak ? mak.get_double('background-opacity') : s.get_double('background-opacity');
    // global-opacity overrides per-surface opacity when the user has set it (default is -1 sentinel, absent from schema so we check a special value)
    // We use global-opacity directly as the master multiplier if it's stored != 0.5 default OR always use it:
    const globalOpacity = mak ? mak.get_double('global-opacity') : 0.5;
    // global-opacity of 0.5 means "not overriding" (default). When changed from 0.5,
    // map it 0→0 .. 1→1 and apply to all per-surface opacities.
    // We always read global-opacity as a master; user can tune per-surface separately.
    const bgOpacity = globalOpacity !== 0.5 ? globalOpacity : _dockOpacity;
    const dockRadius = mak ? mak.get_int('dock-radius') : s.get_int('dock-radius');
    const pillColor = mak ? mak.get_string('pill-color') : s.get_string('pill-color');
    const borderColor = mak ? mak.get_string('border-color') : s.get_string('border-color');
    const borderWidth = mak ? mak.get_int('border-width') : s.get_int('border-width');
    const liquidGlass = mak ? mak.get_boolean('blur-liquid-glass') : false;
    const refractionStrength = mak ? mak.get_double('blur-refraction-strength') : 0.42;
    const chromaticDispersion = mak ? mak.get_double('blur-chromatic-dispersion') : 0.08;

    return {
        // ── Sizing / geometry ──
        scale,
        iconSize,
        zoomMax,
        renderSize,
        placeIconSourceSize: Math.max(32, renderSize),
        cellW: iconSize + iconSpacing,
        cellPad,
        iconSpacing,
        dockH,
        headroom,
        hitH: headroom + dockH,
        vertical,
        // Pre-computed for per-frame hot paths (avoids repeated division).
        invZoom: 1 / zoomMax,
        liftDenom: 1 / Math.max(0.001, zoomMax - 1),
        position,
        alignment: s.get_string('dock-alignment'),
        multiMonitor: s.get_boolean('multi-monitor'),
        isolateMonitors: s.get_boolean('isolate-monitors'),
        autoShrink: s.get_boolean('auto-shrink-to-fit'),
        zoomRange: Math.round(s.get_int('zoom-range') * scale),
        magnificationCurve: s.get_double('magnification-curve'),
        edgeMargin: s.get_int('edge-margin'),
        dockRadius,
        hoverLift,

        // ── Background / chrome & blur ──
        blurRadius,
        blurBrightness,
        dockBlur,
        bgOpacity,
        pillColor,
        borderColor,
        borderWidth,
        liquidGlass,
        refractionStrength,
        chromaticDispersion,

        // ── Sections / behaviour ──
        showApps: s.get_boolean('show-apps-button'),
        appsButtonPosition: s.get_int('apps-button-position'),
        appsIcon: s.get_string('apps-button-icon'),
        showDownloads: s.get_boolean('show-downloads'),
        showCustomFolder: s.get_boolean('show-custom-folder'),
        customFolderUri: s.get_string('custom-folder-uri'),
        useFolderMetadataIcons: s.get_boolean('use-folder-metadata-icons'),
        showCustomDockItems: s.get_boolean('show-custom-dock-items'),
        customDockItems: parseCustomItems(s.get_strv('custom-dock-items')),
        showMountedDevices: s.get_boolean('show-mounted-devices'),
        showRemovableDevices: s.get_boolean('show-removable-devices'),
        showNetworkDevices: s.get_boolean('show-network-devices'),
        showFixedDevices: s.get_boolean('show-fixed-devices'),
        hiddenMountedDevices: s.get_strv('hidden-mounted-devices'),
        showTrash: s.get_boolean('show-trash'),
        clickToMinimize: s.get_boolean('click-to-minimize'),
        leftClickAction: s.get_string('left-click-action'),
        middleClickAction: s.get_string('middle-click-action'),
        scrollAction: s.get_string('scroll-action'),
        dragToOpen: s.get_boolean('drag-to-open'),
        layoutLocked: s.get_boolean('lock-layout'),
        isolateWS: s.get_boolean('isolate-workspaces'),

        // ── Auto-hide ──
        autoHideMode,
        autoHideActive: autoHideMode !== 'never',
        hideDelay: s.get_int('hide-delay'),
        revealPressure: s.get_int('reveal-pressure'),
        showAutohideHandle: s.get_boolean('show-autohide-handle'),
        pressureSense: s.get_boolean('pressure-sense'),
        pressureSenseSensitivity: s.get_double('pressure-sense-sensitivity'),

        // ── Animation / physics ──
        tau: s.get_int('animation-smoothness'),
        springTension: s.get_double('spring-tension'),
        springDamping: s.get_double('spring-damping'),
        bounceHeight: Math.round(s.get_int('bounce-height') * scale),
        bounceDecay: clamp(s.get_double('bounce-decay'), 0.30, 0.95),

        // ── Genie ──
        enableGenieEffect: s.get_boolean('enable-genie-effect'),
        genieDuration: s.get_int('genie-duration'),

        // ── Tooltip ──
        showTooltip: s.get_boolean('show-tooltip'),
        tooltipDelay: s.get_int('tooltip-delay'),
        tooltipRadius: s.get_int('tooltip-radius'),
        tooltipBg: s.get_string('tooltip-bg-color'),
        tooltipFg: s.get_string('tooltip-text-color'),
        tooltipBorderColor: s.get_string('tooltip-border-color'),
        tooltipBorderWidth: s.get_int('tooltip-border-width'),

        // ── Context menu ──
        menuUseGnomeDefault: s.get_boolean('menu-use-gnome-default'),
        menuRadius: s.get_int('menu-radius'),
        menuBg: s.get_string('menu-bg-color'),
        menuFg: s.get_string('menu-text-color'),
        menuBorderColor: s.get_string('menu-border-color'),
        menuBorderWidth: s.get_int('menu-border-width'),

        // ── Previews ──
        showPreviews: s.get_boolean('show-previews'),
        previewDelay: s.get_int('preview-delay'),
        previewSize: Math.round(s.get_int('preview-size') * scale),
        previewWindowMode: s.get_string('preview-window-mode'),
        previewCloseButtons: s.get_boolean('preview-close-buttons'),
        previewOverflowMode: s.get_string('preview-overflow-mode'),
        previewPageSize: s.get_int('preview-page-size'),
        previewKeyboardNavigation: s.get_boolean('preview-keyboard-navigation'),
        previewWindowActions: s.get_boolean('preview-window-actions'),

        // ── Indicators / badges ──
        indicatorStyle: s.get_string('indicator-style'),
        indicatorSize: s.get_int('indicator-size'),
        indicatorColor: s.get_string('indicator-color'),
        showWindowCount: s.get_boolean('show-window-count'),
        showBadges: s.get_boolean('show-badges'),
        badgeColor: s.get_string('badge-color'),
        badgeTextColor: s.get_string('badge-text-color'),

        // ── Downloads stack ──
        downloadsView: s.get_string('downloads-view'),
        downloadsMaxFiles: s.get_int('downloads-max-files'),
        downloadsSort: s.get_string('downloads-sort'),
        downloadsPillColor: s.get_string('downloads-pill-color'),
        downloadsBorderRadius: s.get_int('downloads-border-radius'),
        downloadsBorderColor: s.get_string('downloads-border-color'),
        downloadsBorderWidth: s.get_int('downloads-border-width'),
        dlItemColor: s.get_string('downloads-item-color'),
        dlItemRadius: s.get_int('downloads-item-radius'),
        dlItemBorderColor: s.get_string('downloads-item-border-color'),
        dlItemBorderWidth: s.get_int('downloads-item-border-width'),
        dlItemThumbColor: s.get_string('downloads-item-thumb-color'),
        dlItemFontColor: s.get_string('downloads-item-font-color'),

        // ── Accessibility ──
        reduceMotion: s.get_boolean('reduce-motion'),
        highContrast: s.get_boolean('high-contrast'),
        interfaceTextScale: s.get_double('interface-text-scale'),
        announceItemStatus: s.get_boolean('announce-item-status'),

    };
}

export class SettingsManager {
    constructor(settings, bus, makSettings = null) {
        this._settings = settings;
        this._makSettings = makSettings;
        this._bus = bus;
        migrateSettings(settings);
        this._config = computeConfig(settings, makSettings);

        this._pendingStructural = false;
        this._pendingKeys = new Set();
        this._timers = new TimeoutGroup();
        this._flushId = 0;
        this._retryCount = 0;

        this._changedId = settings.connect('changed', (_s, key) => this._onChanged(key));
        if (makSettings) {
            this._makChangedId = makSettings.connect('changed', (_s, key) => this._onMakChanged(key));
        }
    }

    // The cached, fully-derived snapshot. Stable reference between flushes.
    get config() {
        return this._config;
    }

    // Escape hatch for consumers that must register a keybinding or write a
    // setting. Prefer `config` everywhere else.
    get raw() {
        return this._settings;
    }

    _onMakChanged(key) {
        if (key === 'blur-sigma') {
            this._config.blurRadius = this._makSettings.get_int('blur-sigma');
            this._pendingKeys.add('blur-sigma');
            this._pendingKeys.add('blurRadius');
        } else if (key === 'blur-brightness') {
            this._config.blurBrightness = this._makSettings.get_double('blur-brightness');
            this._pendingKeys.add('blur-brightness');
            this._pendingKeys.add('blurBrightness');
        } else if (key === 'blur-dock' || key === 'dock-blur' || key === 'blur-enabled') {
            this._config.dockBlur = this._makSettings.get_boolean('blur-dock') && this._makSettings.get_boolean('dock-blur') && this._makSettings.get_boolean('blur-enabled');
            this._pendingKeys.add('blur-dock');
            this._pendingKeys.add('dock-blur');
            this._pendingKeys.add('dockBlur');
        } else if (key === 'background-opacity') {
            const globalOpacity = this._makSettings.get_double('global-opacity');
            this._config.bgOpacity = globalOpacity !== 0.5 ? globalOpacity : this._makSettings.get_double('background-opacity');
            this._pendingKeys.add('background-opacity');
        } else if (key === 'global-opacity') {
            const globalOpacity = this._makSettings.get_double('global-opacity');
            this._config.bgOpacity = globalOpacity !== 0.5 ? globalOpacity : this._makSettings.get_double('background-opacity');
            this._pendingKeys.add('background-opacity');
            this._pendingKeys.add('global-opacity');
        } else if (key === 'dock-radius') {
            this._config.dockRadius = this._makSettings.get_int('dock-radius');
            this._pendingKeys.add('dock-radius');
            this._pendingStructural = true;
        } else if (key === 'border-width') {
            this._config.borderWidth = this._makSettings.get_int('border-width');
            this._pendingKeys.add('border-width');
        } else if (key === 'border-color') {
            this._config.borderColor = this._makSettings.get_string('border-color');
            this._pendingKeys.add('border-color');
        } else if (key === 'pill-color') {
            this._config.pillColor = this._makSettings.get_string('pill-color');
            this._pendingKeys.add('pill-color');
        } else if (key === 'dock-position') {
            this._config.position = this._makSettings.get_string('dock-position');
            this._pendingKeys.add('dock-position');
            this._pendingStructural = true;
        } else if (key === 'blur-liquid-glass') {
            this._config.liquidGlass = this._makSettings.get_boolean('blur-liquid-glass');
            this._pendingKeys.add('blur-liquid-glass');
        } else if (key === 'blur-refraction-strength') {
            this._config.refractionStrength = this._makSettings.get_double('blur-refraction-strength');
            this._pendingKeys.add('blur-refraction-strength');
        } else if (key === 'blur-chromatic-dispersion') {
            this._config.chromaticDispersion = this._makSettings.get_double('blur-chromatic-dispersion');
            this._pendingKeys.add('blur-chromatic-dispersion');
        } else {
            return;
        }
        this._scheduleFlush(30);
    }

    _onChanged(key) {
        this._pendingKeys.add(key);
        if (STRUCTURAL_KEYS.has(key)) this._pendingStructural = true;
        this._retryCount = 0;

        this._scheduleFlush(SETTINGS_DEBOUNCE_MS);
    }

    _scheduleFlush(delay) {
        if (this._flushId) this._timers.remove(this._flushId);
        this._flushId = this._timers.addOnce(delay, () => {
            this._flushId = 0;
            this._flush();
        });
    }

    _flush() {
        const structural = this._pendingStructural;
        const keys = new Set(this._pendingKeys);
        let nextConfig;
        try { nextConfig = computeConfig(this._settings, this._makSettings); }
        catch (e) {
            // Preserve the failed batch and retry transient GSettings/read
            // failures a few times with bounded backoff. Permanent failures do
            // not create an endless timer/log loop; the next real settings
            // change resets the retry budget and tries the complete batch again.
            logError(e, 'computeConfig');
            if (this._retryCount < SETTINGS_RETRY_DELAYS_MS.length) {
                const delay = SETTINGS_RETRY_DELAYS_MS[this._retryCount++];
                this._scheduleFlush(delay);
            }
            return;
        }

        this._retryCount = 0;
        this._pendingStructural = false;
        this._pendingKeys.clear();
        this._config = nextConfig;
        this._bus.emit('settings-changed', {
            structural,
            keys,
            config: this._config,
        });
    }

    destroy() {
        this._timers.removeAll();
        this._flushId = 0;
        this._retryCount = 0;
        if (this._changedId && this._settings) {
            this._settings.disconnect(this._changedId);
            this._changedId = 0;
        }
        if (this._makChangedId && this._makSettings) {
            this._makSettings.disconnect(this._makChangedId);
            this._makChangedId = 0;
        }
        this._pendingKeys.clear();
        this._bus = null;
        this._settings = null;
        this._makSettings = null;
        this._config = null;
    }
}
