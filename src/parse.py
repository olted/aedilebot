import json
import os
from collections import defaultdict
import fuzzy as fuzz
from decimal import Decimal

DEV_PATH = "data_dev"
MANUAL_PATH = "data_manual"
MINED_PATH = "data_mined"

VEHICLE_DYNAMIC_DATA = "vehicle_dynamic_data.json"
WEAPON_DYNAMIC_DATA = "weapon_dynamic_data.json"
STRUCTURE_DYNAMIC_DATA_WORLD = "structure_dynamic_data_world.json"
STRUCTURE_DYNAMIC_DATA_TRIPODS = "structure_dynamic_data_tripods.json"
STRUCTURE_DYNAMIC_DATA_PLAYER_BUILT = "structure_dynamic_data_player_built.json"
STRUCTURE_DYNAMIC_DATA_SHIPPABLES = "structure_dynamic_data_shippables.json"
STRUCTURE_DYNAMIC_DATA_FACILITIES = "structure_dynamic_data_facilities.json"
STRUCTURE_DYNAMIC_DATA_EMPLACEMENTS = "structure_dynamic_data_emplacements.json"
STRUCTURE_DYNAMIC_DATA_BUNKERS = "structure_dynamic_data_bunkers.json"
MOUNTS_DYNAMIC_DATA = "mounts_dynamic_data.json"
DAMAGE_PROFILES_DYNAMIC_DATA = "damage_profiles_dynamic_data.json"
AMMO_DYNAMIC_DATA = "ammo_dynamic_data.json"
EMPLACEMENT_DYNAMIC_DATA = "structure_dynamic_data_emplacements.json"
# parsed data
TARGETS_VEHICLES = "targets_vehicles.json"
WEAPONS_BASE = "weapons_base.json"
WEAPONS_VEHICLES = "weapons_vehicles.json"
WEAPONS_INF = "weapons_inf.json"
WEAPONS_EMP = "weapons_emp.json"
DAMAGE = "Damage.json"
# manual (should be low amount of change not accounted by any automation)
VEHICLE_MOUNT_DATA = "vehicle_mount_data.json"
DAMAGE_TYPE_NAME_PAIRS = "damage_type_name_pairs.json"
# alias
ALIAS_MISC_WEAPONS = "alias_misc_weapons.json"
ALIAS_VEHICLES = "alias_vehicles.json"
ALIAS_SHIPPABLES = "alias_shippables.json"
ALIAS_FACILITIES = "alias_facilities.json"
ALIAS_EMPLACEMENTS = "alias_emplacements.json"
ALIAS_PLAYER_BUILT = "alias_player_build.json"
ALIAS_WORLD = "alias_world.json"
ALIAS_INF_WEAPONS = "alias_inf_weapons.json"
ALIAS_TRIPODS = "alias_tripods.json"
# adjustments
ADJUSTMENTS_WEAPONS = "adjustments_weapons.json"
# dev name to name pairs
NAMES_VEHICLES = "names_vehicles.json"
NAMES_AMMOS = "names_ammos.json"
NAMES_INF_WEAPONS = "names_inf_weapons.json"
NAMES_TRIPODS = "names_tripods.json"

def load_json_to_dict(filename, encoding = "utf8"):
    with open(filename, encoding = encoding) as f:
        dict = json.load(f)
        return dict


def load_location_names(filename):
    with open(filename) as f:
        return f.read().split(";")

### functions to generate fresh files:

# to generate a rough match between vehicle and mounts. Dev inconsistent naming convention make this require manual tuning
# not updated for replacing old doc
def generate_vehicle_to_mount_dict(vehicle_dict, mount_dict):
    vehicle_mount_dict = {}
    for vehicle in vehicle_dict:
        matching_mounts = [mount for mount in mount_dict if mount.replace("Gunner", "").startswith(vehicle)]
        if len(matching_mounts) == 0:
            matching_mounts = [mount for mount in mount_dict if mount.replace("Gunner", "").startswith(vehicle[:-1])]
        vehicle_mount_dict[vehicle] = matching_mounts
    return vehicle_mount_dict

