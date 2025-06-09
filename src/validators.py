"""Validation utilities for application parameters"""

import json
import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any

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


class ProcessingValidator:
    """Validates processing parameters"""

    @staticmethod
    def validate_max_files(max_files: Optional[int], total_files: int) -> Optional[int]:
        """
        Validates max_files parameter against available files

        Args:
            max_files: Maximum files to process or None
            total_files: Total files available

        Returns:
            Validated max_files value or None

        Raises:
            ValidationError: If validation fails
        """
        if max_files is None:
            return None

        if max_files <= 0:
            raise ValidationError("max_files must be a positive integer")

        if max_files > total_files:
            logger.warning(
                f"max_files ({max_files}) exceeds available files ({total_files}). Will process all available files."
            )
            return total_files

        logger.debug(f"Will process {max_files} out of {total_files} files")
        return max_files

    @staticmethod
    def validate_limit(limit: int) -> int:
        """
        Validates limit parameter

        Args:
            limit: Records per file limit

        Returns:
            Validated limit value

        Raises:
            ValidationError: If validation fails
        """
        if limit <= 0:
            raise ValidationError("limit must be a positive integer")

        if limit > 1000:
            logger.warning(f"Large limit value ({limit}) may cause memory issues")

        logger.debug(f"Records per file limit set to: {limit}")
        return limit


class OutputValidator:
    """Validates output data before writing"""

    @staticmethod
    def validate_json_data(data: Any) -> bool:
        """
        Validates that data can be serialized to JSON

        Args:
            data: Data to validate

        Returns:
            True if valid

        Raises:
            ValidationError: If data cannot be serialized
        """
        try:
            json.dumps(data)
            return True
        except (TypeError, ValueError) as e:
            raise ValidationError(f"Data cannot be serialized to JSON: {e}")

    @staticmethod
    def validate_output_structure(data: Dict[str, Any]) -> bool:
        """
        Validates the structure of output data

        Args:
            data: Dictionary to validate

        Returns:
            True if structure is valid

        Raises:
            ValidationError: If structure is invalid
        """
        if not isinstance(data, dict):
            raise ValidationError("Output data must be a dictionary")

        # Validate required fields for batch processing
        required_fields = ["batch_info", "records"]
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Missing required field: {field}")

        if not isinstance(data["records"], list):
            raise ValidationError("Records field must be a list")

        return True
