"""Common utilities"""

from pathlib import Path
from typing import List


class FileNameGenerator:
    """Generates sequential file names for batch processing"""

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.base_name = base_path.stem
        self.extension = base_path.suffix
        self.directory = base_path.parent

    def generate_batch_filename(self, batch_number: int) -> Path:
        """
        Generates a filename for the given batch number

        Args:
            batch_number: Batch number (1-based)

        Returns:
            Path object for the batch file
        """
        if batch_number == 1:
            return self.base_path

        # Generate names like: output02.json, output03.json, etc.
        batch_name = f"{self.base_name}{batch_number:02d}{self.extension}"
        return self.directory / batch_name

    def get_existing_batch_files(self) -> List[Path]:
        """
        Gets list of existing batch files that match the pattern

        Returns:
            List of existing batch file paths
        """
        pattern = f"{self.base_name}*.json"
        return sorted(self.directory.glob(pattern))
