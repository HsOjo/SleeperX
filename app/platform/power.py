"""Battery / power-source state via IOKit IOPowerSources.

Reading the power-source dictionaries is done through PyObjC
(`objc.loadBundleFunctions`), which bridges the CFDictionary results to native
dicts. Change notifications use the ctypes `IOPSNotificationCreateRunLoopSource`
binding (see iokit.py) because its C callback pointer is trivial and reliable.
"""
from __future__ import annotations

from typing import Callable, Optional

import objc
from Foundation import NSBundle

from app.core.models import BatteryStatus
from app.platform import iokit

# IOPSKeys.h
_STATE = 'Power Source State'
_CURRENT = 'Current Capacity'
_MAX = 'Max Capacity'
_IS_CHARGING = 'Is Charging'
_TIME_TO_EMPTY = 'Time to Empty'
_BATTERY_POWER = 'Battery Power'

_iops = {}
objc.loadBundleFunctions(
    NSBundle.bundleWithIdentifier_('com.apple.framework.IOKit'),
    _iops,
    [
        ('IOPSCopyPowerSourcesInfo', b'@'),
        ('IOPSCopyPowerSourcesList', b'@@'),
        ('IOPSGetPowerSourceDescription', b'@@@'),
    ],
)


def _derive_status(desc: dict) -> str:
    if desc.get(_STATE) == _BATTERY_POWER:
        return 'discharging'
    if desc.get(_IS_CHARGING):
        return 'charging'
    try:
        current = int(desc.get(_CURRENT, 0))
        maximum = int(desc.get(_MAX, 100)) or 100
    except (TypeError, ValueError):
        current, maximum = 0, 100
    return 'charged' if current >= maximum else 'not charging'


class PowerSource:
    def __init__(self, logger=None):
        self.log = logger
        self._on_change: Optional[Callable[[], None]] = None
        self._callback = None  # keep the ctypes closure alive
        self._source = None

    def get_battery_status(self) -> Optional[BatteryStatus]:
        info = _iops['IOPSCopyPowerSourcesInfo']()
        if info is None:
            return None
        sources = _iops['IOPSCopyPowerSourcesList'](info)
        if not sources:
            return None
        desc = _iops['IOPSGetPowerSourceDescription'](info, sources[0])
        if not desc:
            return None

        try:
            current = int(desc.get(_CURRENT, 0))
            maximum = int(desc.get(_MAX, 100)) or 100
        except (TypeError, ValueError):
            current, maximum = 0, 100
        percent = int(round(current / maximum * 100))

        status = _derive_status(desc)

        remaining = None
        if status == 'discharging':
            minutes = desc.get(_TIME_TO_EMPTY, -1)
            try:
                minutes = int(minutes)
            except (TypeError, ValueError):
                minutes = -1
            if minutes >= 0:
                remaining = minutes * 60

        return BatteryStatus(percent=percent, status=status, remaining=remaining)

    def subscribe(self, on_change: Callable[[], None]) -> None:
        if self._source is not None:
            self.stop()
        self._on_change = on_change

        def _trampoline(_context):
            try:
                if self._on_change:
                    self._on_change()
            except Exception:
                if self.log:
                    self.log.exception('power-source notification handler failed')

        self._callback = iokit.IOPS_CALLBACK(_trampoline)
        self._source = iokit.iokit.IOPSNotificationCreateRunLoopSource(self._callback, None)
        if self._source:
            iokit.add_source_to_main_loop(self._source)
        elif self.log:
            self.log.error('IOPSNotificationCreateRunLoopSource returned NULL')

    def stop(self) -> None:
        if self._source:
            iokit.remove_source_from_main_loop(self._source)
            iokit.cf_release(self._source)
            self._source = None
        self._callback = None
