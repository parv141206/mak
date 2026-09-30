# `window_picker`

The extensions preferences window runs in a separate isolated process which has
no access to GNOME Shell methods. However, the window picking functionality is
based on GNOME Shell's Looking Glass.

To allow the preferences window to communicate with the main process, the code
in this directory creates a DBus service, which has a method to open the window
picker and a signal to transmit the class of the selected window.

## `iface.xml`

Defines the DBus interface for the window picker.

## `service.ts`

Contains the implementation of the DBus interface.

## `client.ts`

Provides wrapper JavaScript functions around the DBus method calls.
