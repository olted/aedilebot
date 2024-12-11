import math
import parse
import utils
import fuzzy as fuzz
import main
import bot


def calculate_hits_to_reach_health(health, damage):
    return math.ceil(float(health) / damage)


class DamageCalculator:
    def __init__(self, weapon_name, target_name, args=None, weapon_name2=None, weapon1_hits=None):
        self.weapon_name = weapon_name
        self.target_name = target_name
        self.weapon_name2 = weapon_name2
        self.weapon1_hits = weapon1_hits
        self.weapon = parse.weapons[weapon_name]
        if target_name == "meta":
            self.target = "meta"
            self.target_type = "Structures"
            self.health = None
        else:
            self.target = parse.targets[target_name]

            self.target_type = self.target["ObjectType"]
            self.health = float(self.target["Health"])
        self.damage_value = float(self.weapon["Damage"])
        self.damage_type = parse.damages[self.weapon['DamageType']]

        self.mitigation_type = None
        self.dmg_multiplier = None

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
            if "bunker_spec" in args:
                # set health and mitigation
                self.health = self.calculate_bunker_health(args["bunker_spec"])
                self.dmg_multiplier = self.get_bunker_wet_multipler(args["bunker_spec"]["wet"])
                self.repair_cost = self.calculate_bunker_repair(args["bunker_spec"])
                self.bunker_string = self.get_bunker_string(args["bunker_spec"])

    def get_bunker_string(self, bunker_spec):
        # TODO descriptor for bunker piece for printing
        tier_words = {1: "tier 1", 2: "tier 2", 3: "tier 3"}
        ret = None
        mod_str = ""
        for mod in bunker_spec:
            if mod in parse.bunker_stats:
                mod_str += str(bunker_spec[mod]) + " " + mod + ", " 
        mod_str = "(" + tier_words[bunker_spec["tier"]] + ", " + str(bunker_spec["size"]) + " pieces, " + mod_str[:-2] + ")"
        ratio = f"{self.health/self.repair_cost:.2f}" 
        health_and_repair = "**" + str(math.ceil(self.health)) + " health** and **" +  str(math.ceil(self.repair_cost)) + " bmat repair cost** (" + ratio + " health/bmat)"
        ret = " with " + health_and_repair + " " + mod_str
        if 0 <= bunker_spec["wet"] < 24:
            ret = " that is " + str(bunker_spec["wet"]) + " hour wet" + ret
        return ret

    def get_bunker_wet_multipler(self, hours):
        if hours == 0:
            return 10
        return max(min(24/hours, 10), 1)
    
    def calculate_bunker_health(self, bunker_spec):
        tier_to_mitigation = {0:"Tier1Structure", 1:"Tier2Structure", 2:"Tier3Structure"}
        empty = bunker_spec["size"] # number of empty bunker pieces
        tier = bunker_spec["tier"] - 1 # zero indexing
        raw_health = 0
        si = 1
        for mod in bunker_spec:
            if mod in parse.bunker_stats:
                raw_health += float(parse.bunker_stats[mod]["health"][tier]) * bunker_spec[mod]
                empty -= bunker_spec[mod]
                si *= float(parse.bunker_stats[mod]["si"][tier]) ** bunker_spec[mod]
        raw_health += float(parse.bunker_stats["piece"]["health"][tier]) * empty
        si *= float(parse.bunker_stats["piece"]["si"][tier]) ** empty
        if bunker_spec["size"] == 1:
            si = 1
        self.mitigation_type = tier_to_mitigation[tier]
        return raw_health*si

    def calculate_bunker_repair(self, bunker_spec):
        repair = 0
        empty = bunker_spec["size"] # number of empty bunker pieces
        tier = bunker_spec["tier"] - 1 # zero indexing
        for mod in bunker_spec:
            if mod in parse.bunker_stats:
                repair += float(parse.bunker_stats[mod]["repair"][tier]) * bunker_spec[mod]
                empty -= bunker_spec[mod]
        repair += float(parse.bunker_stats["piece"]["repair"][tier]) * empty
        return repair
        

    def calculate_damage(self, mitigation_type=None):
        if mitigation_type is None:
            if self.mitigation_type:
                mitigation_type = self.mitigation_type
            else:
                mitigation_type = self.target["Mitigation Type"]
        mitigation_value = self.damage_type[mitigation_type]
        # Here later we can do entrenchment bonus or etc
        real_damage = float(self.damage_value * float((1 - float(mitigation_value))))
        if self.dmg_multiplier is not None:
            real_damage *= self.dmg_multiplier
        return math.ceil(real_damage)

    def get_disable_health(self):
        if "Disable Level" in self.target:
            return self.health * (1.005 - float(self.target["Disable Level"]))
        raise bot.InvalidTypeError

    # returns rounded up hits to kill or a range of hits to kill for any non-kinetic damage
    # this is due to foxhole having inconsistency for impact fuse (non-hitscan) weapons, which can lower damage done as low as around 95%
    def general_damage_calculator(self):
        final_damage = self.calculate_damage()
        min_hits_to_kill = calculate_hits_to_reach_health(self.health, final_damage)
        utils.debug_summary(self.weapon_name, self.target_name, final_damage, min_hits_to_kill)
        # consider low roll possibility
        if self.weapon['DamageType'] in ["AntiTankExplosive", "Explosive", "HighExplosive", "ArmourPiercing", "Demolition"]:
            max_hits_to_kill = calculate_hits_to_reach_health(self.health, final_damage*0.95)
            return f"{min_hits_to_kill} to {max_hits_to_kill}" if min_hits_to_kill < max_hits_to_kill else min_hits_to_kill
        return min_hits_to_kill

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
            hits_to_kill = self.general_damage_calculator()  # vehicle_damage_calculator()
        elif self.target_type == "Multitier_structures":
            hits_to_kill = self.multitier_damage_calculator()
        elif self.target_type == "Emplacements":
            hits_to_kill = self.general_damage_calculator()  # emplacement_damage_calculator()
        elif self.target_type == "Tripods" or self.target_type == "Structures":
            hits_to_kill = self.general_damage_calculator()
        else:
            raise bot.InvalidTypeError(self.target_name,
                                       "There was an unexpected error trying to find the entity. Please contact the "
                                       "developers.")
        
        if self.location_name:
            name = f"{main.clean_capitalize(self.location_name)} ({self.target_name})"
        else:
            name = self.target_name

        

        ret_str = f"It takes {hits_to_kill} {self.weapon_name} to kill a {name}"
        if self.target == "meta":
            ret_str += self.bunker_string
        return ret_str
    
    def get_custom_kill_calculation(self):
        remaining_health = self.health - self.weapon1_hits * self.calculate_damage()
        if remaining_health <= 0:
            return self.get_kill_calculation(self)
        
        # set weapon2 for remaining health
        self.health = remaining_health
        self.weapon = parse.weapons[self.weapon_name2]
        self.damage_value = float(self.weapon["Damage"])
        self.damage_type = parse.damages[self.weapon['DamageType']]
        
        if self.target_type == "Vehicles":
            hits_to_kill = self.general_damage_calculator()  # vehicle_damage_calculator()
        elif self.target_type == "Multitier_structures":
            hits_to_kill = self.multitier_damage_calculator()
        elif self.target_type == "Emplacements":
            hits_to_kill = self.general_damage_calculator()  # emplacement_damage_calculator()
        elif self.target_type == "Tripods" or self.target_type == "Structures":
            hits_to_kill = self.general_damage_calculator()
        else:
            raise bot.InvalidTypeError(self.target_name,
                                       "There was an unexpected error trying to find the entity. Please contact the "
                                       "developers.")

        if self.location_name:
            name = f"{main.clean_capitalize(self.location_name)} ({self.target_name})"
        else:
            name = self.target_name

        ret_str = f"It takes {hits_to_kill} {self.weapon_name2} to kill a {name} after {self.weapon1_hits} {self.weapon_name} hits."
        if self.target == "meta":
            ret_str += self.bunker_string
        return ret_str

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

