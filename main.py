# -*- coding: utf-8 -*-
# main.py
import traceback

from src.cli import CommandLineInterface
from src.logging_config import configure_logging
from src.pdf_meta_json import PdfMetaJson
from src.validators import ValidationError

# --- Global Variables ---
PACKAGE_NAME = "PdfMetaJson"


def main():
    try:
        cli = CommandLineInterface(PACKAGE_NAME)
        args = cli.parse_arguments()
        configure_logging(verbose=args.verbose, quiet=args.quiet)
        if not args.quiet:
            cli.show_banner()
        pdf_meta_to_json = PdfMetaJson(
            input_dir=args.path,
            max_num_files=args.numfiles,
            record_limit=args.limit
        )
        pdf_meta_to_json.process_directory()
    except ValidationError as ve:
        print(f"Please correct your info. {ve}")
    except Exception as e:
        print(f"Some error ocurried: {e}")
        print(traceback.format_exc())


if __name__ == "__main__":
    main()
