import base64
import json
import os

from app import common
from .res.const import Const

CONFIG_NAME = ('com.%s.%s' % (Const.author, Const.app_name)).lower()
CONFIG_FILE = os.path.expanduser('~/Library/Application Support/%s' % CONFIG_NAME)


class Config:
    _protect_fields = [
        'password',
    ]
    welcome = True
    username = ''
    password = ''
    language = 'en'
    low_battery_capacity_sleep = True
    low_battery_capacity = 6
    low_time_remaining = 10
    disable_idle_sleep_in_charging = False
    disable_lid_sleep_in_charging = False
    screen_save_on_lid = False
    short_time_cancel_screen_save = True

    @staticmethod
    def load():
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as io:
                    config = json.load(io)
                    for f in Config._protect_fields:
                        config[f] = base64.b64decode(config[f][::-1].encode()).decode()
                    common.dict_to_object(config, Config, new_fields=False)
                    common.log('config_load', 'Info', common.object_to_dict(Config))
        except:
            pass

    @staticmethod
    def save():
        with open(CONFIG_FILE, 'w') as io:
            config = common.object_to_dict(Config)
            for f in Config._protect_fields:
                config[f] = base64.b64encode(config[f].encode()).decode()[::-1]
            json.dump(config, io, indent='  ')
            common.log('config_save', 'Info', common.object_to_dict(Config))

    @staticmethod
    def clear():
        if os.path.exists(CONFIG_FILE):
            os.unlink(CONFIG_FILE)
