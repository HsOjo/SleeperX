"""System version + current hibernate mode (read-only, unprivileged)."""
from __future__ import annotations

import re
import subprocess
from typing import Optional

from Foundation import NSProcessInfo


class SystemInfo:
    def __init__(self, logger=None):
        self.log = logger

    def version_string(self) -> str:
        v = NSProcessInfo.processInfo().operatingSystemVersion()
        return f'{v.majorVersion}.{v.minorVersion}.{v.patchVersion}'

    def hibernate_mode(self) -> Optional[int]:
        """Read the current hibernatemode from `pmset -g` (no root needed)."""
        try:
            out = subprocess.check_output(['/usr/bin/pmset', '-g'], text=True)
        except (OSError, subprocess.CalledProcessError):
            return None
        m = re.search(r'hibernatemode\s+(\d+)', out)
        return int(m.group(1)) if m else None
