import sys
from io import StringIO

from app import Application

if getattr(sys, 'frozen', False):
    sys.stdout = StringIO()

Application().run()
