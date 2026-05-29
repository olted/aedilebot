import json
import os
import csv
from collections import defaultdict


def load_json_to_dict(filename):
    with open(filename, encoding="utf-8") as f:
        dict = json.load(f)
        return dict


def load_locations_from_csv(filename):
    locations_dict = {}
    with open(filename, encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 3:
                hex_name = row[0].strip()
                location_name = row[1].strip()
                location_type = row[2].strip()
                locations_dict[location_name] = location_type
    return locations_dict

def load_locations_into_targets(location_dict, targets_dict):
    type_key_map = {
        "Post Office TH": "Town Base (Post Office)",
        "Town Center TH": "Town Base (Town Centre)",
        "School TH": "Town Base (School)",
        "Small Relic": "Small Relic Base",
        "Medium Relic": "Medium Relic Base",
        "Large Relic": "Large Relic Base",
    }
    # add location names as additional names to targets
    for location_name, location_type in location_dict.items():
        if location_type in type_key_map:
            target_key = type_key_map[location_type]
            if target_key in targets_dict:
                if "Additional Names" in targets_dict[target_key]:
                    targets_dict[target_key]["Additional Names"] += ";" + location_name
                else:
                    targets_dict[target_key]["Additional Names"] = location_name
            else:
                print(f"WARNING: target key {target_key} not found in targets dictionary")


def get_all_names(dictionary, field_name="Additional Names"):
    names_dictionary = {}
    for key, value in dictionary.items():
        additional_names = [value["Name"]]

        if field_name in value:
            additional_names.extend(value[field_name].split(";"))
        additional_names.append(key) if key not in additional_names else None # add key to list of alias if not already

        for name in additional_names:
            name = name.lower()
            if name == "":
                continue
            if name in names_dictionary:
                # raise RuntimeError(f"Name {name} repeats itself in {names_dictionary[name]} and {key}")
                # prioritize targets over weapon
                if value["ObjectType"] == "Weapons":
                    continue
            names_dictionary[name] = key
    return names_dictionary


# this is inconsistent with other functions, add husk tag in json data later to make consistent
def get_husk_names(names_dictionary):
    husk_names_dict = {}
    for key, value in names_dictionary.items():
        if "husk" in key.lower():
            husk_names_dict[key] = value
            husk_names_dict[key.replace("husk", "")] = value
    return husk_names_dict


def get_vehicle_names(dictionary, field_name="Additional Names"):
    names_dictionary = {}
    for key, value in dictionary.items():
        # for now treat aircraft parts as vehicles
        if value["ObjectType"] != "Vehicles" and value["ObjectType"] != "Aircraft_Parts":
            continue
        additional_names = [value["Name"]]

        if field_name in value:
            additional_names.extend(value[field_name].split(";"))

        for name in additional_names:
            name = name.lower()
            if name == "" or name in names_dictionary:
                continue
            names_dictionary[name] = key
    return names_dictionary


def get_bunker_spec(string):
    # size <number> tier <1/2/3> bunker with <numer> <modification>, <numer> <modification>, ...
    args = defaultdict(int)
    tier_words = {
        "t1": 1,
        "t2": 2,
        "t3": 3,
        "tier 1": 1,
        "tier 2": 2,
        "tier 3": 3,
        "concrete": 3,
    }
    mod_words = {
        "atg": "atg",
        "at": "atg",
        "rg": "rg",
        "rifle": "rg",
        "hg": "hg",
        "howi": "hg",
        "howie": "hg",
        "mg": "mg",
        "machinegun": "mg",
        "machine": "mg",
        "mgg": "mg",
        "ammunition": "ammo",
        "ramp": "ramp",
        "med": "med",
        "medical": "med",
        "hospital": "med",
        "howitzer": "hg",
        "engine": "eng",
        "sc": "sc",
        "storm": "sc",
        "ic": "ic",
        "intel": "ic",
        "intelligence": "ic",
        "weather": "ws",
        "weathers": "ws",
        "base": "core",
        "core": "core",
        "storage": "ammo",
        "ammo": "ammo",
        "obs": "obs",
        "observation": "obs",
        "gen": "eng",
        "generator": "eng",
        "generater": "eng",
        "howitzer": "hg",
        "arty": "hg",
        "artillery": "hg",
        "shelter": "shelter",
        "uf": "fortress",
        "fort": "fortress",
        "underground": "fortress",
        "radar": "radar",
        "aerial": "radar",
        "array": "radar",
        "red": "red",
        "green": "green",
    }
    words = (
        string.lower()
        .replace(",", " ")
        .replace(";", " ")
        .replace("hr", "hour")
        .replace("hours", "hour")
        .split()
    )
    if "size" in words:
        if words[words.index("size") + 1].isdigit():
            args["size"] = int(words[words.index("size") + 1])
        elif (
            words.index("size") - 1 > 0
            and words[words.index("size") - 1].isdigit()
        ):
            args["size"] = int(words[words.index("size") - 1])
        else:
            return None
    else:
        return None

    if "hour" in words:
        if (
            words.index("hour") - 1 >= 0
            and words[words.index("hour") - 1].isdigit()
        ):
            args["wet"] = int(words[words.index("hour") - 1])
    else:
        args["wet"] = 24

    for keyword in tier_words:
        if keyword in words:
            args["tier"] = tier_words[keyword]
            break
    else:
        return None

    # slice so only <number> <modification> pairs remain
    if "with" in words:
        words = words[words.index("with") :]
    else:
        words = words[words.index("size") :]

    mod_count = 0

    for i, word in enumerate(words):
        if word not in mod_words:
            # catch mod word in multiple form (howis, ATGs)
            if word[-1] == "s" and word[:-1] in mod_words:
                word = word[:-1]
        if word in mod_words:
            # if word == "bunker" and i + 1 < len(words) and words[i + 1] in mod_words:
            #     # catch phrases like "bunker ramp"
            #     word = words[i + 1]
            #     print("reached!! " + word)
            # if (word == "arty" or word == "artillery") and i + 1 < len(words) and words[i + 1] == "shelter":
            #     # catch phrases like "arty shelter"
            #     word = "shelter"
            if i - 1 >= 0:
                if words[i - 1].isdigit():
                    args[mod_words[word]] += int(words[i - 1])
                    if word != "green" and word != "red":
                        mod_count += int(words[i - 1])
                else:
                    args[mod_words[word]] += 1
                    if word != "green" and word != "red":
                        mod_count += 1
    if mod_count > args["size"]:
        return None
    return args


# Structure Json parser
locations_dictionary = load_locations_from_csv(
    os.path.join("data", "Locations.csv")
)


def check_if_location_name(name):
    return any(name.casefold() == k.casefold() for k in locations_dictionary)


targets = load_json_to_dict(os.path.join("data", "Targets.json"))
load_locations_into_targets(locations_dictionary, targets)
damages = load_json_to_dict(os.path.join("data", "Damage.json"))
weapons = load_json_to_dict(os.path.join("data", "Weapons.json"))
all = weapons | targets
bunker_stats = load_json_to_dict(os.path.join("data", "Bunker_piece.json"))


targets_dictionary = get_all_names(targets)
husk_dictionary = get_husk_names(targets_dictionary)
vehicle_dictionary = get_vehicle_names(targets)
weapons_dictionary = get_all_names(weapons)
all_dictionary = get_all_names(all)

print("All Data loaded into memory")
# slang
