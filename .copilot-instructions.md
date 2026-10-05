# Python Project Development Guidelines

## Code Style and Formatting

### General Formatting
- Use **Black** formatter with 100-character line length
- Use **isort** for import organization with Black profile
- Follow PEP 8 naming conventions
- Use double quotes for strings consistently
- Add trailing commas in multi-line structures

### Import Organization
```python
# Standard library imports first
import json
import logging
import os
from pathlib import Path

# Third-party imports second
from pypdf import PdfReader
from unidecode import unidecode

# Local imports last
from src.module_name import ClassName
```

## Modern Python Project Structure

### Project Configuration (pyproject.toml)
- Use **pyproject.toml** instead of setup.py and requirements.txt for modern Python projects
- Manage all dependencies, build system, and tool configurations in a single file
- Specify minimum Python version (>=3.13 for this project)
- Include optional development dependencies in `[project.optional-dependencies]`

### Virtual Environment Setup
```bash
# Create virtual environment in .venv directory
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Unix/macOS:
source .venv/bin/activate

# Install project with dependencies
pip install .

# Install with development dependencies
pip install -e ".[dev]"
```

### Directory Layout
```
project_root/
├── main.py                 # Entry point
├── pyproject.toml         # Modern project configuration (replaces setup.py + requirements.txt)
├── README.md              # Documentation
├── LICENSE.txt            # License file
├── .gitignore            # Git ignore rules
├── .venv/                # Virtual environment (local, not in repo)
├── .vscode/              # VS Code configuration
│   ├── launch.json       # Debug configurations
│   └── settings.json     # Editor settings
├── src/                  # Source code (including core modules)
│   ├── cli.py           # Command line interface
│   ├── logging_config.py # Logging configuration
│   ├── validators.py     # Input validation
└── tests/               # Test files
    ├── test_*.py
    └── data/            # Test data files
```

### Module Responsibilities
- **cli.py**: Command-line argument parsing and validation (if required)
- **logging_config.py**: Centralized logging configuration with colorlog
- **validators.py**: Input validation with custom exceptions
- **main.py**: Application entry point and orchestration
- Core modules: Business logic with single responsibility

## Dependency Management

### pyproject.toml Configuration
```toml
[project]
name = "ProjectName"
version = "0.1.0"
description = "Project description"
requires-python = ">=3.13"
dependencies = [
    "pypdf>=6.0.0",
    "colorlog>=6.9.0",
    "unidecode~=1.4.0",
]

[project.optional-dependencies]
dev = [
    "black",
    "flake8", 
    "isort",
    "pytest",
]
```

### Version Pinning Strategy
- Use `>=` for core dependencies where backward compatibility is important
- Use `~=` for patch-level compatibility (e.g., `~=1.4.0` allows 1.4.x but not 1.5.0)
- Pin exact versions only when necessary for stability

### Package Metadata Access
```python
# Access package metadata at runtime
import importlib.metadata

try:
    version = importlib.metadata.version("package_name")
    metadata = importlib.metadata.metadata("package_name")
    name = metadata["Name"]
    description = metadata["Summary"]
except importlib.metadata.PackageNotFoundError:
    # Handle case where package is not installed
    version = "unknown"
```

## Development Environment Setup

### VS Code Configuration
- Configure Python interpreter path to `.venv`
- Enable format on save with Black
- Configure isort for import organization
- Set up flake8 for linting with 100-character line length
- Create debug configurations for different scenarios

### Tool Configuration in pyproject.toml
```toml
[tool.black]
line-length = 100

[tool.isort]
profile = "black"
line_length = 100

[tool.flake8]
max-line-length = 100
extend-ignore = ["E203", "W503"]
```

## Logging Patterns

### Colored Logging Setup
```python
from colorlog import ColoredFormatter

def configure_logging(verbose: bool = False, quiet: bool = False):
    formatter = ColoredFormatter(
        fmt="%(log_color)s%(levelname)s:%(reset)s %(message)s",
        log_colors={
            "DEBUG": "light_blue",
            "INFO": "green",
            "WARNING": "bold_yellow", 
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )
```

