"""Regression tests for the AppKit status-bar wrapper."""
from __future__ import annotations

import logging

import objc
import pytest
from AppKit import (NSApplication, NSStatusBar,
                    NSApplicationActivationPolicyAccessory,
                    NSControlStateValueOn, NSControlStateValueOff)
from Foundation import NSObject

from app.ui.statusbar import StatusBar


@pytest.fixture(autouse=True)
def _setup_app():
    app = NSApplication.sharedApplication()
    app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)


class _DummyTarget(NSObject):
    def menuAction_(self, sender):
        pass


def _simple_model():
    return [
        {'key': 'info', 'kind': 'info', 'title': 'Info'},
        {'key': 'toggle', 'kind': 'checkbox', 'title': 'Toggle', 'checked': False},
        {'key': 'action', 'kind': 'action', 'title': 'Action'},
    ]


def test_statusbar_set_title():
    target = _DummyTarget.alloc().init()
    bar = StatusBar(target)
    bar.build(_simple_model())
    bar.set_title('info', 'Updated')
    assert str(bar.items['info'].title()) == 'Updated'


def test_statusbar_set_checked():
    target = _DummyTarget.alloc().init()
    bar = StatusBar(target)
    bar.build(_simple_model())
    bar.set_checked('toggle', True)
    assert bar.items['toggle'].state() == NSControlStateValueOn
    bar.set_checked('toggle', False)
    assert bar.items['toggle'].state() == NSControlStateValueOff


def test_statusbar_set_enabled():
    target = _DummyTarget.alloc().init()
    bar = StatusBar(target)
    bar.build(_simple_model())
    bar.set_enabled('action', False)
    assert bar.items['action'].isEnabled() is False
    bar.set_enabled('action', True)
    assert bar.items['action'].isEnabled() is True


def test_statusbar_missing_key_is_noop():
    target = _DummyTarget.alloc().init()
    bar = StatusBar(target)
    bar.build(_simple_model())
    # Should not raise.
    bar.set_title('nonexistent', 'X')
    bar.set_checked('nonexistent', True)
    bar.set_enabled('nonexistent', False)


def test_controller_on_main_swallows_exception(caplog):
    from app.ui.controller import Controller
    caplog.set_level(logging.ERROR)
    controller = Controller()
    # On the test runner thread (main thread) this executes synchronously.
    controller._on_main(lambda: (_ for _ in ()).throw(ZeroDivisionError('boom')))
    assert 'UI update failed' in caplog.text
    assert 'ZeroDivisionError' in caplog.text
