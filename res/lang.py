LANGUAGE = {
    'en': {
        'l_this': 'English',
        'unknown': 'unknown',

        'description_about':
            'SleeperX Version %s\n\n'
            'Auto sleep for hackintosh. \n'
            'Protect low battery capacity force shutdown.\n\n'
            'Develop by HsOjo.\n'
            'Below is the link with the project github page.',
        'description_set_password':
            'Set the administrator user password.\n'
            'It will use for execute sleep command.',
        'description_set_username':
            'Set the administrator user name.\n'
            'It will use for execute sleep command.\n'
            '(This is optional. Will use current user if empty.)',
        'description_set_low_time_remaining':
            'Set the low time remaining. (unit: minute)\n'
            'It will execute sleep command on this value and lower.\n'
            '(Just on status discharging valid.)',
        'description_set_low_battery_capacity':
            'Set the low battery capacity. (unit: percent)\n'
            'It will execute sleep command on this value and lower.\n'
            '(Just on status discharging valid.)',
        'description_set_language':
            'Select your language.',
        'description_crash':
            'Oops! Application(SleeperX) Crash!\n'
            'Will export log later. Send the log file to Developer, please.',
        'description_set_startup':
            'Do you want to set startup this app on login?\n'
            '(You can cancel it on `System Preferences` - `User or Group account` - `Login items`)',
        'description_set_sleep_mode':
            'mode0: by default on desktops. \n'
            'The system will not back memory up to persistent storage.\n'
            'The system must wake from the contents of mem-ory; the system will lose context on power loss. \n'
            '\n'
            'mode3: by default on portables. \n'
            'The system will store a copy of memory to persistent storage (the disk), and will power memory during sleep.\n'
            'The system will wake from memory, unless a power loss forces it to restore from hibernate image.\n'
            '\n'
            'mode25: The system will store a copy of memory to persistent storage (the disk), and will remove power to memory. \n'
            'The system will restore from disk image. \n'
            'If you want "hiberna-tion" - slower sleeps, slower wakes, and better battery life, you should use this setting.\n'
            '\n'
            'Current Mode: %s',

        'menu_sleep_now': 'Sleep Now',
        'menu_set_low_battery_capacity': 'Set Low Battery Capacity',
        'menu_set_low_time_remaining': 'Set Low Time Remaining',
        'menu_set_password': 'Set Admin Password',
        'menu_set_username': 'Set Admin Username (optional)',
        'menu_set_language': 'Set Language',
        'menu_set_startup': 'Set Login Startup',
        'menu_set_sleep_mode': 'Set Sleep Mode',
        'menu_check_update': 'Check Update',
        'menu_about': 'About',
        'menu_quit': 'Quit',

        'view_percent': 'Battery Capacity: %d%%',
        'view_status': 'Status: %s',
        'view_remaining': 'Remaining: %s',
        'view_remaining_time': '%d minutes',
        'view_remaining_counting': '(counting...)',

        'status_charging': {
            'not charging': 'not charging',
            'discharging': 'discharging',
            'charging': 'charging',
            'charged': 'charged',
        },

        'title_crash': 'Application Crash',
        'title_export_log': 'Export Log File',

        'noti_update_version': 'Found update: %s',
        'noti_update_time': 'Release Time: %s',
        'noti_update_none': 'Current is the newest version.',
        'noti_update_star': '(If you love this app, give me a star on github, thanks.)',
        'noti_network_error': 'The network maybe have some problem, please retry later.',

        'sleep_mode_0': 'mode 0',
        'sleep_mode_3': 'mode 3',
        'sleep_mode_25': 'mode 25',
    },
    'cn': {
        'l_this': '中文',
        'unknown': '未知',

        'description_about':
            'SleeperX 版本 %s\n\n'
            '在黑苹果实现自动睡眠功能。\n'
            '可以有效防止电池电量不足，导致直接断电关机。\n\n'
            '由HsOjo开发。\n'
            '以下是github页面链接。',
        'description_set_password':
            '设置管理员用户密码。\n'
            '将用于执行睡眠命令。',
        'description_set_username':
            '设置管理员用户名。\n'
            '将用于执行睡眠命令。\n'
            '(可选。如果为空则使用当前用户。)',
        'description_set_low_time_remaining':
            '设置电池时间临界值 (单位: 分钟)\n'
            '当电池时间不足该值，将执行睡眠命令。\n'
            '(只在非充电状态有效。)',
        'description_set_low_battery_capacity':
            '设置低电量临界值。 (单位: 百分比)\n'
            '当电量百分比不足该值，将执行睡眠命令。\n'
            '(只在非充电状态有效。)',
        'description_crash':
            '卧槽! SleeperX崩溃了!\n'
            '接下来将导出日志，请将日志提交给开发者，谢谢配合。',
        'description_set_startup':
            '你确定要将该应用添加到登陆启动项吗？\n'
            '(你可以在 `系统偏好设置` - `用户与群组` - `登陆项`取消。)',
        'description_set_sleep_mode':
            '模式0：默认在台式机上使用。\n'
            '系统不会将内存备份到持久存储（磁盘）。\n'
            '系统必须从内存的内容中唤醒；否则断电将丢失使用状态。\n'
            '\n'
            '模式3：默认在笔记本电脑上使用。\n'
            '系统会将内存的副本存储到持久存储（磁盘），并在睡眠期间为内存供电。\n'
            '系统将从内存中唤醒，除非断电强制它从休眠映像中恢复。\n'
            '\n'
            '模式25：系统将从磁盘映像还原。（休眠）\n'
            '系统将内存的副本存储到持久存储（磁盘），并将切断内存的电源。\n'
            '如果你想要“休眠”——睡眠会更慢，唤醒会更慢，但电池寿命越长，你应该使用这个设置。\n'
            '\n'
            '当前模式：%s',

        'menu_sleep_now': '立即睡眠',
        'menu_set_low_battery_capacity': '设置低电量临界值',
        'menu_set_low_time_remaining': '设置电池时间临界值',
        'menu_set_password': '设置管理员用户密码',
        'menu_set_username': '设置管理员用户名 (可选)',
        'menu_set_language': '设置语言',
        'menu_set_startup': '设置登陆启动',
        'menu_set_sleep_mode': '设置睡眠模式',
        'menu_check_update': '检查更新',
        'menu_about': '关于',
        'menu_quit': '退出',

        'view_percent': '剩余电量: %d%%',
        'view_status': '充电状态: %s',
        'view_remaining': '剩余时间: %s',
        'view_remaining_time': '%d 分钟',
        'view_remaining_counting': '(计算中...)',

        'status_charging': {
            'not charging': '未在充电',
            'discharging': '正在放电',
            'charging': '正在充电',
            'charged': '已充满',
        },

        'title_crash': '应用崩溃',
        'title_export_log': '导出日志文件',

        'noti_update_version': '发现新版本: %s',
        'noti_update_time': '发布时间: %s',
        'noti_update_none': '当前已是最新版本。',
        'noti_update_star': '（如果你喜欢这个应用，请在github给我个star，thanks。）',
        'noti_network_error': '网络出现问题，请稍后重试。',

        'sleep_mode_0': '模式0',
        'sleep_mode_3': '模式3',
        'sleep_mode_25': '模式25',
    },
}
