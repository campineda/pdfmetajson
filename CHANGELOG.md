# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Shared agent instructions for GitHub Copilot and Claude Code (`AGENTS.md`, `src/AGENTS.md`,
  `tests/AGENTS.md`).
- This changelog.

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

[Unreleased]: https://github.com/campineda/pdfmetajson/compare/v0.4.1...HEAD
[0.4.1]: https://github.com/campineda/pdfmetajson/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/campineda/pdfmetajson/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/campineda/pdfmetajson/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/campineda/pdfmetajson/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/campineda/pdfmetajson/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/campineda/pdfmetajson/releases/tag/v0.1.0
