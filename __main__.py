import sys

import common
from app import Application

# is run at pyinstaller
if getattr(sys, 'frozen', False):
    # redirect stdout
    sys.stdout = common.io_log

app = Application()
try:
    app.run()
except:
    app.callback_exception()
