import math
import parse
import utils
import fuzzy as fuzz
import main
import bot

def calculate_damage(weapon, target):
    mitigation_type = target['Mitigation Type']
    damage_type = weapon['DamageType']
    return calculate_damage_inner(weapon["Damage"],damage_type, mitigation_type)

def calculate_damage_inner(damage, damage_type, mitigation_type):
    mitigation_type_damage = parse.damages[damage_type]
    mitigation_value = mitigation_type_damage[mitigation_type]
    real_damage = float(float(damage) * float((1 - float(mitigation_value))))
    return math.ceil(real_damage)

#Arguments are health and damage, returns amount of hits to kill vehicle
def calculate_hits_to_kill(health, damage):
    return math.ceil(float(health) / damage)

def calculate_hits_to_disable(health_to_disable, damage):
    return math.ceil(float(health_to_disable) / damage)

# Arguments are correct weapon and target names
# Function currently returns dictionary with all the useful data possible. Good idea would be to make it a class
def damage_calculator(weapon_name, target_name):
    weapon = parse.weapons[weapon_name]
    target = parse.targets[target_name]
    object_type = target["ObjectType"]
    if object_type == "Vehicles":
        return general_damage_calculator(weapon, target)  #vehicle_damage_calculator()
    elif object_type == "Multitier_structures":
        return multitier_damage_calculator(weapon, target)
    elif object_type == "Emplacements":
        return general_damage_calculator(weapon, target) #emplacement_damage_calculator()
    elif object_type == "Tripods" or object_type == "Structures":
        return general_damage_calculator(weapon, target)
    else:
        raise bot.InvalidTypeError(target_name, "There was an unexpected error trying to find the entity. Please contact the developers.")


    

def general_damage_calculator(weapon, target):
    weapon_name = weapon["Name"]
    target_name = target["Name"]
    final_damage = calculate_damage(weapon, target)
    hits_to_kill = calculate_hits_to_kill(target["Health"], final_damage)
    utils.debug_summary(weapon_name,target_name,final_damage, hits_to_kill)
    return f"It takes {hits_to_kill} {weapon_name} to kill a {target_name}"

def multitier_damage_calculator(weapon, target):
    weapon_name = weapon["Name"]
    target_name = target["Name"]
    #if target["Codename"] in ["TownBase1","TownBase2","TownBase3","RelicBase1","RelicBase2","RelicBase3"]:
     #   print("placeholder")
        #display actual name here
    location_name = ""


    output_string = f"Hits to kill {main.clean_capitalize(location_name)} ({target_name}) with {weapon_name}: "

    if weapon["DamageType"] == "BPDemolitionDamageType":
        #print(weapon['DamageType'])
        return output_string + f"{math.ceil(int(target['Health']) / calculate_damage_inner(weapon['Damage'],weapon['DamageType'],'Tier3GarrisonHouse'))}"

    t = []
    t.append(math.ceil(int(target['Health']) / calculate_damage_inner(weapon["Damage"],weapon["DamageType"],"Tier1GarrisonHouse")))
    t.append( math.ceil(int(target['Health']) / calculate_damage_inner(weapon["Damage"],weapon["DamageType"],"Tier2GarrisonHouse")))
    t.append( math.ceil(int(target['Health']) / calculate_damage_inner(weapon["Damage"],weapon["DamageType"],"Tier3GarrisonHouse")))
    return output_string + f"{t[0]} (Tier 1) {t[1]} (Tier 2) {t[2]} (Tier 3)"


def disable_calculator(weapon_name, target_name):
    weapon = parse.weapons[weapon_name]
    target = parse.targets[target_name]
    if target["ObjectType"]!="Vehicles":
        raise bot.InvalidTypeError(target)
    disable_percentage = float(target["Disable Level"])
    if disable_percentage=="0":
        raise bot.InvalidTypeError(target)
    final_damage = calculate_damage(weapon, target)
    hits_to_disable = calculate_hits_to_disable(float(target["Health"]) - (float(target["Health"]) * disable_percentage), final_damage)
    utils.debug_summary(weapon_name,target_name,final_damage, hits_to_disable)
    return f"It takes {hits_to_disable} {weapon_name} to disable a {target_name}"


# general logic functions

