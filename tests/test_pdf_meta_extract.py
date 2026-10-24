import json
import shutil
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from pdf_factory import long_text, make_corrupt_pdf, make_long_dir, make_pdf

from pdfmetajson.pdf_meta_extract import PdfMetadataExtractor
from pdfmetajson.pdf_utils import long_path

SAMPLE_PDF = Path(__file__).parent / "data" / "sample.pdf"


class MyTestCase(unittest.TestCase):

    def test_pdf_exists(self):
        path_file = Path(__file__).parent / "data" / "sample.pdf"

        self.assertTrue(path_file.exists(), f"File {path_file} does't exist")

        try:
            with path_file.open("rb") as archivo:
                content = archivo.read(10)  # try to read the first 10 bytes
                self.assertGreater(len(content), 0, "The file it's empty or can't be readed")
        except Exception as e:
            self.fail(f"Unable to open file for reading: {e}")

    def test_pdf_metadata_extraction(self):
        try:
            filename = "sample.pdf"
            path_file = Path(__file__).parent / "data" / filename
            pdf_me = PdfMetadataExtractor(file_path=path_file)
            num_file = 1
            info = pdf_me.process(num_file)
            # file_date is the file's modification time, which changes on every checkout
            expected_file_date = datetime.fromtimestamp(path_file.stat().st_mtime).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            self.assertIsNotNone(info)
            self.assertEqual(info["file_num"], num_file)
            self.assertEqual(info["file_name_original"], filename)
            self.assertEqual(info["file_date"], expected_file_date)
            self.assertEqual(info["num_pages"], 1)
            self.assertIsNotNone(info["metadata"])
            self.assertEqual(info["metadata"]["author"], "Lorem Master")
            self.assertEqual(info["metadata"]["software"], "Microsoft® Word para Microsoft 365")
            self.assertEqual(info["metadata"]["title"], "Lorem Ipsum Test")
            self.assertEqual(info["metadata"]["subject"], "A Simple TEst")
            self.assertEqual(info["metadata"]["keywords"], "Tag01;Test")
            self.assertEqual(info["metadata"]["creation_date"], "2025-06-08")
            self.assertEqual(info["metadata"]["modification_date"], "2025-06-08")
            self.assertIsNotNone(info["content_sample"])
            self.assertIsNotNone(info["content_sample"]["page_1"])

        except Exception as e:
            self.fail(f"Unable to extract metadata from file. {e}")


