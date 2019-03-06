import os
import re

import common
from util import osa_api


def battery_info():
    p = common.popen('/usr/bin/pmset -g ps')
    msg = p.stdout.read()

    reg = re.compile('(\d*%); (.*?); (.*?) present: ')
    [res] = reg.findall(msg.replace('AC attached; not charging', 'not charging; (no estimate)'))

    remaining = res[2].replace(' remaining', '')
    remaining = common.convert_minute(remaining) if remaining != '(no estimate)' else None

    info = {
        'percent': int(res[0][:-1]),
        'status': res[1],
        'remaining': remaining,
    }

    return info


def sleep(**kwargs):
    osa_api.run_as_admin('/sbin/shutdown -s now', **kwargs)


def set_sleep_mode(mode, **kwargs):
    if mode in [0, 3, 25]:
        osa_api.run_as_admin('/usr/bin/pmset hibernatemode %d' % mode, **kwargs)


def open_url(url):
    os.system('/usr/bin/open "%s"' % url)
