"""Builds small PDFs for the tests, so each test shows the text it expects to find."""

import os
from pathlib import Path

from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

from pdfmetajson.pdf_utils import long_path

PAGE_WIDTH = 612
PAGE_HEIGHT = 792


def _escape(text):
    # Helvetica with WinAnsiEncoding covers Spanish letters, dashes and typographic quotes
    text = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    return text.encode("cp1252")


def _add_text_page(writer, font, text):
    page = writer.add_blank_page(PAGE_WIDTH, PAGE_HEIGHT)
    if not text:
        return
    lines = b"".join(b"(" + _escape(line) + b") Tj T* " for line in text.split("\n"))
    content = DecodedStreamObject()
    content.set_data(b"BT /F1 8 Tf 10 TL 40 760 Td " + lines + b"ET")
    page[NameObject("/Contents")] = writer._add_object(content)
    page[NameObject("/Resources")] = DictionaryObject(
        {NameObject("/Font"): DictionaryObject({NameObject("/F1"): font})}
    )


def make_pdf(path, pages, metadata=None, password=None):
    """
    Writes a PDF with one page per item of ``pages``.

    Args:
        path: Destination file; long paths are supported.
        pages: Text of each page (lines separated by "\\n"); "" or None makes a blank page.
        metadata: Document info such as {"/Title": "..."}; None writes no info dictionary.
        password: If given, the PDF is encrypted (AES-256) with this user password.

    Returns:
        Path: The path of the PDF.
    """
    writer = PdfWriter()
    font = writer._add_object(
        DictionaryObject(
            {
                NameObject("/Type"): NameObject("/Font"),
                NameObject("/Subtype"): NameObject("/Type1"),
                NameObject("/BaseFont"): NameObject("/Helvetica"),
                NameObject("/Encoding"): NameObject("/WinAnsiEncoding"),
            }
        )
    )
    for text in pages:
        _add_text_page(writer, font, text)
    writer.metadata = None
    if metadata:
        writer.add_metadata(metadata)
    if password is not None:
        writer.encrypt(user_password=password, owner_password=password, algorithm="AES-256")
    with open(long_path(path), "wb") as f:
        writer.write(f)
    return Path(path)


def make_corrupt_pdf(path, size=2048):
    """Writes random bytes with a .pdf name."""
    with open(long_path(path), "wb") as f:
        f.write(os.urandom(size))
    return Path(path)


def long_text(label, num_chars):
    """Text of at least ``num_chars`` characters in lines of 80, starting with ``label``."""
    line = (label + " " + "lorem ipsum dolor sit amet " * 4)[:80]
    num_lines = num_chars // len(line) + 1
    return "\n".join(f"{line[:-4]}{n:04d}" for n in range(num_lines))


def make_long_dir(base, min_length):
    """Creates nested directories under ``base`` until the path has ``min_length`` characters."""
    path = Path(base)
    while len(str(path)) < min_length:
        path = path / ("d" * 60)
        os.mkdir(long_path(path))
    return path
