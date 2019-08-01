from threading import Thread

import rumps

import common
from res.const import CONST
from res.lang import LANGUAGE
from util import osa_api, system_api, github
from .config import Config
from .process_daemon import ProcessDaemon


class Application:
    lang = None  # type: dict
    config = None  # type: dict

    def __init__(self):
        common.log('app_init', 'Info', 'version: %s' % CONST['version'])

        Config.load()
        common.log('config_load', 'Info', Config)

        Application.lang = LANGUAGE.get(Config.language, LANGUAGE['en'])

        self.app = rumps.App(CONST['app_name'], quit_button=None)

        self.pd_noidle = ProcessDaemon('/usr/bin/pmset noidle')
        self.pd_caffeinate = ProcessDaemon('/usr/bin/caffeinate')

        self.menu = {}

        def add_menu(name, title='', callback=None, parent=self.app.menu):
            menu = rumps.MenuItem(name,
                                  callback=((lambda _: self.callback_menu(name)) if callback is not None else None))
            if isinstance(parent, rumps.MenuItem):
                parent.add(menu)
            self.menu[name] = {'object': menu, 'name': name, 'title': title, 'callback': callback, 'parent': parent}
            return menu

        self.app.menu = [
            add_menu('view_percent'),
            add_menu('view_status'),
            add_menu('view_remaining'),
            rumps.separator,
            add_menu('disable_lid_sleep', self.lang['menu_disable_lid_sleep'], self.switch_lid_sleep),
            add_menu('disable_idle_sleep', self.lang['menu_disable_idle_sleep'], self.switch_idle_sleep),
            add_menu('sleep_now', self.lang['menu_sleep_now'], self.sleep_now),
            rumps.separator,
            add_menu('preference', self.lang['menu_preference']),
            add_menu('select_language', self.lang['menu_select_language'], self.select_language),
            rumps.separator,
            add_menu('check_update', self.lang['menu_check_update'], lambda x: self.t_check_update(x)),
            add_menu('about', self.lang['menu_about'], self.about),
            rumps.separator,
            add_menu('quit', self.lang['menu_quit'], self.quit),
        ]

        # menu_preference
        self.menu_preference = self.app.menu['preference']  # type: rumps.MenuItem
        add_menu('set_sleep_mode', self.lang['menu_set_sleep_mode'], self.set_sleep_mode, parent=self.menu_preference),
        self.menu_preference.add(rumps.separator)
        add_menu('set_low_battery_capacity', self.lang['menu_set_low_battery_capacity'],
                 self.set_low_battery_capacity, parent=self.menu_preference),
        add_menu('set_low_time_remaining', self.lang['menu_set_low_time_remaining'], self.set_low_time_remaining,
                 parent=self.menu_preference),
        self.menu_preference.add(rumps.separator)
        add_menu('set_password', self.lang['menu_set_password'], self.set_password, parent=self.menu_preference),
        add_menu('set_username', self.lang['menu_set_username'], self.set_username, parent=self.menu_preference),
        add_menu('set_startup', self.lang['menu_set_startup'], self.set_startup, parent=self.menu_preference),
        self.menu_preference.add(rumps.separator)

        # menu_select_language
        self.menu_select_language = self.app.menu['select_language']  # type: rumps.MenuItem

        g_set_lang = lambda lang: lambda _: self.set_language(lang)
        for k in LANGUAGE:
            add_menu(k, LANGUAGE[k]['l_this'], g_set_lang(k),
                     parent=self.menu_select_language)

        # update menus title.
        for k, v in self.menu.items():
            v['parent'][v['name']].title = v['title']
            del v['title']

    def set_menu_title(self, key, title):
        self.app.menu[key].title = title

    def callback_menu(self, name):
        try:
            common.log(self.callback_menu, 'Info', 'Click %s.' % name)
            menu = self.menu[name]
            menu['callback'](menu['object'])
        except:
            self.callback_exception()

    def callback_refresh(self, sender: rumps.Timer):
        try:
            battery_info = system_api.battery_info()
            if battery_info is not None:
                self.set_menu_title('view_percent',
                                    self.lang['view_percent'] % battery_info['percent'])

                self.set_menu_title('view_status',
                                    self.lang['view_status'] % (
                                        self.lang['status_charging'].get(battery_info['status'], self.lang['unknown'])))

                self.set_menu_title('view_remaining',
                                    self.lang['view_remaining'] % (
                                        (self.lang['view_remaining_time'] % battery_info['remaining'])
                                        if battery_info['remaining'] is not None else self.lang[
                                            'view_remaining_counting']))

                if battery_info['status'] == 'discharging' and (
                        battery_info['percent'] <= Config.low_battery_capacity or
                        (battery_info['remaining'] is not None and
                         battery_info['remaining'] <= Config.low_time_remaining)):
                    system_api.sleep(user=Config.username, pwd=Config.password)
        except:
            sender.stop()
            self.callback_exception()

    @staticmethod
    def callback_exception():
        exc = common.get_exception()
        common.log(Application.callback_exception, 'Error', exc)
        if osa_api.alert(Application.lang['title_crash'], Application.lang['description_crash']):
            Application.export_log()

    def set_low_battery_capacity(self, sender: rumps.MenuItem):
        content = osa_api.dialog_input(sender.title, self.lang['description_set_low_battery_capacity'],
                                       str(self.config.get('low_battery_capacity', '')))

        if isinstance(content, str) and content.isnumeric():
            Config.low_battery_capacity = int(content)
            Config.save()

    def set_low_time_remaining(self, sender: rumps.MenuItem):
        content = osa_api.dialog_input(sender.title, self.lang['description_set_low_time_remaining'],
                                       str(self.config.get('low_time_remaining', '')))
        if isinstance(content, str) and content.isnumeric():
            Config.low_time_remaining = int(content)
            Config.save()

    def set_username(self, sender: rumps.MenuItem):
        content = osa_api.dialog_input(sender.title, self.lang['description_set_username'],
                                       self.config.get('username', ''))
        if content is not None:
            Config.username = content
            Config.save()

    def set_password(self, sender: rumps.MenuItem):
        content = osa_api.dialog_input(sender.title, self.lang['description_set_password'],
                                       hidden=True)
        if content is not None:
            Config.password = content
            Config.save()

    def select_language(self, sender: rumps.MenuItem):
        items = []
        for k in LANGUAGE:
            items.append(LANGUAGE[k]['l_this'])

        index = osa_api.choose_from_list(sender.title, LANGUAGE['en']['description_select_language'], items)
        if index is not None:
            language = None
            description = items[index]
            for k, v in LANGUAGE.items():
                if description == v['l_this']:
                    language = k
                    break

            if language is not None:
                self.set_language(language)

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
        if mode is not None and mode != info['hibernatemode']:
            system_api.set_sleep_mode(mode, user=Config.username, pwd=Config.password)

    def sleep_now(self, sender: rumps.MenuItem):
        system_api.sleep(user=Config.username, pwd=Config.password)

    def switch_lid_sleep(self, sender: rumps.MenuItem):
        sender.state = not sender.state
        if sender.state:
            self.pd_caffeinate.start()
        else:
            self.pd_caffeinate.stop()

    def switch_idle_sleep(self, sender: rumps.MenuItem):
        sender.state = not sender.state
        if sender.state:
            self.pd_noidle.start()
        else:
            self.pd_noidle.stop()

    def about(self, sender: rumps.MenuItem):
        res = osa_api.dialog_input(sender.title, self.lang['description_about'] % CONST['version'],
                                   CONST['github_page'])
        if res == ':export log':
            self.export_log()
        elif res == CONST['github_page']:
            system_api.open_url(CONST['github_page'])

    def export_log(self):
        folder = osa_api.choose_folder(Application.lang['title_export_log'])
        if folder is not None:
            log = common.extract_log().replace(self.config['password'], CONST['pwd_hider'])
            with open('%s/%s' % (folder, 'SleeperX_log.txt'), 'w', encoding='utf8') as io:
                io.write(log)

    def quit(self, sender: rumps.MenuItem = None):
        self.pd_noidle.stop()
        self.pd_caffeinate.stop()
        rumps.quit_application()

    def t_check_update(self, sender: rumps.MenuItem = None):
        Thread(target=self.check_update, args=(sender,)).start()

    def check_update(self, sender):
        try:
            release = github.get_latest_release(CONST['author'], CONST['app_name'], timeout=5)
            common.log(self.check_update, 'Info', release)

            if common.compare_version(CONST['version'], release['tag_name']):
                rumps.notification(
                    self.lang['noti_update_version'] % release['name'],
                    self.lang['noti_update_time'] % release['published_at'],
                    release['body'],
                )

                if isinstance(sender, rumps.MenuItem):
                    if len(release['assets']) > 0:
                        system_api.open_url(release['assets'][0]['browser_download_url'])
                    else:
                        system_api.open_url('html_url')
            else:
                if isinstance(sender, rumps.MenuItem):
                    rumps.notification(sender.title, self.lang['noti_update_none'], self.lang['noti_update_star'])
        except:
            common.log(self.check_update, 'Warning', common.get_exception())
            if isinstance(sender, rumps.MenuItem):
                rumps.notification(sender.title, '', self.lang['noti_network_error'])

    def run(self):
        t_refresh = rumps.Timer(self.callback_refresh, 1)
        t_refresh.start()
        t_check_update = rumps.Timer(self.check_update, 86400)
        t_check_update.start()
        self.app.run()

    def restart(self):
        [_, path] = common.get_application_info()
        system_api.open_url(path, True)
        self.quit()

    def set_language(self, language):
        Config.language = language
        Config.save()
        self.restart()
