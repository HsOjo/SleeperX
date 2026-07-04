from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, fields
from typing import Callable, Optional

from app.res.const import Const


@dataclass
class Config:
    """Persistent user preferences."""

    language: str = ''
    first_run: bool = True

    low_battery_capacity_sleep: bool = True
    low_battery_capacity: int = 6
    low_time_remaining: int = 10

    disable_idle_sleep_in_charging: bool = False
    disable_lid_sleep_in_charging: bool = False

    _path = Const.config_path

    def load(self, detect_language: Optional[Callable[[], str]] = None) -> None:
        dirty = not os.path.exists(self._path)
        if os.path.exists(self._path):
            try:
                with open(self._path, 'r', encoding='utf-8') as io:
                    data = json.load(io)
            except (OSError, ValueError):
                data = {}
                dirty = True
            else:
                known = {f.name for f in fields(self)}
                for k, v in data.items():
                    if k in known:
                        coerced = self._coerce(k, v)
                        if coerced != v:
                            dirty = True
                        setattr(self, k, coerced)
        if not self.language and detect_language:
            self.language = detect_language()
            dirty = True
        # Persist defaults / resolved language only when something changed.
        if dirty:
            self.save()

    def _coerce(self, key: str, value):
        if key == 'language':
            return str(value) if isinstance(value, str) else ''
        if key in ('first_run', 'low_battery_capacity_sleep',
                   'disable_idle_sleep_in_charging', 'disable_lid_sleep_in_charging'):
            return bool(value)
        if key in ('low_battery_capacity', 'low_time_remaining'):
            try:
                return int(value)
            except (TypeError, ValueError):
                return 6 if key == 'low_battery_capacity' else 10
        return value

    def save(self) -> None:
        os.makedirs(os.path.dirname(self._path), exist_ok=True)
        with open(self._path, 'w', encoding='utf-8') as io:
            json.dump(asdict(self), io, indent=2, ensure_ascii=False)

    def clear(self) -> None:
        if os.path.exists(self._path):
            os.unlink(self._path)