def custom_kill_handler(weapon_fuzzy_name1, weapon1_hits, weapon_fuzzy_name2, target_fuzzy_name):
    args = None
    if weapon_fuzzy_name1 in parse.weapons_dictionary:
        weapon_name1 = parse.weapons_dictionary[weapon_fuzzy_name1]
    else:
        weapon_name1 = fuzz.fuzzy_match_weapon_name(weapon_fuzzy_name1)

    if weapon_fuzzy_name2 in parse.weapons_dictionary:
        weapon_name2 = parse.weapons_dictionary[weapon_fuzzy_name2]
    else:
        weapon_name2 = fuzz.fuzzy_match_weapon_name(weapon_fuzzy_name2)

    if target_fuzzy_name in parse.targets_dictionary:
        target_name = parse.targets_dictionary[target_fuzzy_name]
        #if we did direct hit, we dont have to search for other tokens
        if parse.check_if_location_name(target_fuzzy_name):
            args = {"location_name": target_fuzzy_name}
    else:
        target_name, args = fuzz.fuzzy_match_target_name(target_fuzzy_name)

    return DamageCalculator(weapon_name1, target_name, args, weapon_name2, weapon1_hits).get_custom_kill_calculation()

def general_disable_handler(weapon_fuzzy_name, target_fuzzy_name):
    args = None
    if weapon_fuzzy_name in parse.weapons_dictionary:
        weapon_name = parse.weapons_dictionary[weapon_fuzzy_name]
    else:
        weapon_name = fuzz.fuzzy_match_weapon_name(weapon_fuzzy_name)

    if target_fuzzy_name in parse.vehicle_dictionary:
        target_name = parse.vehicle_dictionary[target_fuzzy_name]
    else:
        target_name, args = fuzz.fuzzy_match_target_name(target_fuzzy_name, parse.vehicle_dictionary)

    return DamageCalculator(weapon_name, target_name, args).get_disable_calculation()

