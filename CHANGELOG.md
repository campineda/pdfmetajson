# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.6.0] - 2026-10-24

### Added

- `--initial-pages`, `--final-pages` and `--max-chars` set the size of the content sample
  (defaults: 2, 1 and 700, as before; `--max-chars 0` keeps the whole page).
- `-o/--output-dir` writes the JSON files to another directory, created if missing (default:
  the input directory).
- Records of files that can't be read have an `error` field with `code`, `message` and
  `detail`. Codes: `not_found`, `permission_denied`, `encrypted`, `corrupt`, `os_error`,
  `unexpected`.
- Records whose sample is limited have a `warnings` list: `no_text` (probably a scanned PDF),
  `page_errors` (some pages failed to extract).
- Exit code `3` when the run finishes but some records have an `error` field, and a summary of
  the errors at the end of the log.
- Exit codes and record fields are documented in the README.
- pytest in the `dev` dependencies; CI runs the tests with pytest.

### Changed

- The content sample keeps the Unicode text as pypdf returns it (accents, `ñ`, dashes, typographic
  quotes), normalized to NFC, instead of converting it to ASCII.
- `metadata` and `content_sample` are always present in a record (`{}` when empty).
- `file_num` counts every PDF found, including those that can't be read, so it no longer
  repeats after an error.

### Removed

- The `Unidecode` dependency.

### Fixed

- PDFs with paths longer than 260 characters on Windows were reported as `File  not found`
  (without the file name) and left out of the output. Directories with long paths work too.
- Encrypted, corrupt or otherwise unreadable PDFs were left out of the output without a trace in
  the JSON; they now get a record with `error`.
- No JSON file was written when none of the PDFs could be read.

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

[Unreleased]: https://github.com/campineda/pdfmetajson/compare/v0.6.0...HEAD
[0.6.0]: https://github.com/campineda/pdfmetajson/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/campineda/pdfmetajson/compare/v0.4.1...v0.5.0
[0.4.1]: https://github.com/campineda/pdfmetajson/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/campineda/pdfmetajson/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/campineda/pdfmetajson/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/campineda/pdfmetajson/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/campineda/pdfmetajson/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/campineda/pdfmetajson/releases/tag/v0.1.0
