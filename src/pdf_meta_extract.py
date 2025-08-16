import logging
import os
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
                self.logger.info(
                    f"Processing file{file_num_text}: '{self.file_path}'..."
                )
                reader = PdfReader(f)
                self.metadata = self._extract_metadata(reader) or None
                self._extract_content(reader)

            self.file_date = datetime.fromtimestamp(
                os.path.getmtime(self.file_path)
            ).strftime("%Y-%m-%d %H:%M:%S")
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
            self.logger.error(
                f"You do not have permission to read the file {self.file_name}"
            )
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
            self.logger.warning(
                f"We couldn't find the file's metadata, or the metadata doesn't exist. File: '{self.file_name}' !"
            )
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
            metadata["creation_date"] = self._parse_date(
                creation_date_raw, "creation_date"
            )

        modification_date_raw = reader.metadata.modification_date_raw
        if modification_date_raw is not None:
            metadata["modification_date"] = self._parse_date(
                modification_date_raw, "modification_date"
            )

        return metadata

    def _extract_content(self, reader):
        pdf_pages = {}
        # Intentamos extraer al menos 2 páginas iniciales con contenido (texto > 5 caracteres)
        page_num = 1
        pages_read = 0
        total_pages_read = 0
        keep_reading = True
        num_total_pages = len(reader.pages)
        tries = 0
        pages_with_errors = []
        error_counter = Counter()

        while keep_reading:
            page = reader.pages[page_num - 1]
            # self.logger.debug("page_" + str(page_num) + ":\n" + page.extract_text())
            # self.logger.debug("page_clean_" + str(page_num) + ":\n" + pdf_clean_text.clean_text(page.extract_text()))
            try:
                page_text = pdf_utils.clean_text(page.extract_text())[
                    : PdfMetadataExtractor.MAX_CHARS_PER_PAGE
                ]
            except Exception as e:
                pages_with_errors.append(page_num)
                error_counter[str(e)] += 1
                # self.logger.debug(f"We can't get contents for the file for page {page_num}. Error in page.extract_text: {e}")
                page_text = ""
            if len(page_text) > PdfMetadataExtractor.MIN_CHARS_PER_PAGE:
                pdf_pages["page_" + str(page_num)] = page_text
                pages_read += 1
            else:
                tries += 1
            if (
                pages_read == self.max_initial_pages
                or page_num == num_total_pages
                or tries == self.MAX_CONTENT_EXTRACTION_ATTEMPTS
            ):
                keep_reading = False
            else:
                page_num += 1
        last_page_read = page_num
        total_pages_read = pages_read
        tries = 0
        # intentamos extraer al menos 1 página final con contenido (texto > 5 caracteres)
        # traemos los ultimos MAX_CHARS_PER_PAGE caracteres
        if page_num < len(reader.pages):
            page_num = len(reader.pages)
            pages_read = 0
            if page_num > last_page_read:
                keep_reading = True
            while keep_reading:
                page = reader.pages[page_num - 1]
                try:
                    page_text = pdf_utils.clean_text(page.extract_text())[
                        -PdfMetadataExtractor.MAX_CHARS_PER_PAGE :
                    ]
                except Exception as e:
                    pages_with_errors.append(page_num)
                    error_counter[str(e)] += 1
                    # self.logger.debug(f"We can't get contents for the file for page {page_num}. Error in page.extract_text: {e}")
                    page_text = ""
                if len(page_text) > PdfMetadataExtractor.MIN_CHARS_PER_PAGE:
                    pdf_pages["page_" + str(page_num)] = page_text
                    pages_read += 1
                else:
                    tries += 1
                if (
                    pages_read >= self.max_final_pages
                    or page_num <= last_page_read
                    or tries == self.MAX_CONTENT_EXTRACTION_ATTEMPTS
                ):
                    keep_reading = False
                else:
                    page_num -= 1
        total_pages_read += pages_read
        if len(pages_with_errors) > 0:
            str_lis_pages = ", ".join(str(page) for page in pages_with_errors)
            error_summary = ", ".join(
                f"'{msg}' ({count})" for msg, count in error_counter.items()
            )
            self.logger.debug(
                f"We can't get contents for {len(pages_with_errors)} pages ({str_lis_pages}). Errors: {error_summary}"
            )
        if total_pages_read == 0:
            self.logger.warning(
                f"Was imposible to get contents for the file. Maybe it's a scanned book? We don't support image conversion."
            )
        self.content = pdf_pages

    def _parse_date(self, pdf_date_raw, date_name):
        pdf_date = pdf_utils.convert_date(str(pdf_date_raw))
        if pdf_date is None:
            self.logger.debug(
                f"Date Conversion Error in File '{self.file_name}': '{date_name}' could not be converted. "
                f"We get '{pdf_date}' ({type(pdf_date)}), so we use '{str(pdf_date_raw)}'."
            )
            pdf_date = str(pdf_date_raw)
        else:
            pdf_date = pdf_date.strftime("%Y-%m-%d")
        return pdf_date
