import pytest
from pynput import keyboard

from engine import ClickerConfig, key_label, parse_key_spec


def test_interval_seconds_default():
    assert ClickerConfig().interval_seconds() == pytest.approx(0.1)


def test_interval_seconds_combines_all_units():
    cfg = ClickerConfig(hours=1, minutes=2, seconds=3, milliseconds=500)
    assert cfg.interval_seconds() == pytest.approx(3723.5)


def test_interval_seconds_has_a_floor():
    cfg = ClickerConfig(hours=0, minutes=0, seconds=0, milliseconds=0)
    assert cfg.interval_seconds() == pytest.approx(0.001)


def test_cps_matches_interval():
    assert ClickerConfig(milliseconds=200).cps() == pytest.approx(5.0)


def test_cps_zero_interval_is_handled():
    # milliseconds=0 still floors to 0.001s, so cps stays finite
    assert ClickerConfig(milliseconds=0).cps() == pytest.approx(1000.0)


def test_parse_key_spec_function_key():
    assert parse_key_spec("f5") == [keyboard.Key.f5]


def test_parse_key_spec_combo():
    assert parse_key_spec("ctrl+c") == [keyboard.Key.ctrl_l, "c"]


def test_parse_key_spec_single_char():
    assert parse_key_spec("a") == ["a"]


def test_parse_key_spec_ignores_empty_segments():
    assert parse_key_spec("ctrl++c") == [keyboard.Key.ctrl_l, "c"]


def test_parse_key_spec_aliases():
    assert parse_key_spec("esc") == [keyboard.Key.esc]
    assert parse_key_spec("win") == [keyboard.Key.cmd]


def test_parse_key_spec_is_case_insensitive():
    assert parse_key_spec("F6") == [keyboard.Key.f6]


def test_key_label_named_key():
    assert key_label(keyboard.Key.f6) == "F6"


def test_key_label_char_key():
    assert key_label(keyboard.KeyCode.from_char("a")) == "A"


def test_key_label_vk_only_key():
    assert key_label(keyboard.KeyCode(vk=123)) == "VK123"
