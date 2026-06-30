from inserter import _build_lookup, _parse_actions
from models import TestCase


def _make_tc(values: dict) -> TestCase:
    return TestCase(values=values)


def test_lookup_is_case_insensitive():
    tc = _make_tc({"Name": "Peter", "Surname": "Corp"})
    lookup = _build_lookup(tc)
    assert lookup["name"] == "Peter"
    assert lookup["surname"] == "Corp"


def test_extra_excel_columns_not_in_lookup_conflict():
    # Extra columns (e.g. "Ref No", "Notes") exist in Excel but not in plugin.
    # They end up in the lookup but are never accessed because the plugin
    # only asks for its own field names.
    tc = _make_tc({"Ref No": "1", "Name": "Peter", "Surname": "Corp"})
    lookup = _build_lookup(tc)
    assert lookup.get("name") == "Peter"
    assert lookup.get("surname") == "Corp"
    # "ref no" is in the dict but never queried by the plugin fields
    assert lookup.get("ref no") == "1"


def test_missing_excel_column_returns_empty():
    tc = _make_tc({"Name": "Peter"})
    lookup = _build_lookup(tc)
    # "email" column absent from Excel — should return "" not crash
    assert lookup.get("email", "") == ""


# --- _parse_actions tests ---

def test_parse_empty_returns_empty():
    assert _parse_actions("") == [("empty", "")]
    assert _parse_actions("   ") == [("empty", "")]


def test_parse_plain_text():
    assert _parse_actions("Peter") == [("text", "Peter")]


def test_parse_single_click():
    assert _parse_actions("[CLK]") == [("click", "")]


def test_parse_single_click_case_insensitive():
    assert _parse_actions("[clk]") == [("click", "")]


def test_parse_double_click():
    assert _parse_actions("[DBCLK]") == [("doubleclick", "")]


def test_parse_keyboard_tokens():
    assert _parse_actions("[ESC]") == [("key", "escape")]
    assert _parse_actions("[TAB]") == [("key", "tab")]
    assert _parse_actions("[ENTER]") == [("key", "enter")]
    assert _parse_actions("[SPACE]") == [("key", "space")]


def test_parse_chained_tokens():
    assert _parse_actions("[CLK][ESC]") == [("click", ""), ("key", "escape")]


def test_parse_chained_click_enter():
    assert _parse_actions("[CLK][ENTER]") == [("click", ""), ("key", "enter")]


def test_parse_text_then_token():
    assert _parse_actions("hello[TAB]") == [("text", "hello"), ("key", "tab")]


def test_parse_token_then_text():
    assert _parse_actions("[CLK]world") == [("click", ""), ("text", "world")]


def test_parse_unknown_token_becomes_text():
    assert _parse_actions("[UNKNOWN]") == [("text", "[UNKNOWN]")]


def test_parse_multiple_keys():
    assert _parse_actions("[TAB][TAB][ENTER]") == [
        ("key", "tab"), ("key", "tab"), ("key", "enter")
    ]
