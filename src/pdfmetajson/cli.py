# src/pdfmetajson/cli.py
import argparse
import importlib.metadata
import os
from pathlib import Path

from pdfmetajson.pdf_meta_json import PdfMetaJson
from pdfmetajson.pdf_utils import long_path


class CommandLineInterface:

    def __init__(self, package_name):
        self.package_name = package_name
        self.app_name = self._get_app_name()
        self.app_version = self._get_version()
        self.app_description = self._get_description()
        self.parser = self._create_parser()

    def _get_app_name(self):
        try:
            return importlib.metadata.metadata(self.package_name)["Name"]
        except (importlib.metadata.PackageNotFoundError, KeyError):
            return self.package_name

    def _get_version(self):
        try:
            return importlib.metadata.version(self.package_name)
        except importlib.metadata.PackageNotFoundError:
            return "unknown"

    def _get_description(self):
        try:
            return importlib.metadata.metadata(self.package_name)["Summary"]
        except (importlib.metadata.PackageNotFoundError, KeyError):
            return ""

    def _create_parser(self):
        parser = argparse.ArgumentParser(
            prog=self.app_name,
            description=self.app_description,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="Thanks for using %(prog)s! :)",
        )

        parser.add_argument(
            "--version",
            action="version",
            version=f"{self.app_name} v{self.app_version}",
        )

        # Path
        # By default, is the current directory '.'
        parser.add_argument(
            "path",
            nargs="?",
            default=".",
            help="Input directory to scan .PDF files (default: %(default)s)",
        )
        # Max Files
        parser.add_argument(
            "-n",
            "--numfiles",
            type=int,
            default=PdfMetaJson.DEFAULT_MAX_NUM_FILES,
            help="max PDF files to process; 0 processes all (default: %(default)s)",
        )
        # Limit of registers per Output
        parser.add_argument(
            "-l",
            "--limit",
            type=int,
            default=PdfMetaJson.DEFAULT_RECORD_LIMIT,
            help="max records per JSON file; 0 writes a single file (default: %(default)s)",
        )

        # Output directory
        parser.add_argument(
            "-o",
            "--output-dir",
            default=None,
            help="directory for the JSON files, created if missing (default: the input path)",
        )
        # Content sample
        parser.add_argument(
            "--initial-pages",
            type=int,
            default=PdfMetaJson.DEFAULT_INITIAL_PAGES,
            help="pages with text sampled from the start; 0 samples none (default: %(default)s)",
        )
        parser.add_argument(
            "--final-pages",
            type=int,
            default=PdfMetaJson.DEFAULT_FINAL_PAGES,
            help="pages with text sampled from the end; 0 samples none (default: %(default)s)",
        )
        parser.add_argument(
            "--max-chars",
            type=int,
            default=PdfMetaJson.DEFAULT_MAX_CHARS,
            help="max characters per sampled page; 0 keeps the whole page (default: %(default)s)",
        )

        # Verbose or Quite
        verbosity = parser.add_mutually_exclusive_group()
        verbosity.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="shows detailed information about the process",
        )
        verbosity.add_argument(
            "-q",
            "--quiet",
            action="store_true",
            help="no display info, only errors ",
        )

        return parser

    def parse_arguments(self, argv=None):
        args = self.parser.parse_args(argv)
        self._validate_arguments(args)
        return args

    def _validate_arguments(self, args):
        """
        Performs basic argument validation at CLI level

        Args:
            args: Parsed arguments from argparse

        Raises:
            argparse.ArgumentTypeError: If validation fails
        """
        # Validate path argument
        if args.path is not None:
            path = Path(long_path(args.path))
            if not path.exists():
                self.parser.error(f"Input path does not exist: {args.path}")
            if not path.is_dir():
                self.parser.error(f"Input path is not a directory: {args.path}")
            if not os.access(path, os.R_OK):
                self.parser.error(f"Input path is not readable: {args.path}")

        # Validate numfiles argument (0 = no limit)
        if args.numfiles < 0:
            self.parser.error("numfiles must be 0 (all files) or a positive integer")

        # Validate limit argument (0 = single output file)
        if args.limit < 0:
            self.parser.error("limit must be 0 (single file) or a positive integer")

        # Validate content sample arguments (0 = none for pages, no limit for characters)
        for name in ("initial_pages", "final_pages", "max_chars"):
            if getattr(args, name) < 0:
                self.parser.error(f"--{name.replace('_', '-')} must be 0 or a positive integer")

        # Validate output directory argument (it is created later if it doesn't exist)
        if args.output_dir is not None and Path(long_path(args.output_dir)).is_file():
            self.parser.error(f"Output path is a file, not a directory: {args.output_dir}")

    def show_banner(self):
        print(f"\n{self.app_name} v{self.app_version}")
        print("=" * (len(self.app_name) + len(self.app_version) + 3))

    def get_app_info(self):
        return {
            "name": self.app_name,
            "version": self.app_version,
            "description": self.app_description,
        }
