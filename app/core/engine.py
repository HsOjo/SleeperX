from __future__ import annotations

import threading
import time
from typing import Callable, Optional

from app.core import ports
from app.core.models import BatteryStatus
from app.res.const import Const


class Engine:
    """Framework-agnostic power/sleep decision core (docs/PROJECT.md §4).

    All OS interaction goes through the `ports.*` protocols so the decision
    logic can be unit-tested against in-memory fakes.
    """

    def __init__(
        self,
        config,
        power: ports.PowerSource,
        lid: ports.LidSensor,
        idle: ports.IdleSensor,
        sleep_controller: ports.SleepController,
        sleep_watcher: ports.SleepWatcher,
        privileged: ports.PrivilegedOps,
        ui: ports.UI,
        logger,
        clock: Callable[[], float] = time.time,
    ):
        self.config = config
        self.power = power
        self.lid = lid
        self.idle = idle
        self.sleep_ctl = sleep_controller
        self.sleep_watch = sleep_watcher
        self.priv = privileged
        self.ui = ui
        self.log = logger
        self.clock = clock

        self.battery_status: Optional[BatteryStatus] = None
        self.lid_stat: Optional[bool] = None

        # Runtime-only toggles; never persisted (reset on restart).
        self._state_lock = threading.Lock()
        self.idle_sleep_disabled = False
        self.lid_sleep_disabled = False

        self.cancel_disable_idle_sleep_time: Optional[float] = None
        self.cancel_disable_lid_sleep_time: Optional[float] = None

        self.wake_time = 0.0

    # ----------------------------------------------------------------- lifecycle
    def start(self) -> None:
        self.power.subscribe(self._on_battery_change)
        self.lid.subscribe(self._on_lid_changed)
        self.sleep_watch.subscribe(self._on_will_sleep, self._on_did_wake)

        self.lid_stat = self.lid.get_lid_state()
        self._on_battery_change()
        self._reconcile_disable_sleep()

    def shutdown(self) -> None:
        try:
            self.sleep_ctl.set_idle_sleep_prevented(False)
            if self.lid_sleep_disabled and self.priv.is_installed():
                self.priv.set_disable_sleep(False)
        finally:
            self.power.stop()
            self.lid.stop()
            self.sleep_watch.stop()

    def _reconcile_disable_sleep(self) -> None:
        """On launch, clear a stale `disablesleep=1` left by a hard crash.

        The only legitimate reason to stay disabled at startup is being on AC
        power with the charging rule enabled; otherwise force it back to 0.
        """
        if not self.priv.is_installed():
            return
        status = self.battery_status.status if self.battery_status else None
        should_disable = (status in Const.charging_states) and self.config.disable_lid_sleep_in_charging
        with self._state_lock:
            lid_disabled = self.lid_sleep_disabled
        if not should_disable and not lid_disabled:
            if self.priv.set_disable_sleep(False):
                self.ui.set_lid_sleep_disabled(False)

    # -------------------------------------------------------------------- timer
    def tick(self) -> None:
        """Invoked once per second by the UI timer."""
        now = self.clock()

        with self._state_lock:
            idle_cancel = self.cancel_disable_idle_sleep_time
            lid_cancel = self.cancel_disable_lid_sleep_time
            lid_disabled = self.lid_sleep_disabled
            idle_disabled = self.idle_sleep_disabled

        # Cancel-timer handling must run outside the state lock: set_*_sleep
        # acquires the same non-recursive lock internally.
        if idle_cancel is not None:
            remain = idle_cancel - now
            if remain <= 0:
                self.set_idle_sleep(True)
            else:
                self.ui.set_idle_cancel_countdown(remain)

        if lid_cancel is not None:
            remain = lid_cancel - now
            if remain <= 0:
                self.set_lid_sleep(True)
            else:
                self.ui.set_lid_cancel_countdown(remain)

        # When lid sleep is disabled (`disablesleep=1`), the system also stops
        # honouring idle sleep. Compensate by manually sleeping once the machine
        # has been idle past the configured system idle-sleep timeout.
        if lid_disabled and not idle_disabled:
            timeout = self.sleep_ctl.get_system_idle_sleep_timeout()
            if timeout and timeout > 0:
                if self.idle.get_idle_seconds() >= timeout:
                    self.sleep()

    # ------------------------------------------------------------- event inputs
    def _on_battery_change(self) -> None:
        prev = self.battery_status
        self.battery_status = self.power.get_battery_status()
        bs = self.battery_status
        if bs is None:
            return

        self.ui.set_battery_view(bs.percent, bs.status, bs.remaining)

        if prev is None:
            self._on_charge_changed(bs.status, None)
        elif prev.status != bs.status:
            self._on_charge_changed(bs.status, prev.status)

        if self.config.low_battery_capacity_sleep and bs.is_discharging:
            low_capacity = bs.percent <= self.config.low_battery_capacity
            low_remaining = (bs.remaining is not None
                             and bs.remaining <= self.config.low_time_remaining * 60)
            if low_capacity or low_remaining:
                self.log.info(f'Low battery ({bs.percent}%, remaining={bs.remaining}), sleeping.')
                self.sleep()

    def _on_charge_changed(self, status: str, status_prev: Optional[str]) -> None:
        self.log.info(f'Charge status: "{status_prev}" -> "{status}"')
        if status == 'discharging':
            if self.config.disable_idle_sleep_in_charging:
                self.set_idle_sleep(True)
            if self.config.disable_lid_sleep_in_charging:
                if self.set_lid_sleep(True) and self.lid_stat:
                    self.sleep()
        elif status_prev in (None, 'discharging') and status in Const.charging_states:
            if self.config.disable_idle_sleep_in_charging:
                self.set_idle_sleep(False)
            if self.config.disable_lid_sleep_in_charging:
                self.set_lid_sleep(False)

    def _on_lid_changed(self, state: Optional[bool]) -> None:
        prev = self.lid_stat
        self.lid_stat = state
        if state is None or prev == state:
            return
        self.log.info(f'Lid status: "{prev}" -> "{state}"')
        if state and self.lid_sleep_disabled:
            self._display_sleep_on_lid_async()

    def _display_sleep_on_lid_async(self) -> None:
        """Turn off the display immediately when the lid is closed while lid sleep is disabled."""
        def worker():
            self.log.info('Lid closed while lid sleep disabled; turning display off.')
            self.sleep_ctl.display_sleep()

        threading.Thread(target=worker, daemon=True).start()

    def _on_will_sleep(self) -> None:
        self.log.info('System will sleep.')

    def _on_did_wake(self) -> None:
        now = self.clock()
        if now - self.wake_time < Const.check_sleep_time:
            return
        self.wake_time = now
        self.log.info('System did wake.')

    # ------------------------------------------------------------------ actions
    def action_sleep_now(self) -> None:
        self.sleep()

    def action_display_sleep(self) -> None:
        self.sleep_ctl.display_sleep()

    def sleep(self) -> bool:
        """Temporarily lift any sleep blocks, sleep, then restore after waking."""
        with self._state_lock:
            fix_idle = self.idle_sleep_disabled
            fix_lid = self.lid_sleep_disabled
            # set_*_sleep(True) clears the cancel-timers; save them so the
            # countdown survives this temporary lift and still fires later.
            saved_idle_cancel = self.cancel_disable_idle_sleep_time
            saved_lid_cancel = self.cancel_disable_lid_sleep_time

        if fix_idle:
            self.set_idle_sleep(True)
        if fix_lid:
            self.set_lid_sleep(True)

        self.sleep_ctl.sleep()

        if fix_idle or fix_lid:
            def restore():
                # During a real sleep this thread is frozen and resumes on wake;
                # on a cancelled/fake sleep it simply restores ~2s later.
                time.sleep(2)
                if fix_idle:
                    self.set_idle_sleep(False)
                if fix_lid:
                    self.set_lid_sleep(False)
                # The cancel-timers use wall-clock timestamps, which keep ticking
                # while the machine is asleep; restoring them as-is means a timer
                # that expired during sleep is picked up by the next tick().
                if saved_idle_cancel is not None:
                    with self._state_lock:
                        self.cancel_disable_idle_sleep_time = saved_idle_cancel
                    self.ui.set_idle_cancel_countdown(
                        max(saved_idle_cancel - self.clock(), 0))
                if saved_lid_cancel is not None:
                    with self._state_lock:
                        self.cancel_disable_lid_sleep_time = saved_lid_cancel
                    self.ui.set_lid_cancel_countdown(
                        max(saved_lid_cancel - self.clock(), 0))

            threading.Thread(target=restore, daemon=True).start()
        return True

    def set_idle_sleep(self, available: bool) -> None:
        disabled = not available
        with self._state_lock:
            self.idle_sleep_disabled = disabled
            if available:
                self.cancel_disable_idle_sleep_time = None
        self.sleep_ctl.set_idle_sleep_prevented(disabled)
        if available:
            self.ui.set_idle_cancel_countdown(None)
        self.ui.set_idle_sleep_disabled(disabled)

    def set_lid_sleep(self, available: bool) -> bool:
        disabled = not available
        self.log.info(f'set_lid_sleep({available}): requesting disablesleep={1 if disabled else 0}')
        success = self.priv.set_disable_sleep(disabled)
        self.log.info(f'set_lid_sleep({available}): helper success={success}')
        if success:
            with self._state_lock:
                self.lid_sleep_disabled = disabled
                if available:
                    self.cancel_disable_lid_sleep_time = None
            if available:
                self.ui.set_lid_cancel_countdown(None)
        with self._state_lock:
            current_disabled = self.lid_sleep_disabled
        self.ui.set_lid_sleep_disabled(current_disabled)
        return success

    def schedule_cancel_idle(self, after: float) -> None:
        with self._state_lock:
            self.cancel_disable_idle_sleep_time = self.clock() + after
        self.set_idle_sleep(False)
        self.ui.set_idle_cancel_countdown(after)

    def schedule_cancel_lid(self, after: float) -> None:
        with self._state_lock:
            self.cancel_disable_lid_sleep_time = self.clock() + after
        if self.set_lid_sleep(False):
            self.ui.set_lid_cancel_countdown(after)
        else:
            with self._state_lock:
                self.cancel_disable_lid_sleep_time = None

    def set_sleep_mode(self, mode: int) -> bool:
        if mode in (0, 3, 25):
            return self.priv.set_hibernate_mode(mode)
        return False
