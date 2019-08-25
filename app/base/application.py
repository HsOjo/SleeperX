import os
import sys

import rumps

from app import common
from app.res.const import Const
from app.res.language import LANGUAGES, load_language
from app.res.language.english import English
from app.util import system_api, osa_api


class ApplicationBase:
    def __init__(self, config_class):
        common.log('app_init', 'Info', 'version: %s' % Const.version, system_api.get_system_version())
        self.app = rumps.App(Const.app_name, quit_button=None)

        self.config = config_class()
        self.config.load()

        self.lang = load_language(self.config.language)  # type: English

        self.menu = {}

    def add_menu(self, name, title='', callback=None, parent=None):
        if parent is None:
            parent = self.app.menu

        if name == '-':
            parent.add(rumps.separator)
        else:
            if isinstance(name, rumps.MenuItem):
                menu = name
                name = menu.title  # type: str
            else:
                menu = rumps.MenuItem(name)
                parent.add(menu)

            menu.title = title

            item = {'object': menu, 'name': name, 'callback': None, 'parent': parent}
            self.menu[name] = item
            self.menu[id(menu)] = item
            self.set_menu_callback(name, callback)

            return menu

    def inject_menus(self):
        for k in self.menu:
            if isinstance(k, str):
                key = 'menu_%s' % k
                if hasattr(self, key):
                    setattr(self, key, self.menu[k]['object'])

    def set_menu_title(self, name, title):
        self.app.menu[name].title = title

    def set_menu_callback(self, key, callback=None):
        if not isinstance(key, str):
            key = id(key)

        menu = self.menu[key]
        menu_obj = menu['object']  # type: rumps.MenuItem
        if callback is None:
            menu_obj.set_callback(None)
        else:
            if menu['callback'] is None:
                menu_obj.set_callback(lambda _: self.callback_menu(menu['name']))
            menu['callback'] = callback

    def generate_callback_switch_config(self, key: str):
        """
        Generate switch config field state menu callback function.
        :param key:
        :return: function
        """

        def switch(sender: rumps.MenuItem):
            sender.state = not sender.state
            setattr(self.config, key, bool(sender.state))
            self.config.save()

        return switch

    def generate_callback_config_input(self, key, description, hidden=False, to_int=False, empty_state=False):
        """
        Generate config field input dialog menu callback function.
        """

        def set_input(sender: rumps.MenuItem):
            content = osa_api.dialog_input(sender.title, getattr(self.lang, description),
                                           str(getattr(self.config, key, '')), hidden=hidden)

            if content is not None:
                if to_int:
                    if isinstance(content, str) and content.isnumeric():
                        setattr(self.config, key, int(content))
                else:
                    setattr(self.config, key, content)

                if empty_state:
                    sender.state = content != ''

                self.config.save()
                return True

            return False

        return set_input

    def generate_languages_menu(self, parent):
        g_set_lang = lambda lang: lambda _: self.set_language(lang)
        for i, k in enumerate(LANGUAGES):
            if i > 0:
                self.add_menu('-', parent=parent)
            self.add_menu(k, LANGUAGES[k].l_this, g_set_lang(k), parent=parent)

    def refresh_menu_title(self):
        for k, v in self.menu.items():
            if 'menu_%s' % k in dir(self.lang):
                title = getattr(self.lang, 'menu_%s' % k)
                v['object'].title = title

    def callback_menu(self, name):
        try:
            common.log(self.callback_menu, 'Info', 'Click %s.' % name)
            menu = self.menu[name]
            menu['callback'](menu['object'])
        except:
            self.callback_exception()

    def callback_exception(self):
        exc = common.get_exception()
        common.log(self.callback_exception, 'Error', exc)
        if osa_api.alert(self.lang.title_crash, self.lang.description_crash):
            self.export_log()

    def message_box(self, title, description):
        return osa_api.dialog_select(title, description, [self.lang.ok])

    def run(self):
        self.app.icon = '%s/app/res/icon.png' % common.get_runtime_dir()
        self.app.run()

    def quit(self):
        rumps.quit_application()

    def restart(self):
        [_, path] = common.get_application_info()
        if path is not None:
            self.quit()
            system_api.open_url(path, True)
        else:
            # quick restart for debug.
            self.app.title = '\x00'
            self.app.icon = None

            path = common.runtime_path()
            if path is not None:
                os.system('%s %s' % (path, ' '.join(sys.argv)))

        rumps.quit_application()

    def export_log(self):
        folder = osa_api.choose_folder(self.lang.menu_export_log)
        if folder is not None:
            log = common.extract_log()
            err = common.extract_err()

            for f in self.config._protect_fields:
                v = getattr(self.config, f, '')
                if v != '':
                    log = log.replace(v, Const.protector)
                    err = err.replace(v, Const.protector)

            if log != '':
                with open('%s/%s' % (folder, '%s.log' % Const.app_name), 'w') as io:
                    io.write(log)

            if err != '':
                with open('%s/%s' % (folder, '%s.err' % Const.app_name), 'w') as io:
                    io.write(err)

    def set_language(self, language):
        self.lang = LANGUAGES[language]()
        self.refresh_menu_title()
        self.config.language = language
        self.config.save()

    def select_language(self):
        items = []
        for k in LANGUAGES:
            items.append(LANGUAGES[k].l_this)

        index = osa_api.choose_from_list(English.menu_select_language, English.description_select_language, items)
        if index is not None:
            language = None
            description = items[index]
            for k, v in LANGUAGES.items():
                if description == v.l_this:
                    language = k
                    break

            if language is not None:
                self.set_language(language)
                return True

        return False

    def set_startup(self):
        res = osa_api.alert(self.lang.menu_set_startup, self.lang.description_set_startup)
        if res:
            osa_api.set_login_startup(*common.get_application_info())
