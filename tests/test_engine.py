"""Unit tests for the framework-agnostic Engine using in-memory fakes.

Run: python3 -m pytest tests/test_engine.py
These tests avoid PyObjC entirely — that's the payoff of the ports abstraction.
"""
from __future__ import annotations

import threading

from app.core.engine import Engine
from app.core.models import BatteryStatus
from app.core.config import Config


class FakeClock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now

    def advance(self, dt):
        self.now += dt


class FakePower:
    def __init__(self, status=None):
        self.status = status
        self.on_change = None
        self.stopped = False

    def get_battery_status(self):
        return self.status

    def subscribe(self, on_change):
        self.on_change = on_change

    def stop(self):
        self.stopped = True

    def push(self, status):
        self.status = status
        if self.on_change:
            self.on_change()


class FakeLid:
    def __init__(self, state=False):
        self.state = state
        self.on_change = None

    def get_lid_state(self):
        return self.state

    def subscribe(self, on_change):
        self.on_change = on_change

    def stop(self):
        pass

    def push(self, state):
        self.state = state
        if self.on_change:
            self.on_change(state)


class FakeIdle:
    def __init__(self, seconds=0.0):
        self.seconds = seconds

    def get_idle_seconds(self):
        return self.seconds


class FakeSleepController:
    def __init__(self, timeout=1200, display_event=None):
        self.slept = 0
        self.display_slept = 0
        self.idle_prevented = False
        self.timeout = timeout
        self.display_event = display_event

    def sleep(self):
        self.slept += 1

    def display_sleep(self):
        self.display_slept += 1
        if self.display_event is not None:
            self.display_event.set()

    def set_idle_sleep_prevented(self, prevented):
        self.idle_prevented = prevented

    def get_system_idle_sleep_timeout(self):
        return self.timeout


class FakeSleepWatcher:
    def subscribe(self, on_will_sleep, on_did_wake):
        self.on_will_sleep = on_will_sleep
        self.on_did_wake = on_did_wake

    def stop(self):
        pass


class FakePrivileged:
    def __init__(self, installed=True):
        self.installed = installed
        self.disable_sleep = False
        self.hibernate = 3
        self.set_calls = []

    def is_installed(self):
        return self.installed

    def install(self):
        self.installed = True
        return True

    def uninstall(self):
        self.installed = False
        return True

    def helper_version(self):
        return '2.0.0'

    def set_disable_sleep(self, disabled):
        self.disable_sleep = disabled
        self.set_calls.append(disabled)
        return True

    def set_hibernate_mode(self, mode):
        self.hibernate = mode
        return True


class FakeUI:
    def __init__(self):
        self.battery = None
        self.idle_disabled = None
        self.lid_disabled = None
        self.idle_countdown = 'unset'
        self.lid_countdown = 'unset'

    def set_battery_view(self, percent, status, remaining):
        self.battery = (percent, status, remaining)

    def set_idle_sleep_disabled(self, disabled):
        self.idle_disabled = disabled

    def set_lid_sleep_disabled(self, disabled):
        self.lid_disabled = disabled

    def set_idle_cancel_countdown(self, seconds):
        self.idle_countdown = seconds

    def set_lid_cancel_countdown(self, seconds):
        self.lid_countdown = seconds


class NullLogger:
    def info(self, *a, **k):
        pass

    def exception(self, *a, **k):
        pass


def make_engine(config=None, power_status=None, lid_state=False,
                installed=True, clock=None):
    clock = clock or FakeClock()
    power = FakePower(power_status)
    lid = FakeLid(lid_state)
    idle = FakeIdle()
    sleep_ctl = FakeSleepController()
    watcher = FakeSleepWatcher()
    priv = FakePrivileged(installed=installed)
    ui = FakeUI()
    engine = Engine(
        config or Config(), power, lid, idle, sleep_ctl, watcher, priv, ui,
        NullLogger(), clock=clock)
    engine._fakes = dict(power=power, lid=lid, idle=idle, sleep_ctl=sleep_ctl,
                         watcher=watcher, priv=priv, ui=ui, clock=clock)
    return engine


def test_low_battery_capacity_triggers_sleep():
    cfg = Config(low_battery_capacity_sleep=True, low_battery_capacity=6)
    e = make_engine(cfg, BatteryStatus(5, 'discharging', None), installed=False)
    e.start()
    assert e._fakes['sleep_ctl'].slept == 1


