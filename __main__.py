import os
import re
import time
import traceback


def convert_minute(t):
    h, m = list(map(int, t.split(':')))
    return h * 60 + m


def battery_info():
    msg = os.popen('pmset -g ps').read()

    reg = re.compile('(\d*%); (.*?); (.*?) present: ')
    [res] = reg.findall(msg.replace('AC attached; not charging', 'not charging; (no estimate)'))

    remaining = res[2].replace(' remaining', '')
    remaining = convert_minute(remaining) if remaining != '(no estimate)' else None

    info = {
        'percent': int(res[0][:-1]),
        'status': res[1],
        'remaining': remaining,
    }

    return info


def sleep():
    os.system('shutdown -s now')


if __name__ == '__main__':
    while True:
        try:
            bi = battery_info()
            if bi['status'] == 'discharging' and (bi['percent'] <= 6 or bi['remaining'] <= 10):
                sleep()
            time.sleep(120)
        except:
            traceback.print_exc()
