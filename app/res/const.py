import os


class Const:
    author = 'HsOjo'
    app_name = 'SleeperX'
    version = '2.1.0'

    # Reverse-DNS identifiers (used by launchd / config path).
    # Kept all-lower-case for consistency.
    bundle_id = f'com.{author}.{app_name}'.lower()
    agent_label = bundle_id
    helper_label = f'{agent_label}.helper'

    github_page = f'https://github.com/{author}/{app_name}'
    releases_url = f'{github_page}/releases'

    res_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(res_dir, 'icon.png')

    # Config directory aligned with the bundle id.
    config_dir = os.path.expanduser(f'~/Library/Application Support/{bundle_id}')
    config_path = os.path.join(config_dir, 'config.json')

    log_dir = os.path.join(config_dir, 'logs')
    log_path = os.path.join(log_dir, f'{app_name}.log')

    # Privileged helper install locations (root-owned).
    helper_install_dir = f'/Library/Application Support/{app_name}'
    helper_app_path = os.path.join(helper_install_dir, f'{app_name}.app')
    helper_socket_path = os.path.join(helper_install_dir, 'helper.sock')
    helper_allowed_uid_path = os.path.join(helper_install_dir, 'allowed_uid')
    helper_version_path = os.path.join(helper_install_dir, 'version')
    launch_daemon_plist = f'/Library/LaunchDaemons/{helper_label}.plist'
    launch_agent_plist = os.path.expanduser(
        f'~/Library/LaunchAgents/{agent_label}.plist')

    # Behaviour thresholds carried over from v1 (docs/PROJECT.md §4).
    time_options = [300, 600, 1800, '-', 3600, 7200, 10800, '-', 43200, 86400]
    check_sleep_time = 30
    # Charge status values reported by IOKit power sources.
    charging_states = ['not charging', 'charging', 'finishing charge', 'charged']
