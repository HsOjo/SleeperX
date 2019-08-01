import sys

import common
from app import Application

if getattr(sys, 'frozen', False):
    sys.stdout = common.io_log

app = Application()
try:
    app.run()
except:
    app.callback_exception()
