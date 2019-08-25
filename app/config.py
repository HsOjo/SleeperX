from .base.config import ConfigBase


class Config(ConfigBase):
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
    event_idle_status_changed = ''
    event_lid_status_changed = ''
    event_charge_status_changed = ''
    event_sleep_waked_up = ''
    time_idle_event = 30
    process_timeout = 5
