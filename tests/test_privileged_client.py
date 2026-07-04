"""Unit tests for the privileged helper client (socket IPC side)."""
from __future__ import annotations

import json
import socket
from unittest.mock import MagicMock, patch

import pytest

from app.platform.privileged_client import PrivilegedClient
from app.res.const import Const


@pytest.fixture
def installed_helper(tmp_path, monkeypatch):
    plist = tmp_path / 'daemon.plist'
    app = tmp_path / 'SleeperX.app'
    plist.write_text('plist', encoding='utf-8')
    app.mkdir()
    monkeypatch.setattr(Const, 'launch_daemon_plist', str(plist))
    monkeypatch.setattr(Const, 'helper_app_path', str(app))
    yield


@pytest.fixture
def client():
    return PrivilegedClient()


def test_is_installed_true(installed_helper, client):
    assert client.is_installed() is True


def test_helper_version_parses_response(installed_helper, client, monkeypatch):
    recv_data = bytearray(json.dumps({'version': '2.0.0'}).encode() + b'\n')

    class FakeConn:
        def __init__(self, *a, **k):
            pass
        def settimeout(self, *a):
            pass
        def connect(self, *a):
            pass
        def sendall(self, *a):
            pass
        def recv(self, n):
            chunk = bytes(recv_data[:n])
            del recv_data[:n]
            return chunk
        def close(self):
            pass

    monkeypatch.setattr(socket, 'socket', FakeConn)
    assert client.helper_version() == '2.0.0'


def test_set_disable_sleep_sends_command(installed_helper, client, monkeypatch):
    sent = []
    recv_data = bytearray(json.dumps({'ok': True}).encode() + b'\n')

    class FakeConn:
        def settimeout(self, *a): pass
        def connect(self, *a): pass
        def sendall(self, data): sent.append(data)
        def recv(self, n):
            nonlocal recv_data
            chunk = bytes(recv_data[:n])
            del recv_data[:n]
            return chunk
        def close(self): pass

    monkeypatch.setattr(socket, 'socket', lambda *a, **k: FakeConn())
    assert client.set_disable_sleep(True) is True
    req = json.loads(sent[0].decode().strip())
    assert req['cmd'] == 'disablesleep'
    assert req['value'] == 1


def test_set_hibernate_mode_rejects_invalid_mode(client):
    assert client.set_hibernate_mode(7) is False


def test_set_disable_sleep_returns_false_when_not_installed(client, tmp_path, monkeypatch):
    monkeypatch.setattr(Const, 'launch_daemon_plist', str(tmp_path / 'missing.plist'))
    monkeypatch.setattr(Const, 'helper_app_path', str(tmp_path / 'missing.app'))
    assert client.set_disable_sleep(True) is False


def test_request_returns_none_on_error(installed_helper, client, monkeypatch):
    def raise_error(*a, **k):
        raise OSError('no helper')
    monkeypatch.setattr(socket, 'socket', raise_error)
    assert client.set_disable_sleep(False) is False
