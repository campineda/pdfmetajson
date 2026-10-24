"""Validation utilities for application parameters"""

import logging
import os
from pathlib import Path
from typing import Optional

from pdfmetajson.pdf_utils import long_path

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom exception for validation errors"""

    pass


class PathValidator:
    """Validates path-related parameters"""

    @staticmethod
    def validate_input_directory(path: Optional[str]) -> Optional[Path]:
        """
        Validates input directory path

        Args:
            path: Directory path string or None

        Returns:
            Path object if valid, None if path is None

        Raises:
            ValidationError: If validation fails
        """
        if path is None:
            return None

        try:
            path_obj = Path(os.path.abspath(path))
            # Checked through long_path() so directories longer than MAX_PATH work on Windows
            os_path = Path(long_path(path_obj))

            if not os_path.exists():
                raise ValidationError(f"Input directory does not exist: {path}")

            if not os_path.is_dir():
                raise ValidationError(f"Path is not a directory: {path}")

            if not os.access(os_path, os.R_OK):
                raise ValidationError(f"Directory is not readable: {path}")

            # Check if directory is empty
            if not any(os_path.iterdir()):
                logger.warning(f"Input directory is empty: {path}")

            logger.debug(f"Input directory validated: {path_obj}")
            return path_obj

        except OSError as e:
            raise ValidationError(f"Error accessing path {path}: {e}")

    @staticmethod
    def validate_output_directory(path: Optional[str]) -> Optional[Path]:
        """
        Validates output directory path

        Args:
            path: Output directory path string or None

        Returns:
            Path object if valid, None if output is None

        Raises:
            ValidationError: If validation fails
        """
        if path is None:
            return None

        try:
            output_path = Path(os.path.abspath(path))
            os_path = Path(long_path(output_path))

            if not os_path.exists():
                raise ValidationError(f"Output directory does not exist: {path}")

            if not os_path.is_dir():
                raise ValidationError(f"Path is not a directory: {path}")

            if not os.access(os_path, os.W_OK):
                raise ValidationError(f"Output directory is not writable: {path}")

            logger.debug(f"Output directory validated: {output_path}")
            return output_path

        except OSError as e:
            raise ValidationError(f"Error validating output path {path}: {e}")
