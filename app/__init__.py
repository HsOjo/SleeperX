import time
from threading import Thread

import rumps

from app import common
from .base.application import ApplicationBase
from .config import Config
from .res.const import Const
from .res.language import load_language, LANGUAGES
from .res.language.english import English
from .util import system_api, osa_api, github
from .util.process_daemon import ProcessDaemon
from .view.application import ApplicationView


class Application(ApplicationBase, ApplicationView):
    def __init__(self):
        ApplicationView.__init__(self)
        ApplicationBase.__init__(self, Config)

        self.menu_cat = []
        self.init_menu()

        self.is_admin = system_api.check_admin()
        self.pd_noidle = ProcessDaemon('/usr/bin/pmset noidle')

        self.battery_status = None  # type: dict
        self.lid_stat = None  # type: bool

        # System sleep time. (from pmset)
        self.sleep_idle_time = -1
        # System idle time.
        self.idle_time = -1
        # Refresh last time. (check sleep by twice refresh)
        self.refresh_time = None

        self.cancel_disable_idle_sleep_time = None
        self.cancel_disable_lid_sleep_time = None

    def bind_menu_callback(self):
        # menu_application
        self.set_menu_callback(self.menu_sleep_now, callback=lambda _: self.sleep())
        self.set_menu_callback(self.menu_display_sleep_now, callback=lambda _: system_api.sleep(display_only=True))
        self.set_menu_callback(self.menu_disable_idle_sleep, callback=lambda sender: self.set_idle_sleep(sender.state))
        self.set_menu_callback(self.menu_disable_lid_sleep, callback=self.callback_menu_disable_lid_sleep)
        self.set_menu_callback(self.menu_select_language, callback=lambda _: self.select_language())
        self.set_menu_callback(self.menu_check_update, callback=(
            lambda sender: Thread(target=self.check_update, args=(sender,)).start()
        ))
        self.set_menu_callback(self.menu_about, callback=lambda _: self.about())
        self.set_menu_callback(self.menu_quit, callback=lambda _: self.quit())

        # menu_preferences
        self.set_menu_callback(self.menu_set_startup, callback=lambda _: self.set_startup())
        self.set_menu_callback(self.menu_set_low_battery_capacity, callback=(
            self.generate_callback_config_input(
                'low_battery_capacity', 'description_set_low_battery_capacity', to_int=True)
        ))
        self.set_menu_callback(self.menu_set_low_time_remaining, callback=(
            self.generate_callback_config_input(
                'low_time_remaining', 'description_set_low_time_remaining', to_int=True)
        ))
        self.set_menu_callback(self.menu_disable_idle_sleep_in_charging,
                               callback=self.generate_callback_switch_config('disable_idle_sleep_in_charging'))
        self.set_menu_callback(self.menu_disable_lid_sleep_in_charging,
                               callback=self.generate_callback_switch_config('disable_lid_sleep_in_charging'))
        self.set_menu_callback(self.menu_screen_save_on_lid,
                               callback=self.generate_callback_switch_config('screen_save_on_lid'))
        self.set_menu_callback(self.menu_short_time_cancel_screen_save,
                               callback=self.generate_callback_switch_config('short_time_cancel_screen_save'))
        self.set_menu_callback(self.menu_set_username,
                               callback=self.generate_callback_config_input('username', 'description_set_username'))
        self.set_menu_callback(self.menu_set_password,
                               callback=self.generate_callback_config_input('password', 'description_set_password',
                                                                            hidden=True))

        # menu_advanced_options
        self.set_menu_callback(self.menu_low_battery_capacity_sleep,
                               callback=self.generate_callback_switch_config('low_battery_capacity_sleep'))
        self.set_menu_callback(self.menu_set_sleep_mode, callback=self.set_sleep_mode)
        self.set_menu_callback(self.menu_export_log, callback=lambda _: self.export_log())
        self.set_menu_callback(self.menu_clear_config, callback=self.clear_config)

        # menu_event_callback
        self.set_menu_callback(self.menu_set_idle_status_changed_event,
                               callback=self.generate_callback_config_input('event_idle_status_changed',
                                                                            'description_set_event', empty_state=True))
        self.set_menu_callback(self.menu_set_lid_status_changed_event,
                               callback=self.generate_callback_config_input('event_lid_status_changed',
                                                                            'description_set_event', empty_state=True))
        self.set_menu_callback(self.menu_set_charge_status_changed_event,
                               callback=self.generate_callback_config_input('event_charge_status_changed',
                                                                            'description_set_event', empty_state=True))
        self.set_menu_callback(self.menu_set_sleep_waked_up_event,
                               callback=self.generate_callback_config_input('event_sleep_waked_up',
                                                                            'description_set_event', empty_state=True))

    def add_menu_cancel_after_time(self, time_options: list, name, g_callback, parent):
        for to in time_options:
            if to == '-':
                self.add_menu('-', parent=parent)
            else:
                menu_name = '%s_cat_%d' % (name, to)
                self.add_menu(menu_name, callback=g_callback(to), parent=parent)
                self.menu_cat.append({'name': menu_name, 'time': to})

    def generate_callback_cat_idle(self, cancel_after_time):
        def callback(_):
            self.cancel_disable_idle_sleep_time = time.time() + cancel_after_time
            self.set_idle_sleep(False)

        return callback

    def generate_callback_cat_lid(self, cancel_after_time):
        def callback(_):
            self.cancel_disable_lid_sleep_time = time.time() + cancel_after_time
            self.set_lid_sleep(False)

        return callback

    def callback_menu_disable_lid_sleep(self, sender: rumps.MenuItem):
        if not self.set_lid_sleep(sender.state):
            self.message_box(sender.title, self.lang.description_unable_to_pmset)

    def inject_menu_value(self):
        # inject value to menu.
        self.menu_disable_idle_sleep_in_charging.state = self.config.disable_idle_sleep_in_charging
        self.menu_disable_lid_sleep_in_charging.state = self.config.disable_lid_sleep_in_charging
        self.menu_low_battery_capacity_sleep.state = self.config.low_battery_capacity_sleep
        self.menu_screen_save_on_lid.state = self.config.screen_save_on_lid
        self.menu_short_time_cancel_screen_save.state = self.config.short_time_cancel_screen_save

        [info, _] = system_api.sleep_info()
        self.menu_disable_lid_sleep.state = info.get('SleepDisabled', False)

        self.menu_set_lid_status_changed_event.state = self.config.event_lid_status_changed != ''
        self.menu_set_idle_status_changed_event.state = self.config.event_idle_status_changed != ''
        self.menu_set_charge_status_changed_event.state = self.config.event_charge_status_changed != ''
        self.menu_set_sleep_waked_up_event.state = self.config.event_sleep_waked_up != ''

    def refresh_menu_title(self):
        super().refresh_menu_title()

        for i in self.menu_cat:
            item = self.menu[i['name']]  # type: dict
            menu = item['object']  # type: rumps.MenuItem
            menu.title = self.lang.menu_ex_cancel_after_time % (self.time_convert(i['time']))

    def init_menu(self):
        self.setup_menus()
        self.inject_menus()

        self.generate_languages_menu(self.menu_select_language)

        self.add_menu_cancel_after_time(
            Const.time_options, 'idle', self.generate_callback_cat_idle, self.menu_disable_idle_sleep)
        self.add_menu_cancel_after_time(
            Const.time_options, 'lid', self.generate_callback_cat_lid, self.menu_disable_lid_sleep)

        self.bind_menu_callback()
        self.refresh_menu_title()
        self.inject_menu_value()

    def admin_exec(self, command):
        code = -1

        if self.config.username != '':
            code, out, err = osa_api.run_as_admin(command, self.config.password, self.config.username,
                                                  timeout=self.config.process_timeout)
        else:
            if self.is_admin:
                code, out, err = system_api.sudo(command, self.config.password, timeout=self.config.process_timeout)
                common.log(self.admin_exec, 'Info', {'command': command, 'status': code, 'output': out, 'error': err})

        if code != 0:
            return False

        return True

    def refresh_battery_status_view(self):
        self.set_menu_title(
            'view_percent', self.lang.view_percent % self.battery_status['percent'])

        self.set_menu_title(
            'view_status', self.lang.view_status % (
                self.lang.status_charging.get(self.battery_status['status'], self.lang.unknown)))

        self.set_menu_title(
            'view_remaining', self.lang.view_remaining % (
                self.time_convert(self.battery_status['remaining'] * 60).lower()
                if self.battery_status['remaining'] is not None else self.lang.view_remaining_counting))

    def refresh_sleep_idle_time(self):
        [info, note] = system_api.sleep_info()
        if 'prevented' not in note.get('sleep', ''):
            self.sleep_idle_time = info.get('sleep', 0) * 60
        else:
            self.sleep_idle_time = -1

    def callback_refresh(self, sender: rumps.Timer):
        try:
            # check long time no refresh sleep.
            refresh_time = time.time()
            if self.refresh_time is not None:
                sleep_time = refresh_time - self.refresh_time
                if sleep_time >= Const.check_sleep_time:
                    idle_time = system_api.get_hid_idle_time()
                    if idle_time >= Const.check_sleep_time:
                        self.callback_sleep_waked_up(sleep_time)
            self.refresh_time = refresh_time

            # cancel after time refresh.
            if self.cancel_disable_idle_sleep_time is not None:
                time_remain = self.cancel_disable_idle_sleep_time - time.time()
                if time_remain <= 0:
                    self.set_idle_sleep(True)
                else:
                    self.menu_disable_idle_sleep.title = '%s - %s' % (
                        self.lang.menu_disable_idle_sleep, self.lang.menu_ex_cancel_after_time % (
                            self.time_convert(time_remain)
                        ))
            if self.cancel_disable_lid_sleep_time is not None:
                time_remain = self.cancel_disable_lid_sleep_time - time.time()
                if time_remain <= 0:
                    self.set_lid_sleep(True)
                else:
                    self.menu_disable_lid_sleep.title = '%s - %s' % (
                        self.lang.menu_disable_lid_sleep, self.lang.menu_ex_cancel_after_time % (
                            self.time_convert(time_remain)
                        ))

            e_lid = self.config.event_lid_status_changed != ''
            e_idle = self.config.event_idle_status_changed != ''

            if self.menu_disable_lid_sleep.state or e_lid or e_idle:
                # check lid status
                lid_stat_prev = self.lid_stat
                self.lid_stat = system_api.check_lid()
                if self.lid_stat is not None:
                    if lid_stat_prev is None or lid_stat_prev != self.lid_stat:
                        self.callback_lid_status_changed(self.lid_stat, lid_stat_prev)

                # check idle sleep (on disable (lid) sleep)
                if not self.menu_disable_idle_sleep.state or e_idle:
                    self.refresh_sleep_idle_time()
                    if self.sleep_idle_time > 0 or e_idle:
                        idle_time = system_api.get_hid_idle_time()
                        if 0 < self.sleep_idle_time <= idle_time:
                            self.sleep()
                        if idle_time < self.idle_time:
                            if self.idle_time >= self.config.time_idle_event:
                                self.callback_idle_status_changed(self.idle_time)
                        self.idle_time = idle_time

            # check battery status
            battery_status_prev = self.battery_status
            self.battery_status = system_api.battery_status()
            if self.battery_status is not None:
                if battery_status_prev is None:
                    self.callback_charge_status_changed(self.battery_status['status'])
                else:
                    if battery_status_prev['status'] != self.battery_status['status']:
                        self.callback_charge_status_changed(
                            self.battery_status['status'], battery_status_prev['status'])

                self.refresh_battery_status_view()

                # low battery capacity sleep check
                if self.config.low_battery_capacity_sleep:
                    if self.battery_status['status'] == 'discharging':
                        low_battery_capacity = self.battery_status['percent'] <= self.config.low_battery_capacity

                        low_time_remaining = self.battery_status['remaining'] is not None \
                                             and self.battery_status['remaining'] <= self.config.low_time_remaining

                        if low_battery_capacity or low_time_remaining:
                            self.sleep()
        except:
            sender.stop()
            self.callback_exception()

    def event_trigger(self, source, params: dict, path_event: str):
        if path_event != '':
            params_pop = []
            for k, v in params.items():
                if type(v) not in [None.__class__, bool, int, float, str, list, dict]:
                    params_pop.append(k)
            for k in params_pop:
                params.pop(k)

            [stat, out, err] = common.execute(
                path_event, env={Const.app_env: common.to_json(params)}, sys_env=False,
                timeout=self.config.process_timeout)
            common.log(source, 'Event',
                       {'path': path_event, 'status': stat, 'output': out, 'error': err})

    def callback_idle_status_changed(self, idle_time: float):
        params = locals()

        self.event_trigger(self.callback_idle_status_changed, params, self.config.event_idle_status_changed)

    def callback_sleep_waked_up(self, sleep_time: float):
        params = locals()

        self.event_trigger(self.callback_sleep_waked_up, params, self.config.event_sleep_waked_up)

    def callback_lid_status_changed(self, status: bool, status_prev: bool = None):
        params = locals()

        common.log(self.callback_lid_status_changed, 'Info', 'from "%s" to "%s"' % (status_prev, status))
        if status:
            if self.config.screen_save_on_lid:
                if self.config.short_time_cancel_screen_save:
                    @common.wait_and_check(3, 0.5)
                    def check_lock():
                        return system_api.check_lid()

                    valid = check_lock()
                    if valid:
                        osa_api.screen_save()
                    else:
                        common.log('check_lock', 'Info', 'user cancel lock screen.')
                else:
                    osa_api.screen_save()

        self.event_trigger(self.callback_lid_status_changed, params, self.config.event_lid_status_changed)

    def callback_charge_status_changed(self, status: str, status_prev: str = None):
        params = locals()

        common.log(self.callback_charge_status_changed, 'Info', 'from "%s" to "%s"' % (status_prev, status))
        self.refresh_sleep_idle_time()
        if status == 'discharging':
            if self.config.disable_idle_sleep_in_charging:
                self.set_idle_sleep(True)
            if self.config.disable_lid_sleep_in_charging:
                self.set_lid_sleep(True)
        elif status_prev in [None, 'discharging'] and status in ['not charging', 'charging', 'finishing charge',
                                                                 'charged']:
            if self.config.disable_idle_sleep_in_charging:
                self.set_idle_sleep(False)
            if self.config.disable_lid_sleep_in_charging:
                self.set_lid_sleep(False)

        self.event_trigger(self.callback_charge_status_changed, params, self.config.event_charge_status_changed)

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
            system_api.set_sleep_mode(mode, self.admin_exec)

    def sleep(self):
        fix_idle_sleep = self.menu_disable_idle_sleep.state
        fix_lid_sleep = self.menu_disable_lid_sleep.state

        if fix_idle_sleep:
            self.set_idle_sleep(True)
        if fix_lid_sleep:
            self.set_lid_sleep(True)

        sleep_ready_time = 0
        sleep_begin_time = time.time()

        system_api.sleep()

        @common.wait_and_check(3600, 0.5)
        def check_ready():
            t = system_api.get_hid_idle_time()
            if t > 0.5:
                nonlocal sleep_ready_time
                sleep_ready_time = t
            return t > 0.5

        time.sleep(0.5)
        check_ready()

        # fix callback refresh.
        self.refresh_time = time.time()
        real_sleep_time = time.time() - sleep_begin_time - sleep_ready_time
        common.log(self.sleep, 'Info',
                   'sleep_ready_time: %.2fs, real_sleep_time: %.2fs' % (sleep_ready_time, real_sleep_time))

        if fix_idle_sleep:
            self.set_idle_sleep(False)
        if fix_lid_sleep:
            self.set_lid_sleep(False)

        is_real_sleep = real_sleep_time > 3
        if is_real_sleep:
            self.callback_sleep_waked_up(real_sleep_time)

        return is_real_sleep

    def set_lid_sleep(self, available):
        self.menu_disable_lid_sleep.state = not available
        if available:
            success = system_api.set_sleep_available(True, self.admin_exec)
            self.cancel_disable_lid_sleep_time = None
            self.menu_disable_lid_sleep.title = self.lang.menu_disable_lid_sleep
        else:
            success = system_api.set_sleep_available(False, self.admin_exec)

        if not success:
            [info, _] = system_api.sleep_info()
            self.menu_disable_lid_sleep.state = info.get('SleepDisabled', available)

        return success

    def set_idle_sleep(self, available):
        self.menu_disable_idle_sleep.state = not available
        if available:
            self.pd_noidle.stop()
            self.cancel_disable_idle_sleep_time = None
            self.menu_disable_idle_sleep.title = self.lang.menu_disable_idle_sleep
        else:
            self.pd_noidle.start()

    def time_convert(self, time: int) -> str:
        time = int(time)
        day = time // 86400
        time %= 86400
        hour = time // 3600
        time %= 3600
        minute = time // 60
        time %= 60
        second = time

        result = ''
        if day > 0:
            result += '%d%s' % (day, self.lang.time_days)
        if hour > 0:
            result += '%d%s' % (hour, self.lang.time_hours)
        if minute > 0:
            result += '%d%s' % (minute, self.lang.time_minutes)
        if second > 0 or result == '':
            result += '%d%s' % (second, self.lang.time_seconds)

        return result

    def about(self, welcome=False):
        res = osa_api.dialog_input(self.lang.menu_about if not welcome else self.lang.title_welcome,
                                   self.lang.description_about % Const.version, Const.github_page)

        if isinstance(res, str):
            res = res.strip().lower()

        if res == ':export log':
            self.export_log()
        elif res == ':check update':
            self.check_update(self.menu_check_update, True)
        elif res == ':restart':
            self.restart()
        elif res == ':debug':
            rumps.debug_mode(True)
        elif res == Const.github_page.lower() and not welcome:
            system_api.open_url(Const.github_page)

    def quit(self):
        self.pd_noidle.stop()
        [info, _] = system_api.sleep_info()
        if info.get('SleepDisabled', False):
            system_api.set_sleep_available(True, self.admin_exec)

        super().quit()

    def check_update(self, sender, test=False):
        try:
            release = github.get_latest_release(Const.author, Const.app_name, timeout=5)
            common.log(self.check_update, 'Info', release)

            if test or common.compare_version(Const.version, release['tag_name']):
                rumps.notification(
                    self.lang.noti_update_version % release['name'],
                    self.lang.noti_update_time % release['published_at'],
                    release['body'],
                )

                if sender == self.menu_check_update:
                    if len(release['assets']) > 0:
                        system_api.open_url(release['assets'][0]['browser_download_url'])
                    else:
                        system_api.open_url(release['html_url'])
            else:
                if sender == self.menu_check_update:
                    rumps.notification(sender.title, self.lang.noti_update_none, self.lang.noti_update_star)
        except:
            common.log(self.check_update, 'Warning', common.get_exception())
            if sender == self.menu_check_update:
                rumps.notification(sender.title, '', self.lang.noti_network_error)

    def welcome(self):
        self.about(True)
        self.select_language()

        self.message_box(self.lang.title_welcome, self.lang.description_welcome_why_need_admin)

        cancel_account = False

        if not self.is_admin:
            # set username
            menu_set_username = self.menu['set_username']
            if not menu_set_username['callback'](menu_set_username['object']) or self.config.username == '':
                cancel_account = True
        else:
            self.message_box(self.lang.title_welcome, self.lang.description_welcome_is_admin)

        if not cancel_account:
            # set password
            menu_set_password = self.menu['set_password']
            if not menu_set_password['callback'](menu_set_password['object']):
                cancel_account = True

        if cancel_account:
            self.message_box(self.lang.title_welcome, self.lang.description_welcome_tips_set_account)

        self.message_box(self.lang.title_welcome, self.lang.description_welcome_end)

        self.config.welcome = False
        self.config.save()

    def run(self):
        if self.config.welcome:
            self.welcome()

        t_refresh = rumps.Timer(self.callback_refresh, 1)
        t_refresh.start()

        super().run()

    def clear_config(self, sender: rumps.MenuItem):
        if osa_api.alert(sender.title, self.lang.description_clear_config):
            self.config.clear()
            if osa_api.alert(sender.title, self.lang.description_clear_config_restart):
                self.restart()
