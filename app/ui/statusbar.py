"""NSStatusItem + NSMenu construction from the declarative menu model.

Thin wrapper: builds the tree, indexes actionable items by key, and wires every
actionable item to a single target/action (the delegate's `menuAction:`), using
representedObject to carry the item key back to the handler.
"""
from __future__ import annotations

import objc
from typing import Dict, Optional, Callable

from AppKit import (NSObject, NSStatusBar, NSMenu, NSMenuItem, NSImage,
                    NSVariableStatusItemLength, NSControlStateValueOn,
                    NSControlStateValueOff)


class _MenuDelegate(NSObject):
    def initWithStatusBar_(self, statusbar):
        self = objc.super(_MenuDelegate, self).init()
        self.statusbar = statusbar
        return self

    def menuWillOpen_(self, menu):
        self.statusbar._menu_open = True

    def menuDidClose_(self, menu):
        self.statusbar._menu_open = False
        if self.statusbar._on_menu_close is not None:
            self.statusbar._on_menu_close()


class StatusBar:
    def __init__(self, target, action='menuAction:'):
        self.target = target
        self.action = action
        self.items: Dict[str, NSMenuItem] = {}
        self._status_item = NSStatusBar.systemStatusBar().statusItemWithLength_(
            NSVariableStatusItemLength)
        self._menu_open = False
        self._on_menu_close: Optional[Callable[[], None]] = None

    def set_icon(self, path: str, template: bool = True) -> None:
        image = NSImage.alloc().initWithContentsOfFile_(path)
        if image is not None:
            # Menu bar icons should be small (≈18pt) and template-based.
            image.setSize_((18, 18))
            image.setTemplate_(template)
            self._status_item.button().setImage_(image)

    def build(self, model: list) -> None:
        self.items.clear()
        menu = self._build_menu(model)
        self._status_item.setMenu_(menu)
        delegate = _MenuDelegate.alloc().initWithStatusBar_(self)
        menu.setDelegate_(delegate)
        self._menu_delegate = delegate

    @property
    def is_menu_open(self) -> bool:
        return self._menu_open

    def set_on_menu_close(self, callback: Callable[[], None]) -> None:
        self._on_menu_close = callback

    def _build_menu(self, nodes: list) -> NSMenu:
        menu = NSMenu.alloc().init()
        menu.setAutoenablesItems_(False)
        for node in nodes:
            kind = node['kind']
            if kind == 'separator':
                menu.addItem_(NSMenuItem.separatorItem())
                continue
            item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                node.get('title', ''), None, '')
            key = node.get('key')
            if kind == 'submenu':
                item.setSubmenu_(self._build_menu(node.get('children', [])))
            elif kind == 'info':
                item.setEnabled_(False)
            else:  # action / checkbox
                item.setTarget_(self.target)
                item.setAction_(self.action)
                item.setRepresentedObject_(key)
            if 'checked' in node:
                item.setState_(NSControlStateValueOn if node.get('checked')
                               else NSControlStateValueOff)
            if key:
                self.items[key] = item
            menu.addItem_(item)
        return menu

    # ----------------------------------------------------------- mutations
    def _redraw_item(self, item: NSMenuItem) -> None:
        menu = item.menu()
        if menu is None:
            return
        menu.itemChanged_(item)

    def set_title(self, key: str, title: str) -> None:
        item = self.items.get(key)
        if item is not None:
            item.setTitle_(title)
            self._redraw_item(item)

    def set_checked(self, key: str, checked: bool) -> None:
        item = self.items.get(key)
        if item is not None:
            item.setState_(NSControlStateValueOn if checked else NSControlStateValueOff)
            self._redraw_item(item)

    def set_enabled(self, key: str, enabled: bool) -> None:
        item = self.items.get(key)
        if item is not None:
            item.setEnabled_(enabled)
            self._redraw_item(item)
