# CLAUDE.md — Project Guide for Claude Code

## Project Overview

**mockwise2** is a Python-based testing tool that reads Excel files as input and performs test case insertion. It is designed to streamline the process of loading structured test data from Excel sheets and inserting it into a target system (e.g., a database, API, or test management platform).

## Language & Runtime

- **Python 3.13.x** (no earlier versions)
- Use built-in `venv` for virtual environments

## Key Conventions

- All source code lives under `src/`
- Entry point: `src/main.py`
- Configuration: `config/settings.toml` or `.env` (TBD)
- Tests: `tests/` using `pytest`

## Dependencies (expected — confirm before installing)

- `openpyxl` or `pandas` — Excel file reading
- `pytest` — test runner
- Any DB/API client library depending on the insertion target (TBD)

## Running the Tool

```bash
python src/main.py --input path/to/testcases.xlsx
```

## Development Notes

- Confirm the insertion target (database, REST API, test management system) before implementing the write layer.
- Excel column mapping to test case fields must be defined in a config file, not hardcoded.
- Validate Excel structure on load and report clear errors for malformed files.

## Out of Scope (for now)

- GUI or web interface
- Real-time file watching
- Multi-file batch processing (may be added later)
