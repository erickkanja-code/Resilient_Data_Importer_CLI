import pytest
from unittest.mock import mock_open

from main import (
    User,
    check_duplicate,
    check_if_csv_exists,
    check_file_format,
    DuplicateUserError,
    ImporterError,
    FileFormatError,
)


# Test 1: Check that a User object stores its attributes correctly.
def test_user_creation():
    test_user = User("10", "Erick", "erick@example.com")

    assert test_user.user_id == "10"
    assert test_user.name == "Erick"
    assert test_user.email == "erick@example.com"


# Test 2: Check that duplicate users are rejected.
def test_duplicate_user():
    test_user = User("10", "Erick", "erick@example.com")

    json_content = [
        {
            "user_id": "10",
            "name": "Erick",
            "email": "erick@example.com",
        }
    ]

    # The function should raise this exception for a duplicate ID.
    with pytest.raises(DuplicateUserError):
        check_duplicate(test_user, json_content)


# Test 3: Check that a new user is allowed.
def test_new_user():
    test_user = User("20", "Brian", "brian@example.com")

    json_content = [
        {
            "user_id": "10",
            "name": "Erick",
            "email": "erick@example.com",
        }
    ]

    # No exception should be raised because ID 20 is not in the database.
    check_duplicate(test_user, json_content)


# Test 4: Check that a missing CSV file raises an exception.
def test_missing_csv_file():
    with pytest.raises(ImporterError):
        check_if_csv_exists("missing_file.csv")


# Test 5: Check that an incorrect file extension is rejected.
def test_incorrect_file_format():
    with pytest.raises(FileFormatError):
        check_file_format("users.txt")


# Test 6: Use a fixture to create a temporary CSV file.
@pytest.fixture
def csv_file(tmp_path):
    # tmp_path is a temporary directory provided by pytest.
    file_path = tmp_path / "users.csv"

    file_path.write_text(
        "user_id,name,email\n10,Erick,erick@example.com\n",
        encoding="utf-8",
    )

    return file_path


def test_csv_file_exists(csv_file):
    # The fixture gives this test the path to the temporary CSV file.
    check_if_csv_exists(str(csv_file))


# Test 7: Mock file opening so we don't need to open a real file.
def test_mock_file_open(mocker):
    fake_file = mock_open(
        read_data="user_id,name,email\n10,Erick,erick@example.com\n"
    )

    # Replace open() with our mock for the duration of this test.
    mocker.patch("builtins.open", fake_file)

    with open("users.csv", "r", encoding="utf-8") as file:
        content = file.read()

    assert "Erick" in content
    fake_file.assert_called_once_with(
        "users.csv", "r", encoding="utf-8"
    )