# Resilient Data Importer CLI

A Python command-line application that imports user records from a CSV file into a JSON file, with validation, duplicate detection, custom exceptions, and logging.

## Features

- **CSV parsing:** Reads user records containing `user_id`, `name`, and `email`.
- **Duplicate detection:** Skips records whose user ID already exists in the JSON database.
- **File validation:** Checks whether the input file exists and has a CSV extension.
- **Data validation:** Skips records with empty fields or malformed rows that fail the implemented checks.
- **Custom exceptions:** Defines `ImporterError`, `FileFormatError`, and `DuplicateUserError`.
- **Logging:** Records errors and duplicate-user warnings or information in the configured log outputs.
- **JSON storage:** Saves imported records to `db.json`.

## Requirements

- Python 3.11 or later
- No third-party packages are required by the current implementation.

## Project Structure

```text
resilient-data-importer/
├── main.py
├── users.csv
├── db.json
├── app.log
├── .gitignore
├── requirements.txt
├── .pre-commit-config.yaml
└── README.md
```

The structure above is illustrative. Adjust the filenames to match your actual repository. The current implementation should be saved in `main.py` or another appropriate Python entry-point file.

## Setup

Clone the repository:

```bash
git clone <your-repository-url>
cd <your-repository-directory>
```

Create and activate a virtual environment.

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux/macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

No third-party dependencies are currently required. If you add development tools such as pytest, Ruff, Black, mypy, and pre-commit, list them in `requirements.txt` and install them with:

```bash
pip install -r requirements.txt
```

## Input Format

The input CSV file must contain these column headers:

```csv
user_id,name,email
1,Alice,alice@example.com
2,Brian,brian@example.com
3,Carol,carol@example.com
```

Each record should contain a user ID, name, and email address.

## Usage

Run the importer with the CSV file path as a command-line argument:

```bash
python main.py users.csv
```

The application reads the existing `db.json` file or initializes it as an empty JSON list if it does not exist. It then processes the CSV records and writes the resulting database back to `db.json`.

### Expected behavior

- New records with non-empty fields are added to the JSON database.
- Records with user IDs already present in the database are skipped and logged.
- Records with empty fields are skipped and logged.
- A missing CSV file raises `ImporterError`.
- A file with an unsupported extension raises `FileFormatError`.

The current implementation performs basic field checks. It does not yet fully validate CSV headers, email syntax, or every possible malformed row.

## Output

Imported records are stored in `db.json` as a JSON list:

```json
[
    {
        "user_id": "1",
        "name": "Alice",
        "email": "alice@example.com"
    }
]
```

Log messages are configured to use the following format:

```text
2026-10-18 14:30 - INFO - Example log message
```

The configured file handler writes to `app.log`, while the console handler displays messages on the console. Depending on the logger configuration, some messages may appear in both outputs.

## Error Handling

The application defines three custom exception classes:

| Exception | Purpose |
|---|---|
| `ImporterError` | Reports a missing input CSV file. |
| `FileFormatError` | Reports an unsupported file extension. |
| `DuplicateUserError` | Identifies a user ID that already exists in the database. |

Duplicate records are skipped so that processing can continue with subsequent rows.

## Development and Testing

The project is intended to use pytest for automated testing, including:

- Testing valid CSV imports.
- Testing missing files and unsupported extensions.
- Testing duplicate user IDs.
- Testing rows with missing values.
- Testing JSON database persistence.
- Using fixtures and mocks to isolate components.
- Measuring coverage with coverage.py.

Once the test suite is configured, run:

```bash
pytest
```

Generate a coverage report with:

```bash
coverage run -m pytest
coverage report -m
coverage html
```

The HTML report is generated in `htmlcov/`. These commands require the relevant development dependencies to be installed.

## Git Workflow

The project follows a Git Flow-inspired workflow:

- `main`: stable, release-ready code.
- `develop`: integrated development work.
- `feature/*`: individual features developed independently.

Example workflow:

```bash
git switch -c feature/csv-parser
git add .
git commit -m "Implement CSV parsing"
git push -u origin feature/csv-parser
```

Open a pull request from the feature branch into `develop`. After review and testing, merge the changes. Merge `develop` into `main` when the project is ready for release.

## Current Limitations

- The implementation is currently concentrated in one Python file rather than separate parsing, validation, and storage modules.
- The command-line entry point assumes a CSV argument is provided.
- CSV headers and malformed row structures are not comprehensively validated.
- Email syntax and whitespace-only values are not fully validated.
- JSON persistence is not yet protected against every possible file or data corruption error.
- Automated tests, static type checking, linting, and pre-commit enforcement must be configured and verified separately.

## Future Improvements

- Separate parsing, validation, and storage into dedicated modules.
- Add a proper command-line interface with `argparse`.
- Validate CSV headers and record structure before processing.
- Add comprehensive pytest unit and integration tests.
- Configure Ruff, Black, mypy, and pre-commit hooks.
- Add atomic JSON writes and more robust exception handling.
- Document and verify test coverage above 90%.

## License

Add a license if you intend to distribute the project publicly.
