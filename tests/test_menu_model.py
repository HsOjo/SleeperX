"""Tests for the declarative menu model.

These are pure Python / no PyObjC: they verify the shape, keys, and checked
states produced by menu_model.build_menu().
"""
from __future__ import annotations

import pytest

from app.i18n import load_language
from app.ui import menu_model


@pytest.fixture
def en():
    return load_language('en')


def _collect_keys(nodes):
    """Recursively collect all item keys (excluding separators)."""
    keys = []
    for node in nodes:
        if node.get('kind') == 'separator':
            continue
        keys.append(node.get('key'))
        if 'children' in node:
            keys.extend(_collect_keys(node['children']))
    return keys


def test_build_menu_has_expected_top_level_keys(en):
    state = {
        'idle_sleep_disabled': False,
        'lid_sleep_disabled': False,
        'startup': False,
        'low_battery_capacity_sleep': False,
        'disable_idle_sleep_in_charging': False,
        'disable_lid_sleep_in_charging': False,
    }
    menu = menu_model.build_menu(en, 'en', state)
    top_keys = [node.get('key') for node in menu if node.get('kind') != 'separator']
    assert top_keys == [
        'view_percent', 'view_status', 'view_remaining',
        'sleep_now', 'display_sleep_now',
        'disable_idle_sleep', 'cancel_idle',
        'disable_lid_sleep', 'cancel_lid',
        'preferences', 'select_language',
        'check_update', 'about', 'quit',
    ]


def test_build_menu_advanced_children_include_view_log(en):
    state = {
        'idle_sleep_disabled': False,
        'lid_sleep_disabled': False,
        'startup': False,
        'low_battery_capacity_sleep': False,
        'disable_idle_sleep_in_charging': False,
        'disable_lid_sleep_in_charging': False,
    }
    menu = menu_model.build_menu(en, 'en', state)
    prefs = next(node for node in menu if node.get('key') == 'preferences')
    advanced = next(node for node in prefs['children'] if node.get('key') == 'advanced_options')
    advanced_keys = [node.get('key') for node in advanced['children']
                     if node.get('kind') != 'separator']
    assert advanced_keys == [
        'low_battery_capacity_sleep', 'set_sleep_mode',
        'install_helper', 'uninstall_helper',
        'view_log', 'clear_config',
    ]


def test_build_menu_no_export_log_key(en):
    state = {
        'idle_sleep_disabled': False,
        'lid_sleep_disabled': False,
        'startup': False,
        'low_battery_capacity_sleep': False,
        'disable_idle_sleep_in_charging': False,
        'disable_lid_sleep_in_charging': False,
    }
    menu = menu_model.build_menu(en, 'en', state)
    keys = _collect_keys(menu)
    assert 'export_log' not in keys
    assert 'view_log' in keys


def test_build_menu_checked_states(en):
    state = {
        'idle_sleep_disabled': True,
        'lid_sleep_disabled': True,
        'startup': True,
        'low_battery_capacity_sleep': True,
        'disable_idle_sleep_in_charging': True,
        'disable_lid_sleep_in_charging': True,
    }
    menu = menu_model.build_menu(en, 'en', state)

    def find(nodes, key):
        for node in nodes:
            if node.get('key') == key:
                return node
            if 'children' in node:
                found = find(node['children'], key)
                if found:
                    return found
        return None

    assert find(menu, 'disable_idle_sleep')['checked'] is True
    assert find(menu, 'disable_lid_sleep')['checked'] is True
    assert find(menu, 'set_startup')['checked'] is True
    assert find(menu, 'low_battery_capacity_sleep')['checked'] is True
    assert find(menu, 'disable_idle_sleep_in_charging')['checked'] is True
    assert find(menu, 'disable_lid_sleep_in_charging')['checked'] is True


def test_cancel_idle_submenu_has_time_options_and_separators(en):
    state = {
        'idle_sleep_disabled': False,
        'lid_sleep_disabled': False,
        'startup': False,
        'low_battery_capacity_sleep': False,
        'disable_idle_sleep_in_charging': False,
        'disable_lid_sleep_in_charging': False,
    }
    menu = menu_model.build_menu(en, 'en', state)
    cancel_idle = next(node for node in menu if node.get('key') == 'cancel_idle')
    children = cancel_idle['children']
    assert len(children) == 10  # 8 options + 2 separators
    assert any(node.get('kind') == 'separator' for node in children)
    keys = [node.get('key') for node in children if node.get('kind') != 'separator']
    assert len(keys) == 8
    assert keys[0] == 'cancel_idle:300'
    assert keys[-1] == 'cancel_idle:86400'
