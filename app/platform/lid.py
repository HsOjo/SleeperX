"""Lid (clamshell) state via IOKit — event-driven, no polling fallback.

The initial state is read from `IOPMrootDomain`'s `AppleClamshellState`
property (True == lid closed). Changes are delivered by an
`IOServiceAddInterestNotification` general-interest subscription on
IOPMrootDomain: on any interest message we re-read the clamshell property and
notify. The engine de-dups unchanged states.

M0 GATE: this must be validated on real hardware / Hackintosh — the user
requires the lid to be event-driven and explicitly rejects a polling fallback.
"""
from __future__ import annotations

import ctypes
import threading
from typing import Callable, Optional

from app.platform import iokit

_CLAMSHELL = 'AppleClamshellState'
_GENERAL_INTEREST = b'IOGeneralInterest'


class LidSensor:
    def __init__(self, logger=None):
        self.log = logger
        self._on_change: Optional[Callable[[Optional[bool]], None]] = None
        self._callback = None      # keep the ctypes closure alive
        self._notify_port = None
        self._service = 0
        self._notification = iokit.io_object_t(0)
        self._lock = threading.Lock()

    def get_lid_state(self) -> Optional[bool]:
        return iokit.read_root_domain_bool(_CLAMSHELL)

    def subscribe(self, on_change: Callable[[Optional[bool]], None]) -> None:
        self._on_change = on_change

        self._notify_port = iokit.iokit.IONotificationPortCreate(iokit.kIOMainPortDefault)
        if not self._notify_port:
            if self.log:
                self.log.error('IONotificationPortCreate failed; lid events unavailable')
            return
        source = iokit.iokit.IONotificationPortGetRunLoopSource(self._notify_port)
        iokit.add_source_to_main_loop(source)

        self._service = iokit.iokit.IOServiceGetMatchingService(
            iokit.kIOMainPortDefault, iokit.iokit.IOServiceMatching(b'IOPMrootDomain'))
        if not self._service:
            if self.log:
                self.log.error('IOPMrootDomain not found; lid events unavailable')
            return

        def _trampoline(_refcon, _service, _msg_type, _msg_arg):
            try:
                with self._lock:
                    cb = self._on_change
                if cb:
                    cb(self.get_lid_state())
            except Exception:
                if self.log:
                    self.log.exception('lid interest handler failed')

        self._callback = iokit.INTEREST_CALLBACK(_trampoline)
        kr = iokit.iokit.IOServiceAddInterestNotification(
            self._notify_port, self._service, _GENERAL_INTEREST,
            self._callback, None, ctypes.byref(self._notification))
        if kr != 0 and self.log:
            self.log.error('IOServiceAddInterestNotification failed: 0x%x', kr & 0xffffffff)

    def stop(self) -> None:
        with self._lock:
            self._on_change = None
        if self._notification.value:
            iokit.iokit.IOObjectRelease(self._notification)
            self._notification = iokit.io_object_t(0)
        if self._service:
            iokit.iokit.IOObjectRelease(self._service)
            self._service = 0
        if self._notify_port:
            source = iokit.iokit.IONotificationPortGetRunLoopSource(self._notify_port)
            if source:
                iokit.remove_source_from_main_loop(source)
            iokit.iokit.IONotificationPortDestroy(self._notify_port)
            self._notify_port = None
        self._callback = None
