from rumps import rumps

from app.base.view import ViewBase


class ApplicationView(ViewBase):
    def __init__(self):
        super().__init__()

        self.menu_view_percent = None  # type: rumps.MenuItem
        self.menu_view_status = None  # type: rumps.MenuItem
        self.menu_view_remaining = None  # type: rumps.MenuItem
        self.menu_sleep_now = None  # type: rumps.MenuItem
        self.menu_display_sleep_now = None  # type: rumps.MenuItem
        self.menu_disable_idle_sleep = None  # type: rumps.MenuItem
        self.menu_disable_lid_sleep = None  # type: rumps.MenuItem
        self.menu_preferences = None  # type: rumps.MenuItem
        self.menu_select_language = None  # type: rumps.MenuItem
        self.menu_check_update = None  # type: rumps.MenuItem
        self.menu_about = None  # type: rumps.MenuItem
        self.menu_quit = None  # type: rumps.MenuItem

        self.menu_set_startup = None  # type: rumps.MenuItem
        self.menu_set_low_battery_capacity = None  # type: rumps.MenuItem
        self.menu_set_low_time_remaining = None  # type: rumps.MenuItem
        self.menu_disable_idle_sleep_in_charging = None  # type: rumps.MenuItem
        self.menu_disable_lid_sleep_in_charging = None  # type: rumps.MenuItem
        self.menu_screen_save_on_lid = None  # type: rumps.MenuItem
        self.menu_short_time_cancel_screen_save = None  # type: rumps.MenuItem
        self.menu_set_username = None  # type: rumps.MenuItem
        self.menu_set_password = None  # type: rumps.MenuItem
        self.menu_event_callback = None  # type: rumps.MenuItem
        self.menu_advanced_options = None  # type: rumps.MenuItem

        self.menu_low_battery_capacity_sleep = None  # type: rumps.MenuItem
        self.menu_set_sleep_mode = None  # type: rumps.MenuItem
        self.menu_export_log = None  # type: rumps.MenuItem
        self.menu_clear_config = None  # type: rumps.MenuItem

        self.menu_set_idle_status_changed_event = None  # type: rumps.MenuItem
        self.menu_set_lid_status_changed_event = None  # type: rumps.MenuItem
        self.menu_set_charge_status_changed_event = None  # type: rumps.MenuItem
        self.menu_set_sleep_waked_up_event = None  # type: rumps.MenuItem

    def setup_menus(self):
        # menu_application
        self.add_menu('view_percent')
        self.add_menu('view_status')
        self.add_menu('view_remaining')
        self.add_menu('-')
        self.add_menu('sleep_now')
        self.add_menu('display_sleep_now')
        self.add_menu('-')
        self.add_menu('disable_idle_sleep')
        self.add_menu('disable_lid_sleep')
        self.add_menu('-')
        self.menu_preferences = self.add_menu('preferences', self.lang.menu_preferences)
        self.add_menu('select_language')
        self.add_menu('-')
        self.add_menu('check_update')
        self.add_menu('about')
        self.add_menu('-')
        self.add_menu('quit')
        # menu_application end

        # menu_preferences
        self.add_menu('set_startup', parent=self.menu_preferences)
        self.add_menu('-', parent=self.menu_preferences)
        self.add_menu('set_low_battery_capacity', parent=self.menu_preferences)
        self.add_menu('set_low_time_remaining', parent=self.menu_preferences)
        self.add_menu('-', parent=self.menu_preferences)
        self.add_menu('disable_idle_sleep_in_charging', parent=self.menu_preferences)
        self.add_menu('disable_lid_sleep_in_charging', parent=self.menu_preferences)
        self.add_menu('-', parent=self.menu_preferences)
        self.add_menu('screen_save_on_lid', parent=self.menu_preferences)
        self.add_menu('short_time_cancel_screen_save', parent=self.menu_preferences)
        self.add_menu('-', parent=self.menu_preferences)
        self.add_menu('set_username', parent=self.menu_preferences)
        self.add_menu('set_password', parent=self.menu_preferences)
        self.add_menu('-', parent=self.menu_preferences)
        self.menu_event_callback = self.add_menu('event_callback', parent=self.menu_preferences)
        self.add_menu('-', parent=self.menu_preferences)
        self.menu_advanced_options = self.add_menu('advanced_options', parent=self.menu_preferences)
        # menu_preferences end

        # menu_advanced_options
        self.add_menu('low_battery_capacity_sleep', parent=self.menu_advanced_options)
        self.add_menu('-', parent=self.menu_advanced_options)
        self.add_menu('set_sleep_mode', parent=self.menu_advanced_options)
        self.add_menu('-', parent=self.menu_advanced_options)
        self.add_menu('export_log', parent=self.menu_advanced_options)
        self.add_menu('-', parent=self.menu_advanced_options)
        self.add_menu('clear_config', parent=self.menu_advanced_options)
        # menu_advanced_options end

        # menu_event_callback
        self.add_menu('set_idle_status_changed_event', parent=self.menu_event_callback)
        self.add_menu('set_lid_status_changed_event', parent=self.menu_event_callback)
        self.add_menu('-', parent=self.menu_event_callback)
        self.add_menu('set_charge_status_changed_event', parent=self.menu_event_callback)
        self.add_menu('-', parent=self.menu_event_callback)
        self.add_menu('set_sleep_waked_up_event', parent=self.menu_event_callback)
        # menu_event_callback end
