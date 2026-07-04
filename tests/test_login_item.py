"""Unit tests for user-level LaunchAgent login-item management."""
from __future__ import annotations

from unittest.mock import patch

import pytest

from app.platform.login_item import LoginItem
from app.res.const import Const


@pytest.fixture
def temp_plist(tmp_path, monkeypatch):
    path = tmp_path / 'login.plist'
    monkeypatch.setattr(Const, 'launch_agent_plist', str(path))
    yield path


def test_is_enabled_false_when_missing(temp_plist):
    item = LoginItem()
    assert item.is_enabled() is False


def test_enable_writes_plist_and_bootstraps(temp_plist):
    item = LoginItem()
    with patch('app.platform.login_item.subprocess.run') as mock_run:
        assert item.enable() is True
    assert temp_plist.exists()
    data = temp_plist.read_bytes()
    assert b'RunAtLoad' in data
    assert b'KeepAlive' in data
    assert Const.agent_label.encode() in data
    mock_run.assert_called_once()
    args = mock_run.call_args[0][0]
    assert args[0] == '/bin/launchctl'
    assert args[1] == 'bootstrap'


def test_disable_bootouts_and_removes_plist(temp_plist):
    temp_plist.write_text('placeholder', encoding='utf-8')
    item = LoginItem()
    with patch('app.platform.login_item.subprocess.run') as mock_run:
        assert item.disable() is True
    assert not temp_plist.exists()
    mock_run.assert_called_once()
    args = mock_run.call_args[0][0]
    assert args[1] == 'bootout'
