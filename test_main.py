
import json
import runpy
import sys
from pathlib import Path

import pytest

from main import (
    User,
    DuplicateUserError,
    ImporterError,
    FileFormatError,
    check_duplicate,
    check_if_csv_exists,
    check_file_format,
    main,
)


def test_user_creation():
    user = User("1", "Erick", "erick@example.com")

    assert user.user_id == "1"
    assert user.name == "Erick"
    assert user.email == "erick@example.com"


def test_duplicate_user():
    user = User("1", "Erick", "erick@example.com")
    database = [{"user_id": "1", "name": "Erick", "email": "erick@example.com"}]

    with pytest.raises(DuplicateUserError):
        check_duplicate(user, database)


def test_new_user():
    user = User("2", "Jane", "jane@example.com")

    check_duplicate(user, [])


def test_non_duplicate_user():
    user = User("2", "Jane", "jane@example.com")
    database = [{"user_id": "1", "name": "Erick", "email": "erick@example.com"}]

    check_duplicate(user, database)


def test_missing_csv_file(tmp_path):
    missing_file = tmp_path / "missing.csv"

    with pytest.raises(ImporterError):
        check_if_csv_exists(str(missing_file))


def test_csv_file_exists(tmp_path):
    csv_file = tmp_path / "users.csv"
    csv_file.write_text("user_id,name,email\n", encoding="utf-8")

    check_if_csv_exists(str(csv_file))


def test_incorrect_file_format():
    with pytest.raises(FileFormatError):
        check_file_format("users.txt")


def test_correct_file_format():
    check_file_format("users.csv")


def test_uppercase_csv_extension():
    check_file_format("users.CSV")


def test_main_without_argument(monkeypatch):
    # Pretend the user ran the program without providing a CSV filename.
    monkeypatch.setattr(sys, "argv", ["main.py"])

    with pytest.raises(ImporterError):
        main()


def test_main_creates_database(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["main.py", "users.csv"])

    Path("users.csv").write_text(
        "user_id,name,email\n1,Erick,erick@example.com\n",
        encoding="utf-8",
    )

    main()

    data = json.loads(Path("db.json").read_text(encoding="utf-8"))
    assert len(data) == 1
    assert data[0]["user_id"] == "1"


def test_main_adds_to_existing_database(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["main.py", "users.csv"])

    Path("db.json").write_text(
        json.dumps([{
            "user_id": "1",
            "name": "Erick",
            "email": "erick@example.com",
        }]),
        encoding="utf-8",
    )
    Path("users.csv").write_text(
        "user_id,name,email\n2,Jane,jane@example.com\n",
        encoding="utf-8",
    )

    main()

    data = json.loads(Path("db.json").read_text(encoding="utf-8"))
    assert len(data) == 2


def test_main_skips_duplicate(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["main.py", "users.csv"])

    Path("db.json").write_text(
        json.dumps([{
            "user_id": "1",
            "name": "Erick",
            "email": "erick@example.com",
        }]),
        encoding="utf-8",
    )
    Path("users.csv").write_text(
        "user_id,name,email\n1,Erick,erick@example.com\n",
        encoding="utf-8",
    )

    main()

    data = json.loads(Path("db.json").read_text(encoding="utf-8"))
    assert len(data) == 1


def test_main_skips_empty_fields(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["main.py", "users.csv"])

    Path("users.csv").write_text(
        "user_id,name,email\n1,,erick@example.com\n",
        encoding="utf-8",
    )

    main()

    data = json.loads(Path("db.json").read_text(encoding="utf-8"))
    assert data == []


def test_main_missing_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["main.py", "missing.csv"])

    with pytest.raises(ImporterError):
        main()


def test_main_wrong_extension(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["main.py", "users.txt"])
    Path("users.txt").write_text("some data", encoding="utf-8")

    with pytest.raises(FileFormatError):
        main()


def test_main_missing_headers(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["main.py", "users.csv"])
    Path("users.csv").write_text("username,email\nErick,erick@example.com\n",
                                 encoding="utf-8")

    with pytest.raises(ImporterError):
        main()


def test_main_empty_csv(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["main.py", "users.csv"])
    Path("users.csv").write_text("", encoding="utf-8")

    with pytest.raises(ImporterError):
        main()


def test_main_skips_row_with_missing_column(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["main.py", "users.csv"])
    Path("users.csv").write_text(
        "user_id,name,email\n1,Erick\n",
        encoding="utf-8",
    )

    main()

    data = json.loads(Path("db.json").read_text(encoding="utf-8"))
    assert data == []


def test_script_entry_point(tmp_path, monkeypatch):
    # Run main.py as if it had been started from the terminal.
    monkeypatch.chdir(tmp_path)
    Path("users.csv").write_text(
        "user_id,name,email\n1,Erick,erick@example.com\n",
        encoding="utf-8",
    )

    main_file = str(Path(main.__code__.co_filename).resolve())
    monkeypatch.setattr(sys, "argv", ["main.py", "users.csv"])

    runpy.run_path(main_file, run_name="__main__")

    data = json.loads(Path("db.json").read_text(encoding="utf-8"))
    assert len(data) == 1
