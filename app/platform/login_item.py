"""Login-item management via a user-level LaunchAgent.

Writes ~/Library/LaunchAgents/<agent_label>.plist with RunAtLoad (start at
login) and KeepAlive{SuccessfulExit=false} (relaunch only on crash). No admin
rights or code signing required — unlike SMAppService.
"""
from __future__ import annotations

import os
import subprocess
import sys

from Foundation import (NSDictionary, NSArray, NSNumber)

from app.res.const import Const


def _app_executable() -> str:
    # Under PyInstaller onedir, sys.executable is the frozen app binary.
    return sys.executable


class LoginItem:
    def __init__(self, logger=None):
        self.log = logger
        self.plist_path = Const.launch_agent_plist

    def is_enabled(self) -> bool:
        return os.path.exists(self.plist_path)

    def _write_plist(self) -> bool:
        plist = NSDictionary.dictionaryWithDictionary_({
            'Label': Const.agent_label,
            'ProgramArguments': NSArray.arrayWithArray_([_app_executable()]),
            'RunAtLoad': NSNumber.numberWithBool_(True),
            'KeepAlive': NSDictionary.dictionaryWithDictionary_({
                'SuccessfulExit': NSNumber.numberWithBool_(False),
            }),
            'ProcessType': 'Interactive',
        })
        os.makedirs(os.path.dirname(self.plist_path), exist_ok=True)
        ok = plist.writeToFile_atomically_(self.plist_path, True)
        if not ok and self.log:
            self.log.error(f'failed to write LaunchAgent plist: {self.plist_path}')
        return bool(ok)

    def enable(self) -> bool:
        if not self._write_plist():
            return False
        domain = f'gui/{os.getuid()}'
        try:
            subprocess.run(['/bin/launchctl', 'bootstrap', domain, self.plist_path],
                           check=False)
        except OSError:
            if self.log:
                self.log.exception('launchctl bootstrap failed')
            return False
        return True

    def disable(self) -> bool:
        domain = f'gui/{os.getuid()}'
        try:
            subprocess.run(['/bin/launchctl', 'bootout', domain, self.plist_path],
                           check=False)
        except OSError:
            if self.log:
                self.log.exception('launchctl bootout failed')
        try:
            if os.path.exists(self.plist_path):
                os.remove(self.plist_path)
        except OSError:
            if self.log:
                self.log.exception('failed to remove LaunchAgent plist')
            return False
        return True
