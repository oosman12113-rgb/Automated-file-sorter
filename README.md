# Automated File Sorter

A command-line Python utility that automatically organizes files into folders based on file type.

This project is designed as a practical automation tool rather than a one-off script. It supports configurable file categories, dry-run previews, recursive sorting, duplicate-name protection, logging, and automated tests.

## Features

- Sorts files into categories such as:
  - Images
  - Documents
  - Videos
  - Audio
  - Archives
  - Code
  - Other
- Automatically creates destination folders
- Prevents accidental overwriting of duplicate filenames
- Supports a safe `--dry-run` preview mode
- Supports recursive sorting
- Supports custom file categories through JSON
- Optional file logging
- Includes unit tests
- Uses only the Python standard library

## Project Structure

```text
automated_file_sorter/
├── sorter.py
├── config.example.json
├── README.md
├── .gitignore
└── tests/
    └── test_sorter.py
```

## Requirements

Python 3.10+ is recommended.

No third-party packages are required.

## Quick Start

Clone the project and move into the project directory:

```bash
git clone <your-repository-url>
cd automated_file_sorter
```

Preview what the sorter would do:

```bash
python sorter.py ~/Downloads --dry-run
```

Sort the files:

```bash
python sorter.py ~/Downloads
```

On Windows, you can use a path such as:

```powershell
python sorter.py "C:\Users\YourName\Downloads"
```

## Usage

```text
python sorter.py SOURCE [options]
```

### Useful options

```text
-d, --destination PATH   Put sorted folders somewhere other than SOURCE
-c, --config PATH        Load custom categories from a JSON file
--dry-run                Preview changes without moving anything
-r, --recursive          Include files in subfolders
--log PATH               Save activity to a log file
-v, --verbose            Print additional details
```

## Examples

Sort your Downloads folder:

```bash
python sorter.py ~/Downloads
```

Preview a recursive sort:

```bash
python sorter.py ~/Downloads --recursive --dry-run
```

Sort files into another directory:

```bash
python sorter.py ~/Downloads --destination ~/Organized
```

Save an activity log:

```bash
python sorter.py ~/Downloads --log sorter.log
```

Use custom categories:

```bash
python sorter.py ~/Downloads --config config.example.json
```

## Custom Categories

Edit `config.example.json` or create your own JSON configuration:

```json
{
  "Images": [".jpg", ".jpeg", ".png"],
  "Documents": [".pdf", ".docx", ".txt"],
  "Code": [".py", ".js", ".java"]
}
```

Extensions not listed in the configuration are placed in `Other`.

## Duplicate File Protection

If a file with the same name already exists, the sorter does not overwrite it.

For example:

```text
report.pdf
report (1).pdf
report (2).pdf
```

## Running Tests

From the project folder:

```bash
python -m unittest discover -s tests
```

## Resume Description

**Automated File Sorter | Python**

- Developed a Python command-line automation tool that categorizes and organizes files by extension using configurable rules.
- Implemented recursive directory processing, dry-run previews, logging, and duplicate-file protection to improve reliability and prevent data loss.
- Wrote unit tests for file categorization, sorting behavior, and filename conflict handling using Python's standard testing library.

## Future Improvements

Potential additions include:

- Desktop GUI
- Scheduled background sorting
- File-size and date-based organization
- Undo functionality
- Watch mode for automatic real-time sorting