# TODO
def generate_all_targets(vehicle_mined, names_vehicles, alias_vehicles):
    targets = generate_vehicle_targets(vehicle_mined, names_vehicles, alias_vehicles)

    return targets

def generate_emplacement_targets():
    pass

def generate_tripod_targets():
    pass

def generate_facility_targets():
    pass

# TODO: just add as aliases to base? might be better to do seperate entries actually
def generate_facility_modified_targets():
    pass

def generate_player_built_targets():
    pass

def generate_shippable_targets(shipppable_mined):
    shippable_targets_dict = {}
    for dev_name, data in shipppable_mined.items():
        shippable_targets_dict[data["Name"]] = {}
        shippable_targets_dict[data["Name"]]["Dev Name"] = dev_name
        shippable_targets_dict[data["Name"]]["Name"] = data["Name"]
        shippable_targets_dict[data["Name"]]["Cost"] = get_cost(data["BMat"], data["RMat"], None, 0)
        shippable_targets_dict[data["Name"]]["Health"] = str(data["Max Health"])
        mitigation = extract_suffix(data["Armour Type"])
        shippable_targets_dict[data["Name"]]["Mitigation Type"] = mitigation if mitigation != None else "Tier1Structure"
        shippable_targets_dict[data["Name"]]["Repair Cost"] = str(data["Repair Cost"])
        shippable_targets_dict[data["Name"]]["ObjectType"] = "Shippables"
        shippable_targets_dict[data["Name"]]["Additional Names"] = "" if dev_name not in alias_vehicles.keys() else alias_vehicles[dev_name]
    return shippable_targets_dict

def generate_world_targets():
    pass

# usable to fully replace old doc
def generate_vehicle_targets(vehicle_mined, names_vehicles, alias_vehicles):
    vehicle_targets_dict = {}
    for dev_name, vehicle in vehicle_mined.items():
        vehicle_targets_dict[vehicle["Name"]] = {}
        vehicle_targets_dict[vehicle["Name"]]["Dev Name"] = dev_name
        vehicle_targets_dict[vehicle["Name"]]["Name"] = vehicle["Name"] if dev_name not in names_vehicles.keys() else names_vehicles[dev_name]
        vehicle_targets_dict[vehicle["Name"]]["Cost"] = get_cost(vehicle["BMat"], vehicle["RMat"], vehicle["Relic"], vehicle["ResourcesPerBuildCycle"])
        vehicle_targets_dict[vehicle["Name"]]["Health"] = str(vehicle["Max Health"])
        vehicle_targets_dict[vehicle["Name"]]["Armour Health"] = str(vehicle["TankArmour"])
        vehicle_targets_dict[vehicle["Name"]]["Min Base Penetration Chance"] = str(vehicle["Min Penetration Chance"])
        vehicle_targets_dict[vehicle["Name"]]["Max Base Penetration Chance"] = str(1-Decimal(str(vehicle["Min Tank Armour Percent"])))
        vehicle_targets_dict[vehicle["Name"]]["Mitigation Type"] = extract_suffix(vehicle["ArmourType"])
        vehicle_targets_dict[vehicle["Name"]]["Repair Cost"] = str(vehicle["Repair Cost"])
        vehicle_targets_dict[vehicle["Name"]]["Tracks Disable Chance"] = str(vehicle["Disable Chance: Track"])
        vehicle_targets_dict[vehicle["Name"]]["Engine Disable Chance"] = str(vehicle["Disable Chance: Engine"])
        vehicle_targets_dict[vehicle["Name"]]["Main Gun Disable Chance"] = str(vehicle["Disable Chance: Turret1"])
        vehicle_targets_dict[vehicle["Name"]]["Secondary Gun Disable Chance"] = str(vehicle["Disable Chance: Turret2"])
        vehicle_targets_dict[vehicle["Name"]]["ObjectType"] = "Vehicles"
        vehicle_targets_dict[vehicle["Name"]]["Additional Names"] = "" if dev_name not in alias_vehicles.keys() else alias_vehicles[dev_name]
        # TODO: add slots, weaponary/mounts
    return vehicle_targets_dict

