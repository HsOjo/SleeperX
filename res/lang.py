LANGUAGE = {
    'en': {
        'unknown': '未知',

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

        'menu_sleep_now': 'Sleep Now',
        'menu_set_low_battery_capacity': 'Set Low Battery Capacity',
        'menu_set_low_time_remaining': 'Set Low Time Remaining',
        'menu_set_password': 'Set Admin Password',
        'menu_set_username': 'Set Admin Username (optional)',
        'menu_set_language': 'Set Language',
        'menu_about': 'About',

        'view_percent': 'Battery Capacity: %d%%',
        'view_status': 'Status: %s',
        'view_remaining': 'Remaining: %s',
        'view_remaining_time': '%d minutes',
        'view_remaining_counting': '(counting...)',

        'status_charging': {
            'not charging': 'not charging',
            'discharging': 'discharging',
            'charging': 'charging',
        },

        'title_crash': 'Application Crash',
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

        'menu_sleep_now': '立即睡眠',
        'menu_set_low_battery_capacity': '设置低电量临界值',
        'menu_set_low_time_remaining': '设置电池时间临界值',
        'menu_set_password': '设置管理员用户密码',
        'menu_set_username': '设置管理员用户名 (可选)',
        'menu_set_language': '设置语言',
        'menu_about': '关于',

        'view_percent': '剩余电量: %d%%',
        'view_status': '充电状态: %s',
        'view_remaining': '剩余时间: %s',
        'view_remaining_time': '%d 分钟',
        'view_remaining_counting': '(计算中...)',

        'status_charging': {
            'not charging': '未在充电',
            'discharging': '正在放电',
            'charging': '正在充电',
        },

        'title_crash': '应用崩溃',
    },
}
