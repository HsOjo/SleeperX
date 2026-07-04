"""Sleep-related write operations (all unprivileged).

- sleep(): whole-machine sleep via AppleScript (no root needed).
- display_sleep(): `pmset displaysleepnow` (no root needed).
- set_idle_sleep_prevented(): hold/release an IOPMAssertion to block user-idle
  system sleep (replaces the old `pmset noidle` daemon).
- get_system_idle_sleep_timeout(): current idle-sleep timeout in seconds.
"""
from __future__ import annotations

import re
import subprocess
import time
from typing import Optional

import ctypes

from app.platform import iokit

_SLEEP_SCRIPT = 'tell application "System Events" to sleep'


class SleepController:
    def __init__(self, logger=None):
        self.log = logger
        self._assertion_id: Optional[int] = None
        self._idle_timeout: Optional[int] = None
        self._idle_timeout_at: float = 0.0
        self._idle_timeout_ttl: float = 60.0

    def sleep(self) -> None:
        try:
            subprocess.run(['/usr/bin/osascript', '-e', _SLEEP_SCRIPT], check=False)
        except OSError:
            if self.log:
                self.log.exception('osascript sleep failed')

    def display_sleep(self) -> None:
        try:
            subprocess.run(['/usr/bin/pmset', 'displaysleepnow'], check=False)
        except OSError:
            if self.log:
                self.log.exception('pmset displaysleepnow failed')

    def set_idle_sleep_prevented(self, prevented: bool) -> None:
        if prevented:
            if self._assertion_id is not None:
                return
            aid = iokit.IOPMAssertionID(0)
            assertion_type = iokit.cfstr(iokit.kIOPMAssertionTypePreventUserIdleSystemSleep)
            reason = iokit.cfstr('SleeperX: idle sleep disabled')
            try:
                kr = iokit.iokit.IOPMAssertionCreateWithName(
                    assertion_type, iokit.kIOPMAssertionLevelOn, reason, ctypes.byref(aid))
            finally:
                iokit.cf_release(assertion_type)
                iokit.cf_release(reason)
            if kr == 0:
                self._assertion_id = aid.value
            elif self.log:
                self.log.error('IOPMAssertionCreateWithName failed: 0x%x', kr & 0xffffffff)
        else:
            if self._assertion_id is None:
                return
            iokit.iokit.IOPMAssertionRelease(iokit.IOPMAssertionID(self._assertion_id))
            self._assertion_id = None
        # Assertion state changed; invalidate the idle-timeout cache.
        self._idle_timeout_at = 0.0

    def get_system_idle_sleep_timeout(self) -> Optional[int]:
        if self._assertion_id is not None:
            return None
        now = time.time()
        if self._idle_timeout is not None and now - self._idle_timeout_at < self._idle_timeout_ttl:
            return self._idle_timeout
        try:
            out = subprocess.check_output(['/usr/bin/pmset', '-g'], text=True)
        except (OSError, subprocess.CalledProcessError):
            return None
        m = re.search(r'^\s*sleep\s+(\d+)', out, re.MULTILINE)
        if not m:
            return None
        minutes = int(m.group(1))
        self._idle_timeout = minutes * 60 if minutes > 0 else None
        self._idle_timeout_at = now
        return self._idle_timeout
