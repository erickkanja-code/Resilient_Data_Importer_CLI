import csv
import json
from dataclasses import dataclass
import logging

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



with open("file2.json", "r") as file:
    json_content = json.load(file)


cleaned_csv_content =[]
with open("users.csv", 'r', newline="") as file:
    reader = csv.DictReader(file)
    for row in reader:
        new_user = User(row['user_id'], row['name'], row['email'])
        duplicate = False
        if json_content:
            for record in json_content:
                try:
                    if new_user.user_id == record['user_id']:
                        duplicate = True
                        # Handle duplicate. (Log and then throw exception)
                        raise DuplicateUserError(f"{new_user.name} has already been saved to the database.")

                except DuplicateUserError as error:
                    logging.error(error) 
                    break
            if not duplicate:
                cleaned_csv_content.append(row)
        else:
            cleaned_csv_content.append(row)
        
with open("file2.json", 'w') as file2:
    json.dump(cleaned_csv_content, file2, indent=4)  

print(cleaned_csv_content)







        
        