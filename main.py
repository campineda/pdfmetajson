# -*- coding: utf-8 -*-
# main.py
from src.cli import CommandLineInterface

# --- Global Variables ---
PACKAGE_NAME = "PdfMetaJson"


def main():
    cli = CommandLineInterface(PACKAGE_NAME)
    args = cli.parse_arguments()
    cli.show_banner()
    print("Args: ")
    print(args)


if __name__ == "__main__":
    main()
