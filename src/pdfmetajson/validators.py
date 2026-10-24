"""Validation utilities for application parameters"""

import logging
import os
from pathlib import Path
from typing import Optional

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
            path_obj = Path(path).resolve()

            if not path_obj.exists():
                raise ValidationError(f"Input directory does not exist: {path}")

            if not path_obj.is_dir():
                raise ValidationError(f"Path is not a directory: {path}")

            if not os.access(path_obj, os.R_OK):
                raise ValidationError(f"Directory is not readable: {path}")

            # Check if directory is empty
            if not any(path_obj.iterdir()):
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
            output_path = Path(path).resolve()

            if not output_path.exists():
                raise ValidationError(f"Output directory does not exist: {path}")

            if not output_path.is_dir():
                raise ValidationError(f"Path is not a directory: {path}")

            if not os.access(output_path, os.W_OK):
                raise ValidationError(f"Output directory is not writable: {path}")

            logger.debug(f"Output directory validated: {output_path}")
            return output_path

        except OSError as e:
            raise ValidationError(f"Error validating output path {path}: {e}")