def general_dehusk_handler(weapon_fuzzy_name, target_fuzzy_name):
    args = None
    if weapon_fuzzy_name in parse.weapons_dictionary:
        weapon_name = parse.weapons_dictionary[weapon_fuzzy_name]
    else:
        weapon_name = fuzz.fuzzy_match_weapon_name(weapon_fuzzy_name)

    if target_fuzzy_name in parse.husk_dictionary:
        target_name = parse.husk_dictionary[target_fuzzy_name]
    else:
        target_name, args = fuzz.fuzzy_match_target_name(target_fuzzy_name, parse.husk_dictionary)

    return DamageCalculator(weapon_name, target_name, args).get_kill_calculation()

def general_bunker_kill_handler(weapon_fuzzy_name, target_fuzzy_name):
    args = {}
    if weapon_fuzzy_name in parse.weapons_dictionary:
        weapon_name = parse.weapons_dictionary[weapon_fuzzy_name]
    else:
        weapon_name = fuzz.fuzzy_match_weapon_name(weapon_fuzzy_name)
    
    target_name = "meta"
    args["bunker_spec"] = parse.get_bunker_spec(target_fuzzy_name)
    if args["bunker_spec"] == None:
        raise bot.BunkerSpecParseError(target_fuzzy_name)

    return DamageCalculator(weapon_name, target_name, args).get_kill_calculation()


def statsheet_handler(entity_name):
    try:
        entity = fuzz.fuzzy_match_any(entity_name)
    
        if entity["type"] == "Weapons":
            entity = parse.weapons[fuzz.fuzzy_match_weapon_name(entity_name)]
            name = entity["Name"]
            damage = entity["Damage"]
            damage_type = entity["DamageType"]
            entity_type = entity["ObjectType"]
            return entity_type,name,damage,damage_type
        else:
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
            elif entity["ObjectType"] == "Vehicles" or entity["ObjectType"] == "Emplacements" or entity[
                    "ObjectType"] == "Tripods":
                    entity_type = entity["ObjectType"]
                    name = entity["Name"]
                    raw_hp = entity["Health"]
                    mitigation = entity["Mitigation Type"]
                    try:
                        min_pen = int(float(entity["Min Base Penetration Chance"]) * 100)
                    except:
                        min_pen = ""
                    try:
                        max_pen = int(float(entity["Max Base Penetration Chance"]) * 100)  # note to self: make decimals into fractions, make timer into hours
                    except:
                        max_pen = ""
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
            elif entity["ObjectType"] == "Multitier_structures":
                entity_type = entity["ObjectType"]
                name = entity["Name"]
                raw_hp = entity["Health"]
                bmat_cost = entity["Bmat cost"]
                repair_cost = entity["RepairCost"]
                return entity_type,name,raw_hp,bmat_cost,repair_cost
                
                    
        return "I could not process a request because the entity is not a valid weapon, structure or vehicle."
    except:
        return bot.EntityNotFoundError(entity_name)
