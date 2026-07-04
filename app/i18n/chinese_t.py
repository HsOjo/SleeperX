from app.res.const import Const
from .chinese import Chinese


class TraditionalChinese(Chinese):
    l_this = '繁體中文'

    def unknown(self, key):
        return f'未知內容: ({key})'

    cancel = '取消'
    ok = '確定'

    time_days = '天'
    time_hours = '小時'
    time_minutes = '分鐘'
    time_seconds = '秒'

    description_about = f'''{Const.app_name} 版本 {Const.version}

面向 Hackintosh 使用者的 macOS 選單列電源/睡眠管理工具。

由 {Const.author} 開發。

是否打開 GitHub 項目頁面？'''
    description_set_low_time_remaining = '''設定電池時間臨界值 (單位: 分鐘)
當電池時間不足該值，將執行睡眠命令。
(只在放電狀態有效。)'''
    description_set_low_battery_capacity = '''設定低電量臨界值。 (單位: 百分比)
當電量百分比不足該值，將執行睡眠命令。
(只在放電狀態有效。)'''
    description_select_language = '請選擇語言。'
    description_crash = '''糟糕! 應用程式當機了!
接下來將檢視日誌，請將日誌提交給開發者，謝謝配合。'''
    description_set_startup = '''你確定要將該應用程式加入登入啟動項嗎？
(將建立一個使用者級 LaunchAgent，可在此處再次點擊以移除。)'''
    def description_set_sleep_mode(self, current):
        return f'''範式 0：預設在桌上型電腦上使用。
系統不會將記憶體備份到持久儲存（磁碟）。
系統必須從記憶體的內容中喚醒；否則斷電將遺失使用狀態。

範式 3：預設在筆記型電腦上使用。
系統會將記憶體的副本儲存到持久儲存（磁碟），並在睡眠期間為記憶體供電。
系統將從記憶體中喚醒，除非斷電強制它從休眠映像中恢復。

範式 25：系統將從磁碟映像還原。（休眠）
系統將記憶體的副本儲存到持久儲存（磁碟），並將切斷記憶體的電源。
如果你想要“休眠”——睡眠會更慢，喚醒會更慢，但電池壽命越長，你應該使用這個設定。

目前範式：{current}'''
    description_unable_to_pmset = '''無法更改“電源管理設定”！

此功能需要特權助手。將會請求一次管理員密碼以完成安裝，密碼不會被儲存。
如果安裝被取消或失敗，阻止閤蓋睡眠 / 睡眠範式將無法使用。

你可以檢視日誌（“偏好設定”-“進階選項”）並提交到專案 issues 頁面。'''
    description_install_helper = '''SleeperX 需要安裝一個特權助手來更改“電源管理設定”
（阻止閤蓋睡眠 / 睡眠範式）。

將請求一次管理員密碼，密碼不會被儲存在任何地方。現在安裝嗎？'''
    description_uninstall_helper = '''要移除特權助手（LaunchDaemon）嗎？
將請求一次管理員密碼。'''
    description_clear_config = '''這將會刪除設定檔，確定嗎？'''
    description_clear_config_restart = '''設定檔已經被刪除，請重新啟動該應用程式。'''
    description_welcome = f'''歡迎使用 {Const.app_name}！

這是一個面向 Hackintosh 的選單列電源/睡眠管理工具。
首次使用“阻止閤蓋睡眠 / 更改睡眠範式”時會安裝一個特權助手
（僅彈一次管理員授權，不儲存任何密碼）。

注意：本應用程式未簽章。若被 macOS 攔截，請右鍵點擊應用程式並選擇“打開”。'''

    description_welcome_end = f'''很好！現在 {Const.app_name} 可以開始工作了。
Enjoy yourself!'''

    menu_sleep_now = '立即睡眠'
    menu_display_sleep_now = '立即關閉顯示幕'
    menu_disable_lid_sleep = '阻止閤蓋睡眠'
    menu_disable_idle_sleep = '阻止閒置睡眠'
    menu_disable_idle_sleep_in_charging = '在接通電源時阻止閒置睡眠'
    menu_disable_lid_sleep_in_charging = '在接通電源時阻止閤蓋睡眠'
    menu_preferences = '偏好設定'
    menu_advanced_options = '進階選項'
    menu_low_battery_capacity_sleep = '低電量睡眠（Hackintosh 特性）'
    menu_set_low_battery_capacity = '設定低電量臨界值'
    menu_set_low_time_remaining = '設定續航時間臨界值'
    menu_select_language = '設定語言'
    menu_set_startup = '設定登入啟動'
    menu_set_sleep_mode = '設定睡眠範式'
    menu_install_helper = '安裝特權助手'
    menu_uninstall_helper = '解除安裝特權助手'
    menu_check_update = '檢查更新'
    menu_clear_config = '清空設定檔'
    menu_view_log = '檢視日誌'
    menu_about = '關於'
    menu_quit = '結束'
    menu_cancel_after = '取消於'

    def menu_ex_cancel_after_time(self, duration):
        return f'在 {duration} 後取消'

    def view_percent(self, percent):
        return f'剩餘電量: {percent}%'

    def view_status(self, status):
        return f'充電狀態: {status}'

    def view_remaining(self, remaining):
        return f'剩餘時間: {remaining}'

    view_remaining_counting = '(計算中...)'

    status_charging = {'not charging': '未在充電', 'discharging': '正在放電', 'charging': '正在充電',
                       'finishing charge': '即將充滿', 'charged': '已充滿'}

    title_crash = '應用程式當機'
    title_welcome = '歡迎使用'

    def noti_update_version(self, version):
        return f'發現新版本: {version}'

    def noti_update_time(self, release_time):
        return f'發佈時間: {release_time}'
    noti_update_none = '目前已是最新版本。'
    noti_update_star = '（如果你喜歡這個應用程式，請在 GitHub 給我個 star，thanks。）'
    noti_network_error = '網路出現問題，請稍後重試。'

    sleep_mode_0 = '範式 0'
    sleep_mode_3 = '範式 3'
    sleep_mode_25 = '範式 25'
