from . import Language


class English(Language):
    l_this = 'English'
    unknown = 'Unknown Str: (%s)'
    cancel = 'Cancel'
    ok = 'OK'
    description_about = '''SleeperX Version %s

Auto sleep for hackintosh. 
Protect low battery capacity force shutdown.

Auto disable sleep on use AC power.
And it can disable idle sleep or lid sleep!

Develop by HsOjo.
Below is the link with the project github page.'''
    description_set_password = '''Set the administrator user password.
It will use for execute sleep command.'''
    description_set_username = '''Set the administrator user name.
It will use for execute sleep command.
(This is optional. Will use current user if empty.)'''
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
    description_set_sleep_mode = '''mode0: by default on desktops. 
The system will not back memory up to persistent storage.
The system must wake from the contents of mem-ory; the system will lose context on power loss. 

mode3: by default on portables. 
The system will store a copy of memory to persistent storage (the disk), and will power memory during sleep.
The system will wake from memory, unless a power loss forces it to restore from hibernate image.

mode25: The system will store a copy of memory to persistent storage (the disk), and will remove power to memory. 
The system will restore from disk image. 
If you want "hiberna-tion" - slower sleeps, slower wakes, and better battery life, you should use this setting.

(Only test on macOS 10.14 successful, 10.13- old version maybe different.)

Current Mode: %s'''
    menu_sleep_now = 'Sleep Now'
    menu_display_sleep_now = 'Display Sleep Now'
    menu_disable_lid_sleep = 'Disable Lid Sleep'
    menu_disable_idle_sleep = 'Disable Idle Sleep'
    menu_disable_idle_sleep_in_charging = 'Disable Lid Sleep In Charging'
    menu_disable_lid_sleep_in_charging = 'Disable Idle Sleep In Charging'
    menu_preferences = 'Preferences'
    menu_advanced_options = 'Advanced Options'
    menu_lock_screen_on_lid = 'Lock Screen On Lid (In Disable Lid Sleep)'
    menu_low_battery_capacity_sleep = 'Low Battery Capacity Sleep (Hackintosh Feature)'
    menu_set_low_battery_capacity = 'Set Low Battery Capacity'
    menu_set_low_time_remaining = 'Set Low Time Remaining'
    menu_set_password = 'Set Admin Password'
    menu_set_username = 'Set Admin Username (Optional)'
    menu_select_language = 'Set Language'
    menu_set_startup = 'Set Login Startup'
    menu_set_sleep_mode = 'Set Sleep Mode'
    menu_check_update = 'Check Update'
    menu_about = 'About'
    menu_quit = 'Quit'
    view_percent = 'Battery Capacity: %d%%'
    view_status = 'Status: %s'
    view_remaining = 'Remaining: %s'
    view_remaining_time = '%d minutes'
    view_remaining_counting = '(counting...)'
    status_charging = {'not charging': 'not charging', 'discharging': 'discharging', 'charging': 'charging',
                       'finishing charge': 'finishing charge', 'charged': 'charged'}
    title_crash = 'Application Crash'
    title_export_log = 'Export Log File'
    noti_update_version = 'Found update: %s'
    noti_update_time = 'Release Time: %s'
    noti_update_none = 'Current is the newest version.'
    noti_update_star = '(If you love this app, give me a star on github, thanks.)'
    noti_network_error = 'The network maybe have some problem, please retry later.'
    sleep_mode_0 = 'mode 0'
    sleep_mode_3 = 'mode 3'
    sleep_mode_25 = 'mode 25'
