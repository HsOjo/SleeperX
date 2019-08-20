class Const:
    author = 'HsOjo'
    app_name = 'SleeperX'
    app_env = '%s_ENV' % app_name.upper()
    version = '1.6.3'
    github_page = 'https://github.com/%s/%s' % (author, app_name)
    releases_url = '%s/releases' % github_page
    protector = '[protector]'
    time_options = [300, 600, 1800, '-', 3600, 7200, 10800, '-', 43200, 86400]
    check_sleep_time = 30
