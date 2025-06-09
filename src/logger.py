import logging
import sys
from typing import Optional


class ConsoleLogger:

    def __init__(self, name: str = "app"):
        self.name = name
        self.logger = logging.getLogger(name)
        self._is_configured = False

    def configure(self, verbose: bool = False, quiet: bool = False) -> logging.Logger:
        if self._is_configured:
            return self.logger

        if verbose:
            level = logging.DEBUG
        elif quiet:
            level = logging.ERROR
        else:
            level = logging.INFO

        self.logger.setLevel(level)

        # Create a console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)

        # Create formatter
        formatter = self._create_formatter(verbose)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)

        # To avoid duplicate messages
        self.logger.propagate = False

        self._is_configured = True
        return self.logger

    @staticmethod
    def _create_formatter(verbose: bool) -> logging.Formatter:
        if verbose:
            # detailed format for DEBUG
            fmt = "[%(asctime)s] %(levelname)-8s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"
            datefmt = "%Y-%m-%d %H:%M:%S"
        else:
            # simple format for INFO y ERROR
            fmt = "%(levelname)s: %(message)s"
            datefmt = None

        return logging.Formatter(fmt, datefmt)

    def get_logger(self) -> logging.Logger:
        if not self._is_configured:
            return self.configure()
        return self.logger


# Función de conveniencia para obtener un logger global
_global_logger: Optional[ConsoleLogger] = None


def get_logger(name: str = "app") -> logging.Logger:
    global _global_logger
    if _global_logger is None:
        _global_logger = ConsoleLogger(name)
    return _global_logger.get_logger()


def configure_logging(
    verbose: bool = False, quiet: bool = False, name: str = "app"
) -> logging.Logger:
    global _global_logger
    _global_logger = ConsoleLogger(name)
    return _global_logger.configure(verbose, quiet)
