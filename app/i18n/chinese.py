from app.res.const import Const
from .english import English


class Chinese(English):
    l_this = '简体中文'

    def unknown(self, key):
        return f'未知内容: ({key})'

    cancel = '取消'
    ok = '确定'

    time_days = '天'
    time_hours = '小时'
    time_minutes = '分钟'
    time_seconds = '秒'

    description_about = f'''{Const.app_name} 版本 {Const.version}

面向 Hackintosh 用户的 macOS 菜单栏电源/睡眠管理工具。

由 {Const.author} 开发。

是否打开 GitHub 项目页面？'''
    description_set_low_time_remaining = '''设置电池时间临界值 (单位: 分钟)
当电池时间不足该值，将执行睡眠命令。
(只在放电状态有效。)'''
    description_set_low_battery_capacity = '''设置低电量临界值。 (单位: 百分比)
当电量百分比不足该值，将执行睡眠命令。
(只在放电状态有效。)'''
    description_select_language = '请选择语言。'
    description_crash = '''卧槽! 应用崩溃了!
接下来将打开日志，请将日志提交给开发者，谢谢配合。'''
    description_set_startup = '''你确定要将该应用添加到登录启动项吗？
(将创建一个用户级 LaunchAgent，可在此处再次点击以移除。)'''
    def description_set_sleep_mode(self, current):
        return f'''模式 0：默认在台式机上使用。
系统不会将内存备份到持久存储（磁盘）。
系统必须从内存的内容中唤醒；否则断电将丢失使用状态。

模式 3：默认在笔记本电脑上使用。
系统会将内存的副本存储到持久存储（磁盘），并在睡眠期间为内存供电。
系统将从内存中唤醒，除非断电强制它从休眠映像中恢复。

模式 25：系统将从磁盘映像还原。（休眠）
系统将内存的副本存储到持久存储（磁盘），并将切断内存的电源。
如果你想要“休眠”——睡眠会更慢，唤醒会更慢，但电池寿命越长，你应该使用这个设置。

当前模式：{current}'''
    description_unable_to_pmset = '''无法更改“电源管理设置”！

此功能需要预先安装特权助手。请通过“偏好设置 - 高级选项 - 安装特权助手”进行安装。

你可以查看日志（“偏好设置”-“高级选项”）并提交到项目 issues 页面。'''
    description_install_helper = '''SleeperX 需要安装一个特权助手来更改“电源管理设置”
（阻止合盖睡眠 / 睡眠模式）。

将请求一次管理员密码，密码不会被保存在任何地方。现在安装吗？'''
    description_uninstall_helper = '''要移除特权助手（LaunchDaemon）吗？
将请求一次管理员密码。'''
    description_clear_config = '''这将会删除配置文件，确定吗？'''
    description_clear_config_restart = '''配置文件已经被删除，请重新启动该应用。'''
    description_welcome = f'''欢迎使用 {Const.app_name}！

这是一个面向 Hackintosh 的菜单栏电源/睡眠管理工具。
欢迎流程会提示安装特权助手（仅弹一次管理员授权，不保存任何密码）；
你也可以稍后在“偏好设置 - 高级选项”中手动安装。

注意：本应用未签名。若被 macOS 拦截，请右键点击应用并选择“打开”。'''

    description_welcome_end = f'''很好！现在 {Const.app_name} 可以开始工作了。
Enjoy yourself!'''

    menu_sleep_now = '立即睡眠'
    menu_display_sleep_now = '立即关闭显示器'
    menu_disable_lid_sleep = '阻止合盖睡眠'
    menu_disable_idle_sleep = '阻止闲置睡眠'
    menu_disable_idle_sleep_in_charging = '在接通电源时阻止闲置睡眠'
    menu_disable_lid_sleep_in_charging = '在接通电源时阻止合盖睡眠'
    menu_preferences = '偏好设置'
    menu_advanced_options = '高级选项'
    menu_low_battery_capacity_sleep = '低电量睡眠（Hackintosh 特性）'
    menu_set_low_battery_capacity = '设置低电量临界值'
    menu_set_low_time_remaining = '设置续航时间临界值'
    menu_select_language = '设置语言'
    menu_set_startup = '设置登录启动'
    menu_set_sleep_mode = '设置睡眠模式'
    menu_install_helper = '安装特权助手'
    menu_uninstall_helper = '卸载特权助手'
    menu_check_update = '检查更新'
    menu_clear_config = '清空配置文件'
    menu_view_log = '查看日志'
    menu_about = '关于'
    menu_quit = '退出'
    menu_cancel_after = '取消于'

    def menu_ex_cancel_after_time(self, duration):
        return f'在 {duration} 后取消'

    def view_percent(self, percent):
        return f'剩余电量: {percent}%'

    def view_status(self, status):
        return f'充电状态: {status}'

    def view_remaining(self, remaining):
        return f'剩余时间: {remaining}'

    view_remaining_counting = '(计算中...)'

    status_charging = {'not charging': '未在充电', 'discharging': '正在放电', 'charging': '正在充电',
                       'finishing charge': '即将充满', 'charged': '已充满'}

    title_crash = '应用崩溃'
    title_welcome = '欢迎使用'

    def noti_update_version(self, version):
        return f'发现新版本: {version}'

    def noti_update_time(self, release_time):
        return f'发布时间: {release_time}'
    noti_update_none = '当前已是最新版本。'
    noti_update_star = '（如果你喜欢这个应用，请在 GitHub 给我个 star，thanks。）'
    noti_network_error = '网络出现问题，请稍后重试。'
    noti_checking_update = '正在检查更新...'

    sleep_mode_0 = '模式 0'
    sleep_mode_3 = '模式 3'
    sleep_mode_25 = '模式 25'
