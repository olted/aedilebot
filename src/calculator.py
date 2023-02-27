import math
import parse
import utils
import fuzzy as fuzz
import main
import bot

def calculate_damage(weapon, target):
    mitigation_type = target['MitigationType']
    damage_type = weapon['DamageType']
    mitigation_type_damage = parse.damages_dict[damage_type]
    mitigation_value = mitigation_type_damage[mitigation_type]
    real_damage = float(weapon['Damage']) * float((1 - float(mitigation_value)))
    return math.ceil(real_damage)

#Arguments are health and damage, returns amount of hits to kill vehicle
def calculate_hits_to_kill(health, damage):
    return math.ceil(float(health) / damage)

def calculate_hits_to_disable(health_to_disable, damage):
    return math.ceil(float(health_to_disable) / damage)

# Arguments are correct weapon and target names
# Function currently returns dictionary with all the useful data possible. Good idea would be to make it a class
def damage_calculator(weapon_name, target_name):
    weapon = parse.weapons_dict[weapon_name]
    structure = parse.structures_dict[target_name]

    final_damage = calculate_damage(weapon, structure)

    hits_to_kill = calculate_hits_to_kill(structure["Health"], final_damage)
    utils.debug_summary(weapon_name,target_name,final_damage, hits_to_kill)
    return {"htk": hits_to_kill, "final_damage": final_damage}

def disable_calculator(weapon_name, target_name):
    weapon = parse.weapons_dict[weapon_name]
    structure = parse.structures_dict[target_name]
    if structure["ObjectType"]=="Structures":
        raise bot.InvalidTypeError(structure)
    disable_percentage = float(structure["DisableLevel"])
    if disable_percentage=="0":
        raise bot.InvalidTypeError(structure)
    final_damage = calculate_damage(weapon, structure)
    hits_to_kill = calculate_hits_to_disable(float(structure["Health"]) - (float(structure["Health"]) * disable_percentage), final_damage)
    utils.debug_summary(weapon_name,target_name,final_damage, hits_to_kill)
    return {"htd": hits_to_kill, "final_damage": final_damage}


# general logic functions

def get_th_relic_type(name):
    if name in parse.th_relics_dict:
        return parse.th_relics_dict[name]
    raise RuntimeError


# Made them return tuple of (boolean, str)
# If boolean is true, result was successful and str contains result.
# If boolean is false, result was unsuccessful and str contains error message
def general_kill_handler(weapon_fuzzy_name, target_fuzzy_name):
    weapon_name = fuzz.fuzzy_match_weapon_name(weapon_fuzzy_name)
    structure_name = fuzz.fuzzy_match_structure_name(target_fuzzy_name)
    data = damage_calculator(weapon_name, structure_name)

    return f"It takes {data['htk']} {weapon_name} to kill a {structure_name}"

def general_disable_handler(weapon_fuzzy_name, target_fuzzy_name):
    weapon_name = fuzz.fuzzy_match_weapon_name(weapon_fuzzy_name)
    structure_name = fuzz.fuzzy_match_structure_name(target_fuzzy_name)
    data = disable_calculator(weapon_name, structure_name)

    return f"It takes {data['htd']} {weapon_name} to disable a {structure_name}"


def relic_th_kill_handler(weapon_fuzzy_name, location_fuzzy_name):
    location_name = fuzz.fuzzy_match_th_relic_name(location_fuzzy_name)
    weapon_name = fuzz.fuzzy_match_weapon_name(weapon_fuzzy_name)
    target_name = get_th_relic_type(location_name)
    output_string = f"Hits to kill {main.clean_capitalize(location_name)} ({target_name}) with {weapon_name}: "

    # check if target_name is relic base, should be done better somehow
    if "relic" in target_name:
        return output_string + f"{damage_calculator(weapon_name, target_name)['htk']}"

    # check if damage type is demolition
    if parse.weapons_dict[weapon_name]["DamageType"] == "BPDemolitionDamageType":
        target_name_tiered = f"{target_name} T3"
        return output_string + f"{damage_calculator(weapon_name, target_name_tiered)['htk']}"

    t = []
    for tier in ["T1", "T2", "T3"]:
        t.append(damage_calculator(weapon_name, f"{target_name} {tier}")['htk'])
    return output_string + f"{t[0]} (Tier 1) {t[1]} (Tier 2) {t[2]} (Tier 3)"