import i18n
from engine import ClickButton, ClickType, CursorMode


def test_languages_are_ua_ru_en():
    assert set(i18n.LANGUAGES) == {"UA", "RU", "EN"}


def test_every_string_key_covers_all_languages():
    for key, translations in i18n._STRINGS.items():
        for lang in i18n.LANGUAGES:
            assert lang in translations, f"'{key}' is missing a {lang} translation"
            assert translations[lang], f"'{key}' has an empty {lang} translation"


def test_every_enum_value_covers_all_languages():
    for value, translations in i18n._ENUM_STRINGS.items():
        for lang in i18n.LANGUAGES:
            assert lang in translations, f"'{value}' is missing a {lang} translation"


def test_every_engine_enum_member_is_translated():
    # Guards against adding a new ClickButton/ClickType/CursorMode value in
    # engine.py without wiring up its translated label in i18n.py.
    for enum_cls in (ClickButton, ClickType, CursorMode):
        for member in enum_cls:
            assert member.value in i18n._ENUM_STRINGS, (
                f"{enum_cls.__name__}.{member.name} ({member.value!r}) has no translation"
            )


def test_t_formats_kwargs():
    text = i18n.t("standard_interval", "EN", cps=10.0)
    assert "10.00" in text


def test_t_unknown_key_raises():
    try:
        i18n.t("does_not_exist", "EN")
    except KeyError:
        pass
    else:
        raise AssertionError("expected KeyError for an unknown translation key")


def test_enum_label_falls_back_to_raw_value():
    assert i18n.enum_label("Some Untranslated Value", "EN") == "Some Untranslated Value"
