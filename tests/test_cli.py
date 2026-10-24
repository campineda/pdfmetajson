import contextlib
import io
import unittest
from pathlib import Path

from pdfmetajson import PACKAGE_NAME
from pdfmetajson.cli import CommandLineInterface
from pdfmetajson.pdf_meta_json import PdfMetaJson


class CommandLineInterfaceTestCase(unittest.TestCase):

    def setUp(self):
        self.cli = CommandLineInterface(PACKAGE_NAME)
        self.data_dir = str(Path(__file__).parent / "data")

    def parse_error(self, argv):
        """Parse argv expecting argparse to exit with an error; return its stderr."""
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr), self.assertRaises(SystemExit) as cm:
            self.cli.parse_arguments(argv)
        self.assertEqual(cm.exception.code, 2)
        return stderr.getvalue()

    def test_defaults(self):
        args = self.cli.parse_arguments([self.data_dir])
        self.assertEqual(args.numfiles, PdfMetaJson.DEFAULT_MAX_NUM_FILES)
        self.assertEqual(args.limit, PdfMetaJson.DEFAULT_RECORD_LIMIT)
        self.assertFalse(args.verbose)
        self.assertFalse(args.quiet)
        self.assertIsNone(args.output_dir)
        self.assertEqual(args.initial_pages, PdfMetaJson.DEFAULT_INITIAL_PAGES)
        self.assertEqual(args.final_pages, PdfMetaJson.DEFAULT_FINAL_PAGES)
        self.assertEqual(args.max_chars, PdfMetaJson.DEFAULT_MAX_CHARS)

    def test_current_sample_size_is_the_default(self):
        self.assertEqual(
            (
                PdfMetaJson.DEFAULT_INITIAL_PAGES,
                PdfMetaJson.DEFAULT_FINAL_PAGES,
                PdfMetaJson.DEFAULT_MAX_CHARS,
            ),
            (2, 1, 700),
        )

    def test_sample_options(self):
        args = self.cli.parse_arguments(
            [self.data_dir, "--initial-pages", "5", "--final-pages", "0", "--max-chars", "1500"]
        )
        self.assertEqual((args.initial_pages, args.final_pages, args.max_chars), (5, 0, 1500))

    def test_negative_sample_options_are_rejected(self):
        for option in ("--initial-pages", "--final-pages", "--max-chars"):
            self.assertIn(option, self.parse_error([self.data_dir, option, "-1"]))

    def test_output_dir_option(self):
        args = self.cli.parse_arguments([self.data_dir, "-o", "results"])
        self.assertEqual(args.output_dir, "results")

    def test_output_dir_that_is_a_file_is_rejected(self):
        sample = str(Path(self.data_dir) / "sample.pdf")
        self.assertIn("is a file", self.parse_error([self.data_dir, "--output-dir", sample]))

    def test_zero_means_no_limit(self):
        args = self.cli.parse_arguments([self.data_dir, "-n", "0", "-l", "0"])
        self.assertEqual((args.numfiles, args.limit), (0, 0))

    def test_option_without_value_is_rejected(self):
        self.assertIn("expected one argument", self.parse_error([self.data_dir, "-n"]))
        self.assertIn("expected one argument", self.parse_error([self.data_dir, "-l"]))

    def test_negative_values_are_rejected(self):
        self.assertIn("numfiles", self.parse_error([self.data_dir, "-n", "-1"]))
        self.assertIn("limit", self.parse_error([self.data_dir, "-l", "-1"]))

    def test_missing_directory_is_rejected(self):
        self.assertIn("does not exist", self.parse_error([self.data_dir + "_missing"]))

    def test_verbose_and_quiet_are_exclusive(self):
        self.assertIn("not allowed", self.parse_error([self.data_dir, "-v", "-q"]))


if __name__ == "__main__":
    unittest.main()
