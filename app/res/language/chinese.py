from app.res.const import Const
from .english import English


class Chinese(English):
    l_this = '简体中文'
    unknown = '未知内容: (%s)'
    cancel = '取消'
    ok = '确定'

    time_days = '天'
    time_hours = '小时'
    time_minutes = '分钟'
    time_seconds = '秒'

    description_about = '''SleeperX 版本 %s

在Hackintosh下实现自动睡眠功能。
可以有效防止电池电量不足，导致直接断电关机。

在接通电源时，可以自动禁止睡眠。
并且可以随意关闭闲置睡眠或合盖睡眠。

由HsOjo开发。
以下是GitHub页面链接。'''
    description_set_password = '''设置管理员用户密码。
将用于执行更改“电源管理设置”。（阻止合盖睡眠）'''
    description_set_username = '''设置管理员用户名。（这里的用户名不是全名！您可以在“terminal.app”上查看，登录您的管理用户，并在终端上输入"whoami"。）
将用于执行更改“电源管理设置”。（阻止合盖睡眠）
(如果当前用户是管理员，可留空。如果为空，将使用当前用户名。)'''
    description_set_low_time_remaining = '''设置电池时间临界值 (单位: 分钟)
当电池时间不足该值，将执行睡眠命令。
(只在非充电状态有效。)'''
    description_set_low_battery_capacity = '''设置低电量临界值。 (单位: 百分比)
当电量百分比不足该值，将执行睡眠命令。
(只在非充电状态有效。)'''
    description_crash = '''卧槽! SleeperX崩溃了!
接下来将导出日志，请将日志提交给开发者，谢谢配合。'''
    description_set_startup = '''你确定要将该应用添加到登录启动项吗？
(你可以在 `系统偏好设置` - `用户与群组` - `登录项`取消。)'''
    description_set_sleep_mode = '''模式0：默认在台式机上使用。
系统不会将内存备份到持久存储（磁盘）。
系统必须从内存的内容中唤醒；否则断电将丢失使用状态。

模式3：默认在笔记本电脑上使用。
系统会将内存的副本存储到持久存储（磁盘），并在睡眠期间为内存供电。
系统将从内存中唤醒，除非断电强制它从休眠映像中恢复。

模式25：系统将从磁盘映像还原。（休眠）
系统将内存的副本存储到持久存储（磁盘），并将切断内存的电源。
如果你想要“休眠”——睡眠会更慢，唤醒会更慢，但电池寿命越长，你应该使用这个设置。

(仅在macOS 10.14测试成功, 10.13以下的旧版本情况会有所不同。)

当前模式：%s'''
    description_set_event = '''在此输入可执行程序的路径。如果该事件被触发，将会执行这个程序。
事件参数将通过环境变量进行传递。（JSON 格式, 键值: %s）

有关更多信息，请访问 GitHub 页面下的 “doc/” 目录。（例如使用样例）''' % Const.app_env
    description_welcome_why_need_admin = '''您需要输入管理员帐户以授予SleeperX权限。因为SleeperX会更改“电源管理设置”。（阻止合盖睡眠）'''
    description_welcome_is_admin = '''当前用户是管理员，跳过了管理员用户名设置。（如果要在SleeperX上使用其他管理员帐户工作，可以稍后进行设置。）'''
    description_welcome_tips_set_account = '''您取消了管理帐户设置！禁用合盖睡眠将无法使用。（您可以在偏好设置中找到管理帐户设置。）'''
    description_welcome_end = '''很好！现在SleeperX可以开始工作了。
Enjoy yourself!'''
    unable_to_pmset = '''无法更改“电源管理设置”！
请检查您的管理员帐户（用户名和密码）是否正确。

如果管理帐户是正确的，但始终无法使用，您可以尝试导出日志（在“偏好设置”-“高级选项”），并发送到这个项目的 issues 页面。'''

    menu_sleep_now = '立即睡眠'
    menu_display_sleep_now = '立即关闭显示器'
    menu_disable_lid_sleep = '阻止合盖睡眠'
    menu_disable_idle_sleep = '阻止闲置睡眠'
    menu_disable_idle_sleep_in_charging = '在接通电源时阻止闲置睡眠'
    menu_disable_lid_sleep_in_charging = '在接通电源时阻止合盖睡眠'
    menu_preferences = '偏好设置'
    menu_advanced_options = '高级选项'
    menu_event_callback = '事件回调'
    menu_set_idle_status_changed_event = '设置闲置状态改变事件'
    menu_set_lid_status_changed_event = '设置合盖状态改变事件'
    menu_set_charge_status_changed_event = '设置充电状态改变事件'
    menu_set_sleep_waked_up_event = '设置睡眠唤醒事件'
    menu_screen_save_on_lid = '在合盖时开启屏幕保护（阻止合盖睡眠时使用）'
    menu_short_time_cancel_screen_save = '短时间内取消屏幕保护（合盖时3秒内可取消）'
    menu_low_battery_capacity_sleep = '低电量睡眠（Hackintosh特性）'
    menu_set_low_battery_capacity = '设置低电量临界值'
    menu_set_low_time_remaining = '设置续航时间临界值'
    menu_set_username = '设置管理员用户名 (非管理员用户使用)'
    menu_set_password = '设置管理员用户密码'
    menu_select_language = '设置语言'
    menu_set_startup = '设置登录启动'
    menu_set_sleep_mode = '设置睡眠模式'
    menu_check_update = '检查更新'
    menu_clear_config = '清空配置文件'
    menu_export_log = '导出日志文件'
    menu_about = '关于'
    menu_quit = '退出'

    menu_ex_cancel_after_time = '在%s后取消'

    view_percent = '剩余电量: %d%%'
    view_status = '充电状态: %s'
    view_remaining = '剩余时间: %s'
    view_remaining_counting = '(计算中...)'

    status_charging = {'not charging': '未在充电', 'discharging': '正在放电', 'charging': '正在充电',
                       'finishing charge': '即将充满', 'charged': '已充满'}

    title_crash = '应用崩溃'
    title_welcome = '欢迎使用'

    noti_update_version = '发现新版本: %s'
    noti_update_time = '发布时间: %s'
    noti_update_none = '当前已是最新版本。'
    noti_update_star = '（如果你喜欢这个应用，请在GitHub给我个star，thanks。）'
    noti_network_error = '网络出现问题，请稍后重试。'

    sleep_mode_0 = '模式0'
    sleep_mode_3 = '模式3'
    sleep_mode_25 = '模式25'
