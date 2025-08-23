import logging
import os
import traceback
from collections import Counter
from datetime import datetime

from pypdf import PdfReader

import pdf_utils


class PdfMetadataExtractor:
    MAX_CHARS_PER_PAGE = 700
    MIN_CHARS_PER_PAGE = 5
    MAX_CONTENT_EXTRACTION_ATTEMPTS = 10

    def __init__(self, file_path, max_initial_pages=2, max_final_pages=1):
        self.file_path = file_path
        self.max_initial_pages = max_initial_pages
        self.max_final_pages = max_final_pages
        self.file_name = ""
        self.file_date = ""
        self.num_pages = ""
        self.metadata = {}
        self.content = ""
        self.logger = logging.getLogger(__name__)

    def process(self, file_num=0):
        try:
            with open(self.file_path, "rb") as f:
                self.file_name = os.path.basename(self.file_path)
                file_num_text = f" #{file_num}" if file_num > 0 else ""
                self.logger.info(f"Processing file{file_num_text}: '{self.file_path}'...")
                reader = PdfReader(f)
                self.metadata = self._extract_metadata(reader) or None
                self._extract_content(reader)

            self.file_date = datetime.fromtimestamp(os.path.getmtime(self.file_path)).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            self.num_pages = len(reader.pages)
            pdf_info = {}
            if file_num > 0:
                pdf_info["file_num"] = file_num
            pdf_info.update(
                {
                    "file_name_original": self.file_name,
                    "file_date": self.file_date,
                    "num_pages": self.num_pages,
                }
            )
            if self.metadata is not None:
                pdf_info["metadata"] = self.metadata
            if self.content is not None:
                pdf_info["content_sample"] = self.content
            return pdf_info
        except PermissionError:
            self.logger.error(f"You do not have permission to read the file {self.file_name}")
            return None
        except FileNotFoundError:
            self.logger.error(f"File {self.file_name} not found")
            return None
        except IsADirectoryError:
            self.logger.error("The specified path is a directory, not a file.")
            return None
        except IOError as e:
            self.logger.error(f"An I/O error occurred: : {e}")
            return None

    def _extract_metadata(self, reader):
        metadata = {}
        if reader.metadata is None:
            self.logger.warning(f"We couldn't find the file's metadata. File: '{self.file_name}'")
            return metadata
        if reader.metadata.author is not None:
            metadata["author"] = reader.metadata.author
        if reader.metadata.creator is not None:
            metadata["software"] = reader.metadata.creator
        if reader.metadata.title is not None:
            metadata["title"] = reader.metadata.title
        if reader.metadata.subject is not None:
            metadata["subject"] = reader.metadata.subject
        if reader.metadata.keywords is not None:
            metadata["keywords"] = reader.metadata.keywords

        creation_date_raw = reader.metadata.creation_date_raw
        if creation_date_raw is not None:
            metadata["creation_date"] = self._parse_date(creation_date_raw, "creation_date")

        modification_date_raw = reader.metadata.modification_date_raw
        if modification_date_raw is not None:
            metadata["modification_date"] = self._parse_date(
                modification_date_raw, "modification_date"
            )

        return metadata

    def _extract_content(self, reader):
        pdf_pages = {}
        num_total_pages = len(reader.pages)
        pages_with_errors = []
        error_counter = Counter()
        error_details = []

        # Extract initial pages (forward direction)
        (
            initial_pages,
            initial_errors,
            initial_error_counter,
            last_page_read,
            initial_error_details,
        ) = self._extract_pages_in_direction(
            reader, 1, num_total_pages, self.max_initial_pages, is_forward=True
        )
        pdf_pages.update(initial_pages)
        pages_with_errors.extend(initial_errors)
        error_counter.update(initial_error_counter)
        error_details.extend(initial_error_details)

        # Extract final pages (backward direction) if there are more pages
        if last_page_read < num_total_pages:
            final_pages, final_errors, final_error_counter, _, final_error_details = (
                self._extract_pages_in_direction(
                    reader,
                    num_total_pages,
                    last_page_read,
                    self.max_final_pages,
                    is_forward=False,
                )
            )
            pdf_pages.update(final_pages)
            pages_with_errors.extend(final_errors)
            error_counter.update(final_error_counter)
            error_details.extend(final_error_details)

        # Log errors if any
        if pages_with_errors:
            str_lis_pages = ", ".join(str(page) for page in pages_with_errors)
            error_summary = ", ".join(f"'{msg}' ({count})" for msg, count in error_counter.items())
            self.logger.debug(
                f"We can't get contents for {len(pages_with_errors)} pages "
                f"({str_lis_pages}). Errors: {error_summary}"
            )
            # Log detailed error information
            for error_detail in error_details:
                self.logger.debug(
                    f"Error on page {error_detail['page']}: {error_detail['error']} "
                    f"at {error_detail['file']}:{error_detail['line']} "
                    f"in function '{error_detail['function']}'"
                )

        if not pdf_pages:
            self.logger.warning(
                "Was imposible to get contents for the file. "
                "Maybe it's a scanned book? We don't support image conversion."
            )

        self.content = pdf_pages

    def _extract_pages_in_direction(
        self, reader, start_page, limit_page, max_pages, is_forward=True
    ):
        """
        Extract pages in a specific direction. (forward or backward).

        Args:
            reader: PDF reader object
            start_page: Starting page number (1-indexed)
            limit_page: Limit page number
            max_pages: Maximum number of pages to extract
            is_forward: True for forward direction, False for backward

        Returns:
            tuple: (pages_dict, error_pages_list, error_counter, last_page_read, error_details)
        """
        pages = {}
        pages_with_errors = []
        error_counter = Counter()
        error_details = []
        pages_read = 0
        tries = 0
        page_num = start_page
        direction = 1 if is_forward else -1

        while (
            pages_read < max_pages
            and tries < self.MAX_CONTENT_EXTRACTION_ATTEMPTS
            and (
                (is_forward and page_num <= limit_page)
                or (not is_forward and page_num > limit_page)
            )
        ):

            page = reader.pages[page_num - 1]

            try:
                page_text = pdf_utils.clean_text(page.extract_text())
                # Extract from beginning or end based on direction
                if is_forward:
                    page_text = page_text[: self.MAX_CHARS_PER_PAGE]
                else:
                    page_text = page_text[-self.MAX_CHARS_PER_PAGE :]
            except Exception as e:
                pages_with_errors.append(page_num)
                error_counter[str(e)] += 1

                # Capture detailed error information
                tb_list = traceback.extract_tb(e.__traceback__)
                error_file_path, error_line_number, error_function, error_code = tb_list[-1]
                error_details.append(
                    {
                        "page": page_num,
                        "error": str(e),
                        "file": error_file_path,
                        "line": error_line_number,
                        "function": error_function,
                        "code": error_code,
                    }
                )

                page_text = ""

            if len(page_text) > self.MIN_CHARS_PER_PAGE:
                pages[f"page_{page_num}"] = page_text
                pages_read += 1
            else:
                tries += 1

            page_num += direction

        # Return the last page that was actually processed
        last_page_processed = page_num - direction

        return pages, pages_with_errors, error_counter, last_page_processed, error_details

    def _parse_date(self, pdf_date_raw, date_name):
        pdf_date = pdf_utils.convert_date(str(pdf_date_raw))
        if pdf_date is None:
            self.logger.debug(
                "Date Conversion Error in File "
                f"'{self.file_name}': '{date_name}' could not be converted. "
                f"We get '{pdf_date}' ({type(pdf_date)}), so we use '{str(pdf_date_raw)}'."
            )
            pdf_date = str(pdf_date_raw)
        else:
            pdf_date = pdf_date.strftime("%Y-%m-%d")
        return pdf_date
