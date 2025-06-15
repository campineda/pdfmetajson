import logging
import sys

from colorlog import ColoredFormatter


def _create_formatter(verbose: bool) -> logging.Formatter:
    if verbose:
        # Detailed formar for DEBUG
        fmt = "[%(asctime)s] %(log_color)s%(levelname)-8s%(reset)s [%(name)s:%(lineno)d] %(message)s"
        datefmt = "%Y-%m-%d %H:%M:%S"
    else:
        # Simple format for INFO or ERROR
        fmt = "%(log_color)s%(levelname)s:%(reset)s %(message)s"
        datefmt = None
    formatter = ColoredFormatter(
        fmt,
        datefmt=datefmt,
        log_colors={
            "DEBUG": "yellow",
            "INFO": "green",  # Use 'white' or 'reset' for default color
            "WARNING": "bold_yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
        reset=True,  # Ensures that color is reset after each message
        style="%",
    )

    return formatter


def configure_logging(verbose: bool = False, quiet: bool = False):
    """
    Configures the root logger for the entire application.

    This function must be called ONCE at the start of the program.
    """
    if verbose:
        level = logging.DEBUG
    elif quiet:
        level = logging.ERROR
    else:
        level = logging.INFO

    # We obtain the root logger. All loggers created with
    # logging.getLogger(__name__) will inherit this configuration.
    root_logger = logging.getLogger()

    # We prevent multiple handlers from being added if the function is called more than once.
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    root_logger.setLevel(level)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    formatter = _create_formatter(verbose)
    console_handler.setFormatter(formatter)

    root_logger.addHandler(console_handler)

    # Disable Log messages from Libraries
    # Disable warnings from pypdf library
    logging.getLogger("pypdf._reader").setLevel(logging.ERROR)
    # Disable debug from validator
    logging.getLogger("validators").setLevel(logging.INFO)
