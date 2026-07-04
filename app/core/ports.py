from __future__ import annotations

from typing import Callable, List, Optional, Protocol

from app.core.models import BatteryStatus


class PowerSource(Protocol):
    """IOKit power-source reader + change notifications."""

    def get_battery_status(self) -> Optional[BatteryStatus]: ...

    def subscribe(self, on_change: Callable[[], None]) -> None: ...

    def stop(self) -> None: ...


class LidSensor(Protocol):
    """Clamshell state reader + IOKit interest notification (event-driven)."""

    def get_lid_state(self) -> Optional[bool]: ...

    def subscribe(self, on_change: Callable[[Optional[bool]], None]) -> None: ...

    def stop(self) -> None: ...


class IdleSensor(Protocol):
    def get_idle_seconds(self) -> float: ...


class SleepController(Protocol):
    def sleep(self) -> None:
        """Put the whole machine to sleep (no root required)."""
        ...

    def display_sleep(self) -> None:
        """Turn the display off (no root required)."""
        ...

    def set_idle_sleep_prevented(self, prevented: bool) -> None:
        """Hold/release an IOPMAssertion preventing user-idle system sleep."""
        ...

    def get_system_idle_sleep_timeout(self) -> Optional[int]:
        """System idle-sleep timeout in seconds, or None if sleep is prevented."""
        ...


class SleepWatcher(Protocol):
    def subscribe(self, on_will_sleep: Callable[[], None],
                  on_did_wake: Callable[[], None]) -> None: ...

    def stop(self) -> None: ...


class PrivilegedOps(Protocol):
    """Root-only pmset writes, brokered through the LaunchDaemon helper."""

    def is_installed(self) -> bool: ...

    def install(self) -> bool: ...

    def uninstall(self) -> bool: ...

    def helper_version(self) -> Optional[str]: ...

    def set_disable_sleep(self, disabled: bool) -> bool: ...

    def set_hibernate_mode(self, mode: int) -> bool: ...


class LoginItem(Protocol):
    def is_enabled(self) -> bool: ...

    def enable(self) -> bool: ...

    def disable(self) -> bool: ...


class SystemInfo(Protocol):
    def version_string(self) -> str: ...

    def hibernate_mode(self) -> Optional[int]: ...


class Notifier(Protocol):
    def notify(self, title: str, subtitle: str = '', message: str = '') -> None: ...


class Dialogs(Protocol):
    def input(self, title: str, description: str, default: str = '',
              hidden: bool = False) -> Optional[str]: ...

    def select(self, title: str, description: str, buttons: List[str],
               default: Optional[int] = None) -> Optional[int]: ...

    def alert(self, title: str, description: str) -> bool: ...


class UI(Protocol):
    """The menubar surface the engine drives (state reflection only)."""

    def set_battery_view(self, percent: int, status: str,
                         remaining: Optional[int]) -> None: ...

    def set_idle_sleep_disabled(self, disabled: bool) -> None: ...

    def set_lid_sleep_disabled(self, disabled: bool) -> None: ...

    def set_idle_cancel_countdown(self, seconds: Optional[float]) -> None: ...

    def set_lid_cancel_countdown(self, seconds: Optional[float]) -> None: ...
