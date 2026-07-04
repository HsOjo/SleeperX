"""Notifications via AppleScript `display notification`.

`NSUserNotification` is deprecated and frequently fails to deliver for unsigned
menu-bar apps. `osascript display notification` works without code signing and
does not require the app to be bundled, so we use it as a reliable fallback.

The notification title is always the application name; the caller's `title` is
shown as the subtitle. If a `subtitle` is provided, it is prepended to the body.
"""
from __future__ import annotations

import logging
import subprocess

from app.res.const import Const


log = logging.getLogger(__name__)


def _escape(s: str) -> str:
    return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ')


class Notifier:
    def __init__(self, logger=None):
        self.log = logger

    def notify(self, title: str, subtitle: str = '', message: str = '') -> None:
        """Show a system notification.

        Args:
            title: Shown as the notification subtitle.
            subtitle: If provided, prepended to the informative body text.
            message: Informative body text.
        """
        body = message
        if subtitle:
            body = f'{subtitle}\n{body}' if body else subtitle

        script = (
            f'display notification "{_escape(body)}" '
            f'with title "{_escape(Const.app_name)}" '
            f'subtitle "{_escape(title)}"'
        )
        try:
            subprocess.run(
                ['/usr/bin/osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
        except Exception:
            if self.log:
                self.log.exception('notification delivery failed')