### Logger Setup
```python
import logging

logger = logging.getLogger(__name__)
```

### Logging Levels Usage
- **DEBUG**: Detailed diagnostic information, parameter values
- **INFO**: General application flow, file processing status
- **WARNING**: Recoverable issues, data quality concerns
- **ERROR**: Error conditions that don't stop execution
- **CRITICAL**: Fatal errors that stop execution

### Third-party Library Logging Control
```python
# Disable verbose logging from third-party libraries
logging.getLogger("pypdf._reader").setLevel(logging.ERROR)
logging.getLogger("validators").setLevel(logging.INFO)
```

## Error Handling Patterns

### Custom Exceptions
```python
class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass
```

### Exception Handling Structure
```python
try:
    # Main logic
    result = process_data()
except SpecificError as e:
    logger.error(f"Specific error context: {e}")
    # Handle specific case
except Exception as e:
    logger.error(f"General error context: {e}")
    # Handle general case
    # Optional: Re-raise if needed
```

### Detailed Error Tracking
```python
import traceback

try:
    # risky operation
    process_file()
except Exception as e:
    # Log basic error
    logger.error(f"Error processing file: {e}")
    
    # Capture detailed error information for debugging
    tb_list = traceback.extract_tb(e.__traceback__)
    error_file_path, error_line_number, error_function, error_code = tb_list[-1]
    logger.debug(
        f"Error in {error_file_path}, line {error_line_number}, "
        f"in {error_function}: {error_code!r}"
    )
```

## Class Design Patterns

### Constructor Pattern
```python
class ProcessorClass:
    def __init__(self, required_param, optional_param=default_value):
        self.logger = logging.getLogger(__name__)
        self.logger.debug(f"{__name__}(param='{required_param}')")
        
        # Store parameters
        self.required_param = required_param
        self.optional_param = optional_param
        
        # Initialize state
        self._validate_parameters()
```

### Method Organization
- Public methods for main functionality
- Private methods (prefix with `_`) for internal logic
- Static methods in validator classes for reusability
- Clear method documentation with Args/Returns/Raises

### Validation Pattern
```python
def _validate_parameters(self):
    try:
        self.validated_param = Validator.validate_param(self.param)
    except ValidationError as e:
        self.logger.error(f"Validation failed: {e}")
        raise
```

## File and Path Handling

### Use pathlib.Path
```python
from pathlib import Path

# Preferred approach
path_obj = Path(path_string).resolve()
for file_path in path_obj.glob("*.extension"):
    process_file(file_path)

# For compatibility when needed
file_path = str(path_obj)
```

### File Processing Pattern
```python
def process_file(file_path):
    try:
        with open(file_path, "rb") as f:
            # Process file
            pass
    except PermissionError:
        logger.error(f"Permission denied: {file_path}")
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")
```

## Configuration and CLI Patterns

### Modern CLI with importlib.metadata
```python
import importlib.metadata

class CommandLineInterface:
    def __init__(self, package_name):
        self.package_name = package_name
        self.app_name = self._get_app_name()
        self.app_version = self._get_version()
        
    def _get_version(self):
        try:
            return importlib.metadata.version(self.package_name)
        except importlib.metadata.PackageNotFoundError:
            return "unknown"
```

### argparse Setup
```python
def _create_parser(self):
    parser = argparse.ArgumentParser(
        prog=self.app_name,
        description=self.app_description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Thanks for using %(prog)s! :)"
    )
    
    # Version from package metadata
    parser.add_argument(
        "--version",
        action="version", 
        version=f"{self.app_name} v{self.app_version}"
    )
    
    # Positional arguments with defaults
    parser.add_argument("path", nargs="?", default=".", help="...")
    
    # Optional arguments with proper types
    parser.add_argument("-n", "--numfiles", type=int, default=0, help="...")
    
    # Mutually exclusive groups
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument("-v", "--verbose", action="store_true")
    verbosity.add_argument("-q", "--quiet", action="store_true")
    
    return parser
```

