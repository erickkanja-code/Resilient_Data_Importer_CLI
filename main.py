import csv
import json
from dataclasses import dataclass
import logging
from pathlib import Path

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
    user_id: str
    name: str
    email: str

class DuplicateUserError(Exception):
    pass

class ImporterError(Exception):
    pass
class FileFormatError(Exception):
    pass

def check_duplicate(new_user, json_content):
    if json_content:
        for record in json_content:
            if new_user.user_id == record['user_id']:
                raise DuplicateUserError(f"{new_user.name} has already been saved to the database.")
    else:
        return
    
def check_if_csv_exists(csv_name):
    if not Path(csv_name).exists():
        error_message = "The CSV file could not be found"
        logger.error(error_message)
        
        raise ImporterError(error_message)


if Path("db.json").exists():
    with open("db.json", "r") as file:
        json_content = json.load(file)
else:
    with open("db.json", "w") as file:
        json_content = []
        json.dump(json_content, file)

csv_name = "users.csv"
check_if_csv_exists(csv_name)
if not csv_name.endswith('csv'):
    raise FileFormatError()

with open(csv_name, 'r', newline="") as file:
    reader = csv.DictReader(file)
    for row in reader:
        new_user = User(row['user_id'], row['name'], row['email'])
        try:
            check_duplicate(new_user, json_content)
        except DuplicateUserError as error:
            file_logger.error(error) 
            continue
        json_content.append(row)

    


        
with open("db.json", 'w') as file2:
    json.dump(json_content, file2, indent=4)  









        
        