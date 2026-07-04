"""Tests for the osascript-based notifier."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from app.platform.notifications import Notifier, _escape


def test_escape_quotes_and_backslashes():
    assert _escape('a"b') == 'a\\"b'
    assert _escape('a\\b') == 'a\\\\b'
    assert _escape('line1\nline2') == 'line1 line2'


def test_notify_runs_osascript_with_app_name():
    notifier = Notifier()
    with patch('app.platform.notifications.subprocess.run') as mock_run:
        mock_run.return_value = MagicMock()
        notifier.notify('Update', '', 'A new version is available.')
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        script = args[0]
        assert script[0] == '/usr/bin/osascript'
        assert script[1] == '-e'
        assert 'display notification' in script[2]
        # Title should be app name; caller title becomes subtitle.
        assert 'SleeperX' in script[2]
        assert 'subtitle "Update"' in script[2]
        assert 'A new version is available.' in script[2]
        assert kwargs.get('timeout') == 10


def test_notify_subtitle_prepended_to_body():
    notifier = Notifier()
    with patch('app.platform.notifications.subprocess.run') as mock_run:
        notifier.notify('Title', 'Subtitle', 'Body')
        script = mock_run.call_args[0][0][2]
        assert 'Subtitle Body' in script


def test_notify_swallows_subprocess_errors():
    notifier = Notifier()
    log = MagicMock()
    notifier.log = log
    with patch('app.platform.notifications.subprocess.run',
               side_effect=OSError('broken')):
        notifier.notify('Title', '', 'Body')
        log.exception.assert_called_once_with('notification delivery failed')
