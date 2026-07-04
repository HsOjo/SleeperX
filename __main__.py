"""SleeperX entry point.

Modes:
  <app> --helper   -> run the privileged LaunchDaemon helper (root) and exit.
  <app>            -> launch the menubar application.
"""
from __future__ import annotations

import sys


def _run_helper() -> int:
    from app.helper.daemon import main
    return main()


def _activate_existing_instance() -> None:
    """Try to bring an already-running instance to the foreground."""
    try:
        from AppKit import NSRunningApplication
        from app.res.const import Const
        running = NSRunningApplication.runningApplicationsWithBundleIdentifier_(
            Const.bundle_id)
        if running:
            running[0].activateWithOptions_(1 << 1)  # NSApplicationActivateIgnoringOtherApps
    except Exception:
        pass


def _acquire_instance_lock() -> int | None:
    """Acquire an exclusive file lock to enforce a single running instance.

    Returns the lock file descriptor on success, or None if another instance
    already holds the lock. The descriptor must stay open for the process
    lifetime; closing it releases the lock.
    """
    import fcntl
    import os

    from app.res.const import Const

    os.makedirs(Const.config_dir, exist_ok=True)
    lock_path = os.path.join(Const.config_dir, 'instance.lock')
    fd = os.open(lock_path, os.O_CREAT | os.O_RDWR)
    try:
        fcntl.lockf(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except (OSError, IOError):
        os.close(fd)
        _activate_existing_instance()
        return None
    try:
        os.ftruncate(fd, 0)
        os.write(fd, str(os.getpid()).encode())
    except OSError:
        pass
    return fd


def _run_app() -> int:
    import logging
    import os

    from AppKit import NSApplication
    from app.core.logging_setup import setup_logging, install_excepthook
    from app.ui.controller import Controller
    from app.ui.app_delegate import AppDelegate

    logger = setup_logging(logging.INFO)

    lock_fd = _acquire_instance_lock()
    if lock_fd is None:
        logger.info('Another instance is already running; exiting.')
        return 0

    try:
        controller = Controller(logger)

        def on_crash(exc):
            try:
                controller.notifier.notify(controller.lang.title_crash, '',
                                           controller.lang.description_crash)
            except Exception:
                pass

        install_excepthook(logger, on_crash=on_crash)

        app = NSApplication.sharedApplication()
        delegate = AppDelegate.alloc().initWithController_(controller)
        app.setDelegate_(delegate)
        _run_app._delegate = delegate  # retain against GC
        app.run()
    finally:
        os.close(lock_fd)
    return 0


def main() -> int:
    if '--helper' in sys.argv[1:]:
        return _run_helper()
    return _run_app()


if __name__ == '__main__':
    sys.exit(main())
