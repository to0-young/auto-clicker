"""UI translation strings for the auto clicker: UA / RU / EN."""

LANGUAGES = ("UA", "RU", "EN")

_STRINGS = {
    "interval_configuration": {
        "EN": "Interval Configuration",
        "UA": "Налаштування інтервалу",
        "RU": "Настройка интервала",
    },
    "standard_interval": {
        "EN": "Standard Interval (~{cps:.2f} CPS)",
        "UA": "Стандартний інтервал (~{cps:.2f} CPS)",
        "RU": "Стандартный интервал (~{cps:.2f} CPS)",
    },
    "hours": {"EN": "hours", "UA": "год", "RU": "ч"},
    "mins": {"EN": "mins", "UA": "хв", "RU": "мин"},
    "secs": {"EN": "secs", "UA": "сек", "RU": "сек"},
    "milliseconds": {"EN": "milliseconds", "UA": "мілісекунди", "RU": "миллисекунды"},
    "random_offset": {
        "EN": "Random Offset ±",
        "UA": "Випадкове відхилення ±",
        "RU": "Случайное отклонение ±",
    },
    "ms": {"EN": "ms", "UA": "мс", "RU": "мс"},
    "click_options": {"EN": "Click Options", "UA": "Налаштування кліку", "RU": "Настройки клика"},
    "mouse_button": {"EN": "MOUSE BUTTON", "UA": "КНОПКА МИШІ", "RU": "КНОПКА МЫШИ"},
    "click_type": {"EN": "CLICK TYPE", "UA": "ТИП КЛІКУ", "RU": "ТИП КЛИКА"},
    "click_repeat": {"EN": "Click Repeat", "UA": "Повторення кліку", "RU": "Повтор клика"},
    "repeat": {"EN": "Repeat", "UA": "Повторити", "RU": "Повторить"},
    "times": {"EN": "times", "UA": "разів", "RU": "раз"},
    "repeat_until_stopped": {
        "EN": "Repeat until stopped",
        "UA": "Повторювати, поки не зупинено",
        "RU": "Повторять до остановки",
    },
    "cursor_position": {"EN": "Cursor Position", "UA": "Позиція курсора", "RU": "Позиция курсора"},
    "set_position": {"EN": "Set Position", "UA": "Встановити позицію", "RU": "Установить позицию"},
    "move_mouse_enter": {
        "EN": "Move mouse, press Enter...",
        "UA": "Наведи мишу, натисни Enter...",
        "RU": "Наведи мышь, нажми Enter...",
    },
    "browse": {"EN": "Browse...", "UA": "Огляд...", "RU": "Обзор..."},
    "start": {"EN": "Start", "UA": "Старт", "RU": "Старт"},
    "stop": {"EN": "Stop", "UA": "Стоп", "RU": "Стоп"},
    "record_hotkey": {"EN": "Record Hotkey", "UA": "Записати клавішу", "RU": "Записать клавишу"},
    "press_any_key": {
        "EN": "Press any key...",
        "UA": "Натисни будь-яку клавішу...",
        "RU": "Нажми любую клавишу...",
    },
    "idle": {"EN": "Idle", "UA": "Очікування", "RU": "Ожидание"},
    "clicking": {"EN": "Clicking...", "UA": "Клікає...", "RU": "Кликает..."},
}

_ENUM_STRINGS = {
    "Left": {"EN": "Left", "UA": "Ліва", "RU": "Левая"},
    "Right": {"EN": "Right", "UA": "Права", "RU": "Правая"},
    "Middle": {"EN": "Middle", "UA": "Середня", "RU": "Средняя"},
    "Single": {"EN": "Single", "UA": "Одинарний", "RU": "Одиночный"},
    "Double": {"EN": "Double", "UA": "Подвійний", "RU": "Двойной"},
    "Hold": {"EN": "Hold", "UA": "Утримання", "RU": "Удержание"},
    "Cursor Location": {
        "EN": "Cursor Location",
        "UA": "Поточна позиція курсора",
        "RU": "Текущая позиция курсора",
    },
    "Fixed Location": {"EN": "Fixed Location", "UA": "Фіксована позиція", "RU": "Фиксированная позиция"},
    "Find Image": {"EN": "Find Image", "UA": "Пошук зображення", "RU": "Поиск изображения"},
    "Find Color": {"EN": "Find Color", "UA": "Пошук кольору", "RU": "Поиск цвета"},
}


def t(key: str, lang: str, **kwargs) -> str:
    text = _STRINGS[key][lang]
    return text.format(**kwargs) if kwargs else text


def enum_label(value: str, lang: str) -> str:
    return _ENUM_STRINGS.get(value, {}).get(lang, value)
