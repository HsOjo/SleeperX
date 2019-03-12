import sys

import common
from app import Application

if getattr(sys, 'frozen', False):
    sys.stdout = common.io_log

Application().run()
