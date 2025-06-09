# src/cli.py
import argparse
import importlib.metadata
import os
from pathlib import Path


class CommandLineInterface:

    def __init__(self, package_name):
        self.package_name = package_name
        self.app_name = self._get_app_name()
        self.app_version = self._get_version()
        self.app_description = self._get_description()
        self.parser = self._create_parser()

    def _get_app_name(self):
        try:
            name = importlib.metadata.metadata(self.package_name)["Name"]
            return name.replace("-", " ").title()
        except (importlib.metadata.PackageNotFoundError, KeyError):
            return ""

    def _get_version(self):
        try:
            return importlib.metadata.version(self.package_name)
        except importlib.metadata.PackageNotFoundError:
            return ""

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
            help="take the path to the target directory (default: %(default)s)",
        )
        # Max Files
        parser.add_argument(
            "-n",
            "--numfiles",
            nargs="?",
            type=int,
            default=0,
            help="limit of PDF files to process. All by default.",
        )
        # Limit of registers per Output
        parser.add_argument(
            "-l",
            "--limit",
            nargs="?",
            type=int,
            default=15,
            help="Maximum records per JSON file before creating a new one (default: 15)",
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

    def parse_arguments(self):
        args = self.parser.parse_args()
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
            path = Path(args.path)
            if not path.exists():
                self.parser.error(f"Input path does not exist: {args.path}")
            if not path.is_dir():
                self.parser.error(f"Input path is not a directory: {args.path}")
            if not os.access(path, os.R_OK):
                self.parser.error(f"Input path is not readable: {args.path}")

        # Validate numfiles argument
        if args.numfiles is not None:
            if args.numfiles < 0:
                self.parser.error("numfiles must be a positive integer")

        # Validate limit argument
        if args.limit <= 0:
            self.parser.error("limit must be a positive integer")

    def show_banner(self):
        print(f"\n{self.app_name} v{self.app_version}")
        print("=" * (len(self.app_name) + len(self.app_version) + 3))

    def get_app_info(self):
        return {
            "name": self.app_name,
            "version": self.app_version,
            "description": self.app_description,
        }
