import os
import shutil
from zipfile import ZipFile

from res.const import Const

# reset dist directory.
shutil.rmtree('./build')
shutil.rmtree('./dist')
os.system('pyinstaller ./SleeperX.spec')

# hide dock icon.
INFO_FILE = './dist/SleeperX.app/Contents/Info.plist'

with open(INFO_FILE, 'r', encoding='utf8') as io:
    info = io.read()

dict_pos = info.find('<dict>') + 7
info = info[:dict_pos] + '\t<key>LSUIElement</key>\n\t<string>1</string>\n' + info[dict_pos:]
with open(INFO_FILE, 'w', encoding='utf8') as io:
    io.write(info)

zf = ZipFile('./dist/SleeperX-%s.zip' % Const.version, 'w')
src_dir = './dist/SleeperX.app'
for d, ds, fs in os.walk(src_dir):
    for f in fs:
        path = os.path.join(d, f)
        z_path = path[7:].strip(os.path.sep)
        zf.write(path, z_path)
zf.close()
