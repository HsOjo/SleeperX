"""Client for the privileged helper (app/user side).

Implements the PrivilegedOps port by talking to the socket-activated
LaunchDaemon over a Unix socket. The helper must be installed explicitly
(see `install()`); write operations fail gracefully if it is missing.
"""
from __future__ import annotations

import json
import os
import socket
from typing import Optional

from app.helper import install as helper_install
from app.res.const import Const


class PrivilegedClient:
    def __init__(self, logger=None):
        self.log = logger

    # ------------------------------------------------------------- lifecycle
    def is_installed(self) -> bool:
        return (os.path.exists(Const.launch_daemon_plist)
                and os.path.exists(Const.helper_app_path))

    def install(self) -> bool:
        return helper_install.install(self.log)

    def uninstall(self) -> bool:
        return helper_install.uninstall(self.log)

    # ------------------------------------------------------------------- ipc
    def _request(self, payload: dict, attempts: int = 2) -> Optional[dict]:
        if not self.is_installed():
            if self.log:
                self.log.info('privileged helper not installed; request skipped')
            return None
        last_exc = None
        for attempt in range(attempts):
            try:
                conn = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                # Cold-starting the PyInstaller helper via launchd can take a few
                # seconds; give it enough headroom and retry once on timeout.
                conn.settimeout(15)
                conn.connect(Const.helper_socket_path)
                try:
                    conn.sendall(json.dumps(payload).encode() + b'\n')
                    data = b''
                    while b'\n' not in data:
                        chunk = conn.recv(4096)
                        if not chunk:
                            break
                        data += chunk
                    return json.loads(data.decode().strip() or '{}')
                finally:
                    conn.close()
            except TimeoutError as exc:
                last_exc = exc
                if attempt < attempts - 1:
                    import time
                    time.sleep(0.5)
                continue
            except (OSError, ValueError):
                if self.log:
                    self.log.exception('helper request failed')
                return None
        if last_exc is not None and self.log:
            self.log.exception(f'helper request timed out after {attempts} attempts')
        return None

    def helper_version(self) -> Optional[str]:
        if not self.is_installed():
            return None
        resp = self._request({'cmd': 'version'})
        return resp.get('version') if resp else None

    def set_disable_sleep(self, disabled: bool) -> bool:
        if not self.is_installed():
            if self.log:
                self.log.info('set_disable_sleep: helper not installed')
            return False
        resp = self._request({'cmd': 'disablesleep', 'value': 1 if disabled else 0})
        return bool(resp and resp.get('ok'))

    def set_hibernate_mode(self, mode: int) -> bool:
        if mode not in (0, 3, 25):
            return False
        if not self.is_installed():
            if self.log:
                self.log.info('set_hibernate_mode: helper not installed')
            return False
        resp = self._request({'cmd': 'hibernatemode', 'value': mode})
        return bool(resp and resp.get('ok'))
