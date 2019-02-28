import base64
import json
import os
import traceback

import rumps

import common
from res.const import CONST
from res.lang import LANGUAGE


class SleeperApp:
    CONFIG_FILE = os.path.expanduser('~/Library/Application Support/com.hsojo.sleeperx')

    def __init__(self):
        self.config = {}
        self.load_config()
        self.lang = LANGUAGE[self.config['language']]

        self.app = rumps.App('SleeperX')
        self.menu = {}

        def add_menu(name, title='', callback=None):
            menu = rumps.MenuItem(name,
                                  callback=((lambda _: self.callback_menu(name)) if callback is not None else None))
            self.menu[name] = {'object': menu, 'name': name, 'title': title, 'callback': callback}
            return menu

        self.app.menu = [
            add_menu('view_percent'),
            add_menu('view_status'),
            add_menu('view_remaining'),
            rumps.separator,
            add_menu('sleep_now', self.lang['menu_sleep_now'], self.sleep_now),
            rumps.separator,
            add_menu('set_low_battery_capacity', self.lang['menu_set_low_battery_capacity'],
                     self.set_low_battery_capacity),
            add_menu('set_low_time_remaining', self.lang['menu_set_low_time_remaining'], self.set_low_time_remaining),
            rumps.separator,
            add_menu('set_password', self.lang['menu_set_password'], self.set_password),
            add_menu('set_username', self.lang['menu_set_username'], self.set_username),
            rumps.separator,
            add_menu('set_language', self.lang['menu_set_language'], self.set_language),
            rumps.separator,
            add_menu('about', self.lang['menu_about'], self.about),
            rumps.separator,
        ]

        for k, v in self.menu.items():
            self.app.menu[v['name']].title = v['title']
            del v['title']

    def load_config(self):
        try:
            with open(self.CONFIG_FILE, 'r', encoding='utf8') as io:
                config = json.load(io)
                config['password'] = base64.b64decode(config['password'][::-1].encode()).decode()
                self.config = config
        except FileNotFoundError:
            self.config = {
                'username': '',
                'password': '',
                'language': 'en',
                'low_battery_capacity': 6,
                'low_time_remaining': 10
            }

    def save_config(self):
        with open(self.CONFIG_FILE, 'w', encoding='utf8') as io:
            config = self.config.copy()
            config['password'] = base64.b64encode(config['password'].encode()).decode()[::-1]
            json.dump(config, io, indent='  ')

    def set_menu_title(self, key, title):
        self.app.menu[key].title = title

    def callback_menu(self, name):
        try:
            menu = self.menu[name]
            menu['callback'](menu['object'])
        except:
            traceback.print_exc()

    def callback_refresh(self, sender: rumps.Timer):
        try:
            battery_info = common.battery_info()
            self.set_menu_title('view_percent',
                                self.lang['view_percent'] % battery_info['percent'])

            self.set_menu_title('view_status',
                                self.lang['view_status'] % battery_info['status'])

            self.set_menu_title('view_remaining',
                                self.lang['view_remaining'] % (
                                    (self.lang['view_remaining_time'] % battery_info['remaining'])
                                    if battery_info['remaining'] is not None else self.lang['view_remaining_counting']))

            if battery_info['status'] == 'discharging' and (
                    battery_info['percent'] <= self.config['low_battery_capacity'] or
                    (battery_info['remaining'] is not None and
                     battery_info['remaining'] <= self.config['low_time_remaining'])):
                common.sleep(user=self.config['username'], pwd=self.config['password'])
        except:
            traceback.print_exc()

    def set_low_battery_capacity(self, sender: rumps.MenuItem):
        content = common.gui_input(sender.title, self.lang['description_set_low_battery_capacity'],
                                   str(self.config.get('low_battery_capacity', '')))

        if isinstance(content, str) and content.isnumeric():
            self.config['low_battery_capacity'] = int(content)
            self.save_config()

    def set_low_time_remaining(self, sender: rumps.MenuItem):
        content = common.gui_input(sender.title, self.lang['description_set_low_time_remaining'],
                                   str(self.config.get('low_time_remaining', '')))
        if isinstance(content, str) and content.isnumeric():
            self.config['low_time_remaining'] = int(content)
            self.save_config()

    def set_username(self, sender: rumps.MenuItem):
        content = common.gui_input(sender.title, self.lang['description_set_username'],
                                   self.config.get('username', ''))
        if content is not None:
            self.config['username'] = content
            self.save_config()

    def set_password(self, sender: rumps.MenuItem):
        content = common.gui_input(sender.title, self.lang['description_set_password'],
                                   hidden=True)
        if content is not None:
            self.config['password'] = content
            self.save_config()

    def set_language(self, sender: rumps.MenuItem):
        content = common.gui_input(sender.title, self.lang['description_set_language'],
                                   self.config.get('language', 'en'))
        if isinstance(content, str) and content in LANGUAGE:
            self.config['language'] = content
            self.save_config()

    def sleep_now(self, sender: rumps.MenuItem):
        common.sleep(user=self.config['username'], pwd=self.config['password'])

    def about(self, sender: rumps.MenuItem):
        common.gui_input(sender.title, self.lang['description_about'], CONST['github_page'])

    def run(self):
        t = rumps.Timer(self.callback_refresh, 1)
        t.start()
        self.app.run()
