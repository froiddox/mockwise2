import re
import time

import pyautogui
import pyperclip

from models import Plugin, TestCase


# Timing is controlled per-field by plugin JSON; no global pyautogui delay
pyautogui.PAUSE = 0

_KEY_TOKENS: dict[str, str] = {
    "ESC": "escape",
    "TAB": "tab",
    "ENTER": "enter",
    "SPACE": "space",
}

_TOKEN_RE = re.compile(r"\[([^\]]+)\]", re.IGNORECASE)


def _parse_actions(value: str) -> list[tuple[str, str]]:
    stripped = value.strip()
    if not stripped:
        return [("empty", "")]

    actions: list[tuple[str, str]] = []
    cursor = 0

    for m in _TOKEN_RE.finditer(stripped):
        pre = stripped[cursor : m.start()].strip()
        if pre:
            actions.append(("text", pre))

        inner = m.group(1).upper()
        if inner == "CLK":
            actions.append(("click", ""))
        elif inner == "DBCLK":
            actions.append(("doubleclick", ""))
        elif inner in _KEY_TOKENS:
            actions.append(("key", _KEY_TOKENS[inner]))
        else:
            actions.append(("text", m.group(0)))

        cursor = m.end()

    tail = stripped[cursor:].strip()
    if tail:
        actions.append(("text", tail))

    return actions or [("empty", "")]


def _build_lookup(test_case: TestCase) -> dict[str, str]:
    return {k.strip().lower(): v for k, v in test_case.values.items()}


def execute_test_case(
    plugin: Plugin,
    test_case: TestCase,
    anchor: tuple[int, int],
) -> None:
    anchor_x, anchor_y = anchor
    lookup = _build_lookup(test_case)

    for field_def in plugin.fields:
        value = lookup.get(field_def.field.strip().lower(), "")
        actions = _parse_actions(value)
        abs_x = anchor_x + field_def.cor_x
        abs_y = anchor_y + field_def.cor_y

        for action_type, payload in actions:
            if action_type == "empty":
                pass

            elif action_type == "click":
                pyautogui.moveTo(abs_x, abs_y, duration=0.1)
                pyautogui.click()

            elif action_type == "doubleclick":
                pyautogui.moveTo(abs_x, abs_y, duration=0.1)
                pyautogui.doubleClick()

            elif action_type == "key":
                pyautogui.press(payload)

            elif action_type == "text":
                pyperclip.copy(payload)
                pyautogui.click(abs_x, abs_y, clicks=3, interval=0.05)
                time.sleep(0.15)
                pyautogui.hotkey("ctrl", "v")

        time.sleep(field_def.pause)
