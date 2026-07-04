from app.res.const import Const
from . import Language


class English(Language):
    l_this = 'English'

    def unknown(self, key):
        return f'Unknown Str: ({key})'

    cancel = 'Cancel'
    ok = 'OK'

    time_days = ' Days '
    time_hours = ' Hours '
    time_minutes = ' Minutes '
    time_seconds = ' Seconds'

    description_about = f'''{Const.app_name} Version {Const.version}

Native macOS menubar power/sleep manager for Hackintosh users.

Developed by {Const.author}.

Open the GitHub project page?'''
    description_set_low_time_remaining = '''Set the low time remaining. (unit: minute)
It will execute sleep command on this value and lower.
(Just on status discharging valid.)'''
    description_set_low_battery_capacity = '''Set the low battery capacity. (unit: percent)
It will execute sleep command on this value and lower.
(Just on status discharging valid.)'''
    description_select_language = 'Select your language.'
    description_crash = '''Oops! Application Crash!
The log will be opened for viewing. Send the log file to the Developer, please.'''
    description_set_startup = '''Do you want to launch this app on login?
(This creates a per-user LaunchAgent. Toggle it off here to remove it.)'''
    def description_set_sleep_mode(self, current):
        return f'''mode 0: by default on desktops.
The system will not back memory up to persistent storage.
The system must wake from the contents of memory; the system will lose context on power loss.

mode 3: by default on portables.
The system will store a copy of memory to persistent storage (the disk), and will power memory during sleep.
The system will wake from memory, unless a power loss forces it to restore from hibernate image.

mode 25: The system will store a copy of memory to persistent storage (the disk), and will remove power to memory.
The system will restore from disk image.
If you want "hibernation" - slower sleeps, slower wakes, and better battery life, you should use this setting.

Current Mode: {current}'''
    description_unable_to_pmset = '''Unable to change "Power Management Settings"!

This feature requires the privileged helper to be installed first. Please install
it via Preferences - Advanced Options - Install Privileged Helper.

You can view the log (Preferences - Advanced Options) and open an issue.'''
    description_install_helper = '''SleeperX needs to install a privileged helper to change
"Power Management Settings" (Disable Lid Sleep / Sleep Mode).

You will be asked for your administrator password once. The password is NOT
stored anywhere. Install now?'''
    description_uninstall_helper = '''Remove the privileged helper (LaunchDaemon)?
You will be asked for your administrator password once.'''
    description_clear_config = '''This action will delete config file, Do it now?'''
    description_clear_config_restart = '''Config file is deleted now, please restart the application.'''
    description_welcome = f'''Welcome to {Const.app_name}!

This menu-bar tool manages power/sleep for Hackintosh.
The welcome flow will offer to install a privileged helper (one administrator
prompt, no stored password); you can also install it later from Preferences -
Advanced Options.

Note: this app is unsigned. If macOS blocks it, right-click the app and choose
"Open" once.'''

    menu_sleep_now = 'Sleep Now'
    menu_display_sleep_now = 'Display Sleep Now'
    menu_disable_lid_sleep = 'Disable Lid Sleep'
    menu_disable_idle_sleep = 'Disable Idle Sleep'
    menu_disable_idle_sleep_in_charging = 'Disable Idle Sleep In Charging'
    menu_disable_lid_sleep_in_charging = 'Disable Lid Sleep In Charging'
    menu_preferences = 'Preferences'
    menu_advanced_options = 'Advanced Options'
    menu_low_battery_capacity_sleep = 'Low Battery Capacity Sleep (Hackintosh Feature)'
    menu_set_low_battery_capacity = 'Set Low Battery Capacity'
    menu_set_low_time_remaining = 'Set Low Time Remaining'
    menu_select_language = 'Set Language'
    menu_set_startup = 'Set Login Startup'
    menu_set_sleep_mode = 'Set Sleep Mode'
    menu_install_helper = 'Install Privileged Helper'
    menu_uninstall_helper = 'Uninstall Privileged Helper'
    menu_check_update = 'Check Update'
    menu_clear_config = 'Clear Config'
    menu_view_log = 'View Log'
    menu_about = 'About'
    menu_quit = 'Quit'
    menu_cancel_after = 'Cancel After'

    def menu_ex_cancel_after_time(self, duration):
        return f'Cancel After {duration}'

    def view_percent(self, percent):
        return f'Battery Capacity: {percent}%'

    def view_status(self, status):
        return f'Status: {status}'

    def view_remaining(self, remaining):
        return f'Remaining: {remaining}'

    view_remaining_counting = '(counting...)'

    status_charging = {'not charging': 'not charging', 'discharging': 'discharging', 'charging': 'charging',
                       'finishing charge': 'finishing charge', 'charged': 'charged'}

    title_crash = 'Application Crash'
    title_welcome = 'Welcome'

    def noti_update_version(self, version):
        return f'Found update: {version}'

    def noti_update_time(self, release_time):
        return f'Release Time: {release_time}'
    noti_update_none = 'Current is the newest version.'
    noti_update_star = '(If you love this app, give me a star on GitHub, thanks.)'
    noti_network_error = 'The network maybe have some problem, please retry later.'
    noti_checking_update = 'Checking for updates...'

    sleep_mode_0 = 'mode 0'
    sleep_mode_3 = 'mode 3'
    sleep_mode_25 = 'mode 25'
