"""Native dialogs via NSAlert (replaces AppleScript prompts)."""
from __future__ import annotations

from typing import List, Optional

from Foundation import NSMakeRect
from AppKit import (NSAlert, NSTextField, NSSecureTextField, NSAlertFirstButtonReturn,
                    NSApp, NSView, NSPopUpButton)


def _bring_to_front():
    app = NSApp()
    if app is not None:
        app.activateIgnoringOtherApps_(True)


class Dialogs:
    def __init__(self, i18n=None, logger=None):
        self.i18n = i18n
        self.log = logger

    def _ok_cancel_titles(self):
        if self.i18n is not None:
            return self.i18n.ok, self.i18n.cancel
        return 'OK', 'Cancel'

    def input(self, title: str, description: str, default: str = '',
              hidden: bool = False) -> Optional[str]:
        _bring_to_front()
        alert = NSAlert.alloc().init()
        alert.setMessageText_(title)
        alert.setInformativeText_(description)
        cls = NSSecureTextField if hidden else NSTextField
        field = cls.alloc().initWithFrame_(NSMakeRect(0, 0, 260, 24))
        field.setStringValue_(default or '')
        alert.setAccessoryView_(field)
        ok, cancel = self._ok_cancel_titles()
        alert.addButtonWithTitle_(ok)
        alert.addButtonWithTitle_(cancel)
        alert.window().setInitialFirstResponder_(field)
        if alert.runModal() == NSAlertFirstButtonReturn:
            return str(field.stringValue())
        return None

    def select(self, title: str, description: str, buttons: List[str],
               default: Optional[int] = None) -> Optional[int]:
        _bring_to_front()
        alert = NSAlert.alloc().init()
        alert.setMessageText_(title)
        alert.setInformativeText_(description)
        for label in buttons:
            alert.addButtonWithTitle_(label)
        resp = alert.runModal()
        index = int(resp) - int(NSAlertFirstButtonReturn)
        if 0 <= index < len(buttons):
            return index
        return None

    def select_language(self, languages: dict[str, type],
                        current_code: str = 'en') -> Optional[str]:
        """Show a popup-button language selector.

        `languages` maps language codes to language classes (each having a
        `l_this` label). Returns the selected code, or None if cancelled.
        """
        _bring_to_front()
        alert = NSAlert.alloc().init()
        alert.setMessageText_(self.i18n.menu_select_language)
        alert.setInformativeText_(self.i18n.description_select_language)
        ok, cancel = self._ok_cancel_titles()
        alert.addButtonWithTitle_(ok)
        alert.addButtonWithTitle_(cancel)

        view = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, 300, 28))
        popup = NSPopUpButton.alloc().initWithFrame_(NSMakeRect(0, 2, 300, 26))
        codes = list(languages.keys())
        for code in codes:
            popup.addItemWithTitle_(languages[code]().l_this)
        if current_code in codes:
            popup.selectItemAtIndex_(codes.index(current_code))
        view.addSubview_(popup)
        alert.setAccessoryView_(view)

        if alert.runModal() == NSAlertFirstButtonReturn:
            return codes[popup.indexOfSelectedItem()]
        return None

    def alert(self, title: str, description: str) -> bool:
        _bring_to_front()
        alert = NSAlert.alloc().init()
        alert.setMessageText_(title)
        alert.setInformativeText_(description)
        ok, cancel = self._ok_cancel_titles()
        alert.addButtonWithTitle_(ok)
        alert.addButtonWithTitle_(cancel)
        return alert.runModal() == NSAlertFirstButtonReturn

    def info(self, title: str, description: str) -> None:
        """Single-button informational alert (no Cancel)."""
        _bring_to_front()
        alert = NSAlert.alloc().init()
        alert.setMessageText_(title)
        alert.setInformativeText_(description)
        ok, _ = self._ok_cancel_titles()
        alert.addButtonWithTitle_(ok)
        alert.runModal()
