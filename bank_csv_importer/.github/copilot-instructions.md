# Copilot Instructions for Bank CSV Importer

## Project Overview
Bank CSV Importer is a Python console application for importing, validating, and analyzing bank CSV files.

## Development Guidelines
- Use type hints for all functions
- Add comprehensive docstrings
- Follow PEP 8 style guidelines
- Write unit tests for new features
- Validate user input at CLI boundary

## Common Tasks
- To add support for a new bank format, update `COLUMN_MAPPINGS` in `src/importer.py`
- CLI commands are defined in `src/cli.py` using Click decorators
- Core import logic is in the `BankCSVImporter` class
