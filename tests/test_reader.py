import openpyxl
from pathlib import Path

from reader import read_excel


def _make_workbook(tmp_path: Path, sheets: dict[str, list[list]]) -> str:
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    for sheet_name, rows in sheets.items():
        ws = wb.create_sheet(title=sheet_name)
        for row in rows:
            ws.append(row)
    path = str(tmp_path / "test.xlsx")
    wb.save(path)
    return path


def test_basic_read(tmp_path):
    path = _make_workbook(tmp_path, {
        "fx interbank": [
            ["Trade Date", "Amount"],
            ["2024-01-15", "1000000"],
        ]
    })
    results = read_excel(path)
    assert len(results) == 1
    sheet_name, cases = results[0]
    assert sheet_name == "fx interbank"
    assert len(cases) == 1
    assert cases[0].values["Trade Date"] == "2024-01-15"
    assert cases[0].values["Amount"] == "1000000"


def test_blank_row_ends_data(tmp_path):
    path = _make_workbook(tmp_path, {
        "test": [
            ["Name"],
            ["Alice"],
            [""],        # blank row — stops here
            ["Bob"],     # should be ignored
        ]
    })
    _, cases = read_excel(path)[0]
    assert len(cases) == 1
    assert cases[0].values["Name"] == "Alice"


def test_multiple_sheets(tmp_path):
    path = _make_workbook(tmp_path, {
        "screen a": [["Field1"], ["val1"]],
        "screen b": [["Field2"], ["val2"]],
    })
    results = read_excel(path)
    names = [r[0] for r in results]
    assert "screen a" in names
    assert "screen b" in names


def test_sheet_name_lowercased(tmp_path):
    path = _make_workbook(tmp_path, {
        "FX Interbank": [["Field"], ["value"]],
    })
    results = read_excel(path)
    assert results[0][0] == "fx interbank"


def test_event_token_preserved(tmp_path):
    path = _make_workbook(tmp_path, {
        "test": [["Button"], ["[CLK]"]],
    })
    _, cases = read_excel(path)[0]
    assert cases[0].values["Button"] == "[CLK]"


def test_empty_leading_column_does_not_shift_values(tmp_path):
    # Column A header is empty; Name is in column B, value must not shift left.
    path = _make_workbook(tmp_path, {
        "test": [
            [None, "Name", "Surname"],
            ["1",  "Peter", "Corp"],
        ]
    })
    _, cases = read_excel(path)[0]
    assert cases[0].values["Name"] == "Peter"
    assert cases[0].values["Surname"] == "Corp"
    assert "Name" in cases[0].values
    assert cases[0].values.get("Name") != "1"


def test_row_index_is_populated(tmp_path):
    path = _make_workbook(tmp_path, {
        "test": [
            ["Name"],
            ["Alice"],   # row 2
            ["Bob"],     # row 3
        ]
    })
    _, cases = read_excel(path)[0]
    assert cases[0].row_index == 2
    assert cases[1].row_index == 3


def test_done_rows_are_skipped(tmp_path):
    path = _make_workbook(tmp_path, {
        "test": [
            ["Name", "Status"],
            ["Alice", "Done"],
            ["Bob",   ""],
            ["Carol", "done"],   # case-insensitive
        ]
    })
    _, cases = read_excel(path)[0]
    assert len(cases) == 1
    assert cases[0].values["Name"] == "Bob"


def test_status_column_excluded_from_values(tmp_path):
    path = _make_workbook(tmp_path, {
        "test": [
            ["Name", "Status"],
            ["Alice", ""],
        ]
    })
    _, cases = read_excel(path)[0]
    assert "Status" not in cases[0].values
    assert "status" not in cases[0].values
