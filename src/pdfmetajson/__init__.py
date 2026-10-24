"""Scan a directory for PDF files and export their metadata and a content sample to JSON."""

import importlib.metadata

PACKAGE_NAME = "PdfMetaJson"

try:
    __version__ = importlib.metadata.version(PACKAGE_NAME)
except importlib.metadata.PackageNotFoundError:
    __version__ = "unknown"
