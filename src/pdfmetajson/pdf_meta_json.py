import json
import logging
import os
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from pdfmetajson import pdf_utils
from pdfmetajson.pdf_meta_extract import PdfMetadataExtractor
from pdfmetajson.validators import PathValidator, ValidationError


@dataclass
class ProcessingSummary:
    """Counts of a process_directory() run."""

    num_files: int = 0
    errors: Counter = field(default_factory=Counter)

    @property
    def num_errors(self):
        return sum(self.errors.values())


class PdfMetaJson:
    # 0 means no limit: process every PDF / write a single output file
    DEFAULT_MAX_NUM_FILES = 0
    DEFAULT_RECORD_LIMIT = 15
    DEFAULT_INITIAL_PAGES = PdfMetadataExtractor.DEFAULT_INITIAL_PAGES
    DEFAULT_FINAL_PAGES = PdfMetadataExtractor.DEFAULT_FINAL_PAGES
    # 0 means no limit: the whole text of each sampled page
    DEFAULT_MAX_CHARS = PdfMetadataExtractor.MAX_CHARS_PER_PAGE

    def __init__(
        self,
        input_dir,
        max_num_files=DEFAULT_MAX_NUM_FILES,
        record_limit=DEFAULT_RECORD_LIMIT,
        max_initial_pages=DEFAULT_INITIAL_PAGES,
        max_final_pages=DEFAULT_FINAL_PAGES,
        max_chars_per_page=DEFAULT_MAX_CHARS,
        output_dir=None,
    ):
        self.logger = logging.getLogger(__name__)
        self.logger.debug(
            f"{__name__}(input_dir='{input_dir}', max_num_files={max_num_files}, "
            f"record_limit={record_limit}, max_initial_pages={max_initial_pages}, "
            f"max_final_pages={max_final_pages}, max_chars_per_page={max_chars_per_page}, "
            f"output_dir='{output_dir}')"
        )
        self.input_dir = str(input_dir)
        # By default, the output files are written next to the PDFs
        self.output_dir = str(output_dir) if output_dir is not None else self.input_dir
        self.max_num_files = max_num_files
        self.max_initial_pages = max_initial_pages
        self.max_records_per_file = record_limit
        self.max_final_pages = max_final_pages
        self.max_chars_per_page = max_chars_per_page
        self.file_output_basename = "base"
        self._validate_parameters()

    def _validate_parameters(self):
        try:
            # Validate input directory
            self.input_path = PathValidator.validate_input_directory(self.input_dir)

            # Create the output directory if needed, then validate it
            self._create_output_directory()
            self.output_path = PathValidator.validate_output_directory(self.output_dir)

        except ValidationError as e:
            self.logger.error(f"Validation failed: {e}")
            raise

    def _create_output_directory(self):
        try:
            os.makedirs(pdf_utils.long_path(self.output_dir), exist_ok=True)
        except OSError as e:
            raise ValidationError(f"Output directory can't be created: {self.output_dir}: {e}")

    def process_directory(self):
        """
        Writes a record for every PDF in the input directory, including those that can't be
        read (they get an "error" field).

        Returns:
            ProcessingSummary: number of files processed and errors by code.
        """
        self.logger.info(f"Processing directory '{self.input_dir}'...")
        path = Path(self.input_dir)
        self.file_output_basename = "out_" + path.name
        summary = ProcessingSummary()
        records_pdf_batch = []
        file_index = 1

        # Listed through long_path() so directories longer than MAX_PATH work on Windows
        for os_path in Path(pdf_utils.long_path(path)).glob("*.pdf", case_sensitive=False):
            if os_path.is_dir():
                continue
            file_path = path / os_path.name
            summary.num_files += 1
            record = self._process_file(file_path, summary.num_files)
            if "error" in record:
                summary.errors[record["error"]["code"]] += 1
            records_pdf_batch.append(record)

            if 0 < self.max_num_files == summary.num_files:
                break

            if 0 < self.max_records_per_file <= len(records_pdf_batch):
                self.logger.info(f"Batch completed with {len(records_pdf_batch)} records")
                self._write_records(records_pdf_batch, file_index)
                records_pdf_batch = []
                file_index += 1

        if summary.num_files == 0:
            self.logger.info("No pdf files were found in the directory.")
            return summary

        if records_pdf_batch:
            self.logger.info(f"Final Batch with {len(records_pdf_batch)} records")
            self._write_records(records_pdf_batch, file_index)

        self._log_summary(summary)
        return summary

    def _process_file(self, file_path, file_num):
        # process() never raises: files that can't be read get a record with an "error" field
        file_processor = PdfMetadataExtractor(
            file_path, self.max_initial_pages, self.max_final_pages, self.max_chars_per_page
        )
        return file_processor.process(file_num)

    def _log_summary(self, summary):
        num_ok = summary.num_files - summary.num_errors
        message = f"{summary.num_files} files: {num_ok} ok, {summary.num_errors} with error"
        if summary.errors:
            details = ", ".join(f"{code} {count}" for code, count in summary.errors.items())
            self.logger.warning(f"{message} ({details})")
        else:
            self.logger.info(message)

    def _write_records(self, records, index):
        output_filename = f"{self.file_output_basename}_{index:02d}.json"
        file_path = os.path.join(self.output_dir, output_filename)

        with open(pdf_utils.long_path(file_path), "w", encoding="utf-8") as file:
            file.write(json.dumps(records, ensure_ascii=False))

        self.logger.info(f"Output file: {file_path}")
