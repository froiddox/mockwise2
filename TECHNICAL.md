# TECHNICAL.md — Technical Specification

## Purpose

A CLI tool that reads test cases from an Excel (.xlsx) file and inserts them into a target system. Intended to replace manual test case entry and serve as a repeatable, auditable data-loading pipeline.

---

## Runtime Requirements
Python version : 3.13.x 
Platform : Windows (primary), cross-platform where possible 
Package manager : pip + venv 

---

## Proposed Project Structure

```
mockwise2/
├── CLAUDE.md
├── TECHNICAL.md
├── README.md
├── pyproject.toml          # build metadata and dependencies
├── .env.example            # template for environment variables
├── config/
│   └── settings.toml       # column mapping, target config, etc.
├── src/
│   ├── main.py             # CLI entry point
│   ├── reader.py           # Excel reading and validation
│   ├── models.py           # TestCase dataclass / schema
│   ├── inserter.py         # insertion logic (DB, API, etc.)
│   └── utils.py            # shared helpers
└── tests/
    ├── conftest.py
    ├── test_reader.py
    └── test_inserter.py
```

---

## Excel Input Format

The tool expects a `.xlsx` file with a header row. The exact column names are configurable in `config/settings.toml`. A typical layout:

| Column | Description | Required |
|---|---|---|
| `test_id` | Unique test case identifier | Yes |
| `title` | Short description of the test | Yes |
| `steps` | Step-by-step instructions (can be multi-line) | Yes |
| `expected_result` | Expected outcome | Yes |
| `priority` | High / Medium / Low | No |
| `tags` | Comma-separated labels | No |
| `status` | Draft / Ready / Deprecated | No |

> Column names above are placeholders — update `config/settings.toml` to match the actual Excel headers.

---

## Data Flow

```
Excel file (.xlsx)
       │
       ▼
 reader.py          ← validates sheet name, required columns, data types
       │
       ▼
 models.py          ← parses rows into TestCase objects
       │
       ▼
 inserter.py        ← writes to target system (DB / API / TMS)
       │
       ▼
 Console report     ← inserted count, skipped rows, error list
```

---

## Configuration (`config/settings.toml`)

```toml
[excel]
sheet_name = "Test Cases"    # which sheet to read; 0 = first sheet
header_row = 1               # 1-based row index of the header

[columns]
# Map logical field name → actual Excel column header
test_id        = "Test ID"
title          = "Title"
steps          = "Steps"
expected_result = "Expected Result"
priority       = "Priority"
tags           = "Tags"
status         = "Status"

[target]
# Fill in once the insertion target is decided
type = "database"            # "database" | "api" | "file"
# connection_string = ""
# api_url = ""
```

---

## CLI Interface

```
usage: main.py [-h] --input INPUT [--sheet SHEET] [--dry-run] [--verbose]

options:
  --input    Path to the Excel file
  --sheet    Sheet name or index (overrides config)
  --dry-run  Parse and validate only; do not insert
  --verbose  Print each row as it is processed
```

---

## Error Handling Strategy

- Missing required columns → exit with a clear message listing the missing columns
- Empty / blank required fields → skip the row, log a warning, continue
- Duplicate `test_id` → configurable: skip, overwrite, or error
- Target system unreachable → exit immediately with the connection error

---

## Testing Strategy

- Unit tests for `reader.py` using fixture `.xlsx` files in `tests/fixtures/`
- Unit tests for `models.py` covering edge cases (empty cells, special characters)
- Integration tests for `inserter.py` against a local test target (mock or real)
- Run with: `pytest tests/ -v`

---

## Open Questions (to resolve before coding)

1. **Insertion target**: database (which engine?), REST API, or a test management system (Jira Xray, TestRail, Azure DevOps)?
2. **Authentication**: connection string, API key, OAuth?
3. **Duplicate handling policy**: skip, overwrite, or error?
4. **Multi-sheet support**: single sheet only, or iterate all sheets?
5. **Output**: console only, or also write a CSV/log report file?
