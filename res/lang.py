LANGUAGE = {
    'en': {
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
            'Options: en,cn\n'
            '(Restart app need.)',
        'description_crash':
            'Oops! Application Crash!\n'
            'Submit the below message to issue, please.\n\n%s',
        'description_set_startup':
            'Do you want to set startup this app on login?\n'
            '(You can cancel it on `System Preferences` - `User or Group account` - `Login items`)',

        'menu_sleep_now': 'Sleep Now',
        'menu_set_low_battery_capacity': 'Set Low Battery Capacity',
        'menu_set_low_time_remaining': 'Set Low Time Remaining',
        'menu_set_password': 'Set Admin Password',
        'menu_set_username': 'Set Admin Username (optional)',
        'menu_set_language': 'Set Language',
        'menu_set_startup': 'Set Login Startup',
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

        'noti_update_version': 'Found update: %s',
        'noti_update_time': 'Release Time: %s',
        'noti_update_none': 'Current is the newest version.',
        'noti_update_star': '(If you love this app, give me a star on github, thanks.)',
    },
    'cn': {
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
        'description_set_language':
            '选项: en,cn\n'
            '(需要重启App。)',
        'description_crash':
            '卧槽! 程序崩溃了!\n'
            '请将以下消息提交到issues，谢谢配合。\n\n%s',
        'description_set_startup':
            '你确定要将该应用添加到登陆启动项吗？\n'
            '(你可以在 `系统偏好设置` - `用户与群组` - `登陆项`取消。)',

        'menu_sleep_now': '立即睡眠',
        'menu_set_low_battery_capacity': '设置低电量临界值',
        'menu_set_low_time_remaining': '设置电池时间临界值',
        'menu_set_password': '设置管理员用户密码',
        'menu_set_username': '设置管理员用户名 (可选)',
        'menu_set_language': '设置语言',
        'menu_set_startup': '设置登陆启动',
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

        'noti_update_version': '发现新版本: %s',
        'noti_update_time': '发布时间: %s',
        'noti_update_none': '当前已是最新版本。',
        'noti_update_star': '（如果你喜欢这个应用，请在github给我个star，thanks。）',
    },
}
