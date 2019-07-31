from common import popen


class BusyWork:
    def __init__(self):
        self._process = None

    def start(self):
        if self._process is None:
            self._process = popen('/usr/bin/pmset noidle')

    def stop(self):
        if self._process is not None:
            self._process.terminate()
        self._process = None
