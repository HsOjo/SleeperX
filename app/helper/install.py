"""Privileged helper install / uninstall (one-time admin authorization).

Builds a shell script that (as root, via `osascript ... with administrator
privileges`): copies the frozen app bundle into a root-owned directory, writes
the allowed-uid + version files, drops the socket-activated LaunchDaemon plist,
and bootstraps it. Uninstall reverses this. Exactly one password prompt per
operation; nothing is stored.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile

from app.res.const import Const

# The previous bundle id used a capital-S app segment; leftover plist can
# conflict with the new socket-activated daemon.
_OLD_HELPER_LABEL = f'com.{Const.author.lower()}.{Const.app_name}.helper'
_OLD_HELPER_PLIST = f'/Library/LaunchDaemons/{_OLD_HELPER_LABEL}.plist'


def _app_bundle_and_exec():
    """Return (app_bundle_path, installed_helper_exec_path).

    When running from the frozen .app, sys.executable lives inside
    Contents/MacOS, so walking up 3 levels gives the bundle. When running from
    source/venv (development), fall back to dist/SleeperX.app in the project root.
    """
    exe = os.path.abspath(sys.executable)
    bundle = exe
    for _ in range(3):  # .../X.app/Contents/MacOS/X -> .../X.app
        bundle = os.path.dirname(bundle)
    if bundle.endswith('.app'):
        return bundle, os.path.join(Const.helper_app_path, 'Contents', 'MacOS',
                                   os.path.basename(exe))
    # Source/venv run: locate the built .app next to the project root.
    project_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    built = os.path.join(project_root, 'dist', f'{Const.app_name}.app')
    if not os.path.isdir(built):
        raise RuntimeError(
            f'Cannot locate built {Const.app_name}.app; run `python build.py` first.')
    macos_dir = os.path.join(built, 'Contents', 'MacOS')
    entries = [f for f in os.listdir(macos_dir) if not f.startswith('.')]
    if not entries:
        raise RuntimeError('Built .app has no executable in Contents/MacOS')
    return built, os.path.join(Const.helper_app_path, 'Contents', 'MacOS', entries[0])


def _plist_xml(helper_exec: str) -> str:
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{Const.helper_label}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{helper_exec}</string>
        <string>--helper</string>
    </array>
    <key>Sockets</key>
    <dict>
        <key>Listeners</key>
        <dict>
            <key>SockPathName</key>
            <string>{Const.helper_socket_path}</string>
            <key>SockPathMode</key>
            <integer>438</integer>
        </dict>
    </dict>
    <key>ThrottleInterval</key>
    <integer>0</integer>
    <key>StandardOutPath</key>
    <string>{Const.helper_install_dir}/helper.log</string>
    <key>StandardErrorPath</key>
    <string>{Const.helper_install_dir}/helper.log</string>
</dict>
</plist>
'''


def _run_privileged_script(script: str, logger=None) -> bool:
    fd, path = tempfile.mkstemp(suffix='.sh')
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(script)
        os.chmod(path, 0o755)
        apple = (f'do shell script "/bin/bash \\"{path}\\"" with administrator privileges')
        result = subprocess.run(['/usr/bin/osascript', '-e', apple], check=False)
        if result.returncode != 0:
            if logger:
                logger.info(f'privileged script cancelled/failed (rc={result.returncode})')
            return False
        return True
    finally:
        try:
            os.remove(path)
        except OSError:
            pass


def install(logger=None) -> bool:
    bundle, helper_exec = _app_bundle_and_exec()
    uid = os.getuid()
    plist = _plist_xml(helper_exec)
    script = f'''#!/bin/bash
set -e
INSTALL_DIR="{Const.helper_install_dir}"
rm -rf "{Const.helper_app_path}"
mkdir -p "$INSTALL_DIR"
cp -R "{bundle}" "{Const.helper_app_path}"
printf '%s' "{uid}" > "{Const.helper_allowed_uid_path}"
printf '%s' "{Const.version}" > "{Const.helper_version_path}"
# Remove any leftover daemon from the previous capital-S bundle id.
launchctl bootout system "{_OLD_HELPER_PLIST}" 2>/dev/null || true
rm -f "{_OLD_HELPER_PLIST}"
cat > "{Const.launch_daemon_plist}" <<'PLIST'
{plist}
PLIST
chown -R root:wheel "$INSTALL_DIR"
chmod 755 "$INSTALL_DIR"
chown root:wheel "{Const.launch_daemon_plist}"
chmod 644 "{Const.launch_daemon_plist}"
launchctl bootout system "{Const.launch_daemon_plist}" 2>/dev/null || true
launchctl bootstrap system "{Const.launch_daemon_plist}"
'''
    return _run_privileged_script(script, logger)


def uninstall(logger=None) -> bool:
    script = f'''#!/bin/bash
launchctl bootout system "{Const.launch_daemon_plist}" 2>/dev/null || true
rm -f "{Const.launch_daemon_plist}"
rm -rf "{Const.helper_install_dir}"
'''
    return _run_privileged_script(script, logger)
