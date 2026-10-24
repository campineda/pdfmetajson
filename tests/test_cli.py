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
