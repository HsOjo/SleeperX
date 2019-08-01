from .english import English


class Chinese(English):
    l_this = '中文'
    unknown = '未知内容: (%s)'
    cancel = '取消'
    ok = '确定'
    description_about = '''SleeperX 版本 %s

在黑苹果实现自动睡眠功能。
可以有效防止电池电量不足，导致直接断电关机。

在接通电源时，可以自动禁止睡眠。
并且可以随意关闭闲置睡眠或合盖睡眠。

由HsOjo开发。
以下是github页面链接。'''
    description_set_password = '''设置管理员用户密码。
将用于执行睡眠命令。'''
    description_set_username = '''设置管理员用户名。
将用于执行睡眠命令。
(可选。如果为空则使用当前用户。)'''
    description_set_low_time_remaining = '''设置电池时间临界值 (单位: 分钟)
当电池时间不足该值，将执行睡眠命令。
(只在非充电状态有效。)'''
    description_set_low_battery_capacity = '''设置低电量临界值。 (单位: 百分比)
当电量百分比不足该值，将执行睡眠命令。
(只在非充电状态有效。)'''
    description_crash = '''卧槽! SleeperX崩溃了!
接下来将导出日志，请将日志提交给开发者，谢谢配合。'''
    description_set_startup = '''你确定要将该应用添加到登陆启动项吗？
(你可以在 `系统偏好设置` - `用户与群组` - `登陆项`取消。)'''
    description_set_sleep_mode = '''模式0：默认在台式机上使用。
系统不会将内存备份到持久存储（磁盘）。
系统必须从内存的内容中唤醒；否则断电将丢失使用状态。

模式3：默认在笔记本电脑上使用。
系统会将内存的副本存储到持久存储（磁盘），并在睡眠期间为内存供电。
系统将从内存中唤醒，除非断电强制它从休眠映像中恢复。

模式25：系统将从磁盘映像还原。（休眠）
系统将内存的副本存储到持久存储（磁盘），并将切断内存的电源。
如果你想要“休眠”——睡眠会更慢，唤醒会更慢，但电池寿命越长，你应该使用这个设置。

(仅在macOS 10.14测试成功, 10.13以下的老版本情况会有所不同。)

当前模式：%s'''
    menu_sleep_now = '立即睡眠'
    menu_display_sleep_now = '立即关闭显示器'
    menu_disable_lid_sleep = '阻止合盖睡眠'
    menu_disable_idle_sleep = '阻止闲置睡眠'
    menu_disable_idle_sleep_in_charging = '在接通电源时阻止闲置睡眠'
    menu_disable_lid_sleep_in_charging = '在接通电源时阻止合盖睡眠'
    menu_preferences = '偏好设置'
    menu_advanced_options = '高级选项'
    menu_lock_screen_on_lid = '在合盖时锁屏（阻止合盖睡眠时使用）'
    menu_low_battery_capacity_sleep = '低电量睡眠（黑苹果特性）'
    menu_set_low_battery_capacity = '设置低电量临界值'
    menu_set_low_time_remaining = '设置续航时间临界值'
    menu_set_password = '设置管理员用户密码'
    menu_set_username = '设置管理员用户名 (可选)'
    menu_select_language = '设置语言'
    menu_set_startup = '设置登陆启动'
    menu_set_sleep_mode = '设置睡眠模式'
    menu_check_update = '检查更新'
    menu_about = '关于'
    menu_quit = '退出'
    view_percent = '剩余电量: %d%%'
    view_status = '充电状态: %s'
    view_remaining = '剩余时间: %s'
    view_remaining_time = '%d 分钟'
    view_remaining_counting = '(计算中...)'
    status_charging = {'not charging': '未在充电', 'discharging': '正在放电', 'charging': '正在充电',
                       'finishing charge': '即将充满', 'charged': '已充满'}
    title_crash = '应用崩溃'
    title_export_log = '导出日志文件'
    noti_update_version = '发现新版本: %s'
    noti_update_time = '发布时间: %s'
    noti_update_none = '当前已是最新版本。'
    noti_update_star = '（如果你喜欢这个应用，请在github给我个star，thanks。）'
    noti_network_error = '网络出现问题，请稍后重试。'
    sleep_mode_0 = '模式0'
    sleep_mode_3 = '模式3'
    sleep_mode_25 = '模式25'