def test_low_time_remaining_triggers_sleep():
    cfg = Config(low_battery_capacity_sleep=True, low_battery_capacity=6,
                 low_time_remaining=10)
    e = make_engine(cfg, BatteryStatus(50, 'discharging', 9 * 60), installed=False)
    e.start()
    assert e._fakes['sleep_ctl'].slept == 1


def test_healthy_battery_no_sleep():
    cfg = Config(low_battery_capacity_sleep=True, low_battery_capacity=6)
    e = make_engine(cfg, BatteryStatus(80, 'discharging', 120 * 60), installed=False)
    e.start()
    assert e._fakes['sleep_ctl'].slept == 0


def test_charging_disables_idle_and_lid_when_configured():
    cfg = Config(disable_idle_sleep_in_charging=True,
                 disable_lid_sleep_in_charging=True,
                 low_battery_capacity_sleep=False)
    e = make_engine(cfg, BatteryStatus(90, 'discharging', 100 * 60))
    e.start()
    e._fakes['power'].push(BatteryStatus(90, 'charging', None))
    assert e.idle_sleep_disabled is True
    assert e.lid_sleep_disabled is True


def test_discharge_restores_idle_and_lid():
    cfg = Config(disable_idle_sleep_in_charging=True,
                 disable_lid_sleep_in_charging=True,
                 low_battery_capacity_sleep=False)
    e = make_engine(cfg, BatteryStatus(90, 'charging', None))
    e.start()
    assert e.idle_sleep_disabled is True
    e._fakes['power'].push(BatteryStatus(90, 'discharging', 100 * 60))
    assert e.idle_sleep_disabled is False
    assert e.lid_sleep_disabled is False


def test_lid_close_display_sleeps_when_lid_sleep_disabled():
    cfg = Config(low_battery_capacity_sleep=False)
    e = make_engine(cfg, BatteryStatus(90, 'discharging', 100 * 60), lid_state=False,
                    installed=True)
    e.start()
    e.set_lid_sleep(False)  # disables lid sleep
    event = threading.Event()
    e._fakes['sleep_ctl'].display_event = event
    e._fakes['lid'].push(True)
    assert event.wait(timeout=2), 'display_sleep was not called'
    assert e._fakes['sleep_ctl'].display_slept == 1


def test_lid_close_no_display_sleep_when_lid_sleep_enabled():
    cfg = Config(low_battery_capacity_sleep=False)
    e = make_engine(cfg, BatteryStatus(90, 'discharging', 100 * 60), lid_state=False,
                    installed=True)
    e.start()
    # lid sleep stays enabled (default)
    event = threading.Event()
    e._fakes['sleep_ctl'].display_event = event
    e._fakes['lid'].push(True)
    assert not event.wait(timeout=0.2), 'display_sleep should not have been called'
    assert e._fakes['sleep_ctl'].display_slept == 0


def test_reconcile_clears_stale_disable_sleep_on_battery():
    cfg = Config(disable_lid_sleep_in_charging=True, low_battery_capacity_sleep=False)
    e = make_engine(cfg, BatteryStatus(90, 'discharging', 100 * 60), installed=True)
    e.start()
    # discharging + not manually disabled => must force disablesleep 0
    assert e._fakes['priv'].disable_sleep is False
    assert False in e._fakes['priv'].set_calls


def test_idle_compensation_sleeps_past_timeout():
    cfg = Config(low_battery_capacity_sleep=False)
    e = make_engine(cfg, BatteryStatus(90, 'discharging', 100 * 60), installed=True)
    e.start()
    e.lid_sleep_disabled = True
    e._fakes['idle'].seconds = 2000
    e._fakes['sleep_ctl'].timeout = 1200
    e.tick()
    assert e._fakes['sleep_ctl'].slept >= 1


def test_set_sleep_mode_whitelist():
    e = make_engine(Config(), BatteryStatus(90, 'charged', None))
    assert e.set_sleep_mode(3) is True
    assert e._fakes['priv'].hibernate == 3
    assert e.set_sleep_mode(7) is False


def test_set_lid_sleep_available_false_disables():
    e = make_engine(Config(), BatteryStatus(90, 'discharging', 100 * 60), installed=True)
    e.start()
    assert e.set_lid_sleep(False) is True
    assert e.lid_sleep_disabled is True
    assert e._fakes['priv'].disable_sleep is True
    assert e._fakes['ui'].lid_disabled is True


