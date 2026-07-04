"""Application controller: assembles the engine + platform layer and drives the
menubar UI. Implements the engine's UI port and handles all menu actions.

This object is plain Python; the NSObject bridging (target/action, app delegate
callbacks) lives in app_delegate.py and forwards here.
"""
from __future__ import annotations

import logging
import threading

from AppKit import NSApp, NSWorkspace
from Foundation import NSURL, NSOperationQueue, NSThread

from app.core.config import Config
from app.core.engine import Engine
from app.core import updater
from app.i18n import load_language, format_duration, format_countdown, map_locale, LANGUAGES
from app.res.const import Const
from app.ui import menu_model
from app.ui.statusbar import StatusBar

from app.platform.power import PowerSource
from app.platform.lid import LidSensor
from app.platform.idle import IdleSensor
from app.platform.sleep import SleepController
from app.platform.sleepwatch import SleepWatcher
from app.platform.privileged_client import PrivilegedClient
from app.platform.login_item import LoginItem
from app.platform.sysinfo import SystemInfo
from app.platform.dialogs import Dialogs
from app.platform.notifications import Notifier

log = logging.getLogger(__name__)


def _detect_language() -> str:
    try:
        from Foundation import NSLocale
        ident = NSLocale.preferredLanguages()[0]
        return map_locale(str(ident))
    except Exception:
        return 'en'


