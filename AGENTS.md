# PdfMetaJson

CLI utility that scans a directory for `.pdf` files, extracts metadata and a text sample from the
first/last pages, and writes the results in batches to `out_<dirname>_NN.json` files.

More specific guidance lives next to the code and is loaded when working there:
`src/AGENTS.md` (application code) and `tests/AGENTS.md` (tests).

## Commands

Run everything from the repository root (imports use the `src.` prefix).

```bash
python -m venv .venv
.venv\Scripts\activate              # Windows (source .venv/bin/activate on Unix)
pip install -e ".[dev]"             # project + black, isort, flake8

python main.py [PATH] [-n NUMFILES] [-l LIMIT] [-v | -q]
python -m unittest discover tests
black . && isort .
```

## Layout

- `main.py` — entry point: CLI → logging → `PdfMetaJson.process_directory()`
- `src/cli.py` — `CommandLineInterface`: argparse, version/name from package metadata
- `src/logging_config.py` — `configure_logging()`, colorlog on the root logger
- `src/pdf_meta_json.py` — `PdfMetaJson`: directory loop, batching, JSON output
- `src/pdf_meta_extract.py` — `PdfMetadataExtractor`: metadata + content sample of one PDF (pypdf)
- `src/pdf_utils.py` — date conversion and text cleaning helpers
- `src/validators.py` — `ValidationError` and static validator classes
- `tests/` — unittest suite; `tests/data/` sample PDFs
- `samples-pdf/` — PDFs and JSON outputs for manual testing and documentation

## Conventions

- Python >= 3.13. All dependencies and tool settings live in `pyproject.toml`
  (no `setup.py` / `requirements.txt`).
- Black and isort (profile `black`), line length 100; flake8 ignores E203, W503.
- Double quotes, f-strings, trailing commas in multi-line structures, PEP 8 names.
- Imports grouped: standard library, third party, local (`from src.module import Name`).
- Use `pathlib.Path` for paths; convert to `str` only when an API requires it.
- Dependency pins: `>=` for core libraries, `~=` for patch-level compatibility; exact pins only
  when needed for stability.
- When the CLI or output format changes, update `README.md` (features, usage examples, sample JSON).
