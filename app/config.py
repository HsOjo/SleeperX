import base64
import json
import os

import common

CONFIG_FILE = os.path.expanduser('~/Library/Application Support/com.hsojo.sleeperx')


class Config:
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
                with open(CONFIG_FILE, 'r', encoding='utf8') as io:
                    config = json.load(io)
                    config['password'] = base64.b64decode(config['password'][::-1].encode()).decode()
                    common.dict_to_object(config, Config, new_fields=False)
                    common.log('config_load', 'Info', common.object_to_dict(Config))
        except:
            pass

    @staticmethod
    def save():
        with open(CONFIG_FILE, 'w', encoding='utf8') as io:
            config = common.object_to_dict(Config)
            config['password'] = base64.b64encode(config['password'].encode()).decode()[::-1]
            json.dump(config, io, indent='  ')
            common.log('config_save', 'Info', common.object_to_dict(Config))

    @staticmethod
    def clear():
        if os.path.exists(CONFIG_FILE):
            os.unlink(CONFIG_FILE)
