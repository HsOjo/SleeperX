from app.res.const import Const
from . import Language


class English(Language):
    l_this = 'English'
    unknown = 'Unknown Str: (%s)'
    cancel = 'Cancel'
    ok = 'OK'

    time_days = ' Days '
    time_hours = ' Hours '
    time_minutes = ' Minutes '
    time_seconds = ' Seconds'

    description_about = '''SleeperX Version %s

Auto sleep for hackintosh. 
Protect low battery capacity force shutdown.

Auto disable sleep on use AC power.
And it can disable idle sleep or lid sleep!

Develop by HsOjo.
Below is the link with the project GitHub page.'''
    description_set_password = '''Set the administrator user password.
It will use for execute change "Power Management Settings". (Disable Lid Sleep)'''
    description_set_username = '''Set the administrator username. (This username isn't full name! You can query it on "Terminal.app", login your admin user and input "whoami" on terminal.)
It will use for change "Power Management Settings". (Disable Lid Sleep)
(If current user is administrator then this is optional. Will use current username if empty.)'''
    description_set_low_time_remaining = '''Set the low time remaining. (unit: minute)
It will execute sleep command on this value and lower.
(Just on status discharging valid.)'''
    description_set_low_battery_capacity = '''Set the low battery capacity. (unit: percent)
It will execute sleep command on this value and lower.
(Just on status discharging valid.)'''
    description_select_language = 'Select your language.'
    description_crash = '''Oops! Application(SleeperX) Crash!
Will export log later. Send the log file to Developer, please.'''
    description_set_startup = '''Do you want to set startup this app on login?
(You can cancel it on `System Preferences` - `User or Group account` - `Login items`)'''
    description_set_sleep_mode = '''mode 0: by default on desktops. 
The system will not back memory up to persistent storage.
The system must wake from the contents of memory; the system will lose context on power loss. 

mode 3: by default on portables. 
The system will store a copy of memory to persistent storage (the disk), and will power memory during sleep.
The system will wake from memory, unless a power loss forces it to restore from hibernate image.

mode 25: The system will store a copy of memory to persistent storage (the disk), and will remove power to memory. 
The system will restore from disk image. 
If you want "hibernation" - slower sleeps, slower wakes, and better battery life, you should use this setting.

(Only test on macOS 10.14 successful, 10.13- old version maybe different.)

Current Mode: %s'''
    description_set_event = '''Input executable program path on here. If this event triggered, will execute this program.
Event parameter will passing through Environment. (JSON Format, key: %s)

More information can found on GitHub "doc/" folder. (such as examples.)''' % Const.app_env
    description_welcome_why_need_admin = '''You need to input your administrator account to grant privileges for SleeperX. Because SleeperX will change "Power Management Settings". (Disable Lid Sleep)'''
    description_welcome_is_admin = '''Current user is administrator, skiped the admin username setting. (If you want use other admin account work on SleeperX, You can set it later.)'''
    description_welcome_tips_set_account = '''You canceled admin account settings! Disable lid sleep will be invalid. (You can find admin account settings in preferences.)'''
    description_welcome_end = '''Excellent! Now SleeperX will be working.
Enjoy yourself!'''
    unable_to_pmset = '''Unable to change "Power Management Settings"!
Please check your admin account (username and password) is correct.

If admin account is correct, But always can't do this, You can try to export log (in "Preferences" - "Advanced Options"), and send to this project issues page.'''

    menu_sleep_now = 'Sleep Now'
    menu_display_sleep_now = 'Display Sleep Now'
    menu_disable_lid_sleep = 'Disable Lid Sleep'
    menu_disable_idle_sleep = 'Disable Idle Sleep'
    menu_disable_idle_sleep_in_charging = 'Disable Idle Sleep In Charging'
    menu_disable_lid_sleep_in_charging = 'Disable Lid Sleep In Charging'
    menu_preferences = 'Preferences'
    menu_advanced_options = 'Advanced Options'
    menu_event_callback = 'Event Callback'
    menu_set_idle_status_changed_event = 'Set Idle Status Changed Event'
    menu_set_lid_status_changed_event = 'Set Lid Status Changed Event'
    menu_set_charge_status_changed_event = 'Set Charge Status Changed Event'
    menu_set_sleep_waked_up_event = 'Set Sleep Waked Up Event'
    menu_screen_save_on_lid = 'ScreenSave On Lid (In Disable Lid Sleep)'
    menu_short_time_cancel_screen_save = 'Short Time Cancel ScreenSave (On Lid, 3 seconds Cancel)'
    menu_low_battery_capacity_sleep = 'Low Battery Capacity Sleep (Hackintosh Feature)'
    menu_set_low_battery_capacity = 'Set Low Battery Capacity'
    menu_set_low_time_remaining = 'Set Low Time Remaining'
    menu_set_username = 'Set Admin Username (Not Admin User Need)'
    menu_set_password = 'Set Admin Password'
    menu_select_language = 'Set Language'
    menu_set_startup = 'Set Login Startup'
    menu_set_sleep_mode = 'Set Sleep Mode'
    menu_check_update = 'Check Update'
    menu_clear_config = 'Clear Config'
    menu_export_log = 'Export Log File'
    menu_about = 'About'
    menu_quit = 'Quit'

    menu_ex_cancel_after_time = 'Cancel After %s'

    view_percent = 'Battery Capacity: %d%%'
    view_status = 'Status: %s'
    view_remaining = 'Remaining: %s'
    view_remaining_counting = '(counting...)'

    status_charging = {'not charging': 'not charging', 'discharging': 'discharging', 'charging': 'charging',
                       'finishing charge': 'finishing charge', 'charged': 'charged'}

    title_crash = 'Application Crash'
    title_welcome = 'Welcome'

    noti_update_version = 'Found update: %s'
    noti_update_time = 'Release Time: %s'
    noti_update_none = 'Current is the newest version.'
    noti_update_star = '(If you love this app, give me a star on GitHub, thanks.)'
    noti_network_error = 'The network maybe have some problem, please retry later.'

    sleep_mode_0 = 'mode 0'
    sleep_mode_3 = 'mode 3'
    sleep_mode_25 = 'mode 25'
