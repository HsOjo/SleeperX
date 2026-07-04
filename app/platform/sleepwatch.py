"""NSWorkspace sleep/wake notifications via NSNotificationCenter."""
from __future__ import annotations

from typing import Callable, Optional

from AppKit import NSWorkspace, NSWorkspaceWillSleepNotification, NSWorkspaceDidWakeNotification


class SleepWatcher:
    def __init__(self, logger=None):
        self.log = logger
        self._will_sleep: Optional[Callable[[], None]] = None
        self._did_wake: Optional[Callable[[], None]] = None
        self._observers: list = []

    def subscribe(self, on_will_sleep: Callable[[], None],
                  on_did_wake: Callable[[], None]) -> None:
        self._will_sleep = on_will_sleep
        self._did_wake = on_did_wake
        nc = NSWorkspace.sharedWorkspace().notificationCenter()

        def _will_sleep_note(_note):
            try:
                if self._will_sleep:
                    self._will_sleep()
            except Exception:
                if self.log:
                    self.log.exception('willSleep notification handler failed')

        def _did_wake_note(_note):
            try:
                if self._did_wake:
                    self._did_wake()
            except Exception:
                if self.log:
                    self.log.exception('didWake notification handler failed')

        self._observers = [
            nc.addObserverForName_object_queue_usingBlock_(
                NSWorkspaceWillSleepNotification, None, None, _will_sleep_note),
            nc.addObserverForName_object_queue_usingBlock_(
                NSWorkspaceDidWakeNotification, None, None, _did_wake_note),
        ]

    def stop(self) -> None:
        nc = NSWorkspace.sharedWorkspace().notificationCenter()
        for observer in self._observers:
            nc.removeObserver_(observer)
        self._observers.clear()
