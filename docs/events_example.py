#!/usr/local/bin/python3
import os
import time


def take_photo(path):
    import cv2
    cap = cv2.VideoCapture(0)
    _, frame = cap.read()
    cv2.imwrite(path, frame)
    cap.release()


PHOTO_DIR = os.path.expanduser('~/SleeperX')
time_now = lambda: time.strftime('%Y_%m_%d_%H_%M_%S')


def event_idle_status_changed(idle_time: int, **env):
    if idle_time >= 300:
        take_photo('%s/idle_%s.png' % (PHOTO_DIR, time_now()))


def event_sleep_waked_up(sleep_time: float, **env):
    time.sleep(3)
    take_photo('%s/sleep_%s_%.2f.png' % (PHOTO_DIR, time_now(), sleep_time))


def event_lid_status_changed(status: bool, status_prev: bool, **env):
    if status_prev and not status:
        take_photo('%s/lid_%s.png' % (PHOTO_DIR, time_now()))


def event_charge_status_changed(status: str, status_prev: str, **env):
    print(status, status_prev)
    # TODO: something you want to do.


if __name__ == '__main__':
    import sys
    import json

    from_json = lambda x: json.loads(x)

    env = os.environ
    if len(sys.argv) >= 2:
        event = sys.argv[1]
        events = {
            'idle': event_idle_status_changed,
            'lid': event_lid_status_changed,
            'charge': event_charge_status_changed,
            'sleep': event_sleep_waked_up,
        }

        if event in events:
            events[event](**from_json(env.pop('SLEEPERX_ENV')), **env)
        else:
            print("Can't execute valid function: %s" % event)
    else:
        print('Must add one event arg.')
