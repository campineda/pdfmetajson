# src/pdfmetajson/__main__.py
import sys
import traceback

from pdfmetajson import PACKAGE_NAME
from pdfmetajson.cli import CommandLineInterface
from pdfmetajson.logging_config import configure_logging
from pdfmetajson.pdf_meta_json import PdfMetaJson
from pdfmetajson.validators import ValidationError

# Exit codes. argparse exits with 2 on invalid arguments.
EXIT_OK = 0
EXIT_ERROR = 1
EXIT_FILE_ERRORS = 3


def main(argv=None) -> int:
    """
    Runs the command line utility.

    Args:
        argv: Arguments without the program name; None reads sys.argv.

    Returns:
        int: EXIT_OK, EXIT_ERROR (validation or unexpected error) or EXIT_FILE_ERRORS (the run
        finished but some records have an "error" field).
    """
    try:
        cli = CommandLineInterface(PACKAGE_NAME)
        args = cli.parse_arguments(argv)
        configure_logging(verbose=args.verbose, quiet=args.quiet)
        if not args.quiet:
            cli.show_banner()
        pdf_meta_to_json = PdfMetaJson(
            input_dir=args.path,
            max_num_files=args.numfiles,
            record_limit=args.limit,
            max_initial_pages=args.initial_pages,
            max_final_pages=args.final_pages,
            max_chars_per_page=args.max_chars,
            output_dir=args.output_dir,
        )
        summary = pdf_meta_to_json.process_directory()
    except ValidationError as ve:
        print(f"Please correct your info. {ve}", file=sys.stderr)
        return EXIT_ERROR
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        return EXIT_ERROR
    return EXIT_FILE_ERRORS if summary.num_errors else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
