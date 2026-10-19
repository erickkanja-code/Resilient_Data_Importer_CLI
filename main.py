
import csv
import json
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


logger = logging.getLogger("console_and_file_logger")
file_logger = logging.getLogger("file_logger")

logger.setLevel(logging.INFO)
file_logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
file_handler = logging.FileHandler("app.log", mode="a", encoding="utf-8")

formatter = logging.Formatter(
    "{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
)

console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)
file_logger.addHandler(file_handler)


@dataclass
class User:
    """Represent a user record."""

    user_id: str
    name: str
    email: str


class DuplicateUserError(Exception):
    """Raised when a user already exists in the database."""


class ImporterError(Exception):
    """Raised when an error occurs during importing."""


class FileFormatError(Exception):
    """Raised when the supplied file has an unsupported format."""


def check_duplicate(
    new_user: User, json_content: list[dict[str, Any]]
) -> None:
    """Check whether a user ID already exists.

    Args:
        new_user: The user being imported.
        json_content: Existing database records.

    Raises:
        DuplicateUserError: If the user ID already exists.
    """
    for record in json_content:
        if new_user.user_id == record["user_id"]:
            raise DuplicateUserError(
                f"{new_user.name} has already been saved to the database."
            )


def check_if_csv_exists(csv_name: str) -> None:
    """Check whether the CSV file exists.

    Args:
        csv_name: The path to the CSV file.

    Raises:
        ImporterError: If the file does not exist.
    """
    if not Path(csv_name).exists():
        error_message = "The CSV file could not be found"
        logger.error(error_message)
        raise ImporterError(error_message)


def check_file_format(csv_name: str) -> None:
    """Check whether the file has a CSV extension.

    Args:
        csv_name: The path to the file.

    Raises:
        FileFormatError: If the extension is not CSV.
    """
    if Path(csv_name).suffix.lower() != ".csv":
        error_message = "Incorrect format. Upload csv file."
        logger.error(error_message)
        raise FileFormatError(error_message)


def main() -> None:
    """Import CSV user records into the JSON database."""
    if len(sys.argv) < 2:
        logger.error("Please provide a CSV filename.")
        raise ImporterError("Please provide a CSV filename.")

    database_path = Path("db.json")

    if database_path.exists():
        with open(database_path, "r", encoding="utf-8") as file:
            json_content: list[dict[str, Any]] = json.load(file)
    else:
        json_content = []

    csv_name = sys.argv[1]

    check_if_csv_exists(csv_name)
    check_file_format(csv_name)

    with open(csv_name, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        required_fields = {"user_id", "name", "email"}

        if reader.fieldnames is None or not required_fields.issubset(
            reader.fieldnames
        ):
            logger.error("CSV file is missing required headers.")
            raise ImporterError("CSV file is missing required headers.")

        for row in reader:
            new_user = User(
                row.get("user_id") or "",
                row.get("name") or "",
                row.get("email") or "",
            )

            try:
                check_duplicate(new_user, json_content)
            except DuplicateUserError as error:
                file_logger.info(error)
                continue

            if not new_user.user_id or not new_user.name or not new_user.email:
                file_logger.error(
                    f"Record {new_user.user_id} has empty fields. "
                    "Not recorded in database."
                )
                continue

            json_content.append(
                {
                    "user_id": new_user.user_id,
                    "name": new_user.name,
                    "email": new_user.email,
                }
            )

    with open(database_path, "w", encoding="utf-8") as file:
        json.dump(json_content, file, indent=4)

    logger.info("Import completed successfully.")


if __name__ == "__main__":
    main()
