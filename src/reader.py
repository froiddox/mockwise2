import openpyxl

from models import TestCase


def read_excel(file_path: str) -> list[tuple[str, list[TestCase]]]:
    """
    Returns (plugin_key, test_cases) for every sheet in the workbook.
    - plugin_key is the sheet title lowercased/stripped for plugin matching.
    - Rows whose 'Status' column contains 'Done' (case-insensitive) are skipped.
    - The 'Status' column is excluded from TestCase.values (it is internal metadata).
    - Each TestCase carries row_index (1-based Excel row) so the caller can write back.
    """
    wb = openpyxl.load_workbook(file_path, data_only=True)
    results: list[tuple[str, list[TestCase]]] = []

    for sheet in wb.worksheets:
        plugin_key = sheet.title.strip().lower()
        rows = list(sheet.iter_rows(values_only=True))

        if not rows:
            continue

        header_map: list[tuple[int, str]] = [
            (col_idx, str(cell).strip())
            for col_idx, cell in enumerate(rows[0])
            if cell is not None and str(cell).strip()
        ]

        if not header_map:
            continue

        # Locate the Status column so Done rows can be skipped
        status_col_idx: int | None = next(
            (idx for idx, name in header_map if name.lower() == "status"),
            None,
        )

        test_cases: list[TestCase] = []
        for row_num, row in enumerate(rows[1:], start=2):
            if all(cell is None or str(cell).strip() == "" for cell in row):
                break

            # Skip rows already marked Done
            if status_col_idx is not None:
                status_val = row[status_col_idx] if status_col_idx < len(row) else None
                if status_val and str(status_val).strip().lower() == "done":
                    continue

            values: dict[str, str] = {}
            for col_idx, header in header_map:
                if header.lower() == "status":
                    continue  # keep Status out of the values dict
                cell = row[col_idx] if col_idx < len(row) else None
                values[header] = str(cell).strip() if cell is not None else ""

            test_cases.append(TestCase(values=values, row_index=row_num))

        results.append((plugin_key, test_cases))

    return results