class ExtractorRecordTestCase(unittest.TestCase):
    """Records built from generated PDFs (see tests/pdf_factory.py)."""

    RECORD_KEYS = {
        "file_num",
        "file_name_original",
        "file_date",
        "num_pages",
        "metadata",
        "content_sample",
    }

    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(long_path(self.tmp_dir), ignore_errors=True)

    def process(self, path, **kwargs):
        return PdfMetadataExtractor(path, **kwargs).process(1)

    def assert_error(self, record, code):
        self.assertEqual(set(record), self.RECORD_KEYS | {"error"})
        self.assertEqual(record["error"]["code"], code)
        self.assertTrue(record["error"]["message"])
        self.assertTrue(record["error"]["detail"])
        self.assertEqual(record["metadata"], {})
        self.assertEqual(record["content_sample"], {})

    def test_spanish_text_and_quotes_survive_extraction_and_json(self):
        text = (
            "Guía para la Gestión de Riesgos – Pequeñas Entidades\n"
            'Cita: "What If" en C:\\ruta (año 2019) — “fin”'
        )
        pdf = make_pdf(self.tmp_dir / "es.pdf", [text], {"/Title": "Guía práctica"})

        record = self.process(pdf)

        self.assertEqual(record["content_sample"], {"page_1": text})
        self.assertEqual(record["metadata"]["title"], "Guía práctica")
        round_trip = json.loads(json.dumps(record, ensure_ascii=False))
        self.assertEqual(round_trip["content_sample"]["page_1"], text)

    def test_pdf_without_metadata_has_empty_metadata(self):
        pdf = make_pdf(self.tmp_dir / "plain.pdf", ["Some text on the page"])

        with self.assertLogs(level="WARNING"):
            record = self.process(pdf)

        self.assertEqual(set(record), self.RECORD_KEYS)
        self.assertEqual(record["metadata"], {})

    def test_pdf_without_text_has_no_text_warning(self):
        pdf = make_pdf(self.tmp_dir / "scanned.pdf", ["", ""], {"/Title": "Scanned"})

        with self.assertLogs(level="WARNING"):
            record = self.process(pdf)

        self.assertEqual(record["num_pages"], 2)
        self.assertEqual(record["content_sample"], {})
        self.assertEqual(record["warnings"], [PdfMetadataExtractor.WARNING_NO_TEXT])
        self.assertNotIn("error", record)

    def test_default_sample_is_two_initial_pages_one_final_and_700_chars(self):
        pages = [long_text(f"page {n}", 2000) for n in range(1, 11)]
        pdf = make_pdf(self.tmp_dir / "book.pdf", pages, {"/Title": "Book"})

        sample = self.process(pdf)["content_sample"]

        self.assertEqual(list(sample), ["page_1", "page_2", "page_10"])
        self.assertTrue(all(len(text) == 700 for text in sample.values()))
        self.assertTrue(sample["page_1"].startswith("page 1 "))
        # The final page keeps its last characters
        self.assertTrue(pages[9].endswith(sample["page_10"]))

    def test_sample_size_is_configurable_and_blank_pages_are_skipped(self):
        pages = [long_text(f"page {n}", 2000) for n in range(1, 11)]
        pages[0] = pages[2] = ""
        pdf = make_pdf(self.tmp_dir / "book.pdf", pages, {"/Title": "Book"})

        sample = self.process(pdf, max_initial_pages=5, max_chars_per_page=1500)["content_sample"]

        self.assertEqual(
            list(sample), ["page_2", "page_4", "page_5", "page_6", "page_7", "page_10"]
        )
        self.assertTrue(all(len(text) == 1500 for text in sample.values()))

    def test_max_chars_zero_keeps_the_whole_page(self):
        text = long_text("page 1", 2000)
        pdf = make_pdf(self.tmp_dir / "page.pdf", [text], {"/Title": "Page"})

        sample = self.process(pdf, max_chars_per_page=0)["content_sample"]

        self.assertEqual(sample["page_1"], text)

    def test_file_with_path_longer_than_260_chars_is_read(self):
        long_dir = make_long_dir(self.tmp_dir, 280)
        pdf = long_dir / "sample.pdf"
        shutil.copyfile(SAMPLE_PDF, long_path(pdf))
        self.assertGreater(len(str(pdf)), 260)

        record = self.process(pdf)

        self.assertEqual(set(record), self.RECORD_KEYS)
        self.assertEqual(record["file_name_original"], "sample.pdf")
        self.assertEqual(record["num_pages"], 1)
        self.assertEqual(record["metadata"]["title"], "Lorem Ipsum Test")
        self.assertIn("page_1", record["content_sample"])

    def test_missing_file_gives_not_found_error(self):
        with self.assertLogs(level="ERROR") as logs:
            record = self.process(self.tmp_dir / "missing.pdf")

        self.assert_error(record, PdfMetadataExtractor.ERROR_NOT_FOUND)
        self.assertEqual(record["file_name_original"], "missing.pdf")
        self.assertIsNone(record["file_date"])
        self.assertIsNone(record["num_pages"])
        self.assertIn("missing.pdf", logs.output[0])

    def test_corrupt_file_gives_corrupt_error(self):
        pdf = make_corrupt_pdf(self.tmp_dir / "corrupt.pdf")

        with self.assertLogs(level="ERROR"):
            record = self.process(pdf)

        self.assert_error(record, PdfMetadataExtractor.ERROR_CORRUPT)
        self.assertIsNotNone(record["file_date"])

    def test_password_protected_file_gives_encrypted_error(self):
        pdf = make_pdf(self.tmp_dir / "locked.pdf", ["Secret text"], password="secret")

        with self.assertLogs(level="ERROR"):
            record = self.process(pdf)

        self.assert_error(record, PdfMetadataExtractor.ERROR_ENCRYPTED)

    def test_file_encrypted_with_empty_password_is_read(self):
        pdf = make_pdf(self.tmp_dir / "open.pdf", ["Readable text"], {"/Title": "T"}, "")

        record = self.process(pdf)

        self.assertNotIn("error", record)
        self.assertEqual(record["content_sample"], {"page_1": "Readable text"})


if __name__ == "__main__":
    unittest.main()
