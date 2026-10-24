# Tests (`tests/`)

- Framework: `unittest` test cases, run with pytest (`python -m pytest`) or
  `python -m unittest discover tests` from the repository root.
- Test files are named `test_*.py`; test methods describe the behavior (`test_<what>_<expected>`).
- Test PDFs live in `tests/data/`; build paths with `Path(__file__).parent / "data" / "file.pdf"`.
- Prefer generating PDFs in a temporary directory with `tests/pdf_factory.py` (`make_pdf`,
  `make_corrupt_pdf`, `make_long_dir`, `long_text`), imported as `from pdf_factory import ...`, so
  each test shows the text it expects; don't commit new binary fixtures unless a real PDF is needed.
- Remove temporary directories with `shutil.rmtree(long_path(path), ignore_errors=True)`.
- Check that a fixture exists and is readable before testing behavior that depends on it.
- Prefer assertions on returned values over printing them.
