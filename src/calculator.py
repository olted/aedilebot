import math
import parse
import utils
import fuzzy as fuzz
import main
import bot


def calculate_hits_to_reach_health(health, damage):
    return math.ceil(float(health) / damage)


class DamageCalculator:
    def __init__(self, weapon_name, target_name, args=None):
        self.weapon_name = weapon_name
        self.target_name = target_name
        self.weapon = parse.weapons[weapon_name]
        self.target = parse.targets[target_name]

        self.target_type = self.target["ObjectType"]
        self.health = float(self.target["Health"])
        self.damage_value = float(self.weapon["Damage"])
        self.damage_type = parse.damages[self.weapon['DamageType']]

        self.location_name = None
        self.emplaced = None
        self.veterancy = None
        self.devastation = None

        if args is not None:
            if "location_name" in args:
                self.location_name = args["location_name"]
            if "emplaced" in args:
                self.emplaced = args["emplaced"]
            if "veterancy" in args:
                self.veterancy = args["veterancy"]
            if "devastation" in args:
                self.devastation = args["devastation"]

    def calculate_damage(self, mitigation_type=None):
        if mitigation_type is None:
            mitigation_type = self.target["Mitigation Type"]
        mitigation_value = self.damage_type[mitigation_type]
        # Here later we can do entrenchment bonus or etc
        real_damage = float(self.damage_value * float((1 - float(mitigation_value))))
        return math.ceil(real_damage)

    def get_disable_health(self):
        if "Disable Level" in self.target:
            return self.health * (1.005 - float(self.target["Disable Level"]))
        raise bot.InvalidTypeError

    def general_damage_calculator(self):
        final_damage = self.calculate_damage()
        hits_to_kill = calculate_hits_to_reach_health(self.health, final_damage)

        if self.location_name:
            name = f"{main.clean_capitalize(self.location_name)} ({self.target_name})"
        else:
            name = self.target_name

        utils.debug_summary(self.weapon_name, self.target_name, final_damage, hits_to_kill)
        return f"It takes {hits_to_kill} {self.weapon_name} to kill a {name}"

    def multitier_damage_calculator(self):
        if self.location_name:
            output_string = \
                f"Hits to kill {main.clean_capitalize(self.location_name)} ({self.target_name}) with {self.weapon_name}: "
        else:
            output_string = f"Hits to kill {self.target_name} with {self.weapon_name}: "

        if self.damage_type == "BPDemolitionDamageType":
            return output_string + f"{calculate_hits_to_reach_health(self.health, self.calculate_damage('Tier3GarrisonHouse'))}"

        t = [calculate_hits_to_reach_health(self.health, self.calculate_damage("Tier1GarrisonHouse")),
             calculate_hits_to_reach_health(self.health, self.calculate_damage("Tier2GarrisonHouse")),
             calculate_hits_to_reach_health(self.health, self.calculate_damage("Tier3GarrisonHouse"))]
        return output_string + f"{t[0]} (Tier 1) {t[1]} (Tier 2) {t[2]} (Tier 3)"

    def get_kill_calculation(self):
        if self.target_type == "Vehicles":
            return self.general_damage_calculator()  # vehicle_damage_calculator()
        elif self.target_type == "Multitier_structures":
            return self.multitier_damage_calculator()
        elif self.target_type == "Emplacements":
            return self.general_damage_calculator()  # emplacement_damage_calculator()
        elif self.target_type == "Tripods" or self.target_type == "Structures":
            return self.general_damage_calculator()
        else:
            raise bot.InvalidTypeError(self.target_name,
                                       "There was an unexpected error trying to find the entity. Please contact the "
                                       "developers.")

    def get_disable_calculation(self):
        if self.target_type != "Vehicles":
            raise bot.InvalidTypeError(self.target_name)
        final_damage = self.calculate_damage()
        hits_to_disable = calculate_hits_to_reach_health(self.get_disable_health(), final_damage)
        utils.debug_summary(self.weapon_name, self.target_name, final_damage, hits_to_disable)
        return f"It takes {hits_to_disable} {self.weapon_name} to disable a {self.target_name}"


# general logic functions

# Made them return tuple of (boolean, str)
# If boolean is true, result was successful and str contains result.
# If boolean is false, result was unsuccessful and str contains error message
def general_kill_handler(weapon_fuzzy_name, target_fuzzy_name):
    args = None
    if weapon_fuzzy_name in parse.weapons_dictionary:
        weapon_name = parse.weapons_dictionary[weapon_fuzzy_name]
    else:
        weapon_name = fuzz.fuzzy_match_weapon_name(weapon_fuzzy_name)

    if target_fuzzy_name in parse.targets_dictionary:
        target_name = parse.targets_dictionary[target_fuzzy_name]
        #if we did direct hit, we dont have to search for other tokens
        if parse.check_if_location_name(target_fuzzy_name):
            args = {"location_name": target_fuzzy_name}
    else:
        target_name, args = fuzz.fuzzy_match_target_name(target_fuzzy_name)

    return DamageCalculator(weapon_name, target_name, args).get_kill_calculation()


def general_disable_handler(weapon_fuzzy_name, target_fuzzy_name):
    args = None
    if weapon_fuzzy_name in parse.weapons_dictionary:
        weapon_name = parse.weapons_dictionary[weapon_fuzzy_name]
    else:
        weapon_name = fuzz.fuzzy_match_weapon_name(weapon_fuzzy_name)

    if target_fuzzy_name in parse.targets_dictionary:
        target_name = parse.targets_dictionary[target_fuzzy_name]
    else:
        target_name, args = fuzz.fuzzy_match_target_name(target_fuzzy_name)

    return DamageCalculator(weapon_name, target_name, args).get_disable_calculation()


def statsheet_handler(entity_name):
    try:
        entity = fuzz.fuzzy_match_any(entity_name)
    
        if entity["type"] == "weapon":
            entity = parse.weapons[fuzz.fuzzy_match_weapon_name(entity_name)]
            name = entity["Name"]
            damage = entity["Damage"]
            damage_type = entity["DamageType"]
            entity_type = entity["ObjectType"]
            return entity_type,name,damage,damage_type
        elif entity["type"] == "target":
            entity = parse.targets[fuzz.fuzzy_match_target_name(entity_name)[0]]
            if entity["ObjectType"] == "Structures":
                name = entity["Name"]
                raw_hp = entity["Health"]
                mitigation = entity["Mitigation Type"]
                repair_cost = entity["RepairCost"]
                decay_start = entity["DecayStartHours"]
                decay_duration = entity["DecayDurationHours"]
                entity_type = entity["ObjectType"]
                return entity_type,name,raw_hp,mitigation,repair_cost,decay_start,decay_duration
            else:
                if entity["ObjectType"] == "Vehicles" or entity["ObjectType"] == "Emplacements" or entity[
                    "ObjectType"] == "Tripods":
                    entity_type = entity["ObjectType"]
                    name = entity["Name"]
                    raw_hp = entity["Health"]
                    mitigation = entity["Mitigation Type"]
                    min_pen = int(float(entity["Min Base Penetration Chance"]) * 100)
                    max_pen = int(float(entity[
                                            "Max Base Penetration Chance"]) * 100)  # note to self: make decimals into fractions, make timer into hours
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
                        track_disable = int(float(entity["Tracks Disable Chance"]) * 100)
                    except:
                        track_disable = ""
                    return entity_type,name,raw_hp,mitigation,min_pen,max_pen,armour_hp,reload,main,main_disable,track_disable
                    
        return "I could not process a request because the entity is not a valid weapon, structure or vehicle."
    except:
        return bot.EntityNotFoundError(entity_name)
