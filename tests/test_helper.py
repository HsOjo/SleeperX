"""Unit tests for the privileged helper daemon and installer."""
from __future__ import annotations

import sys
from unittest.mock import patch

import pytest

from app.helper import daemon as helper_daemon
from app.helper import install as helper_install
from app.res.const import Const


def test_dispatch_version():
    with patch.object(helper_daemon, '_run_pmset'):
        resp = helper_daemon._dispatch({'cmd': 'version'})
    assert resp['ok'] is True
    assert resp['version'] == Const.version


@pytest.mark.parametrize('cmd,value', [
    ('disablesleep', 0),
    ('disablesleep', 1),
    ('hibernatemode', 0),
    ('hibernatemode', 3),
    ('hibernatemode', 25),
])
def test_dispatch_whitelisted_commands(cmd, value):
    with patch.object(helper_daemon, '_run_pmset', return_value=True) as mock_pmset:
        resp = helper_daemon._dispatch({'cmd': cmd, 'value': value})
    assert resp['ok'] is True
    mock_pmset.assert_called_once()


def test_dispatch_rejects_unknown_command():
    with patch.object(helper_daemon, '_run_pmset'):
        resp = helper_daemon._dispatch({'cmd': 'reboot'})
    assert resp['ok'] is False


def test_dispatch_rejects_invalid_value():
    with patch.object(helper_daemon, '_run_pmset'):
        resp = helper_daemon._dispatch({'cmd': 'disablesleep', 'value': 2})
    assert resp['ok'] is False


def test_plist_xml_contains_required_keys():
    xml = helper_install._plist_xml('/path/to/SleeperX')
    assert Const.helper_label in xml
    assert '/path/to/SleeperX' in xml
    assert '--helper' in xml
    assert Const.helper_socket_path in xml


def test_app_bundle_and_exec_from_frozen_app(monkeypatch, tmp_path):
    app = tmp_path / 'SleeperX.app'
    macos = app / 'Contents' / 'MacOS'
    macos.mkdir(parents=True)
    (macos / 'SleeperX').write_text('binary', encoding='utf-8')
    monkeypatch.setattr(sys, 'executable', str(macos / 'SleeperX'))
    bundle, exec_path = helper_install._app_bundle_and_exec()
    assert bundle == str(app)
    assert exec_path.endswith('Contents/MacOS/SleeperX')
