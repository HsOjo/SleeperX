from threading import Thread

import rumps

import common
from res.const import Const
from res.language import load_language, LANGUAGES
from util import osa_api, system_api, github
from .config import Config
from .process_daemon import ProcessDaemon


class Application:
    def __init__(self):
        common.log('app_init', 'Info', 'version: %s' % Const.version)

        Config.load()

        self.lang = load_language(Config.language)

        self.app = rumps.App(Const.app_name, quit_button=None)

        self.pd_noidle = ProcessDaemon('/usr/bin/pmset noidle')

        self.menu = {}
        self.menu_preference = None  # type: rumps.MenuItem
        self.menu_advanced_options = None  # type: rumps.MenuItem
        self.menu_select_language = None  # type: rumps.MenuItem
        self.menu_disable_idle_sleep = None  # type: rumps.MenuItem
        self.menu_disable_lid_sleep = None  # type: rumps.MenuItem
        self.menu_disable_idle_sleep_in_charging = None  # type: rumps.MenuItem
        self.menu_disable_lid_sleep_in_charging = None  # type: rumps.MenuItem

        self.init_menu()
        self.battery_info = None  # type: dict

    def init_menu(self):
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
            add_menu('sleep_now', self.lang.menu_sleep_now, self.sleep_now),
            add_menu('display_sleep_now', self.lang.menu_display_sleep_now, self.display_sleep_now),
            rumps.separator,
            add_menu('disable_lid_sleep', self.lang.menu_disable_lid_sleep, self.switch_lid_sleep),
            add_menu('disable_idle_sleep', self.lang.menu_disable_idle_sleep, self.switch_idle_sleep),
            rumps.separator,
            add_menu('preference', self.lang.menu_preference),
            add_menu('select_language', self.lang.menu_select_language, self.select_language),
            rumps.separator,
            add_menu('check_update', self.lang.menu_check_update, self.t_check_update),
            add_menu('about', self.lang.menu_about, self.about),
            rumps.separator,
            add_menu('quit', self.lang.menu_quit, self.quit),
        ]

        self.menu_preference = self.app.menu['preference']
        self.menu_select_language = self.app.menu['select_language']
        self.menu_disable_idle_sleep = self.app.menu['disable_idle_sleep']
        self.menu_disable_lid_sleep = self.app.menu['disable_lid_sleep']

        # menu_preference
        add_menu('set_startup', self.lang.menu_set_startup, self.set_startup, parent=self.menu_preference)
        self.menu_preference.add(rumps.separator)
        add_menu('set_low_battery_capacity', self.lang.menu_set_low_battery_capacity,
                 self.set_low_battery_capacity, parent=self.menu_preference)
        add_menu('set_low_time_remaining', self.lang.menu_set_low_time_remaining, self.set_low_time_remaining,
                 parent=self.menu_preference)
        self.menu_preference.add(rumps.separator)
        self.menu_disable_idle_sleep_in_charging = add_menu('disable_idle_sleep_in_charging',
                                                            self.lang.menu_disable_idle_sleep_in_charging,
                                                            self.switch_idle_sleep_in_charging,
                                                            parent=self.menu_preference)
        self.menu_disable_lid_sleep_in_charging = add_menu('disable_lid_sleep_in_charging',
                                                           self.lang.menu_disable_lid_sleep_in_charging,
                                                           self.switch_lid_sleep_in_charging,
                                                           parent=self.menu_preference)
        self.menu_preference.add(rumps.separator)
        add_menu('set_password', self.lang.menu_set_password, self.set_password, parent=self.menu_preference)
        self.menu_preference.add(rumps.separator)
        self.menu_advanced_options = add_menu('advanced_options', self.lang.menu_advanced_options,
                                              parent=self.menu_preference)

        # menu_select_language
        g_set_lang = lambda lang: lambda _: self.set_language(lang)
        for k in LANGUAGES:
            add_menu(k, LANGUAGES[k].l_this, g_set_lang(k),
                     parent=self.menu_select_language)

        # menu_advanced_options
        add_menu('set_sleep_mode', self.lang.menu_set_sleep_mode, self.set_sleep_mode,
                 parent=self.menu_advanced_options)
        self.menu_advanced_options.add(rumps.separator)
        add_menu('set_username', self.lang.menu_set_username, self.set_username, parent=self.menu_advanced_options)

        # update menus title.
        for k, v in self.menu.items():
            v['parent'][v['name']].title = v['title']
            del v['title']

        # inject value to menu.
        self.menu_disable_idle_sleep_in_charging.state = Config.disable_idle_sleep_in_charging
        self.menu_disable_lid_sleep_in_charging.state = Config.disable_lid_sleep_in_charging

    @property
    def _admin_account(self):
        return dict(user=Config.username, pwd=Config.password)

    def set_menu_title(self, key, title):
        self.app.menu[key].title = title

    def refresh_view(self):
        self.set_menu_title('view_percent',
                            self.lang.view_percent % self.battery_info['percent'])

        self.set_menu_title('view_status',
                            self.lang.view_status % (
                                self.lang.status_charging.get(self.battery_info['status'], self.lang.unknown)))

        self.set_menu_title('view_remaining',
                            self.lang.view_remaining % (
                                (self.lang.view_remaining_time % self.battery_info['remaining'])
                                if self.battery_info[
                                       'remaining'] is not None else self.lang.view_remaining_counting))

    def callback_menu(self, name):
        try:
            common.log(self.callback_menu, 'Info', 'Click %s.' % name)
            menu = self.menu[name]
            menu['callback'](menu['object'])
        except:
            self.callback_exception()

    def callback_refresh(self, sender: rumps.Timer):
        try:
            battery_info_prev = self.battery_info
            self.battery_info = system_api.battery_info()
            if self.battery_info is not None:
                if battery_info_prev is None or battery_info_prev['status'] != self.battery_info['status']:
                    if battery_info_prev is not None:
                        self.callback_status_change(self.battery_info['status'], battery_info_prev['status'])
                    else:
                        self.callback_status_change(self.battery_info['status'])

                self.refresh_view()
                if self.battery_info['status'] == 'discharging' and (
                        self.battery_info['percent'] <= Config.low_battery_capacity or
                        (self.battery_info['remaining'] is not None and
                         self.battery_info['remaining'] <= Config.low_time_remaining)):
                    system_api.sleep()
        except:
            sender.stop()
            self.callback_exception()

    def callback_status_change(self, status, status_prev=None):
        if status == 'discharging':
            if Config.disable_idle_sleep_in_charging:
                self.set_idle_sleep(False)
            if Config.disable_lid_sleep_in_charging:
                self.set_lid_sleep(False)
        elif status == 'charging' or status == 'charged':
            if Config.disable_idle_sleep_in_charging:
                self.set_idle_sleep(True)
            if Config.disable_lid_sleep_in_charging:
                self.set_lid_sleep(True)

    def callback_exception(self):
        exc = common.get_exception()
        common.log(self.callback_exception, 'Error', exc)
        if osa_api.alert(self.lang.title_crash, self.lang.description_crash):
            Application.export_log()

    def set_low_battery_capacity(self, sender: rumps.MenuItem):
        content = osa_api.dialog_input(sender.title, self.lang.description_set_low_battery_capacity,
                                       str(Config.low_battery_capacity))

        if isinstance(content, str) and content.isnumeric():
            Config.low_battery_capacity = int(content)
            Config.save()

    def set_low_time_remaining(self, sender: rumps.MenuItem):
        content = osa_api.dialog_input(sender.title, self.lang.description_set_low_time_remaining,
                                       str(Config.low_time_remaining))
        if isinstance(content, str) and content.isnumeric():
            Config.low_time_remaining = int(content)
            Config.save()

    def set_username(self, sender: rumps.MenuItem):
        content = osa_api.dialog_input(sender.title, self.lang.description_set_username,
                                       Config.username)
        if content is not None:
            Config.username = content
            Config.save()

    def set_password(self, sender: rumps.MenuItem):
        content = osa_api.dialog_input(sender.title, self.lang.description_set_password,
                                       hidden=True)
        if content is not None:
            Config.password = content
            Config.save()

    def select_language(self, sender: rumps.MenuItem):
        items = []
        for k in LANGUAGES:
            items.append(LANGUAGES[k].l_this)

        index = osa_api.choose_from_list(sender.title, LANGUAGES['en'].description_select_language, items)
        if index is not None:
            language = None
            description = items[index]
            for k, v in LANGUAGES.items():
                if description == v['l_this']:
                    language = k
                    break

            if language is not None:
                self.set_language(language)

    def set_startup(self, sender: rumps.MenuItem):
        res = osa_api.alert(sender.title, self.lang.description_set_startup)
        if res:
            osa_api.set_login_startup(*common.get_application_info())

    def set_sleep_mode(self, sender: rumps.MenuItem):
        [info, _] = system_api.sleep_info()
        items = [self.lang.sleep_mode_0, self.lang.sleep_mode_3, self.lang.sleep_mode_25]
        items_value = {
            0: 0,
            1: 3,
            2: 25,
        }
        default = None
        for k, v in items_value.items():
            if v == info['hibernatemode']:
                default = k
        res = osa_api.dialog_select(sender.title, self.lang.description_set_sleep_mode % info['hibernatemode'],
                                    items, default)
        mode = items_value.get(res)
        if mode is not None and mode != info['hibernatemode']:
            system_api.set_sleep_mode(mode, **self._admin_account)

    def sleep_now(self, sender: rumps.MenuItem):
        system_api.sleep()

    def display_sleep_now(self, sender: rumps.MenuItem):
        system_api.sleep(True)

    def switch_lid_sleep(self, sender: rumps.MenuItem):
        self.set_lid_sleep(not sender.state)

    def switch_idle_sleep(self, sender: rumps.MenuItem):
        self.set_idle_sleep(not sender.state)

    def set_lid_sleep(self, available):
        self.menu_disable_lid_sleep.state = available
        if available:
            system_api.set_sleep_available(False, **self._admin_account)
        else:
            system_api.set_sleep_available(True, **self._admin_account)

    def set_idle_sleep(self, available):
        self.menu_disable_idle_sleep.state = available
        if available:
            self.pd_noidle.start()
        else:
            self.pd_noidle.stop()

    def switch_idle_sleep_in_charging(self, sender: rumps.MenuItem):
        sender.state = not sender.state
        Config.disable_idle_sleep_in_charging = bool(sender.state)
        Config.save()

    def switch_lid_sleep_in_charging(self, sender: rumps.MenuItem):
        sender.state = not sender.state
        Config.disable_lid_sleep_in_charging = bool(sender.state)
        Config.save()

    def about(self, sender: rumps.MenuItem):
        res = osa_api.dialog_input(sender.title, self.lang.description_about % Const.version,
                                   Const.github_page)
        if res == ':export log':
            self.export_log()
        elif res == Const.github_page:
            system_api.open_url(Const.github_page)

    def export_log(self):
        folder = osa_api.choose_folder(self.lang.title_export_log)
        if folder is not None:
            log = common.extract_log().replace(Config.password, Const.pwd_hider)
            with open('%s/%s' % (folder, 'SleeperX_log.txt'), 'w', encoding='utf8') as io:
                io.write(log)

    def quit(self, sender: rumps.MenuItem = None):
        self.pd_noidle.stop()
        [info, _] = system_api.sleep_info()
        if info['SleepDisabled']:
            system_api.set_sleep_available(True, **self._admin_account)
        rumps.quit_application()

    def t_check_update(self, sender: rumps.MenuItem = None):
        Thread(target=self.check_update, args=(sender,)).start()

    def check_update(self, sender):
        try:
            release = github.get_latest_release(Const.author, Const.app_name, timeout=5)
            common.log(self.check_update, 'Info', release)

            if common.compare_version(Const.version, release['tag_name']):
                rumps.notification(
                    self.lang.noti_update_version % release['name'],
                    self.lang.noti_update_time % release['published_at'],
                    release['body'],
                )

                if isinstance(sender, rumps.MenuItem):
                    if len(release['assets']) > 0:
                        system_api.open_url(release['assets'][0]['browser_download_url'])
                    else:
                        system_api.open_url('html_url')
            else:
                if isinstance(sender, rumps.MenuItem):
                    rumps.notification(sender.title, self.lang.noti_update_none, self.lang.noti_update_star)
        except:
            common.log(self.check_update, 'Warning', common.get_exception())
            if isinstance(sender, rumps.MenuItem):
                rumps.notification(sender.title, '', self.lang.noti_network_error)

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
