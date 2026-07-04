"""Regression test: SleepWatcher must subscribe without raising.

Previously `sleepwatch.py` referenced `NSWorkspace.willSleepNotification` and
`NSWorkspace.didWakeNotification`, which do not exist in PyObjC/AppKit. This
caused `controller.start()` to raise inside `applicationDidFinishLaunching_`,
which in turn prevented the 1-second NSTimer from being scheduled. As a
result the countdown UI never refreshed.
"""
from __future__ import annotations

from app.platform.sleepwatch import SleepWatcher


def test_subscribe_uses_valid_workspace_notifications():
    """Subscribe should not raise and should return two observer tokens."""
    watcher = SleepWatcher()
    watcher.subscribe(lambda: None, lambda: None)
    assert len(watcher._observers) == 2
    watcher.stop()
