# `patch`

This directory contains functions which are used to monkey patch GNOME Shell
methods. See `extension.ts` for more information.

## `add_shadow_in_overview.ts`

Contains a function that adds a shadow actor to a window preview in
the overview. Used to patch the `WindowPreview._addWindow` method.

## `workspace_switch.ts`

Contains functions for handling shadows during workspace switching. Used to
patch the `WorkspaceAnimationController._prepareWorkspaceSwitch` and
`WorkspaceAnimationController._finishWorkspaceSwitch` methods.
