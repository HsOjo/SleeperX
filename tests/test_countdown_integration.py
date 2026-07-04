"""End-to-end functional test for the paused countdown menu-title behavior.

When the status-bar menu is open, the "取消于" submenu title must stay fixed at
the remaining time captured at menu-open time; live tick updates are paused to
avoid hover-rendering glitches. After the menu closes, the timer resumes and the
title catches up to the current remaining time.

NOTE: This test requires an active AppKit/NSRunLoop and is intended to be run
manually as a standalone script. It is skipped under pytest.
"""
from __future__ import annotations

import sys
from typing import Callable, Optional

import pytest
import objc
from AppKit import (NSApplication, NSStatusBar,
                    NSVariableStatusItemLength,
                    NSApplicationActivationPolicyAccessory)
from Foundation import NSTimer, NSRunLoop, NSRunLoopCommonModes, NSObject

from app.ui.app_delegate import AppDelegate
from app.ui.controller import Controller
from app.ui.statusbar import _MenuDelegate
from app.core.engine import Engine
from app.core.models import BatteryStatus

pytestmark = pytest.mark.skip(reason='Manual test: requires active AppKit/NSRunLoop. Run as `python tests/test_countdown_integration.py`.')


class _StubPowerSource:
    def get_battery_status(self) -> Optional[BatteryStatus]:
        return None
    def subscribe(self, on_change: Callable[[], None]) -> None:
        pass
    def stop(self) -> None:
        pass


class _StubLidSensor:
    def get_lid_state(self) -> Optional[bool]:
        return None
    def subscribe(self, on_change: Callable[[Optional[bool]], None]) -> None:
        pass
    def stop(self) -> None:
        pass


class _StubIdleSensor:
    def get_idle_seconds(self) -> float:
        return 0.0


class _StubSleepController:
    def sleep(self) -> None:
        pass
    def display_sleep(self) -> None:
        pass
    def set_idle_sleep_prevented(self, prevented: bool) -> None:
        pass
    def get_system_idle_sleep_timeout(self) -> Optional[int]:
        return None


class _StubSleepWatcher:
    def subscribe(self, on_will_sleep: Callable[[], None],
                  on_did_wake: Callable[[], None]) -> None:
        pass
    def stop(self) -> None:
        pass


class _StubPrivilegedOps:
    def is_installed(self) -> bool:
        return False
    def install(self) -> bool:
        return False
    def uninstall(self) -> bool:
        return False
    def helper_version(self) -> Optional[str]:
        return None
    def set_disable_sleep(self, disabled: bool) -> bool:
        return True
    def set_hibernate_mode(self, mode: int) -> bool:
        return True


class _StubLoginItem:
    def is_enabled(self) -> bool:
        return False
    def enable(self) -> bool:
        return True
    def disable(self) -> bool:
        return True


class _StubSystemInfo:
    def version_string(self) -> str:
        return '14.0'
    def hibernate_mode(self) -> Optional[int]:
        return 3


class _StubNotifier:
    def notify(self, title: str, subtitle: str = '', message: str = '') -> None:
        pass


class _StubDialogs:
    def input(self, title: str, description: str, default: str = '',
              hidden: bool = False) -> Optional[str]:
        return None
    def select(self, title: str, description: str, buttons: list[str],
               default: Optional[int] = None) -> Optional[int]:
        return None
    def alert(self, title: str, description: str) -> bool:
        return False


class _Harness(NSObject):
    def initWithController_(self, controller):
        self = objc.super(_Harness, self).init()
        self.controller = controller
        return self

    def engineTick_(self, timer):
        self.controller.tick()

    def close_(self, timer):
        print('[test] closing menu', flush=True)
        if self.controller.statusbar:
            menu = self.controller.statusbar._status_item.menu()
            if menu is not None:
                menu.cancelTracking()


class _RecordingMenuDelegate(_MenuDelegate):
    """Records the cancel_idle title whenever the menu opens or closes."""

    def initWithStatusBar_(self, statusbar):
        self = objc.super(_RecordingMenuDelegate, self).initWithStatusBar_(statusbar)
        self.titles: list[str] = []
        return self

    def _record(self):
        item = self.statusbar.items.get('cancel_idle')
        if item is not None:
            self.titles.append(str(item.title()))

    def menuWillOpen_(self, menu):
        self._record()
        objc.super(_RecordingMenuDelegate, self).menuWillOpen_(menu)

    def menuDidClose_(self, menu):
        self._record()
        objc.super(_RecordingMenuDelegate, self).menuDidClose_(menu)


def test_countdown_title_pauses_while_menu_open():
    app = NSApplication.sharedApplication()
    app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)

    controller = Controller()
    controller.engine = Engine(
        controller.config,
        _StubPowerSource(), _StubLidSensor(), _StubIdleSensor(),
        _StubSleepController(), _StubSleepWatcher(), _StubPrivilegedOps(),
        controller, controller.log,
    )

    delegate = AppDelegate.alloc().initWithController_(controller)
    controller.attach_statusbar(delegate)

    # Replace the menu delegate with one that records titles at open/close.
    recorder = _RecordingMenuDelegate.alloc().initWithStatusBar_(controller.statusbar)
    controller.statusbar._status_item.menu().setDelegate_(recorder)
    controller.statusbar._menu_delegate = recorder

    # Trigger a 10-second idle-sleep cancel countdown.
    print('[test] starting 10s countdown', flush=True)
    controller.on_menu('cancel_idle:10')

    harness = _Harness.alloc().initWithController_(controller)

    tick_timer = NSTimer.timerWithTimeInterval_target_selector_userInfo_repeats_(
        1.0, harness, 'engineTick:', None, True)
    NSRunLoop.currentRunLoop().addTimer_forMode_(tick_timer, NSRunLoopCommonModes)

    close_timer = NSTimer.timerWithTimeInterval_target_selector_userInfo_repeats_(
        1.5, harness, 'close:', None, False)
    NSRunLoop.currentRunLoop().addTimer_forMode_(close_timer, NSRunLoopCommonModes)

    menu = controller.statusbar._status_item.menu()
    print('[test] opening menu', flush=True)
    controller.statusbar._status_item.popUpStatusItemMenu_(menu)
    print('[test] menu closed', flush=True)

    # Capture the title after the menu has closed and the engine has caught up.
    after_title = str(controller.statusbar.items['cancel_idle'].title())
    print(f'[test] title after close: {after_title}', flush=True)

    NSStatusBar.systemStatusBar().removeStatusItem_(
        controller.statusbar._status_item)

    print('[test] recorded titles while open:', recorder.titles, flush=True)
    assert len(recorder.titles) >= 2, (
        f'expected open and close recordings, got {recorder.titles}')
    # While the menu was open the title must remain exactly at the snapshot value.
    assert all(t == recorder.titles[0] for t in recorder.titles), (
        f'countdown title changed while menu was open: {recorder.titles}')
    # After the menu closes the title must catch up to the current remaining time.
    assert after_title != recorder.titles[0], (
        f'title did not update after menu closed: {recorder.titles[0]} -> {after_title}')
    print('[test] PASS', flush=True)


if __name__ == '__main__':
    test_countdown_title_pauses_while_menu_open()
    sys.exit(0)
