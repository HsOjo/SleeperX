"""Idle time via CoreGraphics.

`CGEventSourceSecondsSinceLastEventType` with the HID system state source
reports seconds since the last user input. Reading the idle value does NOT
require Accessibility permission (only event taps do).
"""
from __future__ import annotations

import Quartz

# kCGEventSourceStateHIDSystemState = 1; kCGAnyInputEventType = ~0 (0xFFFFFFFF)
_SOURCE_STATE = getattr(Quartz, 'kCGEventSourceStateHIDSystemState', 1)
_ANY_EVENT = getattr(Quartz, 'kCGAnyInputEventType', 0xFFFFFFFF)


class IdleSensor:
    def get_idle_seconds(self) -> float:
        try:
            return float(Quartz.CGEventSourceSecondsSinceLastEventType(_SOURCE_STATE, _ANY_EVENT))
        except Exception:
            return 0.0
