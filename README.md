# PdfMetaJson

A Python command-line utility to extract metadata and content samples from PDF files within a directory and save the structured data into JSON files.

## Features

-   **Batch Processing**: Scans a specified directory for `.pdf` files.
-   **Metadata Extraction**: Extracts standard metadata including Title, Author, Subject, Keywords, Creator, Creation Date, and Modification Date.
-   **Content Sampling**: Extracts a text sample from the initial and final pages of each PDF to provide a glimpse of the content. The number of pages and characters is configurable, and the text keeps its accents and punctuation (Unicode, NFC).
-   **No File Left Behind**: Every PDF gets a record. Corrupted, encrypted or unreadable files get an `error` field and the process continues with the next file. Paths longer than 260 characters work on Windows.
-   **Flexible Output**: Batches the extracted data into multiple JSON files, with a configurable number of records per file, in the input directory or in another one.
-   **Exit Codes**: Tells callers whether the run succeeded, failed, or finished with some unreadable files.
-   **Configurable Logging**: Offers multiple logging levels (verbose for debugging, normal, and quiet for errors only).
-   **Simple CLI**: An intuitive command-line interface for easy operation.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/campineda/pdfmetajson
    cd PdfMetaJson
    ```

2.  **Install the package and its dependencies** (Python 3.13 or later):
    The project uses `pyproject.toml` to manage dependencies. Install the package and its requirements using pip:
    ```bash
    pip install .
    ```
    For development (editable install plus black, isort, flake8 and pre-commit):
    ```bash
    pip install -e ".[dev]"
    pre-commit install    # run the formatters and linters on every commit
    ```

## Usage

Run the `pdfmetajson` command, pointing it to the directory containing your PDF files.

```bash
pdfmetajson [PATH] [OPTIONS]
```

`python -m pdfmetajson [PATH] [OPTIONS]` works too, and so does `python main.py [PATH] [OPTIONS]` from the repository root once the package is installed.

### Arguments

-   `path`: (Optional) The input directory to scan for `.pdf` files. Defaults to the current directory (`.`).
-   `-n, --numfiles`: (Optional) The maximum number of PDF files to process. Defaults to `0`, which processes all files found.
-   `-l, --limit`: (Optional) The maximum number of records (PDFs) to include in a single output JSON file before creating a new one. Defaults to `15`; `0` writes all records to a single file.
-   `-o, --output-dir`: (Optional) Directory for the JSON files; it is created if it doesn't exist. Defaults to the input directory. Existing output files with the same name are overwritten.
-   `--initial-pages`: (Optional) Number of pages with text sampled from the start of each PDF. Pages with almost no text (such as blank pages) are skipped. Defaults to `2`; `0` samples none.
-   `--final-pages`: (Optional) Number of pages with text sampled from the end of each PDF. Defaults to `1`; `0` samples none.
-   `--max-chars`: (Optional) Maximum characters kept from each sampled page (the first ones for initial pages, the last ones for final pages). Defaults to `700`; `0` keeps the whole page.
-   `-v, --verbose`: (Optional) Enables verbose mode, showing detailed information about the process, including DEBUG logs.
-   `-q, --quiet`: (Optional) Enables quiet mode, which suppresses all informational output and only displays errors.
-   `--version`: Displays the application name and version.

### Examples

**1. Process PDFs in the current directory:**
```bash
pdfmetajson
```

**2. Process PDFs in a specific directory:**
```bash
pdfmetajson /path/to/your/pdfs
```

**3. Process a maximum of 50 files and set a limit of 10 records per JSON file:**
```bash
pdfmetajson /path/to/your/pdfs --numfiles 50 --limit 10
```

**4. Write the JSON files to another directory and take a bigger sample (useful to reach the copyright page of books):**
```bash
pdfmetajson /path/to/your/pdfs --output-dir /path/to/results --initial-pages 5 --max-chars 1500
```

**5. Run with detailed logging for debugging:**
```bash
pdfmetajson /path/to/your/pdfs --verbose
```

### Exit Codes

| Code | Meaning |
|------|---------|
| `0`  | Every PDF was processed. |
| `1`  | The run failed: invalid input or output directory, or an unexpected error. |
| `2`  | Invalid command-line arguments (for example, a missing input directory). |
| `3`  | The run finished, but some records have an `error` field (see below). |

## Output Format

The script generates one or more JSON files named `out_<directory_name>_XX.json` (where `<directory_name>` is the name of the input directory) in the input directory, or in `--output-dir` when given. Each file contains a JSON array of objects, where each object represents a PDF file. Every PDF found gets a record, even if it could not be read.

### Sample JSON Output

```json
[
  {
    "file_num": 1,
    "file_name_original": "sample-document.pdf",
    "file_date": "2023-10-27 15:45:10",
    "num_pages": 25,
    "metadata": {
      "author": "Jane Doe",
      "software": "Microsoft® Word for Microsoft 365",
      "title": "Project Proposal",
      "subject": "Q4 Initiatives",
      "creation_date": "2023-10-26",
      "modification_date": "2023-10-27"
    },
    "content_sample": {
      "page_1": "This is the text extracted from the first page of the document. It serves as a brief preview...",
      "page_2": "This is the text from the second page, providing more context about the document's contents...",
      "page_25": "...and this is a snippet from the last page, often containing conclusions or final remarks."
    }
  },
  {
    "file_num": 2,
    "file_name_original": "scanned-book.pdf",
    "file_date": "2023-10-28 09:12:00",
    "num_pages": 180,
    "metadata": {},
    "content_sample": {},
    "warnings": ["no_text"]
  },
  {
    "file_num": 3,
    "file_name_original": "locked.pdf",
    "file_date": "2023-10-29 11:30:42",
    "num_pages": null,
    "metadata": {},
    "content_sample": {},
    "error": {
      "code": "encrypted",
      "message": "The PDF requires a password to be read",
      "detail": "FileNotDecryptedError: File has not been decrypted"
    }
  }
]
```

### Record Fields

| Field | Type | Description |
|-------|------|-------------|
| `file_num` | integer | Position of the file in the run, starting at 1. Files with errors are counted too. |
| `file_name_original` | string | File name, without the directory. |
| `file_date` | string or `null` | Last modification date of the file on disk (`YYYY-MM-DD HH:MM:SS`, local time); not a date from the PDF. `null` if it can't be read. |
| `num_pages` | integer or `null` | Number of pages; `null` when the PDF couldn't be opened. |
| `metadata` | object | Document metadata (`author`, `software`, `title`, `subject`, `keywords`, `creation_date`, `modification_date`); only the keys present in the PDF. Always present, `{}` if there is none. |
| `content_sample` | object | Text of the sampled pages, keyed `page_<number>`. Always present, `{}` if no text was found. |
| `warnings` | list of strings | Only when the record is valid but its sample is limited. See below. |
| `error` | object | Only when the file couldn't be read: `code`, `message` (human-readable) and `detail` (the original exception). See below. |

**Error codes** (`error.code`):

| Code | Cause | Suggested action |
|------|-------|------------------|
| `not_found` | The file disappeared before it could be read. | Check the file. |
| `permission_denied` | No permission to read it, or locked by another process. | Try again later. |
| `encrypted` | The PDF requires a password. | Manual review. |
| `corrupt` | The PDF structure is damaged or the file is incomplete. | Manual review; the file may be truncated. |
| `os_error` | Another I/O error (for example, a network drive). | Try again. |
| `unexpected` | Any other error. | Manual review; please report it. |

**Warning codes** (`warnings`):

| Code | Meaning |
|------|---------|
| `no_text` | No text was found in the sampled pages; probably a scanned PDF (OCR is not supported). |
| `page_errors` | Some pages failed to extract; the sample may be incomplete. |

## Dependencies

-   pypdf: A pure-python PDF library for reading and manipulating PDF files.
-   colorlog: For adding color to log output.
-   cryptography: Installed through `pypdf[crypto]`; required for handling encrypted PDF files.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for the release history.

## License

This project is licensed under the MIT License.
