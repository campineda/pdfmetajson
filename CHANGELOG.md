# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.5.0] - 2026-10-24

### Added

- `pdfmetajson` console command and `python -m pdfmetajson`; `python main.py` still works from
  the repository root once the package is installed.
- CI workflow (GitHub Actions) running black, isort, flake8 and the tests on Linux and Windows
  with Python 3.13 and 3.14.
- pre-commit hooks (black, isort, flake8 and basic file checks) and Dependabot updates.
- Tests for the CLI arguments and the text and date utilities.
- Shared agent instructions for GitHub Copilot and Claude Code (`AGENTS.md`, `src/AGENTS.md`,
  `tests/AGENTS.md`).
- This changelog.

### Changed

- The code is now the `pdfmetajson` package (`src/pdfmetajson/`). It no longer installs generic
  top-level modules such as `cli` or `validators`, which could clash with other packages.
- `cryptography` is pulled in through `pypdf[crypto]` instead of being a direct dependency.
- The application name is shown as `PdfMetaJson` (was `Pdfmetajson`), and error messages go to
  stderr with a non-zero exit code.
- `-n/--numfiles` and `-l/--limit` now require a value; `0` means no limit (documented in
  `--help`).
- Removed the unused `ProcessingValidator` and `OutputValidator` classes.

### Fixed

- `--version` could show a stale version (`0.1.0`) when run from the repository root.
- Validation errors raised while processing were reported as unexpected errors with a traceback
  instead of a friendly message.
- Files with an uppercase `.PDF` extension were skipped on case-sensitive file systems.
- A PDF that could not be opened was written to the JSON output as `null`.
- An empty JSON file was written when the number of PDFs was an exact multiple of `--limit`.
- Double quotes and backslashes in the content sample were escaped twice, so the JSON contained
  `\"` instead of `"`.
- `-n` or `-l` without a value crashed with a `TypeError`.

## [0.4.1] - 2025-08-23

### Fixed

- "no such group" warnings raised by some PDFs; the text of those pages is now extracted
  correctly.

### Changed

- Clearer error and validation messages; more detail in debug logs.
- Improved handling of the output directory.
- Adjusted the date regular expression and cleaned up text utilities.
- Code style line length raised from 88 to 100 (black, isort, flake8).

## [0.4.0] - 2025-08-17

### Added

- `README.md` with features, installation, usage examples and sample JSON output.

### Changed

- Shorter help text for `-l/--limit`.

## [0.3.0] - 2025-08-16

### Changed

- Upgraded pypdf from 5.6.0 to 6.0.0 for better interpretation of the content of some PDFs.

## [0.2.1] - 2025-08-16

### Added

- `cryptography` dependency, required by pypdf to read some encrypted PDFs.

### Changed

- Simplified and unified debug messages when PDF pages cannot be read, with more error details.
- Clearer wording in some warning messages.

### Fixed

- Date conversion for some specific date formats.

## [0.2.0] - 2025-06-15

### Fixed

- Infinite loop in the index-cleaning regular expression (`clean_index_text`).
- When a page cannot be read, the next page is tried, up to a maximum number of attempts.
- When the content of a PDF cannot be read, the metadata obtained so far is still returned.
- Debug logs from the validators module are silenced.

## [0.1.0] - 2025-06-15

### Added

- First functional version: scans a directory for PDFs, extracts metadata and a content sample
  from the first and last pages, and writes the results in batches to `out_<dirname>_NN.json`.
- CLI with `PATH`, `-n/--numfiles`, `-l/--limit`, `-v/--verbose`, `-q/--quiet` and `--version`.
- Colored logging based on the standard `logging` module (colorlog); pypdf warnings silenced.
- Configuration and dependencies in `pyproject.toml`.
- MIT license.

[Unreleased]: https://github.com/campineda/pdfmetajson/compare/v0.5.0...HEAD
[0.5.0]: https://github.com/campineda/pdfmetajson/compare/v0.4.1...v0.5.0
[0.4.1]: https://github.com/campineda/pdfmetajson/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/campineda/pdfmetajson/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/campineda/pdfmetajson/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/campineda/pdfmetajson/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/campineda/pdfmetajson/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/campineda/pdfmetajson/releases/tag/v0.1.0