# uses fuzzy to find best match for old name and apply name and aliases
def apply_old_vehicle_names_and_aliases(vehicle_target_dict):
    vehicle_target_dict_new = {}
    for vehicle_name, data in vehicle_target_dict.items():
        if vehicle_name == "null" or data["Name"] is None:
            continue
        if vehicle_name in vehicle_dictionary:
            target_name = vehicle_dictionary[vehicle_name]
        else:
            try:
                target_name, args = fuzz.fuzzy_match_target_name(vehicle_name, targets_dictionary)
            except Exception as e:
                vehicle_target_dict_new[vehicle_name] = data
                continue
        vehicle_target_dict_new[target_name] = data
        vehicle_target_dict_new[target_name]["Name"] = target_name
        vehicle_target_dict_new[target_name]["Additional Names"] = targets[target_name]["Additional Names"]
    return vehicle_target_dict_new

def extract_alias(mined_dict, old_dict, old_dictionary_dict):
    alias_dict = {}
    for dev_name, data in mined_dict.items():
        if data["Name"] in old_dict.keys():
            old_key = data["Name"]
        elif (ret := find_dev_name_match(dev_name, old_dict)) is not None:
            old_key = ret
        elif dev_name == "null" or data["Name"] is None or data["Name"] == "":
            # does this thing really exist??
            print("Entity without a name found: "+ dev_name + "\nData dump:\n" + json.dumps(data, indent=4))
            continue
        else:
            try:
                old_key, args = fuzz.fuzzy_match_target_name(data["Name"], old_dictionary_dict)
            except Exception as e:
                alias_dict[dev_name] = data["Name"]
                print("alias not found for: "+dev_name)
                continue
        if "Additional Names" in old_dict[old_key].keys():
            alias_dict[dev_name] = old_dict[old_key]["Additional Names"]
        else:
            alias_dict[dev_name] = ""
    return alias_dict

def find_dev_name_match(dev_name, old_dict):
    for key, data in old_dict.items():
        if "Code name" not in data.keys():
            continue
        if data["Code name"] == dev_name:
            return key
    return None
        
# extendible adjustment func for manual final touches
def apply_adjustments(adjustment_dict, base_dict):
    weapons_dict_new = {}
    for name, data in base_dict.items():
        if name in adjustment_dict["exclude"]:
            continue
        weapons_dict_new[name] = data
    return weapons_dict_new

# programatically generate a weapons file
# TODO: still missing melee (guh)
def generate_all_weapons(alias_misc_weapons,ammo_dict, names_ammos, alias_vehicles, vehicle_dict, names_vehicles, vehicle_to_mount, mount_dict, alias_inf_weapons, inf_weapon_dict, names_inf_weapons, alias_emplacements, emplacement_dict, alias_tripods, names_tripods, tripod_dict, adjustments_weapons):
    weapons = generate_base_weapons(alias_misc_weapons,ammo_dict, names_ammos)
    weapons = generate_vehicle_weapons(alias_vehicles, vehicle_dict, vehicle_to_mount, mount_dict, weapons, names_ammos, names_vehicles)
    weapons = generate_infantry_weapons(alias_inf_weapons, inf_weapon_dict, weapons, names_ammos, names_inf_weapons)
    weapons = generate_emplacement_weapons(alias_emplacements, emplacement_dict, mount_dict, weapons, names_ammos)
    weapons = generate_tripod_weapons(alias_tripods, names_tripods, tripod_dict, mount_dict, weapons, names_ammos)
    weapons = remove_zero_damage_weapons(weapons)
    weapons = apply_adjustments(adjustments_weapons, weapons)
    return weapons

def ammo_name_dev_substitution(ammo_name_dev):
    ammo_name_dev_subbed = None
    if ammo_name_dev == "RPGAmmo":
        ammo_name_dev_subbed = "RpgAmmo"
    elif ammo_name_dev == "MortarAmmo, MortarAmmoSH, MortarAmmoFL, MortarAmmoFlame":
        # assume people care only about HE mortar
        ammo_name_dev_subbed = "MortarAmmo"
    elif ammo_name_dev == "HELaunchedGrenade, SmokeGrenade, GreenAsh, GrenadeW, ATLaunchedGrenadeW" or ammo_name_dev == "HELaunchedGrenade, SmokeGrenade, GreenAsh":
        # assume people care only about HE (launched) grenade
        ammo_name_dev_subbed = "HELaunchedGrenade"
    else:
        print("Missing ammo_name_dev: " + ammo_name_dev)
    return ammo_name_dev_subbed

