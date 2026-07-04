"""Unit tests for Controller menu-action logic.

These tests avoid PyObjC by using stub engine/statusbar/dialogs objects and
running the background threads synchronously.
"""
from __future__ import annotations

import threading
from unittest.mock import MagicMock, patch

from app.ui.controller import Controller


def _make_controller():
    controller = Controller()
    controller.engine = MagicMock()
    controller.engine._state_lock = threading.Lock()
    controller.engine.cancel_disable_lid_sleep_time = None
    controller.engine.lid_sleep_disabled = False
    controller.engine.set_lid_sleep = MagicMock(return_value=True)
    controller.dialogs = MagicMock()
    controller.log = MagicMock()
    return controller


def _run_toggle_inline(controller):
    """Call _toggle_lid_sleep_async and execute its worker on the calling thread."""
    with patch('app.ui.controller.threading.Thread') as mock_thread:
        def run_inline(*a, **k):
            target = k.get('target')
            if target is not None:
                target()
            return MagicMock()
        mock_thread.side_effect = run_inline
        controller._toggle_lid_sleep_async()


def test_lid_toggle_enables_when_disabled():
    controller = _make_controller()
    controller.engine.lid_sleep_disabled = True
    _run_toggle_inline(controller)
    controller.engine.set_lid_sleep.assert_called_once_with(True)


def test_lid_toggle_disables_when_enabled():
    controller = _make_controller()
    controller.engine.lid_sleep_disabled = False
    _run_toggle_inline(controller)
    controller.engine.set_lid_sleep.assert_called_once_with(False)


def test_lid_toggle_enables_when_cancel_timer_active():
    """Clicking the main item while a 'cancel after X' timer is active should
    immediately re-enable lid sleep, not keep it disabled.
    """
    controller = _make_controller()
    controller.engine.lid_sleep_disabled = True
    controller.engine.cancel_disable_lid_sleep_time = 1234.0
    _run_toggle_inline(controller)
    controller.engine.set_lid_sleep.assert_called_once_with(True)


def test_lid_toggle_shows_alert_on_helper_failure():
    controller = _make_controller()
    controller.engine.lid_sleep_disabled = False
    controller.engine.set_lid_sleep.return_value = False
    _run_toggle_inline(controller)
    controller.engine.set_lid_sleep.assert_called_once_with(False)
    controller.dialogs.alert.assert_called_once()
