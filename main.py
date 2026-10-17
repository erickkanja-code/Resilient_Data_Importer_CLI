import csv
import json
from dataclasses import dataclass
import logging
from pathlib import Path

logging.basicConfig(filename="app.log", 
                    encoding='utf-8', 
                    filemode='a',
                    level=10, 
                    format="{asctime} - {levelname} - {message}", style='{'
                    )

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

if Path("db.json").exists():
    with open("db.json", "r") as file:
        json_content = json.load(file)
else:
    with open("db.json", "w") as file:
        json_content = []


cleaned_csv_content =[]
with open("users2.csv", 'r', newline="") as file:
    reader = csv.DictReader(file)
    for row in reader:
        new_user = User(row['user_id'], row['name'], row['email'])
        # if json_content:
        #     for record in json_content:
        #         try:
        #             if new_user.user_id == record['user_id']:
        #                 duplicate = True
        #                 # Handle duplicate. (Log and then throw exception)
        #                 raise DuplicateUserError(f"{new_user.name} has already been saved to the database.")
        try:
            check_duplicate(new_user, json_content)
        except DuplicateUserError as error:
            logging.error(error) 
            continue
        cleaned_csv_content.append(row)

        
with open("db.json", 'a') as file2:
    json.dump(cleaned_csv_content, file2, indent=4)  









        
        