def generate_base_weapons(alias_misc_weapons, ammo_dict, names_ammos):
    weapons = {}
    for dev_name, data in ammo_dict.items():
        if dev_name in names_ammos.keys():
            # old name
            new_key = names_ammos[dev_name]
        elif data["Name"] in weapons.keys():
            # duplicate exists!
            new_key = dev_name
        else:
            # new name?!
            print("New weapon dev name (not in manual names_ammo.json): " + dev_name)
            new_key = data["Name"]
        weapons[new_key] = {}
        weapons[new_key]["Name"] = data["Name"] if data["Name"] is not None else new_key
        weapons[new_key]["Dev Name"] = dev_name
        weapons[new_key]["Damage"] = str(data["Damage"] if not "Kinetic" in data["Damage Type Display Name"] else data["Damage"]*1.25) # Kinetic Damage Modifier Average (Between 1 and 1.5)
        weapons[new_key]["DamageType"] = damage_type_name_pairs.get(data["Damage Type Display Name"], data["Damage Type Display Name"])
        weapons[new_key]["ObjectType"] = "Weapons"
        weapons[new_key]["Additional Names"] = "" if dev_name not in alias_misc_weapons.keys() else alias_misc_weapons[dev_name]
    return weapons

# add new entries for HV or add aliases
def generate_vehicle_weapons(alias_vehicles, vehicle_dict, vehicle_to_mount, mount_dict, weapons_dict, names_ammos, names_vehicles):
    weapons_dict_new = weapons_dict
    for vehicle_dev_name, data in vehicle_dict.items():
        if vehicle_dev_name not in vehicle_to_mount.keys():
            print("new vehicle detected (not in vehicle to mount json): " + vehicle_dev_name)
            continue
        if len(vehicle_to_mount[vehicle_dev_name]) == 0:
            continue
        mount_name = vehicle_to_mount[vehicle_dev_name][0] # only the primary mount
        if mount_dict[mount_name]["Ammo Name"] is not None and mount_dict[mount_name]["Ammo Name"] != "":
            ammo_name_dev = mount_dict[mount_name]["Ammo Name"]
        elif mount_dict[mount_name]["Multi Ammo"] is not None and mount_dict[mount_name]["Multi Ammo"] != "":
            ammo_name_dev = mount_dict[mount_name]["Multi Ammo"]
        else:
            continue
        if ammo_name_dev not in names_ammos.keys():
            ammo_name_dev = ammo_name_dev_substitution(ammo_name_dev)
            if ammo_name_dev is None:
                continue
        ammo_name = names_ammos[ammo_name_dev]
        if mount_dict[mount_name]["Damage Multiplier"] != 1:
            # make new tmp entry for HV/LV. Will need manual touch up for name
            key_name = names_vehicles[vehicle_dev_name]+" ammo"
            weapons_dict_new[key_name] = {}
            weapons_dict_new[key_name]["Name"] = names_vehicles[vehicle_dev_name]
            weapons_dict_new[key_name]["Dev Name"] = ammo_name_dev
            weapons_dict_new[key_name]["Vehicle Dev Name"] = vehicle_dev_name
            weapons_dict_new[key_name]["Mount Dev Name"] = mount_name
            damage = float(weapons_dict[ammo_name]["Damage"])*mount_dict[mount_name]["Damage Multiplier"]
            weapons_dict_new[key_name]["Damage"] = str(damage) 
            weapons_dict_new[key_name]["DamageType"] = weapons_dict[ammo_name]["DamageType"]
            weapons_dict_new[key_name]["ObjectType"] = "Weapons"
            weapons_dict_new[key_name]["Additional Names"] = alias_vehicles[vehicle_dev_name]
            continue
        weapons_dict_new[ammo_name]["Additional Names"] = concat_alias(weapons_dict[ammo_name]["Additional Names"],alias_vehicles[vehicle_dev_name])
    return weapons_dict_new

