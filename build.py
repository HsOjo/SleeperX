import os
import shutil

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
