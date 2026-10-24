# -*- coding: utf-8 -*-
# main.py
# Convenience entry point for running from the repository root. Requires the package to be
# installed (`pip install -e .`); otherwise use the `pdfmetajson` command or
# `python -m pdfmetajson`.
import sys

from pdfmetajson.__main__ import main

if __name__ == "__main__":
    sys.exit(main())
