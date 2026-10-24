# Application code (`src/`, `main.py`)

## Logging

- Each module or class uses `logging.getLogger(__name__)`; never configure handlers outside
  `configure_logging()`, which is called once from `main.py`.
- Levels: DEBUG for diagnostics and parameter values, INFO for flow and per-file progress,
  WARNING for recoverable data issues, ERROR for failures that don't stop the run, CRITICAL for
  fatal errors.
- `-v` sets DEBUG with a detailed format, `-q` sets ERROR; keep pypdf's noisy loggers silenced in
  `configure_logging()`.

## Errors and robustness

- One bad PDF must never stop the run: catch per file, log ERROR with the file name, log the last
  traceback frame (`traceback.extract_tb`) at DEBUG, and continue.
- Repeated per-page errors are aggregated with `collections.Counter` and summarized once.
- Input problems raise `ValidationError` (from `src.validators`); `main.py` turns it into a
  user-friendly message.
- Handle empty directories and unreadable files explicitly; check permissions with `os.access()`.
- Use context managers for every file handle.

## Classes and functions

- Constructors store parameters, create `self.logger`, and validate through a private
  `_validate_parameters()` that delegates to the validator classes.
- Validators are classes of `@staticmethod`s returning the normalized value or raising
  `ValidationError`.
- Public methods for the main operations, `_private` helpers for internals; type hints on new code.
- Docstrings use the Google style (`Args:`, `Returns:`, `Raises:`).
- Size limits are class constants (e.g. `MAX_CHARS_PER_PAGE`); process files in batches to bound
  memory.

## CLI (`src/cli.py`)

- App name, version, and description come from `importlib.metadata` (fallback `"unknown"`).
- Validate arguments at the CLI level with `parser.error()` for immediate feedback.
- `--verbose` and `--quiet` are mutually exclusive.
