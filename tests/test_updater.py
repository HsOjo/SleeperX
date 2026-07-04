"""Unit tests for the update checker."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from app.core import updater


@pytest.mark.parametrize('current,latest,expected', [
    ('2.0.0', '2.0.1', True),
    ('2.0.0', '2.0.0', False),
    ('2.0.0', '1.9.9', False),
    ('v2.0.0', 'V2.0.1', True),
    ('2.0.0-beta', '2.0.1', True),
    ('2.0.0', '2.1.0-beta', False),  # pre-release latest is ignored
    ('1.10.0', '2.0.0', True),       # would be wrong with integer concatenation
    ('2.0', '2.0.0', False),
    ('2.0.0', '2.0.0.1', True),
])
def test_compare_version(current, latest, expected):
    assert updater.compare_version(current, latest) is expected


def _fake_release_response(tag: str):
    resp = MagicMock()
    resp.json.return_value = {
        'name': tag,
        'tag_name': tag,
        'published_at': '2026-01-01T00:00:00Z',
        'html_url': 'https://example.com',
        'body': 'notes',
        'assets': [{'browser_download_url': 'https://example.com/app.zip'}],
    }
    resp.raise_for_status = MagicMock()
    return resp


def test_get_latest_release_parses_response():
    with patch('app.core.updater.requests.get', return_value=_fake_release_response('v2.0.1')):
        release = updater.get_latest_release()
    assert release.tag_name == 'v2.0.1'
    assert release.published_at == '2026-01-01 00:00:00'
    assert release.download_url == 'https://example.com/app.zip'


def test_check_update_returns_have_new():
    with patch('app.core.updater.requests.get', return_value=_fake_release_response('v2.0.1')):
        release, have_new = updater.check_update()
    assert release is not None
    assert have_new is True


def test_check_update_respects_current_version():
    with patch('app.core.updater.requests.get', return_value=_fake_release_response('v2.0.0')):
        release, have_new = updater.check_update()
    assert release is not None
    assert have_new is False
