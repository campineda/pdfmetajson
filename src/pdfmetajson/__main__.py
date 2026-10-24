# src/pdfmetajson/__main__.py
import sys
import traceback

from pdfmetajson import PACKAGE_NAME
from pdfmetajson.cli import CommandLineInterface
from pdfmetajson.logging_config import configure_logging
from pdfmetajson.pdf_meta_json import PdfMetaJson
from pdfmetajson.validators import ValidationError


def main() -> int:
    try:
        cli = CommandLineInterface(PACKAGE_NAME)
        args = cli.parse_arguments()
        configure_logging(verbose=args.verbose, quiet=args.quiet)
        if not args.quiet:
            cli.show_banner()
        pdf_meta_to_json = PdfMetaJson(
            input_dir=args.path,
            max_num_files=args.numfiles,
            record_limit=args.limit,
        )
        pdf_meta_to_json.process_directory()
    except ValidationError as ve:
        print(f"Please correct your info. {ve}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
