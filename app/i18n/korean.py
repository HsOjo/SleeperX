from app.res.const import Const
from .english import English


class Korean(English):
    l_this = '한국어'

    def unknown(self, key):
        return f'알 수 없는 문자열: ({key})'

    cancel = '취소'
    ok = '확인'

    time_days = '일 '
    time_hours = '시간 '
    time_minutes = '분 '
    time_seconds = '초'

    description_about = f'''{Const.app_name} 버전 {Const.version}

Hackintosh 사용자를 위한 macOS 메뉴 막대 전원/절전 관리 도구.

개발자: {Const.author}

GitHub 프로젝트 페이지를 열까요?'''
    description_set_low_time_remaining = '''남은 시간 임계값을 설정합니다. (단위: 분)
이 값 이하가 되면 절전 명령을 실행합니다.
(방전 중일 때만 유효합니다.)'''
    description_set_low_battery_capacity = '''낮은 배터리 임계값을 설정합니다. (단위: 퍼센트)
이 값 이하가 되면 절전 명령을 실행합니다.
(방전 중일 때만 유효합니다.)'''
    description_select_language = '언어를 선택하세요.'
    description_crash = '''이런! 앱이 충돌했습니다!
잠시 후 로그를 보여줍니다. 로그 파일을 개발자에게 보내주세요.'''
    description_set_startup = '''로그인 시 이 앱을 시작하시겠습니까?
(사용자별 LaunchAgent를 생성합니다. 여기서 다시 클릭하면 제거됩니다.)'''
    description_unable_to_pmset = '''"전원 관리 설정"을 변경할 수 없습니다!

이 기능에는 권한 도우미가 필요합니다. 설치를 위해 관리자 암호를 한 번
입력받습니다. 암호는 저장되지 않습니다. 설치가 취소되거나 실패하면
덮개 절전 비활성화 / 절전 모드가 동작하지 않습니다.

로그 보기(환경설정 - 고급 옵션)로 이슈를 등록할 수 있습니다.'''
    description_install_helper = '''SleeperX는 "전원 관리 설정"(덮개 절전 비활성화 / 절전 모드)을 변경하기 위해
권한 도우미를 설치해야 합니다.

관리자 암호를 한 번 입력받습니다. 암호는 어디에도 저장되지 않습니다.
지금 설치하시겠습니까?'''
    description_uninstall_helper = '''권한 도우미(LaunchDaemon)를 제거하시겠습니까?
관리자 암호를 한 번 입력받습니다.'''
    description_clear_config = '''이 작업은 설정 파일을 삭제합니다. 진행할까요?'''
    description_clear_config_restart = '''설정 파일이 삭제되었습니다. 앱을 다시 시작하세요.'''
    description_welcome = f'''{Const.app_name}에 오신 것을 환영합니다!

이 메뉴 막대 도구는 해킨토시의 전원/절전을 관리합니다.
"덮개 절전 비활성화 / 절전 모드 변경"을 처음 사용할 때 권한 도우미를
설치합니다(관리자 인증 한 번, 암호 저장 없음).

참고: 이 앱은 서명되지 않았습니다. macOS가 차단하면 앱을 오른쪽 클릭하여
"열기"를 한 번 선택하세요.'''

    description_welcome_end = f'''훌륭합니다! 이제 {Const.app_name}가 작동합니다.
즐기세요!'''

    menu_sleep_now = '지금 절전'
    menu_display_sleep_now = '지금 디스플레이 끄기'
    menu_disable_lid_sleep = '덮개 절전 비활성화'
    menu_disable_idle_sleep = '유휴 절전 비활성화'
    menu_disable_idle_sleep_in_charging = '충전 중 유휴 절전 비활성화'
    menu_disable_lid_sleep_in_charging = '충전 중 덮개 절전 비활성화'
    menu_preferences = '환경설정'
    menu_advanced_options = '고급 옵션'
    menu_low_battery_capacity_sleep = '저전력 절전 (해킨토시 기능)'
    menu_set_low_battery_capacity = '낮은 배터리 임계값 설정'
    menu_set_low_time_remaining = '남은 시간 임계값 설정'
    menu_select_language = '언어 설정'
    menu_set_startup = '로그인 시작 설정'
    menu_set_sleep_mode = '절전 모드 설정'
    menu_install_helper = '권한 도우미 설치'
    menu_uninstall_helper = '권한 도우미 제거'
    menu_check_update = '업데이트 확인'
    menu_clear_config = '설정 지우기'
    menu_view_log = '로그 보기'
    menu_about = '정보'
    menu_quit = '종료'
    menu_cancel_after = '후 취소'

    def menu_ex_cancel_after_time(self, duration):
        return f'{duration} 후 취소'

    def view_percent(self, percent):
        return f'배터리 용량: {percent}%'

    def view_status(self, status):
        return f'상태: {status}'

    def view_remaining(self, remaining):
        return f'남은 시간: {remaining}'

    view_remaining_counting = '(계산 중...)'

    status_charging = {'not charging': '충전 안 함', 'discharging': '방전 중', 'charging': '충전 중',
                       'finishing charge': '충전 완료 임박', 'charged': '충전 완료'}

    title_crash = '앱 충돌'
    title_welcome = '환영합니다'

    def noti_update_version(self, version):
        return f'업데이트 발견: {version}'

    def noti_update_time(self, release_time):
        return f'릴리스 시간: {release_time}'
    noti_update_none = '현재 최신 버전입니다.'
    noti_update_star = '(이 앱이 마음에 드신다면 GitHub에서 star를 부탁드립니다, 감사합니다.)'
    noti_network_error = '네트워크에 문제가 있는 것 같습니다. 나중에 다시 시도해 주세요.'

    sleep_mode_0 = '모드 0'
    sleep_mode_3 = '모드 3'
    sleep_mode_25 = '모드 25'
