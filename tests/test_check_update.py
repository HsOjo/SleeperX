"""Unit tests for the Check Update feedback path.

Notifications are delivered via AppleScript `display notification` because
`NSUserNotification` is unreliable for unsigned menu-bar apps. The path also
updates the menu item text while checking and shows a guaranteed NSAlert dialog
with the result on the main thread.
"""
from __future__ import annotations

import threading
from unittest.mock import patch, MagicMock, call

from app.core.updater import Release
from app.ui.controller import Controller


def _make_controller():
    controller = Controller()
    controller.notifier = MagicMock()
    controller.dialogs = MagicMock()
    controller.statusbar = MagicMock()
    return controller


def test_check_update_shows_checking_in_menu():
    controller = _make_controller()
    release = Release(
        name='v2.0.0',
        tag_name='v2.0.0',
        published_at='2026-01-01 00:00:00',
        html_url='https://example.com',
        body='',
    )
    started = []
    original_start = threading.Thread.start
    def patched_start(self):
        started.append(self)
        return original_start(self)

    with patch('app.ui.controller.updater.check_update') as mock_check, \
         patch('app.ui.controller.NSOperationQueue') as mock_queue, \
         patch('app.ui.controller.threading.Thread.start', patched_start):
        mock_queue.mainQueue.return_value.addOperationWithBlock_ = lambda block: block()
        mock_check.return_value = (release, False)
        controller._check_update()
        calls = controller.statusbar.set_title.call_args_list
        assert calls[0] == call('check_update', controller.lang.noti_checking_update)
        # Wait for the background thread to finish.
        for t in started:
            t.join(timeout=2)
        controller.dialogs.info.assert_called_once()
        text = controller.dialogs.info.call_args[0][1]
        assert controller.lang.noti_update_none in text
        assert controller.lang.noti_update_star in text
        controller.notifier.notify.assert_not_called()


def test_check_update_no_update_shows_latest_dialog():
    controller = _make_controller()
    release = Release(
        name='v1.0.0',
        tag_name='v1.0.0',
        published_at='2026-01-01 00:00:00',
        html_url='https://example.com',
        body='',
    )
    controller._show_update_result(release, False)
    controller.statusbar.set_title.assert_called_once_with(
        'check_update', controller.lang.menu_check_update)
    controller.notifier.notify.assert_not_called()
    controller.dialogs.info.assert_called_once()
    title, text = controller.dialogs.info.call_args[0]
    assert title == controller.lang.menu_check_update
    assert controller.lang.noti_update_none in text
    assert controller.lang.noti_update_star in text


def test_check_update_new_version_shows_update_dialog():
    controller = _make_controller()
    release = Release(
        name='v99.0.0',
        tag_name='v99.0.0',
        published_at='2026-01-01 00:00:00',
        html_url='https://example.com',
        body='release notes',
    )
    controller._show_update_result(release, True)
    controller.statusbar.set_title.assert_called_once_with(
        'check_update', controller.lang.menu_check_update)
    controller.notifier.notify.assert_called_once_with(
        controller.lang.noti_update_version('v99.0.0'),
        controller.lang.noti_update_time(release.published_at),
        release.body)
    controller.dialogs.info.assert_called_once()
    title, text = controller.dialogs.info.call_args[0]
    assert title == controller.lang.noti_update_version('v99.0.0')
    assert controller.lang.noti_update_time(release.published_at) in text
    assert controller.lang.noti_update_star in text


def test_check_update_new_version_opens_release_page():
    controller = _make_controller()
    release = Release(
        name='v99.0.0',
        tag_name='v99.0.0',
        published_at='2026-01-01 00:00:00',
        html_url='https://example.com/release',
        body='',
    )
    with patch('app.ui.controller.NSWorkspace') as mock_ws:
        controller._show_update_result(release, True)
        mock_ws.sharedWorkspace.return_value.openURL_.assert_called_once()
        url_arg = mock_ws.sharedWorkspace.return_value.openURL_.call_args[0][0]
        assert str(url_arg) == release.html_url


def test_check_update_network_error_shows_error_dialog():
    controller = _make_controller()
    controller._show_update_result(None, False)
    controller.statusbar.set_title.assert_called_once_with(
        'check_update', controller.lang.menu_check_update)
    controller.notifier.notify.assert_not_called()
    controller.dialogs.info.assert_called_once_with(
        controller.lang.menu_check_update, controller.lang.noti_network_error)