# add new entries for HV or add aliases
def generate_infantry_weapons(alias_inf_weapons, inf_weapon_mined, weapons_dict, names_ammos, names_inf_weapons):
    weapons_dict_new = weapons_dict
    for inf_weapon_dev_name, data in inf_weapon_mined.items():
        if data["Compatible Ammo"] is not None and data["Compatible Ammo"] != "":
            ammo_name_dev = data["Compatible Ammo"]
        elif data["Multi Ammo"] is not None and data["Multi Ammo"] != "":
            ammo_name_dev = data["Multi Ammo"]
        else:
            continue

        if ammo_name_dev not in names_ammos.keys():
            ammo_name_dev = ammo_name_dev_substitution(ammo_name_dev)
            if ammo_name_dev is None:
                continue

        if inf_weapon_dev_name == "AssaultRifleSingleShot":
            ammo_name_dev = "AssaultRifleSingleShotAmmo"
        elif inf_weapon_dev_name == "RifleAutomaticWSingleShot":
            ammo_name_dev = "RifleAutomaticWSingleShotAmmo"
        
        ammo_name = names_ammos[ammo_name_dev]
        if data["Damage Multiplier"] != 1:
            # make new tmp entry for HV/LV. Will need manual touch up for name
            key_name = names_inf_weapons[inf_weapon_dev_name]+" ammo"
            weapons_dict_new[key_name] = {}
            weapons_dict_new[key_name]["Name"] = names_inf_weapons[inf_weapon_dev_name]
            weapons_dict_new[key_name]["Dev Name"] = ammo_name_dev
            weapons_dict_new[key_name]["Infantry Weapon Dev Name"] = inf_weapon_dev_name
            damage = float(weapons_dict[ammo_name]["Damage"])*data["Damage Multiplier"]
            weapons_dict_new[key_name]["Damage"] = str(damage) 
            weapons_dict_new[key_name]["DamageType"] = weapons_dict[ammo_name]["DamageType"]
            weapons_dict_new[key_name]["ObjectType"] = "Weapons"
            weapons_dict_new[key_name]["Additional Names"] = alias_inf_weapons[inf_weapon_dev_name]
            continue
        weapons_dict_new[ammo_name]["Additional Names"] = concat_alias(weapons_dict[ammo_name]["Additional Names"],alias_inf_weapons[inf_weapon_dev_name])
    return weapons_dict_new

# add new entries for HV or add aliases
def generate_emplacement_weapons(alias_emplacements, emplacement_dict, mount_dict, weapons_dict, names_ammos):
    weapons_dict_new = weapons_dict
    for emp_dev_name, data in emplacement_dict.items():
        mount_name = data["MountCodeName"]
        if mount_dict[mount_name]["Ammo Name"] is not None and mount_dict[mount_name]["Ammo Name"] != "":
            ammo_name_dev = mount_dict[mount_name]["Ammo Name"]
        elif mount_dict[mount_name]["Multi Ammo"] is not None and mount_dict[mount_name]["Multi Ammo"] != "":
            ammo_name_dev = mount_dict[mount_name]["Multi Ammo"]
        else:
            # a mount that doesnt use ammo (spotter seats)
            continue
        if ammo_name_dev not in names_ammos.keys():
            ammo_name_dev = ammo_name_dev_substitution(ammo_name_dev)
            if ammo_name_dev is None:
                continue
        ammo_name = names_ammos[ammo_name_dev]
        if mount_dict[mount_name]["Damage Multiplier"] != 1:
            # make new tmp entry for HV/LV. Will need manual touch up for name
            key_name = data["Name"]+" ammo"
            weapons_dict_new[key_name] = {}
            weapons_dict_new[key_name]["Name"] = data["Name"]
            weapons_dict_new[key_name]["Dev Name"] = ammo_name_dev
            weapons_dict_new[key_name]["Emplacement Dev Name"] = emp_dev_name
            weapons_dict_new[key_name]["Mount Dev Name"] = mount_name
            damage = float(weapons_dict[ammo_name]["Damage"])*mount_dict[mount_name]["Damage Multiplier"]
            weapons_dict_new[key_name]["Damage"] = str(damage) 
            weapons_dict_new[key_name]["DamageType"] = weapons_dict[ammo_name]["DamageType"]
            weapons_dict_new[key_name]["ObjectType"] = "Weapons"
            weapons_dict_new[key_name]["Additional Names"] = alias_emplacements[emp_dev_name]
            continue
        weapons_dict_new[ammo_name]["Additional Names"] = concat_alias(weapons_dict[ammo_name]["Additional Names"],alias_emplacements[emp_dev_name])
    return weapons_dict_new