def test_set_lid_sleep_available_true_enables():
    e = make_engine(Config(), BatteryStatus(90, 'discharging', 100 * 60), installed=True)
    e.start()
    assert e.set_lid_sleep(False) is True
    assert e.set_lid_sleep(True) is True
    assert e.lid_sleep_disabled is False
    assert e._fakes['priv'].disable_sleep is False
    assert e._fakes['ui'].lid_disabled is False


def _wait_restore(engine, attr, timeout=5.0):
    """Wait for sleep()'s restore thread to re-disable the given block."""
    import time
    deadline = time.time() + timeout
    while time.time() < deadline:
        if getattr(engine, attr):
            return True
        time.sleep(0.05)
    return False


def test_sleep_preserves_idle_countdown():
    e = make_engine(Config(low_battery_capacity_sleep=False),
                    BatteryStatus(90, 'discharging', 100 * 60))
    e.start()
    e.schedule_cancel_idle(300)
    assert e.cancel_disable_idle_sleep_time is not None
    assert e.idle_sleep_disabled is True

    e.sleep()
    # Temporarily lifted: block released and timer cleared.
    assert e.idle_sleep_disabled is False
    assert e.cancel_disable_idle_sleep_time is None

    assert _wait_restore(e, 'idle_sleep_disabled')
    # Restore must bring back both the block and the countdown timer.
    assert e._fakes['sleep_ctl'].idle_prevented is True
    assert e.cancel_disable_idle_sleep_time is not None
    assert e._fakes['ui'].idle_countdown is not None

    # The timer must still fire after restore.
    e._fakes['clock'].advance(400)
    e.tick()
    assert e.cancel_disable_idle_sleep_time is None
    assert e.idle_sleep_disabled is False
    assert e._fakes['sleep_ctl'].idle_prevented is False


def test_sleep_preserves_lid_countdown():
    e = make_engine(Config(low_battery_capacity_sleep=False),
                    BatteryStatus(90, 'discharging', 100 * 60), installed=True)
    e.start()
    e.schedule_cancel_lid(300)
    assert e.cancel_disable_lid_sleep_time is not None
    assert e.lid_sleep_disabled is True

    e.sleep()
    assert e.lid_sleep_disabled is False
    assert e.cancel_disable_lid_sleep_time is None

    assert _wait_restore(e, 'lid_sleep_disabled')
    assert e._fakes['priv'].disable_sleep is True
    assert e.cancel_disable_lid_sleep_time is not None
    assert e._fakes['ui'].lid_countdown is not None

    e._fakes['clock'].advance(400)
    e.tick()
    assert e.cancel_disable_lid_sleep_time is None
    assert e.lid_sleep_disabled is False
    assert e._fakes['priv'].disable_sleep is False


def test_idle_compensation_preserves_lid_countdown():
    """Lid countdown must survive the idle-compensation auto-sleep."""
    e = make_engine(Config(low_battery_capacity_sleep=False),
                    BatteryStatus(90, 'discharging', 100 * 60), installed=True)
    e.start()
    e.schedule_cancel_lid(300)
    e._fakes['idle'].seconds = 2000
    e._fakes['sleep_ctl'].timeout = 1200

    e.tick()  # idle past timeout -> auto sleep() -> restore thread
    assert e._fakes['sleep_ctl'].slept >= 1

    assert _wait_restore(e, 'lid_sleep_disabled')
    assert e.cancel_disable_lid_sleep_time is not None

    # After the original timer expires, lid sleep must actually be re-enabled.
    e._fakes['clock'].advance(400)
    e.tick()
    assert e.cancel_disable_lid_sleep_time is None
    assert e.lid_sleep_disabled is False
    assert e._fakes['priv'].disable_sleep is False


def test_set_lid_sleep_keeps_countdown_ui_when_disabling():
    """Enabling the lid block must not wipe an active countdown display."""
    e = make_engine(Config(low_battery_capacity_sleep=False),
                    BatteryStatus(90, 'discharging', 100 * 60), installed=True)
    e.start()
    e.schedule_cancel_lid(300)
    assert e._fakes['ui'].lid_countdown == 300

    # Re-disabling (e.g. charge-status change) must leave the countdown intact.
    e.set_lid_sleep(False)
    assert e._fakes['ui'].lid_countdown == 300
