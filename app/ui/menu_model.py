"""Declarative menu tree (mirrors the old view/application.py structure).

Each node is a dict:
  {'key': str, 'kind': 'info'|'action'|'checkbox'|'submenu'|'separator',
   'title': str, 'children': [...], 'checked': bool}
Titles are resolved from the active language table at build time; the menu is
rebuilt when the language changes.

The "disable sleep" toggles are standalone action/checkbox items; their
"cancel after X" options are grouped in a separate submenu titled by
`menu_cancel_after`.
"""
from __future__ import annotations

from app.i18n import format_duration
from app.res.const import Const


def _sep():
    return {'kind': 'separator'}


def _item(key, kind, title, checked=None):
    node = {'key': key, 'kind': kind, 'title': title}
    if checked is not None:
        node['checked'] = checked
    return node


def _cancel_items(lang, prefix):
    items = []
    for opt in Const.time_options:
        if opt == '-':
            items.append(_sep())
        else:
            label = lang.menu_ex_cancel_after_time(format_duration(lang, opt))
            items.append(_item(f'{prefix}:{opt}', 'action', label))
    return items


def build_menu(lang, current_language_code, state):
    """`state` carries current toggle/config values for initial checkmarks."""
    def m(key):
        return getattr(lang, f'menu_{key}')

    advanced = {
        'key': 'advanced_options', 'kind': 'submenu', 'title': m('advanced_options'),
        'children': [
            _item('low_battery_capacity_sleep', 'checkbox',
                  m('low_battery_capacity_sleep'), checked=state['low_battery_capacity_sleep']),
            _sep(),
            _item('set_sleep_mode', 'action', m('set_sleep_mode')),
            _sep(),
            _item('install_helper', 'action', m('install_helper')),
            _item('uninstall_helper', 'action', m('uninstall_helper')),
            _sep(),
            _item('view_log', 'action', m('view_log')),
            _sep(),
            _item('clear_config', 'action', m('clear_config')),
        ],
    }

    preferences = {
        'key': 'preferences', 'kind': 'submenu', 'title': m('preferences'),
        'children': [
            _item('set_startup', 'checkbox', m('set_startup'), checked=state['startup']),
            _sep(),
            _item('set_low_battery_capacity', 'action', m('set_low_battery_capacity')),
            _item('set_low_time_remaining', 'action', m('set_low_time_remaining')),
            _sep(),
            _item('disable_idle_sleep_in_charging', 'checkbox',
                  m('disable_idle_sleep_in_charging'), checked=state['disable_idle_sleep_in_charging']),
            _item('disable_lid_sleep_in_charging', 'checkbox',
                  m('disable_lid_sleep_in_charging'), checked=state['disable_lid_sleep_in_charging']),
            _sep(),
            advanced,
        ],
    }

    return [
        _item('view_percent', 'info', lang.view_percent('?')),
        _item('view_status', 'info', lang.view_status('?')),
        _item('view_remaining', 'info', lang.view_remaining('?')),
        _sep(),
        _item('sleep_now', 'action', m('sleep_now')),
        _item('display_sleep_now', 'action', m('display_sleep_now')),
        _sep(),
        _item('disable_idle_sleep', 'action', m('disable_idle_sleep'),
              checked=state['idle_sleep_disabled']),
        {'key': 'cancel_idle', 'kind': 'submenu', 'title': lang.menu_cancel_after,
         'children': _cancel_items(lang, 'cancel_idle')},
        _sep(),
        _item('disable_lid_sleep', 'action', m('disable_lid_sleep'),
              checked=state['lid_sleep_disabled']),
        {'key': 'cancel_lid', 'kind': 'submenu', 'title': lang.menu_cancel_after,
         'children': _cancel_items(lang, 'cancel_lid')},
        _sep(),
        preferences,
        _item('select_language', 'action', m('select_language')),
        _sep(),
        _item('check_update', 'action', m('check_update')),
        _item('about', 'action', m('about')),
        _sep(),
        _item('quit', 'action', m('quit')),
    ]
