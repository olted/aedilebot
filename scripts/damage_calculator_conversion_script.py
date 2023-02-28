import csv
import json

misc_names = ["Damage"]
weapon_names = ["Weapons"]
target_names = ["Vehicles", "Emplacements", "Tripods", "Structures", "Multitier_structures"]


def csv_to_dictionary(csvFilePath, type="Entity"):
    jsonDictionary = {}
    with open(csvFilePath, encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf)

        for row in csvReader:
            # everything we want to do with data before we put it into jsonArray
            row["ObjectType"] = type
            jsonDictionary[row["Name"]] = row

    return jsonDictionary


def dictionary_to_json(json_dictionary, json_file_path):
    # convert python jsonArray to JSON String and write to file
    with open(json_file_path, 'w', encoding='utf-8') as jsonf:
        jsonString = json.dumps(json_dictionary, indent=4)
        jsonf.write(jsonString)



for file_name in misc_names:
    csv_file, json_file = file_name + ".csv", file_name + ".json"
    dictionary_to_json(csv_to_dictionary(csv_file, file_name), json_file)

for file_name in weapon_names:
    csv_file, json_file = file_name + ".csv", file_name + ".json"
    dictionary_to_json(csv_to_dictionary(csv_file, file_name), json_file)

targets = dict()
for file_name in target_names:
    csv_file, json_file = file_name + ".csv", file_name + ".json"
    targets = targets | csv_to_dictionary(csv_file, file_name)
dictionary_to_json(targets, "Targets.json")