def get_th_relic_type(name):
    if name in parse.th_relics_dict:
        return parse.th_relics_dict[name]
    raise RuntimeError


# Made them return tuple of (boolean, str)
# If boolean is true, result was successful and str contains result.
# If boolean is false, result was unsuccessful and str contains error message
def general_kill_handler(weapon_fuzzy_name, target_fuzzy_name):

    if weapon_fuzzy_name in parse.weapons_dictionary:
        weapon_name = parse.weapons_dictionary[weapon_fuzzy_name]
    else:
        weapon_name = fuzz.fuzzy_match_weapon_name(weapon_fuzzy_name)

    if target_fuzzy_name in parse.targets_dictionary:
        target_name = parse.targets_dictionary[target_fuzzy_name]
    else:
        target_name = fuzz.fuzzy_match_target_name(target_fuzzy_name)
    return damage_calculator(weapon_name, target_name)

def general_disable_handler(weapon_fuzzy_name, target_fuzzy_name):
    if weapon_fuzzy_name in parse.weapons_dictionary:
        weapon_name = parse.weapons_dictionary[weapon_fuzzy_name]
    else:
        weapon_name = fuzz.fuzzy_match_weapon_name(weapon_fuzzy_name)
    if target_fuzzy_name in parse.targets_dictionary:
        target_name = parse.targets_dictionary[target_fuzzy_name]
    else:
        target_name = fuzz.fuzzy_match_target_name(target_fuzzy_name)

    return disable_calculator(weapon_name,target_name)


def statsheet_handler(entity_name):
    try:
        entity = fuzz.fuzzy_match_any(entity_name)
        if entity["type"] == "weapon":
            entity = parse.weapons[fuzz.fuzzy_match_weapon_name(entity_name)]
            name = entity["Name"]
            damage = entity["Damage"]
            damage_type = entity["DamageType"]
            print("im here")
            return f"Weapon name: {name} \nWeapon raw damage: {damage} \nWeapon damage type: {damage_type}"
        elif entity["type"] == "target":
            entity=parse.targets[fuzz.fuzzy_match_target_name(entity_name)]
            if entity["ObjectType"]=="Structures":
                name = entity["Name"]
                raw_hp = entity["Health"]
                mitigation = entity["Mitigation Type"]
                repair_cost = entity["RepairCost"]
                decay_start = entity["DecayStartHours"]
                decay_duration = entity["DecayDurationHours"]
                return f"Structure name: {name}\nRaw HP: {raw_hp}\nMitigation Type: {mitigation}\nRepair Cost: {repair_cost}\nDecay Timer: {decay_start} hours\nTime to Decay: {decay_duration} hours"
            else:
                if entity["ObjectType"]=="Vehicles" or entity["ObjectType"]=="Emplacements" or entity["ObjectType"]=="Tripods":
                    name = entity["Name"]
                    raw_hp = entity["Health"]
                    mitigation = entity["Mitigation Type"]
                    min_pen = int(float(entity["Min Base Penetration Chance"]) * 100)
                    max_pen = int(float(entity["Max Base Penetration Chance"]) * 100)  #note to self: make decimals into fractions, make timer into hours
                    armour_hp = entity["Armour Health"]
                    reload = entity["Reload time (pre-reload+reload) (magazine size) (artillery spread?)"]
                    try:
                        main = entity["Main Weapon (damage bonus)(max range, reach)(artillery range)"]
                    except:
                        main = ""
                    try:
                        main_disable = int(float(entity["Main Gun Disable Chance"]) * 100)
                    except:
                        main_disable = ""
                    try:
                        track_disable = int(float(entity["Tracks Disable Chance"])* 100)
                    except:
                        track_disable = ""
                    return f"Name: {name}\nRaw HP: {raw_hp}\nMitigation Type: {mitigation}\nMinimum Penetration Chance (Max Armour): {min_pen}%\nMaximum Penetration Chance (Stripped Armour): {max_pen}%\nArmour HP (Penetration damage to strip): {armour_hp}\nReload Time: {reload}\nTrack Chance: {track_disable}%\nMain Gun Disable Chance: {main_disable}%\nMain Weapon: {main}"
        return "I could not process a request because the entity is not a valid weapon, structure or vehicle." 
    except:
        return bot.EntityNotFoundError(entity_name) 