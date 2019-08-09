#!/Users/hsojo/Projects/PycharmProjects/VirtualEnv/bin/python
import os


def take_photo(path):
    import cv2
    cap = cv2.VideoCapture(0)
    _, frame = cap.read()
    cv2.imwrite(path, frame)
    cap.release()


def event_idle_status_changed(idle_time: int, **env):
    if idle_time >= 300:
        take_photo(os.path.expanduser("~/Downloads/idle.png"))


def event_sleep_waked_up(sleep_time: int, **env):
    if sleep_time > 60:
        os.system('open %s' % os.path.expanduser('~/Automator/RestartBluetooth.app'))


def event_lid_status_changed(status: bool, status_prev: bool, **env):
    if status_prev and not status:
        take_photo(os.path.expanduser("~/Downloads/lid.png"))


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
