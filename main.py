import csv
import json
from dataclasses import dataclass

@dataclass
class User:
    user_id: str
    name: str
    email: str





with open("file2.json", "r") as file:
    json_content = json.load(file)


cleaned_csv_content =[]
with open("users.csv", 'r', newline="") as file:
    reader = csv.DictReader(file)
    for row in reader:
        new_user = User(row['user_id'], row['name'], row['email'])
        if json_content:
            for record in json_content:
                if new_user.user_id == record['user_id']:
                    # Handle duplicate. (Log and then throw exception)
                    print("This is a duplicate")
                    break
            cleaned_csv_content.append(row)
        else:
            cleaned_csv_content.append(row)
        
with open("file2.json", 'w') as file2:
    json.dump(cleaned_csv_content, file2, indent=4)  

print(cleaned_csv_content)









        

        
        