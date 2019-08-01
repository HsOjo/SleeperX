from subprocess import Popen
from threading import Thread, Lock

import common
from util import system_api


class ProcessDaemon:
    def __init__(self, command):
        self._command = command
        self._process = None  # type: Popen

        self._t_daemon = None  # type: Thread
        self._lock = Lock()

    def with_lock(func):
        def core(self, *args, **kwargs):
            with self._lock:
                return func(self, *args, **kwargs)

        return core

    @property
    @with_lock
    def is_working(self):
        return self._process is not None

    @property
    @with_lock
    def is_running(self):
        if self._process is not None:
            p = system_api.check_process(self._process.pid)
            if p is not None and p['STAT'] == 'S':
                return True
        return False

    def start(self, daemon=True):
        if not self.is_working:
            with self._lock:
                self._process = common.popen(self._command)

            if daemon:
                self._t_daemon = Thread(target=self._daemon)
                self._t_daemon.start()

    def stop(self, daemon=True):
        if self.is_working:
            with self._lock:
                self._process.terminate()

        with self._lock:
            self._process = None

        if daemon:
            self._t_daemon.join(timeout=3)
            self._t_daemon = None

    def _daemon(self):
        @common.wait_and_check(3, 0.18)
        def check():
            return self.is_working

        while self.is_working:
            if not check():
                break

            if self.is_working and not self.is_running:
                self.stop(False)
                self.start(False)
