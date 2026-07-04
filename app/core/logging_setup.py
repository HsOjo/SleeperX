"""Logging setup: fixed FileHandler under the config dir + crash excepthook."""
from __future__ import annotations

import logging
import os
import sys

from app.res.const import Const


def setup_logging(level=logging.INFO) -> logging.Logger:
    # A stale file at the config directory path blocks makedirs for the log dir.
    if os.path.isfile(Const.config_dir):
        os.unlink(Const.config_dir)
    os.makedirs(Const.log_dir, exist_ok=True)
    logger = logging.getLogger()
    logger.setLevel(level)
    if not logger.handlers:
        handler = logging.FileHandler(Const.log_path, encoding='utf-8')
        handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s'))
        logger.addHandler(handler)

        stream = logging.StreamHandler()
        stream.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
        logger.addHandler(stream)
    return logger


def install_excepthook(logger, on_crash=None) -> None:
    """Log uncaught exceptions, optionally notify, then exit non-zero.

    A non-zero exit lets the LaunchAgent's KeepAlive{SuccessfulExit=false}
    relaunch the app (the crash-recovery path).
    """
    def hook(exc_type, exc_value, tb):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, tb)
            return
        logger.critical('Uncaught exception', exc_info=(exc_type, exc_value, tb))
        for handler in logger.handlers:
            try:
                handler.flush()
            except Exception:
                pass
        if on_crash is not None:
            try:
                on_crash(exc_value)
            except Exception:
                logger.exception('on_crash handler failed')
        os._exit(1)

    sys.excepthook = hook
