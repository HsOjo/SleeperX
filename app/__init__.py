import base64
import json
import os
from threading import Thread

import rumps

import common
from res.const import CONST
from res.lang import LANGUAGE
from util import osa_api, system_api, github


class Application:
    CONFIG_FILE = os.path.expanduser('~/Library/Application Support/com.hsojo.sleeperx')

    def __init__(self):
        self.config = {}
        self.load_config()
        self.lang = LANGUAGE[self.config['language']]

        self.t_check_update()
        self.app = rumps.App('SleeperX', quit_button=None)
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
            add_menu('set_sleep_mode', self.lang['menu_set_sleep_mode'], self.set_sleep_mode),
            rumps.separator,
            add_menu('set_low_battery_capacity', self.lang['menu_set_low_battery_capacity'],
                     self.set_low_battery_capacity),
            add_menu('set_low_time_remaining', self.lang['menu_set_low_time_remaining'], self.set_low_time_remaining),
            rumps.separator,
            add_menu('set_password', self.lang['menu_set_password'], self.set_password),
            add_menu('set_username', self.lang['menu_set_username'], self.set_username),
            add_menu('set_startup', self.lang['menu_set_startup'], self.set_startup),
            rumps.separator,
            add_menu('set_language', self.lang['menu_set_language'], self.set_language),
            rumps.separator,
            add_menu('check_update', self.lang['menu_check_update'], lambda x: self.t_check_update(x)),
            add_menu('about', self.lang['menu_about'], self.about),
            rumps.separator,
            add_menu('quit', self.lang['menu_quit'], self.quit),
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
            print('[Menu] Click %s.' % name)
            menu = self.menu[name]
            menu['callback'](menu['object'])
        except:
            self.callback_exception()

    def callback_refresh(self, sender: rumps.Timer):
        try:
            battery_info = system_api.battery_info()
            self.set_menu_title('view_percent',
                                self.lang['view_percent'] % battery_info['percent'])

            self.set_menu_title('view_status',
                                self.lang['view_status'] % (
                                    self.lang['status_charging'].get(battery_info['status'], self.lang['unknown'])))

            self.set_menu_title('view_remaining',
                                self.lang['view_remaining'] % (
                                    (self.lang['view_remaining_time'] % battery_info['remaining'])
                                    if battery_info['remaining'] is not None else self.lang['view_remaining_counting']))

            if battery_info['status'] == 'discharging' and (
                    battery_info['percent'] <= self.config['low_battery_capacity'] or
                    (battery_info['remaining'] is not None and
                     battery_info['remaining'] <= self.config['low_time_remaining'])):
                system_api.sleep(user=self.config['username'], pwd=self.config['password'])
        except:
            self.callback_exception()

    def callback_exception(self):
        exc = common.get_exception()
        print('[Exception] %s' % exc)
        if osa_api.alert(self.lang['title_crash'], self.lang['description_crash']):
            self.export_log()

    def set_low_battery_capacity(self, sender: rumps.MenuItem):
        content = osa_api.dialog_input(sender.title, self.lang['description_set_low_battery_capacity'],
                                       str(self.config.get('low_battery_capacity', '')))

        if isinstance(content, str) and content.isnumeric():
            self.config['low_battery_capacity'] = int(content)
            self.save_config()

    def set_low_time_remaining(self, sender: rumps.MenuItem):
        content = osa_api.dialog_input(sender.title, self.lang['description_set_low_time_remaining'],
                                       str(self.config.get('low_time_remaining', '')))
        if isinstance(content, str) and content.isnumeric():
            self.config['low_time_remaining'] = int(content)
            self.save_config()

    def set_username(self, sender: rumps.MenuItem):
        content = osa_api.dialog_input(sender.title, self.lang['description_set_username'],
                                       self.config.get('username', ''))
        if content is not None:
            self.config['username'] = content
            self.save_config()

    def set_password(self, sender: rumps.MenuItem):
        content = osa_api.dialog_input(sender.title, self.lang['description_set_password'],
                                       hidden=True)
        if content is not None:
            self.config['password'] = content
            self.save_config()

    def set_language(self, sender: rumps.MenuItem):
        items = []
        for k in LANGUAGE:
            items.append(LANGUAGE[k]['l_this'])

        index = osa_api.choose_from_list(sender.title, LANGUAGE['en']['description_set_language'], items)
        if index is not None:
            language = None
            description = items[index]
            for k, v in LANGUAGE.items():
                if description == v['l_this']:
                    language = k
                    break

            if language is not None:
                self.config['language'] = language
                self.save_config()

                [_, path] = common.get_application_info()
                system_api.open_url(path, True)
                self.quit()

    def set_startup(self, sender: rumps.MenuItem):
        res = osa_api.alert(sender.title, self.lang['description_set_startup'])
        if res:
            osa_api.set_login_startup(*common.get_application_info())

    def set_sleep_mode(self, sender: rumps.MenuItem):
        info = system_api.sleep_info()
        items = [self.lang['sleep_mode_0'], self.lang['sleep_mode_3'], self.lang['sleep_mode_25']]
        items_value = {
            0: 0,
            1: 3,
            2: 25,
        }
        default = None
        for k, v in items_value.items():
            if v == info['hibernatemode']:
                default = k
        res = osa_api.dialog_select(sender.title, self.lang['description_set_sleep_mode'] % info['hibernatemode'],
                                    items, default)
        mode = items_value.get(res)
        if mode is not None:
            system_api.set_sleep_mode(mode, user=self.config['username'], pwd=self.config['password'])

    def sleep_now(self, sender: rumps.MenuItem):
        system_api.sleep(user=self.config['username'], pwd=self.config['password'])

    def about(self, sender: rumps.MenuItem):
        res = osa_api.dialog_input(sender.title, self.lang['description_about'] % CONST['version'],
                                   CONST['github_page'])
        if res == ':export log':
            self.export_log()

    def export_log(self):
        folder = osa_api.choose_folder(self.lang['title_export_log'])
        if folder is not None:
            log = common.extract_log().replace(self.config['password'], '[password]')
            with open('%s/%s' % (folder, 'SleeperX_log.txt'), 'w') as io:
                io.write(log)

    def quit(self, sender: rumps.MenuItem = None):
        rumps.quit_application()

    def t_check_update(self, sender: rumps.MenuItem = None):
        Thread(target=self.check_update, args=(sender,)).start()

    def check_update(self, sender: rumps.MenuItem):
        try:
            have_new = False
            rs = github.get_releases(CONST['releases_url'], timeout=5)
            for r in rs:
                if common.compare_version(CONST['version'], r['title']):
                    have_new = True
                    rumps.notification(
                        self.lang['noti_update_version'] % r['title'],
                        self.lang['noti_update_time'] % r['datetime'],
                        r['description']
                    )
                    if sender is not None:
                        system_api.open_url(r['url'])
                    break

            if sender is not None and have_new is False:
                rumps.notification(sender.title, self.lang['noti_update_none'], self.lang['noti_update_star'])
        except:
            if sender is not None:
                rumps.notification(sender.title, '', self.lang['noti_network_error'])

    def run(self):
        print('[Version] %s' % CONST['version'])
        t = rumps.Timer(self.callback_refresh, 1)
        t.start()
        self.app.run()