# add new entries for HV or add aliases
def generate_tripod_weapons(alias_tripods, names_tripods, tripod_dict, mount_dict, weapons_dict, names_ammos):
    weapons_dict_new = weapons_dict
    for tripod_dev_name, data in tripod_dict.items():
        mount_name = data["MountCodeName"]
        if mount_name == None or mount_name == "":
            continue
        if mount_dict[mount_name]["Ammo Name"] is not None and mount_dict[mount_name]["Ammo Name"] != "":
            ammo_name_dev = mount_dict[mount_name]["Ammo Name"]
        elif mount_dict[mount_name]["Multi Ammo"] is not None and mount_dict[mount_name]["Multi Ammo"] != "":
            ammo_name_dev = mount_dict[mount_name]["Multi Ammo"]
        else:
            # a mount that doesnt use ammo (spotter seats)
            continue
        if ammo_name_dev not in names_ammos.keys():
            ammo_name_dev = ammo_name_dev_substitution(ammo_name_dev)
            if ammo_name_dev is None:
                continue
        ammo_name = names_ammos[ammo_name_dev]
        if mount_dict[mount_name]["Damage Multiplier"] != 1:
            # make new tmp entry for HV/LV. Will need manual touch up for name
            key_name = names_tripods[tripod_dev_name]+" ammo"
            weapons_dict_new[key_name] = {}
            weapons_dict_new[key_name]["Name"] = names_tripods[tripod_dev_name]
            weapons_dict_new[key_name]["Dev Name"] = ammo_name_dev
            weapons_dict_new[key_name]["Tripod Dev Name"] = tripod_dev_name
            weapons_dict_new[key_name]["Mount Dev Name"] = mount_name
            damage = float(weapons_dict[ammo_name]["Damage"])*mount_dict[mount_name]["Damage Multiplier"]
            weapons_dict_new[key_name]["Damage"] = str(damage) 
            weapons_dict_new[key_name]["DamageType"] = weapons_dict[ammo_name]["DamageType"]
            weapons_dict_new[key_name]["ObjectType"] = "Weapons"
            weapons_dict_new[key_name]["Additional Names"] = alias_tripods[tripod_dev_name]
            continue
        weapons_dict_new[ammo_name]["Additional Names"] = concat_alias(weapons_dict[ammo_name]["Additional Names"],alias_tripods[tripod_dev_name])
    return weapons_dict_new

# remove all the weapons that does 0 damage like smoke
# i know i can modify dict in place because it is mutable but this is better for readability for whoever sees this in the future
def remove_zero_damage_weapons(weapons_dict):
    weapons_dict_new = {}
    for name, data in weapons_dict.items():
        if float(data["Damage"]) == 0:
            continue
        weapons_dict_new[name] = data
    return weapons_dict_new

# programmatically generate damage profile json (mitigation stuff)
def generate_damage(damage_profiles_mined):
    damage_dict = {}
    for damage_type, data in damage_profile_mined.items():
        damage_dict[damage_type] = {}
        damage_dict[damage_type]["Name"] = damage_type
        for mitigation_name_dev, value in data.items():
            mitigation_name = mitigation_name_dev.replace(" Damage Mitigation", "")
            damage_dict[damage_type][mitigation_name] = str(value)
        damage_dict[damage_type]["Nomitigation"] = "0"
        damage_dict[damage_type]["ObjectType"] = "Damage"
    return damage_dict
        

def get_cost(bmat, rmat, relic, rss_per_hammer):
    value = bmat or rmat or relic
    if value is None:
        return "-"
    return str(value*rss_per_hammer)

def extract_suffix(string):
    if string is None:
        return None
    return string.split("::")[-1]