class Controller:
    def __init__(self, logger=None):
        self.log = logger or log

        self.config = Config()
        self.config.load(detect_language=_detect_language)
        self.lang = load_language(self.config.language)

        # Platform capabilities.
        self.power = PowerSource(self.log)
        self.lid = LidSensor(self.log)
        self.idle = IdleSensor()
        self.sleep_ctl = SleepController(self.log)
        self.sleep_watch = SleepWatcher(self.log)
        self.privileged = PrivilegedClient(self.log)
        self.login_item = LoginItem(self.log)
        self.sysinfo = SystemInfo(self.log)
        self.dialogs = Dialogs(self.lang, self.log)
        self.notifier = Notifier(self.log)

        self.engine = Engine(
            self.config, self.power, self.lid, self.idle, self.sleep_ctl,
            self.sleep_watch, self.privileged, self, self.log)

        self.statusbar = None  # set by set_target once the delegate exists
        self._last_battery = None

    # --------------------------------------------------------------- UI setup
    def attach_statusbar(self, target) -> None:
        self.statusbar = StatusBar(target)
        self.statusbar.set_icon(Const.icon_path)
        self.statusbar.set_on_menu_close(self.engine.tick)
        self.rebuild_menu()

    def rebuild_menu(self) -> None:
        state = {
            'idle_sleep_disabled': self.engine.idle_sleep_disabled,
            'lid_sleep_disabled': self.engine.lid_sleep_disabled,
            'startup': self.login_item.is_enabled(),
            'low_battery_capacity_sleep': self.config.low_battery_capacity_sleep,
            'disable_idle_sleep_in_charging': self.config.disable_idle_sleep_in_charging,
            'disable_lid_sleep_in_charging': self.config.disable_lid_sleep_in_charging,
        }
        model = menu_model.build_menu(self.lang, self.config.language, state)
        self.statusbar.build(model)
        if self._last_battery:
            self.set_battery_view(*self._last_battery)

    # --------------------------------------------------------------- lifecycle
    def start(self) -> None:
        self.engine.start()
        self._check_helper_version()
        if self.config.first_run:
            # Let the user pick the language before showing the welcome dialog.
            code = self._select_language()
            if code is not None:
                self._set_language(code)
            self._welcome()
            # Offer to install the privileged helper right after welcome, so the
            # user is never interrupted by an install prompt while using a feature.
            if not self.privileged.is_installed():
                self._install_helper()
            self.config.first_run = False
            self.config.save()

    def shutdown(self) -> None:
        try:
            self.engine.shutdown()
        finally:
            self.config.save()

    def tick(self) -> None:
        if self.statusbar is not None and self.statusbar.is_menu_open:
            return
        self.engine.tick()

    def _check_helper_version(self) -> None:
        def work():
            if not self.privileged.is_installed():
                return
            version = self.privileged.helper_version()
            if version and version != Const.version:
                self.log.info(f'Helper version mismatch ({version} != {Const.version}); reinstalling')
                if not self.privileged.install():
                    self._on_main(lambda: self.dialogs.alert(
                        self.lang.menu_install_helper,
                        self.lang.description_unable_to_pmset))

        threading.Thread(target=work, daemon=True).start()

    def _welcome(self) -> None:
        self.dialogs.info(self.lang.title_welcome, self.lang.description_welcome)

    def _on_main(self, block) -> None:
        """Run a block on the main thread (AppKit UI must happen there).

        Swallows Python exceptions to prevent PyObjC from turning them into an
        Objective-C abort while a UI update is running on the main queue.
        """
        def safe():
            try:
                block()
            except Exception:
                self.log.exception('UI update failed')

        if NSThread.isMainThread():
            safe()
        else:
            NSOperationQueue.mainQueue().addOperationWithBlock_(safe)

    # -------------------------------------------------------------- UI port
    def set_battery_view(self, percent, status, remaining) -> None:
        def _update():
            self._last_battery = (percent, status, remaining)
            if not self.statusbar:
                return
            self.statusbar.set_title('view_percent', self.lang.view_percent(percent))
            label = self.lang.status_charging.get(status) or status
            self.statusbar.set_title('view_status', self.lang.view_status(label))
            if remaining is None:
                rem = self.lang.view_remaining_counting
            else:
                rem = format_duration(self.lang, remaining).lower()
            self.statusbar.set_title('view_remaining', self.lang.view_remaining(rem))
        self._on_main(_update)

    def set_idle_sleep_disabled(self, disabled) -> None:
        self._on_main(lambda: self.statusbar.set_checked('disable_idle_sleep', disabled))

    def set_lid_sleep_disabled(self, disabled) -> None:
        self._on_main(lambda: self.statusbar.set_checked('disable_lid_sleep', disabled))

    def set_idle_cancel_countdown(self, seconds) -> None:
        self._on_main(lambda: (
            self._set_countdown('disable_idle_sleep', self.lang.menu_disable_idle_sleep, seconds),
            self._set_cancel_submenu('cancel_idle', seconds),
        ))

    def set_lid_cancel_countdown(self, seconds) -> None:
        self._on_main(lambda: (
            self._set_countdown('disable_lid_sleep', self.lang.menu_disable_lid_sleep, seconds),
            self._set_cancel_submenu('cancel_lid', seconds),
        ))

    def _set_countdown(self, key, base_title, seconds) -> None:
        if not self.statusbar:
            return
        self.statusbar.set_title(key, base_title)

    def _set_cancel_submenu(self, key, seconds) -> None:
        if not self.statusbar:
            return
        if seconds is None:
            self.statusbar.set_title(key, self.lang.menu_cancel_after)
        else:
            self.statusbar.set_title(
                key, f'{self.lang.menu_cancel_after} ({format_countdown(seconds)})')

    # ------------------------------------------------------------- menu actions
    def on_menu(self, key) -> None:
        try:
            self._dispatch(key)
        except Exception:
            self.log.exception(f'menu action failed: {key}')

    def _dispatch(self, key) -> None:
        if key == 'sleep_now':
            self.engine.action_sleep_now()
        elif key == 'display_sleep_now':
            self.engine.action_display_sleep()
        elif key == 'disable_idle_sleep':
            if self.engine.cancel_disable_idle_sleep_time is not None:
                self.engine.set_idle_sleep(True)
            else:
                self.engine.set_idle_sleep(self.engine.idle_sleep_disabled)
        elif key == 'disable_lid_sleep':
            self.log.info('menu: disable_lid_sleep clicked')
            self._toggle_lid_sleep_async()
        elif key.startswith('cancel_idle:'):
            if self.engine.cancel_disable_idle_sleep_time is not None:
                self.engine.set_idle_sleep(True)
            else:
                self.engine.schedule_cancel_idle(int(key.split(':', 1)[1]))
        elif key.startswith('cancel_lid:'):
            if self.engine.cancel_disable_lid_sleep_time is not None:
                threading.Thread(target=self.engine.set_lid_sleep, args=(True,), daemon=True).start()
            else:
                threading.Thread(
                    target=self.engine.schedule_cancel_lid,
                    args=(int(key.split(':', 1)[1]),), daemon=True).start()
        elif key == 'set_low_battery_capacity':
            self._edit_int('low_battery_capacity', 'description_set_low_battery_capacity')
        elif key == 'set_low_time_remaining':
            self._edit_int('low_time_remaining', 'description_set_low_time_remaining')
        elif key in ('disable_idle_sleep_in_charging', 'disable_lid_sleep_in_charging',
                     'low_battery_capacity_sleep'):
            self._toggle_config(key)
        elif key == 'set_sleep_mode':
            self._set_sleep_mode()
        elif key == 'install_helper':
            self._install_helper()
        elif key == 'uninstall_helper':
            self._uninstall_helper()
        elif key == 'view_log':
            self._view_log()
        elif key == 'clear_config':
            self._clear_config()
        elif key == 'set_startup':
            self._toggle_startup()
        elif key == 'select_language':
            self._select_language()
        elif key == 'check_update':
            threading.Thread(target=self._check_update, daemon=True).start()
        elif key == 'about':
            self._about()
        elif key == 'quit':
            NSApp().terminate_(None)

    def _edit_int(self, attr, desc_key) -> None:
        current = str(getattr(self.config, attr))
        menu_key = f'menu_{"set_low_battery_capacity" if attr == "low_battery_capacity" else "set_low_time_remaining"}'
        result = self.dialogs.input(getattr(self.lang, menu_key), getattr(self.lang, desc_key), current)
        if result is None:
            return
        try:
            value = int(result)
        except ValueError:
            return
        # Clamp to sensible ranges to avoid broken configs.
        if attr == 'low_battery_capacity':
            value = max(0, min(100, value))
        elif attr == 'low_time_remaining':
            value = max(0, value)
        setattr(self.config, attr, value)
        self.config.save()

    def _toggle_config(self, attr) -> None:
        value = not getattr(self.config, attr)
        setattr(self.config, attr, value)
        self.config.save()
        self.statusbar.set_checked(attr, value)

    def _toggle_lid_sleep_async(self) -> None:
        """Toggle lid sleep on a background thread to avoid freezing the menubar."""
        with self.engine._state_lock:
            cancel_active = self.engine.cancel_disable_lid_sleep_time is not None
            current_disabled = self.engine.lid_sleep_disabled
        # If a "cancel after X" timer is counting down, the main menu click means
        # "cancel the block right now" -> re-enable lid sleep (available=True).
        desired_disabled = False if cancel_active else not current_disabled
        available = not desired_disabled
        self.log.info(f'lid toggle: cancel_active={cancel_active}, current_disabled={current_disabled}, desired_disabled={desired_disabled}')

        def work():
            result = self.engine.set_lid_sleep(available)
            self.log.info(f'lid toggle: set_lid_sleep({available}) -> {result}')
            if not result:
                self._on_main(lambda: self.dialogs.alert(
                    self.lang.menu_disable_lid_sleep,
                    self.lang.description_unable_to_pmset))

        threading.Thread(target=work, daemon=True).start()

    def _set_sleep_mode(self) -> None:
        modes = [0, 3, 25]
        current = self.sysinfo.hibernate_mode()
        labels = [self.lang.sleep_mode_0, self.lang.sleep_mode_3, self.lang.sleep_mode_25]
        default = modes.index(current) if current in modes else None
        desc = self.lang.description_set_sleep_mode(current if current is not None else '?')
        index = self.dialogs.select(self.lang.menu_set_sleep_mode, desc, labels, default)
        if index is None:
            return
        mode = modes[index]
        if mode == current:
            return

        def work():
            if not self.engine.set_sleep_mode(mode):
                self._on_main(lambda: self.dialogs.alert(
                    self.lang.menu_set_sleep_mode,
                    self.lang.description_unable_to_pmset))

        threading.Thread(target=work, daemon=True).start()

    def _install_helper(self) -> None:
        if not self.dialogs.alert(self.lang.menu_install_helper,
                                  self.lang.description_install_helper):
            return

        def work():
            success = self.privileged.install()
            self._on_main(lambda: self._check_helper_version())
            if not success:
                self._on_main(lambda: self.dialogs.alert(
                    self.lang.menu_install_helper,
                    self.lang.description_unable_to_pmset))

        threading.Thread(target=work, daemon=True).start()

    def _uninstall_helper(self) -> None:
        if not self.dialogs.alert(self.lang.menu_uninstall_helper,
                                  self.lang.description_uninstall_helper):
            return

        def work():
            if not self.privileged.uninstall():
                self._on_main(lambda: self.dialogs.alert(
                    self.lang.menu_uninstall_helper,
                    self.lang.description_unable_to_pmset))

        threading.Thread(target=work, daemon=True).start()

    def _view_log(self) -> None:
        NSWorkspace.sharedWorkspace().openFile_(Const.log_path)

    def _clear_config(self) -> None:
        if not self.dialogs.alert(self.lang.menu_clear_config,
                                  self.lang.description_clear_config):
            return
        self.config.clear()
        self.dialogs.alert(self.lang.menu_clear_config,
                           self.lang.description_clear_config_restart)

    def _toggle_startup(self) -> None:
        if self.login_item.is_enabled():
            self.login_item.disable()
        else:
            self.login_item.enable()
        self.statusbar.set_checked('set_startup', self.login_item.is_enabled())

    def _select_language(self) -> None:
        code = self.dialogs.select_language(LANGUAGES, self.config.language)
        if code is not None:
            self._set_language(code)

    def _set_language(self, code) -> None:
        self.config.language = code
        self.config.save()
        self.lang = load_language(code)
        self.dialogs.i18n = self.lang
        self.rebuild_menu()

    def _about(self) -> None:
        if self.dialogs.alert(self.lang.menu_about, self.lang.description_about):
            NSWorkspace.sharedWorkspace().openURL_(
                NSURL.URLWithString_(Const.github_page))

    def _check_update(self) -> None:
        if self.statusbar is not None:
            self.statusbar.set_title('check_update', self.lang.noti_checking_update)
        threading.Thread(target=self._fetch_update, daemon=True).start()

    def _fetch_update(self) -> None:
        try:
            release, have_new = updater.check_update(timeout=5)
        except Exception:
            NSOperationQueue.mainQueue().addOperationWithBlock_(
                lambda: self._show_update_result(None, False))
            return
        NSOperationQueue.mainQueue().addOperationWithBlock_(
            lambda: self._show_update_result(release, have_new))

    def _show_update_result(self, release, have_new) -> None:
        if self.statusbar is not None:
            self.statusbar.set_title('check_update', self.lang.menu_check_update)
        if release is None:
            self.dialogs.info(
                self.lang.menu_check_update, self.lang.noti_network_error)
            return
        if have_new:
            title = self.lang.noti_update_version(release.tag_name)
            subtitle = self.lang.noti_update_time(release.published_at)
            self.notifier.notify(title, subtitle, release.body or '')
            message = (
                f'{subtitle}\n'
                f'{self.lang.noti_update_star}\n\n'
                f'{Const.releases_url}')
            self.dialogs.info(title, message)
            if release.download_url:
                NSWorkspace.sharedWorkspace().openURL_(
                    NSURL.URLWithString_(release.download_url))
        else:
            message = f'{self.lang.noti_update_none}\n{self.lang.noti_update_star}'
            self.dialogs.info(self.lang.menu_check_update, message)
