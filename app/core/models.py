from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class BatteryStatus:
    """Snapshot of the power source, framework-agnostic."""
    percent: int
    # One of: 'discharging', 'not charging', 'charging', 'finishing charge', 'charged'.
    status: str
    # Estimated seconds remaining, or None while the system is still calculating.
    remaining: Optional[int]

    @property
    def is_discharging(self) -> bool:
        return self.status == 'discharging'


# Lid state is a bare bool across the codebase: True == closed (clamshell shut).
LidClosed = bool
