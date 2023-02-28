import csv
import json

file_names = ["Damage", "Vehicles_Tripods_Emplacements", "Weapons", "Structures", "Multitier_Structures"]

def csv_to_json(csvFilePath, jsonFilePath):
    jsonArray = []

    # read csv file
    with open(csvFilePath, encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf)

        # convert each csv row into python dict
        for row in csvReader:
            # add this python dict to json array
            jsonArray.append(row)

    # convert python jsonArray to JSON String and write to file
    with open(jsonFilePath, 'w', encoding='utf-8') as jsonf:
        jsonString = json.dumps(jsonArray, indent=4)
        jsonf.write(jsonString)


def json_to_js(jsonFilePath, jsFilePath, object_name):

    with open(jsonFilePath, encoding='utf-8') as jsonf:
        with open(jsFilePath, 'w', encoding='utf-8') as jsf:
            jsf.write(f"export const {object_name} = ")
            for row in jsonf.readlines():
                final = ""
                if ":" in row:
                    splited = row.split(":")
                    without = splited[0]
                    if "(" in without:
                        without = without.split("(")[0] + "\""
                    without = without.replace(" ", "")
                    if (without == "\"Name\""):
                        jsf.write(f"\"ObjectType\":\"{object_name}\",\n")
                    final = ":".join([without] + splited[1:])
                else:
                    final = row
                jsf.write(final)

#MAIN

for file_name in file_names:
    csv_file, json_file, js_file = file_name + ".csv", file_name + ".json", file_name + ".js"
    csv_to_json(csv_file, json_file)
    json_to_js(json_file, js_file, file_name)