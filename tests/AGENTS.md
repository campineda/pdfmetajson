# Tests (`tests/`)

- Framework: `unittest`. Run from the repository root: `python -m unittest discover tests`.
- Test files are named `test_*.py`; test methods describe the behavior (`test_<what>_<expected>`).
- Test PDFs live in `tests/data/`; build paths with `Path(__file__).parent / "data" / "file.pdf"`.
- Check that a fixture exists and is readable before testing behavior that depends on it.
- Prefer assertions on returned values over printing them.
