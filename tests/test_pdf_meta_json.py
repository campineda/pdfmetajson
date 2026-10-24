import contextlib
import io
import json
import logging
import shutil
import tempfile
import unittest
from pathlib import Path

from pdf_factory import long_text, make_corrupt_pdf, make_long_dir, make_pdf

from pdfmetajson.__main__ import EXIT_ERROR, EXIT_FILE_ERRORS, EXIT_OK, main
from pdfmetajson.pdf_meta_json import PdfMetaJson
from pdfmetajson.pdf_utils import long_path
from pdfmetajson.validators import ValidationError


class PdfMetaJsonTestCase(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.sample_pdf = Path(__file__).parent / "data" / "sample.pdf"

    def tearDown(self):
        shutil.rmtree(long_path(self.tmp_dir), ignore_errors=True)

    def test_missing_directory_raises_validation_error(self):
        with self.assertRaises(ValidationError), self.assertLogs(level="ERROR"):
            PdfMetaJson(input_dir=str(self.tmp_dir / "missing"))

    def test_process_directory_writes_batches(self):
        for name in ("a.pdf", "b.PDF", "c.pdf"):
            shutil.copy(self.sample_pdf, self.tmp_dir / name)

        PdfMetaJson(input_dir=str(self.tmp_dir), record_limit=2).process_directory()

        basename = f"out_{self.tmp_dir.name}"
        first = json.loads((self.tmp_dir / f"{basename}_01.json").read_text(encoding="utf-8"))
        second = json.loads((self.tmp_dir / f"{basename}_02.json").read_text(encoding="utf-8"))
        self.assertEqual(len(first), 2)
        self.assertEqual(len(second), 1)
        names = {record["file_name_original"] for record in first + second}
        self.assertEqual(names, {"a.pdf", "b.PDF", "c.pdf"})

    def test_exact_multiple_of_limit_writes_no_empty_batch(self):
        for name in ("a.pdf", "b.pdf"):
            shutil.copy(self.sample_pdf, self.tmp_dir / name)

        PdfMetaJson(input_dir=str(self.tmp_dir), record_limit=2).process_directory()

        outputs = sorted(p.name for p in self.tmp_dir.glob("out_*.json"))
        self.assertEqual(outputs, [f"out_{self.tmp_dir.name}_01.json"])

    def read_output(self, directory, basename=None):
        basename = basename or f"out_{self.tmp_dir.name}"
        output = Path(long_path(Path(directory) / f"{basename}_01.json"))
        return json.loads(output.read_text(encoding="utf-8"))

    def test_unreadable_files_keep_their_record_and_numbering(self):
        shutil.copy(self.sample_pdf, self.tmp_dir / "a.pdf")
        make_corrupt_pdf(self.tmp_dir / "b.pdf")
        shutil.copy(self.sample_pdf, self.tmp_dir / "c.pdf")

        with self.assertLogs(level="ERROR"):
            summary = PdfMetaJson(input_dir=self.tmp_dir, record_limit=0).process_directory()

        records = sorted(self.read_output(self.tmp_dir), key=lambda r: r["file_name_original"])
        self.assertEqual([r["file_name_original"] for r in records], ["a.pdf", "b.pdf", "c.pdf"])
        self.assertEqual(sorted(r["file_num"] for r in records), [1, 2, 3])
        self.assertEqual(records[1]["error"]["code"], "corrupt")
        self.assertNotIn("error", records[0])
        self.assertEqual((summary.num_files, summary.num_errors), (3, 1))
        self.assertEqual(summary.errors, {"corrupt": 1})

    def test_output_is_written_even_if_every_file_fails(self):
        make_corrupt_pdf(self.tmp_dir / "bad.pdf")

        with self.assertLogs(level="ERROR"):
            PdfMetaJson(input_dir=self.tmp_dir).process_directory()

        records = self.read_output(self.tmp_dir)
        self.assertEqual(len(records), 1)
        self.assertIn("error", records[0])

    def test_output_dir_is_created_and_input_dir_is_left_untouched(self):
        shutil.copy(self.sample_pdf, self.tmp_dir / "a.pdf")
        output_dir = self.tmp_dir / "results" / "batch_01"

        PdfMetaJson(input_dir=self.tmp_dir, output_dir=output_dir).process_directory()

        self.assertEqual(list(self.tmp_dir.glob("out_*.json")), [])
        records = self.read_output(output_dir)
        self.assertEqual(records[0]["file_name_original"], "a.pdf")

    def test_output_dir_that_is_a_file_raises_validation_error(self):
        not_a_dir = self.tmp_dir / "file.txt"
        not_a_dir.write_text("x")

        with self.assertRaises(ValidationError), self.assertLogs(level="ERROR"):
            PdfMetaJson(input_dir=self.tmp_dir, output_dir=not_a_dir)

    def test_directory_with_path_longer_than_260_chars_is_processed(self):
        long_dir = make_long_dir(self.tmp_dir, 280)
        shutil.copyfile(self.sample_pdf, long_path(long_dir / "sample.pdf"))

        summary = PdfMetaJson(input_dir=long_dir).process_directory()

        records = self.read_output(long_dir, f"out_{long_dir.name}")
        self.assertEqual(summary.num_errors, 0)
        self.assertEqual(records[0]["file_name_original"], "sample.pdf")
        self.assertEqual(records[0]["metadata"]["title"], "Lorem Ipsum Test")


class MainTestCase(unittest.TestCase):
    """Exit codes of the command."""

    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.sample_pdf = Path(__file__).parent / "data" / "sample.pdf"

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)
        # main() configures the root logger; leave it as the other tests expect
        logging.getLogger().handlers.clear()

    def run_main(self, *args):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return main(["-q", *args])

    def test_success_exits_with_0(self):
        shutil.copy(self.sample_pdf, self.tmp_dir / "a.pdf")
        self.assertEqual(self.run_main(str(self.tmp_dir)), EXIT_OK)

    def test_missing_directory_exits_with_2(self):
        with self.assertRaises(SystemExit) as cm:
            self.run_main(str(self.tmp_dir / "missing"))
        self.assertEqual(cm.exception.code, 2)

    def test_validation_error_exits_with_1(self):
        # The output directory can't be created inside a file
        not_a_dir = self.tmp_dir / "file.txt"
        not_a_dir.write_text("x")
        output_dir = str(not_a_dir / "out")
        self.assertEqual(self.run_main(str(self.tmp_dir), "-o", output_dir), EXIT_ERROR)

    def test_files_with_errors_exit_with_3(self):
        shutil.copy(self.sample_pdf, self.tmp_dir / "a.pdf")
        make_corrupt_pdf(self.tmp_dir / "b.pdf")
        self.assertEqual(self.run_main(str(self.tmp_dir)), EXIT_FILE_ERRORS)

    def test_sample_options_reach_the_output(self):
        pages = [long_text(f"page {n}", 2000) for n in range(1, 8)]
        make_pdf(self.tmp_dir / "book.pdf", pages, {"/Title": "Book"})
        output_dir = self.tmp_dir / "out"

        exit_code = self.run_main(
            str(self.tmp_dir),
            "--initial-pages",
            "5",
            "--final-pages",
            "0",
            "--max-chars",
            "1500",
            "--output-dir",
            str(output_dir),
        )

        self.assertEqual(exit_code, EXIT_OK)
        output = output_dir / f"out_{self.tmp_dir.name}_01.json"
        sample = json.loads(output.read_text(encoding="utf-8"))[0]["content_sample"]
        self.assertEqual(list(sample), [f"page_{n}" for n in range(1, 6)])
        self.assertTrue(all(len(text) == 1500 for text in sample.values()))


if __name__ == "__main__":
    unittest.main()
