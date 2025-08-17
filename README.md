# PdfMetaJson

A Python command-line utility to extract metadata and content samples from PDF files within a directory and save the structured data into JSON files.

## Features

-   **Batch Processing**: Scans a specified directory for `.pdf` files.
-   **Metadata Extraction**: Extracts standard metadata including Title, Author, Subject, Keywords, Creator, Creation Date, and Modification Date.
-   **Content Sampling**: Extracts a text sample from the initial and final pages of each PDF to provide a glimpse of the content.
-   **Robust Error Handling**: Gracefully handles and logs errors for corrupted or unreadable files, continuing the process with the next available file.
-   **Flexible Output**: Batches the extracted data into multiple JSON files, with a configurable number of records per file.
-   **Configurable Logging**: Offers multiple logging levels (verbose for debugging, normal, and quiet for errors only).
-   **Simple CLI**: An intuitive command-line interface for easy operation.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd PdfMetaJson
    ```

2.  **Install the package and its dependencies:**
    The project uses `pyproject.toml` to manage dependencies. Install the package and its requirements using pip:
    ```bash
    pip install .
    ```

## Usage

Run the script from the command line, pointing it to the directory containing your PDF files.

```bash
python main.py [PATH] [OPTIONS]
```

### Arguments

-   `path`: (Optional) The input directory to scan for `.pdf` files. Defaults to the current directory (`.`).
-   `-n, --numfiles`: (Optional) The maximum number of PDF files to process. By default, it processes all files found.
-   `-l, --limit`: (Optional) The maximum number of records (PDFs) to include in a single output JSON file before creating a new one. Defaults to `15`.
-   `-v, --verbose`: (Optional) Enables verbose mode, showing detailed information about the process, including DEBUG logs.
-   `-q, --quiet`: (Optional) Enables quiet mode, which suppresses all informational output and only displays errors.
-   `--version`: Displays the application name and version.

### Examples

**1. Process PDFs in the current directory:**
```bash
python main.py
```

**2. Process PDFs in a specific directory:**
```bash
python main.py /path/to/your/pdfs
```

**3. Process a maximum of 50 files and set a limit of 10 records per JSON file:**
```bash
python main.py /path/to/your/pdfs --numfiles 50 --limit 10
```

**4. Run with detailed logging for debugging:**
```bash
python main.py /path/to/your/pdfs --verbose
```

## Output Format

The script generates one or more JSON files named `out_<directory_name>_XX.json` in the input directory. Each file contains a JSON array of objects, where each object represents a processed PDF file.

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
  }
]
```

## Dependencies

-   pypdf: A pure-python PDF library for reading and manipulating PDF files.
-   Unidecode: For ASCII transliterations of Unicode text.
-   colorlog: For adding color to log output.
-   cryptography: Required by `pypdf` for handling encrypted PDF files.

## License

This project is licensed under the MIT License.
