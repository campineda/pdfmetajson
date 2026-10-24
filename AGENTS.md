# PdfMetaJson

CLI utility that scans a directory for `.pdf` files, extracts metadata and a text sample from the
first/last pages, and writes the results in batches to `out_<dirname>_NN.json` files.

More specific guidance lives next to the code and is loaded when working there:
`src/AGENTS.md` (application code) and `tests/AGENTS.md` (tests).

## Commands

Run everything from the repository root. The code is the `pdfmetajson` package under `src/`
(src layout), so it must be installed (`pip install -e`) before running it or its tests.

```bash
python -m venv .venv
.venv\Scripts\activate              # Windows (source .venv/bin/activate on Unix)
pip install -e ".[dev]"             # project + black, isort, flake8 (+ Flake8-pyproject), pre-commit
pre-commit install                  # once: hooks run black, isort, flake8 on every commit

pdfmetajson [PATH] [-n NUMFILES] [-l LIMIT] [-o OUTPUT_DIR] [--initial-pages N] [--final-pages N]
            [--max-chars N] [-v | -q]                 # or: python -m pdfmetajson / python main.py
python -m pytest                    # or: python -m unittest discover tests
pre-commit run --all-files          # or: black . && isort . && flake8
```

`-n 0`, `-l 0` and `--max-chars 0` mean "no limit" (`--initial-pages 0` / `--final-pages 0` sample
no pages); defaults are `PdfMetaJson.DEFAULT_*` constants, shared by the CLI. Exit codes: 0 ok,
1 validation or unexpected error, 2 invalid arguments (argparse), 3 some records have `error`.

## Layout

- `src/pdfmetajson/__main__.py` — `main()`: CLI → logging → `PdfMetaJson.process_directory()`;
  exposed as the `pdfmetajson` console script (`[project.scripts]`)
- `main.py` — thin wrapper around `pdfmetajson.__main__.main` for running from the repo root
- `src/pdfmetajson/__init__.py` — `PACKAGE_NAME` and `__version__` (from package metadata)
- `src/pdfmetajson/cli.py` — `CommandLineInterface`: argparse, version/name from package metadata
- `src/pdfmetajson/logging_config.py` — `configure_logging()`, colorlog on the root logger
- `src/pdfmetajson/pdf_meta_json.py` — `PdfMetaJson`: directory loop, batching, JSON output
- `src/pdfmetajson/pdf_meta_extract.py` — `PdfMetadataExtractor`: metadata + content sample of one PDF (pypdf)
- `src/pdfmetajson/pdf_utils.py` — date conversion, text cleaning and `long_path()` helpers
- `src/pdfmetajson/validators.py` — `ValidationError` and static validator classes
- `tests/` — unittest suite (run with pytest or unittest); `tests/pdf_factory.py` builds test PDFs;
  `tests/data/` sample PDFs
- `.github/workflows/ci.yml` — lint + tests (Linux, Windows; Python 3.13, 3.14) on every push and PR
- `.github/dependabot.yml` — monthly grouped update PRs for pip dependencies and GitHub Actions
- `.pre-commit-config.yaml` — commit hooks; keep its black/isort/flake8 revs close to the dev
  versions installed by pip
- `samples-pdf/` — local PDFs for manual testing; git-ignored (size and copyright), never commit it

## Conventions

- Python >= 3.13. All dependencies and tool settings live in `pyproject.toml`
  (no `setup.py` / `requirements.txt`).
- Black and isort (profile `black`), line length 100; flake8 ignores E203, W503.
- Double quotes, f-strings, trailing commas in multi-line structures, PEP 8 names.
- Imports grouped: standard library, third party, local (`from pdfmetajson.module import Name`).
  Always use absolute `pdfmetajson.` imports; never import modules by their bare name.
- Use `pathlib.Path` for paths; convert to `str` only when an API requires it.
- Dependency pins: `>=` for core libraries, `~=` for patch-level compatibility; exact pins only
  when needed for stability.
- When the CLI or output format changes, update `README.md` (features, usage examples, sample JSON,
  record fields, error/warning codes, exit codes).
- The record schema is a contract with consumers (e.g. ebooks-organizer): keep every key present,
  don't rename keys or `error`/`warnings` codes without a changelog entry.

## Versioning and changelog

- Semantic Versioning; the single source of the version is `version` in `pyproject.toml`.
- `CHANGELOG.md` follows Keep a Changelog. Every user-visible change adds an entry under
  `## [Unreleased]` (`Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`).
  Internal-only changes (refactors, tooling) don't need an entry.
- On release: bump `version`, rename `[Unreleased]` to `[X.Y.Z] - YYYY-MM-DD`, add a new empty
  `[Unreleased]`, update the compare links at the bottom, and tag the commit `vX.Y.Z`.
