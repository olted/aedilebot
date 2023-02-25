
import parse
from fuzzywuzzy import fuzz
import main
import utils
import bot



# fuzzy stuff
# If they return true, they need to return proper location/vehicle/structure name.

def fuzzy_match_th_relic_name(name):
    max_score = 0
    max_key = None
    good_score_list = {}
    for key in parse.th_relics_dict.keys():
        if fuzz.token_set_ratio(name, key) > max_score:
            max_score = fuzz.token_set_ratio(name, key)
            max_key = key

    if max_score < 90:
        raise bot.LocationNotFoundError(name)
        
    utils.debug_fuzzy(name,'Null for THs/Relics',max_key)
    return max_key


def fuzzy_match_structure_name(name):
    name = main.unslangify_structure(name)
    max_score = 0
    max_key = None
    perfect_score_list = []
    for key in parse.structures_dict.keys():
        if fuzz.token_set_ratio(name, key) > max_score:
            max_score = fuzz.token_set_ratio(name, key)
            max_key = key
        if fuzz.token_set_ratio(name, key) > 60:
            perfect_score_list.append(key)
    if max_score < 50:
        raise bot.TargetNotFoundError(name)
    if len(perfect_score_list) >= 1:
        harsh_max_score = 0
        harsh_max_key = None
        for key in perfect_score_list:
            if fuzz.ratio(name, key) > harsh_max_score:
                harsh_max_score = fuzz.ratio(name, key)
                harsh_max_key = key
                utils.debug_fuzzy(name,perfect_score_list,key)
        return harsh_max_key
    else:
        utils.debug_fuzzy(name,perfect_score_list,max_key)
        return max_key


def fuzzy_match_weapon_name(name):
    name = main.unslangify_weapon(name)
    max_score = 0
    max_key = None
    for key in parse.weapons_dict.keys():
        if fuzz.token_set_ratio(name, key) > max_score:
            max_score = fuzz.token_set_ratio(name, key)
            max_key = key
            
    if max_score < 45:
        raise bot.WeaponNotFoundError(name)
    utils.debug_fuzzy(name,'Null for weapons',max_key)
    return max_key

def fuzzy_match_to_slang_weapon(name):
    max_score = 0
    max_key = None
    for key in parse.weapon_slang_dict.keys():
        if fuzz.token_set_ratio(name, key) > max_score:
            max_score = fuzz.token_set_ratio(name, key)
            max_key = key
    utils.debug_fuzzy(name,'Null for weapons',max_key)
    if max_score>80:
        return max_key
    return name

def fuzzy_match_to_slang_structure(name):
    max_score = 0
    max_key = None
    for key in parse.structure_slang_dict.keys():
        if fuzz.token_set_ratio(name, key) > max_score:
            max_score = fuzz.token_set_ratio(name, key)
            max_key = key
    utils.debug_fuzzy(name,'Null for weapons',max_key)
    if max_score>80:
        return max_key
    return name