"""Unit tests for the dataclass-based config store."""
from __future__ import annotations

import json
import os

import pytest

from app.core.config import Config


@pytest.fixture
def temp_config(tmp_path, monkeypatch):
    path = tmp_path / 'config.json'
    monkeypatch.setattr(Config, '_path', str(path))
    yield path


def test_config_defaults():
    cfg = Config()
    assert cfg.first_run is True
    assert cfg.low_battery_capacity == 6
    assert cfg.language == ''


def test_config_loads_saved_values(temp_config):
    cfg = Config()
    cfg.language = 'cn'
    cfg.low_battery_capacity = 10
    cfg.save()

    cfg2 = Config()
    cfg2.load()
    assert cfg2.language == 'cn'
    assert cfg2.low_battery_capacity == 10


def test_config_detect_language_when_empty(temp_config):
    cfg = Config()
    cfg.load(detect_language=lambda: 'jp')
    assert cfg.language == 'jp'
    assert temp_config.exists()


def test_config_ignores_unknown_keys(temp_config):
    temp_config.write_text(json.dumps({'unknown_key': 123, 'language': 'ko'}), encoding='utf-8')
    cfg = Config()
    cfg.load()
    assert cfg.language == 'ko'
    assert not hasattr(cfg, 'unknown_key')


def test_config_clear_removes_file(temp_config):
    cfg = Config()
    cfg.save()
    assert temp_config.exists()
    cfg.clear()
    assert not temp_config.exists()


def test_config_load_invalid_json_uses_defaults(temp_config):
    temp_config.write_text('not json', encoding='utf-8')
    cfg = Config()
    cfg.load()
    assert cfg.first_run is True
    assert cfg.language == ''
