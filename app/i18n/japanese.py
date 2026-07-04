from app.res.const import Const
from .english import English


class Japanese(English):
    l_this = '日本語'

    def unknown(self, key):
        return f'不明な文字列: ({key})'

    cancel = 'キャンセル'
    ok = 'OK'

    time_days = ' 日 '
    time_hours = ' 時間 '
    time_minutes = ' 分 '
    time_seconds = ' 秒'

    description_about = f'''{Const.app_name} バージョン {Const.version}

Hackintosh ユーザー向けの macOS メニューバー電源/スリープ管理ツール。

開発者：{Const.author}

GitHub プロジェクトページを開きますか？'''
    description_set_low_time_remaining = '''残り時間のしきい値を設定します。(単位: 分)
この値以下になるとスリープコマンドを実行します。
(放電中のみ有効です。)'''
    description_set_low_battery_capacity = '''バッテリー残量のしきい値を設定します。(単位: パーセント)
この値以下になるとスリープコマンドを実行します。
(放電中のみ有効です。)'''
    description_select_language = '言語を選択してください。'
    description_crash = '''おっと！アプリがクラッシュしました！
このあとログを表示します。ログファイルを開発者に送ってください。'''
    description_set_startup = '''ログイン時にこのアプリを起動しますか？
(ユーザー単位の LaunchAgent を作成します。ここで再度クリックすると解除できます。)'''
    description_unable_to_pmset = '''「省エネルギー設定」を変更できません！

この機能には特権ヘルパーが必要です。インストールのため管理者パスワードを
一度求められます。パスワードは保存されません。インストールを中止・失敗すると
閉じたときのスリープ無効化 / スリープモードは動作しません。

ログを表示して（環境設定 - 詳細オプション）issue を作成できます。'''
    description_install_helper = '''SleeperX は「省エネルギー設定」（閉じたときのスリープ無効化 / スリープモード）
を変更するため、特権ヘルパーをインストールする必要があります。

管理者パスワードを一度求められます。パスワードはどこにも保存されません。
今すぐインストールしますか？'''
    description_uninstall_helper = '''特権ヘルパー（LaunchDaemon）を削除しますか？
管理者パスワードを一度求められます。'''
    description_clear_config = '''設定ファイルを削除します。よろしいですか？'''
    description_clear_config_restart = '''設定ファイルを削除しました。アプリを再起動してください。'''
    description_welcome = f'''{Const.app_name} へようこそ！

これは Hackintosh 向けの電源/スリープ管理メニューバーツールです。
「閉じたときのスリープ無効化 / スリープモード変更」を初めて使うとき、特権ヘルパー
をインストールします（管理者認証は一度のみ、パスワードは保存しません）。

注意：このアプリは署名されていません。macOS にブロックされた場合は、
アプリを右クリックして「開く」を選んでください。'''

    description_welcome_end = f'''素晴らしい！{Const.app_name} が動作を開始しました。
お楽しみください！'''

    menu_sleep_now = '今すぐスリープ'
    menu_display_sleep_now = 'ディスプレイをオフ'
    menu_disable_lid_sleep = '閉じたときのスリープを無効化'
    menu_disable_idle_sleep = 'アイドルスリープを無効化'
    menu_disable_idle_sleep_in_charging = '充電中はアイドルスリープを無効化'
    menu_disable_lid_sleep_in_charging = '充電中は閉じたときのスリープを無効化'
    menu_preferences = '環境設定'
    menu_advanced_options = '詳細オプション'
    menu_low_battery_capacity_sleep = '低残量スリープ（Hackintosh 機能）'
    menu_set_low_battery_capacity = '低残量しきい値を設定'
    menu_set_low_time_remaining = '残り時間しきい値を設定'
    menu_select_language = '言語を設定'
    menu_set_startup = 'ログイン起動を設定'
    menu_set_sleep_mode = 'スリープモードを設定'
    menu_install_helper = '特権ヘルパーをインストール'
    menu_uninstall_helper = '特権ヘルパーをアンインストール'
    menu_check_update = '更新を確認'
    menu_clear_config = '設定をクリア'
    menu_view_log = 'ログを表示'
    menu_about = 'このアプリについて'
    menu_quit = '終了'
    menu_cancel_after = '後で取消'

    def menu_ex_cancel_after_time(self, duration):
        return f'{duration} 後に取消'

    def view_percent(self, percent):
        return f'バッテリー残量: {percent}%'

    def view_status(self, status):
        return f'状態: {status}'

    def view_remaining(self, remaining):
        return f'残り時間: {remaining}'

    view_remaining_counting = '(計算中...)'

    status_charging = {'not charging': '充電していません', 'discharging': '放電中', 'charging': '充電中',
                       'finishing charge': 'まもなく満充電', 'charged': '満充電'}

    title_crash = 'アプリのクラッシュ'
    title_welcome = 'ようこそ'

    def noti_update_version(self, version):
        return f'更新が見つかりました: {version}'

    def noti_update_time(self, release_time):
        return f'リリース日時: {release_time}'
    noti_update_none = '現在は最新バージョンです。'
    noti_update_star = '（このアプリが気に入ったら GitHub で star をお願いします。）'
    noti_network_error = 'ネットワークに問題があるようです。後でもう一度お試しください。'

    sleep_mode_0 = 'モード 0'
    sleep_mode_3 = 'モード 3'
    sleep_mode_25 = 'モード 25'