def concat_alias(str1, str2):
    """
    Concatenate two semicolon-separated strings into a single string
    with unique entries and no duplicate or trailing semicolons.

    Args:
        str1 (str): The first semicolon-separated string.
        str2 (str): The second semicolon-separated string.

    Returns:
        str: The concatenated, cleaned-up string.
    """
    # Split the strings into lists of entries
    entries1 = str1.split(';') if str1 else []
    entries2 = str2.split(';') if str2 else []
    
    # Combine both lists, remove duplicates, and filter out empty entries
    unique_entries = set(entries1 + entries2)
    unique_entries.discard('')  # Remove empty strings
    
    # Join the unique entries back into a single semicolon-separated string
    result = ';'.join(sorted(unique_entries))
    
    return result

def get_all_names(dictionary, field_name="Additional Names"):
    names_dictionary = {}
    for key, value in dictionary.items():
        additional_names = [value["Name"]]

        if field_name in value:
            additional_names.extend(value[field_name].split(";"))

        for name in additional_names:
            if name is None:
                print("error on: " + key)
                continue
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
        if value["ObjectType"] != "Vehicles":
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
        "howitzer": "hg",
        "engine": "eng",
        "sc": "sc",
        "storm": "sc",
        "ic": "ic",
        "intel": "ic",
        "intelligence": "ic",
        "weather":"ws",
        "weathers":"ws",
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
            if (
                word == "bunker"
                and i + 1 < len(word)
                and words[i + 1] in mod_words
            ):
                # catch phrases like "bunker ramp"
                word = words[i + 1]
            if i - 1 >= 0:
                if words[i - 1].isdigit():
                    args[mod_words[word]] += int(words[i - 1])
                    mod_count += int(words[i - 1])
                else:
                    args[mod_words[word]] += 1
                    mod_count += 1
    if mod_count > args["size"]:
        return None
    return args


# Structure Json parser
location_names = load_location_names(
    os.path.join("data", "Location_names.json")
)


def check_if_location_name(name):
    return name in location_names


targets = load_json_to_dict(os.path.join("data", "Targets.json"))
damages = load_json_to_dict(os.path.join("data", "Damage.json"))
weapons = load_json_to_dict(os.path.join("data", "Weapons.json"))
all = weapons | targets
bunker_stats = load_json_to_dict(os.path.join("data", "Bunker_piece.json"))


targets_dictionary = get_all_names(targets)
husk_dictionary = get_husk_names(targets_dictionary)
vehicle_dictionary = get_vehicle_names(targets)
weapons_dictionary = get_all_names(weapons)
all_dictionary = get_all_names(all)

damage_type_name_pairs = load_json_to_dict(os.path.join(MANUAL_PATH, DAMAGE_TYPE_NAME_PAIRS))
vehicle_to_mount = load_json_to_dict(os.path.join(MANUAL_PATH,VEHICLE_MOUNT_DATA))
alias_vehicles = load_json_to_dict(os.path.join(MANUAL_PATH,ALIAS_VEHICLES))
names_vehicles = load_json_to_dict(os.path.join(MANUAL_PATH,NAMES_VEHICLES))
names_ammos = load_json_to_dict(os.path.join(MANUAL_PATH,NAMES_AMMOS))
alias_inf_weapons = load_json_to_dict(os.path.join(MANUAL_PATH,ALIAS_INF_WEAPONS))
names_inf_weapons = load_json_to_dict(os.path.join(MANUAL_PATH,NAMES_INF_WEAPONS))
names_tripods = load_json_to_dict(os.path.join(MANUAL_PATH,NAMES_TRIPODS))
alias_tripods = load_json_to_dict(os.path.join(MANUAL_PATH,ALIAS_TRIPODS))
alias_emplacements = load_json_to_dict(os.path.join(MANUAL_PATH,ALIAS_EMPLACEMENTS))
alias_misc_weapons = load_json_to_dict(os.path.join(MANUAL_PATH,ALIAS_MISC_WEAPONS))

adjustments_weapons = load_json_to_dict(os.path.join(MANUAL_PATH,ADJUSTMENTS_WEAPONS))

