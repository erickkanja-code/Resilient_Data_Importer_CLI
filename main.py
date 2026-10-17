import csv
import json
from dataclasses import dataclass
import logging
from pathlib import Path
import sys


logger = logging.getLogger("console_and _file_logger")
file_logger = logging.getLogger("file_logger")

console_handler = logging.StreamHandler()
file_handler = logging.FileHandler("app.log", mode='a', encoding='utf-8')

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
    """Represent a user record.

    Attributes:
        user_id: The unique identifier assigned to the user.
        name: The user's name.
        email: The user's email address.
    """

    user_id: str
    name: str
    email: str


class DuplicateUserError(Exception):
    """Raised when a user already exists in the database."""


class ImporterError(Exception):
    """Raised when an error occurs during the import process."""


class FileFormatError(Exception):
    """Raised when the supplied file has an unsupported format."""


def check_duplicate(new_user, json_content):
    """Check whether a user already exists in the database.

    Args:
        new_user: The User object to check.
        json_content: The existing user records loaded from the JSON database.

    Raises:
        DuplicateUserError: If the user's ID already exists in the database.
    """
    if json_content:
        for record in json_content:
            if new_user.user_id == record['user_id']:
                raise DuplicateUserError(f"{new_user.name} has already been saved to the database.")
    else:
        return


def check_if_csv_exists(csv_name):
    """Check whether the specified CSV file exists.

    Args:
        csv_name: The path to the CSV file.

    Raises:
        ImporterError: If the specified file does not exist.
    """
    if not Path(csv_name).exists():
        error_message = "The CSV file could not be found"
        logger.error(error_message)
        raise ImporterError(error_message)


def check_file_format(csv_name):
    """Validate the file extension.

    Args:
        csv_name: The path or name of the file to validate.

    Raises:
        FileFormatError: If the file does not have a CSV extension.
    """
    if not csv_name.endswith("csv"):
        error_message = "Incorrect format. Upload csv file."
        logger.error(error_message)
        raise FileFormatError(error_message)


if __name__ == "__main__":
    if Path("db.json").exists():
        with open("db.json", "r") as file:
            json_content = json.load(file)
    else:
        with open("db.json", "w") as file:
            json_content = []
            json.dump(json_content, file)

    csv_name = sys.argv[1]
    check_if_csv_exists(csv_name)
    check_file_format(csv_name)

    with open(csv_name, 'r', newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            new_user = User(row['user_id'], row['name'], row['email'])

            try:
                check_duplicate(new_user, json_content)
            except DuplicateUserError as error:
                file_logger.info(error)
                continue

            if row['user_id'] and row["name"] and row['email']:
                if not isinstance(row['user_id'], str) or not isinstance(row["name"], str) or not isinstance(row['email'], str):
                    file_logger.error(f"Record {row['user_id']} has some wrong/malformed fields. Not recorded in database")
                    continue
            else:
                file_logger.error(f"Record {row['user_id']} has some empty cells. Not recorded in database")
                continue

            json_content.append({'user_id': row['user_id'], 'name': row['name'], 'email': row['email']})

    with open("db.json", 'w') as file2:
        json.dump(json_content, file2, indent=4)