### CLI Validation
- Validate inputs at CLI level for immediate feedback using `parser.error()`
- Use dedicated validator classes for complex validation
- Provide helpful error messages with context

## Data Processing Patterns

### Batch Processing with Progress Tracking
```python
def process_batch(items, batch_size):
    batch = []
    for item in items:
        try:
            processed_item = process_item(item)
            batch.append(processed_item)
        except Exception as e:
            logger.error(f"Failed to process {item}: {e}")
            continue
            
        if len(batch) >= batch_size:
            logger.info(f"Batch completed with {len(batch)} records")
            write_batch(batch)
            batch = []
    
    # Process remaining items
    if batch:
        logger.info(f"Final batch with {len(batch)} records")
        write_batch(batch)
```

### Counter-based Error Tracking
```python
from collections import Counter

def process_with_error_tracking(items):
    error_counter = Counter()
    error_details = []
    
    for item in items:
        try:
            process_item(item)
        except Exception as e:
            error_counter[str(e)] += 1
            error_details.append({
                "item": item,
                "error": str(e),
                "traceback": traceback.format_exc()
            })
    
    # Log error summary
    if error_counter:
        error_summary = ", ".join(f"'{msg}' ({count})" for msg, count in error_counter.items())
        logger.debug(f"Errors encountered: {error_summary}")
```

## Testing Patterns

### Test Structure with pathlib
```python
import unittest
from pathlib import Path

class TestClassName(unittest.TestCase):
    
    def test_descriptive_name(self):
        # Use pathlib for test data
        test_file = Path(__file__).parent / "data" / "sample.pdf"
        self.assertTrue(test_file.exists())
        
        # Test the functionality
        result = function_under_test(test_file)
        
        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(result.property, expected_value)
```

### Test Data Management
- Store test files in `tests/data/` directory
- Use `Path(__file__).parent` for relative paths from test file location
- Verify test file existence and readability in tests

## Documentation Patterns

### Docstring Format
```python
def function_name(param1: type, param2: type = default) -> return_type:
    """
    Brief description of function purpose
    
    Args:
        param1: Description of parameter
        param2: Description with default mentioned
        
    Returns:
        Description of return value
        
    Raises:
        SpecificError: When this specific condition occurs
    """
```

### README Structure for CLI Applications
- Clear feature list with bullet points
- Installation instructions using pip and pyproject.toml
- Usage examples with CLI commands and different argument combinations
- Output format examples with JSON structure
- Dependency list (automatically managed via pyproject.toml)

## Performance and Resource Management

### Memory Considerations
- Process files in batches to limit memory usage
- Use generators for large datasets
- Warn about potentially memory-intensive operations
- Set reasonable limits (e.g., MAX_CHARS_PER_PAGE constants)

### Resource Cleanup
- Use context managers (`with` statements) for file operations
- Handle cleanup in exception scenarios
- Avoid resource leaks in long-running processes

## Security and Robustness

### Input Validation
- Validate all user inputs at entry points
- Check file permissions before processing
- Handle edge cases (empty directories, unreadable files)
- Use os.access() for permission checking

### Error Recovery
- Continue processing after individual failures
- Provide summary of errors at the end
- Use counters for error tracking and reporting
- Log detailed error information for debugging while showing user-friendly messages

## Modern Python Features

### Python 3.13+ Compatibility
- Use modern Python features and type hints
- Leverage pathlib for all path operations
- Use f-strings for string formatting
- Utilize importlib.metadata for package information

### Development Dependencies
- Include development tools in optional dependencies: `pip install -e ".[dev]"`
- Configure all tools through pyproject.toml
- Use modern linting and formatting tools (Black, isort, flake8)