vehicle_mined = load_json_to_dict(os.path.join(MINED_PATH, VEHICLE_DYNAMIC_DATA))
ammos_mined = load_json_to_dict(os.path.join(MINED_PATH, AMMO_DYNAMIC_DATA))
inf_weapons_mined = load_json_to_dict(os.path.join(MINED_PATH, WEAPON_DYNAMIC_DATA))
emplacements_mined = load_json_to_dict(os.path.join(MINED_PATH, EMPLACEMENT_DYNAMIC_DATA))
tripods_mined = load_json_to_dict(os.path.join(MINED_PATH, STRUCTURE_DYNAMIC_DATA_TRIPODS))
damage_profile_mined = load_json_to_dict(os.path.join(MINED_PATH, DAMAGE_PROFILES_DYNAMIC_DATA))
mount_mined = load_json_to_dict(os.path.join(MINED_PATH, MOUNTS_DYNAMIC_DATA))
shippables_mined = load_json_to_dict(os.path.join(MINED_PATH, STRUCTURE_DYNAMIC_DATA_SHIPPABLES))
facilities_mined = load_json_to_dict(os.path.join(MINED_PATH, STRUCTURE_DYNAMIC_DATA_FACILITIES))
player_built_mined = load_json_to_dict(os.path.join(MINED_PATH, STRUCTURE_DYNAMIC_DATA_PLAYER_BUILT))
world_mined = load_json_to_dict(os.path.join(MINED_PATH, STRUCTURE_DYNAMIC_DATA_WORLD))

targets_vehicles = load_json_to_dict(os.path.join(DEV_PATH, TARGETS_VEHICLES))
weapons_base = load_json_to_dict(os.path.join(DEV_PATH, WEAPONS_BASE))
weapons_vehicles = load_json_to_dict(os.path.join(DEV_PATH, WEAPONS_VEHICLES))

#print("All Data loaded into memory")
# slang

def print_dict_as_json(dictionary):
    formatted_json = json.dumps(dictionary, indent=4)
    print(formatted_json)

def save_dict_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)

# def extract_alias(in_dict):
#     alias = {}
#     for key, data in in_dict.items():
#         if "Additional Names" not in data.keys():
#             data["Additional Names"] = ""
#         else:
#             alias[data["Dev Name"]] = data["Additional Names"]
#     return alias

def extract_name_from_parsed(in_dict):
    names = {}
    for key, data in in_dict.items():
        names[data["Dev Name"]] = data["Name"]
    return names

def extract_name_from_mined(in_dict):
    names = {}
    for dev_name, data in in_dict.items():
        names[dev_name] = data["Name"]
    return names

if __name__ == "__main__":
    #save_dict_to_json(generate_all_weapons(alias_misc_weapons, ammos_mined,names_ammos,alias_vehicles,vehicle_mined, names_vehicles,vehicle_to_mount,mount_mined,alias_inf_weapons,inf_weapons_mined,names_inf_weapons, alias_emplacements, emplacements_mined, alias_tripods, names_tripods, tripods_mined, adjustments_weapons), os.path.join(DEV_PATH, "Weapons.json"))
    #save_dict_to_json(generate_damage(damage_profile_mined), os.path.join(DEV_PATH,DAMAGE))
    # cannot run facility yet because of lack of husk inplementation
    #save_dict_to_json(extract_alias(facilities_mined, targets, targets_dictionary), os.path.join(MANUAL_PATH,ALIAS_FACILITIES))
    #save_dict_to_json(extract_alias(emplacements_mined, targets, targets_dictionary), os.path.join(MANUAL_PATH,ALIAS_EMPLACEMENTS))
    #save_dict_to_json(extract_alias(player_built_mined, targets, targets_dictionary), os.path.join(MANUAL_PATH,ALIAS_PLAYER_BUILT))
    #save_dict_to_json(extract_alias(world_mined, targets, targets_dictionary), os.path.join(MANUAL_PATH,ALIAS_WORLD))
    save_dict_to_json(generate_vehicle_targets(vehicle_mined, names_vehicles, alias_vehicles), os.path.join(MANUAL_PATH, "vehicle_targets.json"))
    pass