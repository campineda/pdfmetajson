import json
import logging
import os
import traceback
from pathlib import Path

from pdfmetajson.pdf_meta_extract import PdfMetadataExtractor
from pdfmetajson.validators import PathValidator, ValidationError


class PdfMetaJson:
    # 0 means no limit: process every PDF / write a single output file
    DEFAULT_MAX_NUM_FILES = 0
    DEFAULT_RECORD_LIMIT = 15

    def __init__(
        self,
        input_dir,
        max_num_files=DEFAULT_MAX_NUM_FILES,
        record_limit=DEFAULT_RECORD_LIMIT,
        max_initial_pages=2,
        max_final_pages=1,
    ):
        self.logger = logging.getLogger(__name__)
        self.logger.debug(
            f"{__name__}(input_dir='{input_dir}', max_num_files={max_num_files}, "
            f"record_limit={record_limit}, max_initial_pages={max_initial_pages}, "
            f"max_final_pages={max_final_pages})"
        )
        self.input_dir = str(input_dir)
        # For now, the output directory is the same as the input directory
        self.output_dir = str(input_dir)
        self.max_num_files = max_num_files
        self.max_initial_pages = max_initial_pages
        self.max_records_per_file = record_limit
        self.max_final_pages = max_final_pages
        self.file_output_basename = "base"
        self._validate_parameters()

    def _validate_parameters(self):
        try:
            # Validate input directory
            self.input_path = PathValidator.validate_input_directory(self.input_dir)

            # Validate output directory
            self.output_path = PathValidator.validate_output_directory(self.output_dir)

        except ValidationError as e:
            self.logger.error(f"Validation failed: {e}")
            raise

    def process_directory(self):
        self.logger.info(f"Processing directory '{self.input_dir}'...")
        path = Path(self.input_dir)
        self.file_output_basename = "out_" + path.name
        num_files = 0
        num_pdfs_readed = 0
        records_pdf_batch = []
        file_index = 1

        for file_path in path.glob("*.pdf", case_sensitive=False):
            try:
                file_processor = PdfMetadataExtractor(
                    file_path, self.max_initial_pages, self.max_final_pages
                )
                record = file_processor.process(num_pdfs_readed + 1)
                # process() logs and returns None when the file can't be opened
                if record is not None:
                    records_pdf_batch.append(record)
                    num_pdfs_readed += 1
            except Exception as e:
                self.logger.info(
                    f"The file '{file_path}' could not be processed by the library. "
                    "We continue with another one."
                )
                self.logger.error(f"Error with file: '{file_path}': {e}")
                # self.logger.debug(traceback.format_exc())
                tb_list = traceback.extract_tb(e.__traceback__)
                error_file_path, error_line_number, error_function, error_code = tb_list[-1]
                self.logger.debug(
                    f"Error in {error_file_path}, line {error_line_number}, "
                    f"in {error_function}: {error_code!r}"
                )

            num_files += 1
            if 0 < self.max_num_files == num_files:
                break

            if 0 < self.max_records_per_file <= len(records_pdf_batch):
                self.logger.info(f"Batch completed with {len(records_pdf_batch)} records")
                self._write_records(records_pdf_batch, file_index)
                records_pdf_batch = []
                file_index += 1

        if num_files == 0:
            self.logger.info("No pdf files were found in the directory.")
        elif num_pdfs_readed == 0:
            self.logger.info(
                "The files in the directory could not be read. Please try other directory or files."
            )
        elif records_pdf_batch:
            self.logger.info(f"Final Batch with {len(records_pdf_batch)} records")
            self._write_records(records_pdf_batch, file_index)

    def _write_records(self, records, index):
        output_filename = f"{self.file_output_basename}_{index:02d}.json"
        file_path = os.path.join(self.output_dir, output_filename)

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(json.dumps(records, ensure_ascii=False))

        self.logger.info(f"Output file: {file_path}")
