"""Privileged helper daemon (root side).

Launched on demand by launchd via socket activation (see helper/install.py).
Reads one JSON request per connection over the launchd-provided Unix socket,
verifies the peer's uid with getpeereid() against the allowed-uid file, executes
a STRICTLY whitelisted pmset command, replies with JSON, then exits.

Entry point: `<app> --helper` routes here (see __main__.py).
"""
from __future__ import annotations

import ctypes
import json
import os
import socket
import subprocess
import sys
import time

from app.res.const import Const

_libc = ctypes.CDLL(None, use_errno=True)

# int launch_activate_socket(const char *name, int **fds, size_t *cnt)
_libc.launch_activate_socket.restype = ctypes.c_int
_libc.launch_activate_socket.argtypes = [
    ctypes.c_char_p, ctypes.POINTER(ctypes.POINTER(ctypes.c_int)),
    ctypes.POINTER(ctypes.c_size_t)]
# int getpeereid(int, uid_t*, gid_t*)
_libc.getpeereid.restype = ctypes.c_int
_libc.getpeereid.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_uint32),
                             ctypes.POINTER(ctypes.c_uint32)]

_SOCKET_NAME = 'Listeners'


def _activate_sockets(name: str = _SOCKET_NAME):
    fds_ptr = ctypes.POINTER(ctypes.c_int)()
    cnt = ctypes.c_size_t(0)
    rc = _libc.launch_activate_socket(name.encode(), ctypes.byref(fds_ptr),
                                      ctypes.byref(cnt))
    if rc != 0:
        return []
    fds = [fds_ptr[i] for i in range(cnt.value)]
    _libc.free(fds_ptr)
    return fds


def _peer_uid(conn: socket.socket):
    uid = ctypes.c_uint32(0)
    gid = ctypes.c_uint32(0)
    if _libc.getpeereid(conn.fileno(), ctypes.byref(uid), ctypes.byref(gid)) != 0:
        return None
    return uid.value


def _allowed_uid():
    try:
        with open(Const.helper_allowed_uid_path) as f:
            return int(f.read().strip())
    except (OSError, ValueError):
        return None


def _run_pmset(*args) -> bool:
    start = time.time()
    try:
        rc = subprocess.run(['/usr/bin/pmset', *args], check=False).returncode
    except OSError:
        return False
    finally:
        rc_str = rc if 'rc' in dir() else '?'
        sys.stderr.write(f'[helper] pmset {" ".join(args)} took {time.time() - start:.3f}s (rc={rc_str})\n')
        sys.stderr.flush()
    return rc == 0


def _dispatch(req: dict) -> dict:
    cmd = req.get('cmd')
    if cmd == 'version':
        return {'ok': True, 'version': Const.version}
    if cmd == 'disablesleep':
        value = req.get('value')
        if value in (0, 1):
            return {'ok': _run_pmset('-a', 'disablesleep', str(value))}
    elif cmd == 'hibernatemode':
        value = req.get('value')
        if value in (0, 3, 25):
            return {'ok': _run_pmset('-a', 'hibernatemode', str(value))}
    return {'ok': False, 'error': 'rejected'}


def _handle(conn: socket.socket, allowed: int) -> None:
    try:
        uid = _peer_uid(conn)
        if uid is None or (allowed is not None and uid != allowed):
            conn.sendall(json.dumps({'ok': False, 'error': 'uid'}).encode() + b'\n')
            return
        conn.settimeout(5)
        data = b''
        while b'\n' not in data:
            chunk = conn.recv(4096)
            if not chunk:
                break
            data += chunk
            if len(data) > 4096:
                break
        try:
            req = json.loads(data.decode().strip() or '{}')
        except ValueError:
            req = {}
        resp = _dispatch(req)
        conn.sendall(json.dumps(resp).encode() + b'\n')
    finally:
        conn.close()


def main() -> int:
    allowed = _allowed_uid()
    fds = _activate_sockets()
    if not fds:
        return 1
    for fd in fds:
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM, fileno=fd)
        # Stay alive for a while so repeated UI toggles reuse the same daemon
        # instead of paying the launchd cold-start / throttle penalty each time.
        server.settimeout(60)
        try:
            while True:
                try:
                    conn, _ = server.accept()
                except socket.timeout:
                    break
                _handle(conn, allowed)
        finally:
            server.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
