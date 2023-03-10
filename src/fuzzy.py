
import parse
from fuzzywuzzy import fuzz
import main
import utils
import bot
from fuzzywuzzy import process



# fuzzy stuff
# If they return true, they need to return proper location/vehicle/structure name.


 #stygian slang <->
def fuzzy_match_target_name(name):
    print(f"ratio for trench:",fuzz.token_set_ratio("trench t2","trench t2"),"ratio for trench husk:",fuzz.token_set_ratio("trench t2","trench (husk) (t2)"))
    max_score = 0
    max_key = None
    max_value = None
    tokens = {}
    perfect_score_list = []
    for key, value in parse.targets_dictionary.items():
        if fuzz.token_set_ratio(name, key) > max_score:
            max_score = fuzz.token_set_ratio(name, key)
            max_key, max_value = key, value
        if fuzz.token_set_ratio(name, key) > 90:
            perfect_score_list.append(key)
    if max_score < 65:
        raise bot.TargetNotFoundError(name)
    utils.debug_fuzzy(name,perfect_score_list,max_value)
    if parse.check_if_location_name(max_key):
        tokens["location_name"] = max_key
    if len(perfect_score_list)>5:  #this is INSANELY inefficient and yet I can't find a proper solution to the bug this fixes
            max_score = 0          #in the amount of time I currently have to work on this so it'll have to do. We're not low on processing time anyway.
            max_key = None
            max_value = None
            tokens = {}
            perfect_score_list = {}
            for key, value in parse.targets_dictionary.items():
                if fuzz.token_sort_ratio(name, key) > max_score:
                    max_score = fuzz.token_sort_ratio(name, key)
                    max_key, max_value = key, value


    return max_value, tokens

        
def fuzzy_match_weapon_name(name):
    max_score = 0
    max_value = None
    for key,value in parse.weapons_dictionary.items():
        if fuzz.token_set_ratio(name, key) > max_score:
            max_score = fuzz.token_set_ratio(name, key)
            max_value = value
            
    if max_score < 65:
        raise bot.WeaponNotFoundError(name)
    utils.debug_fuzzy(name,'Null for weapons',max_value)
    return max_value

def fuzzy_match_any(name):
    max_score = 0
    max_value = None
    type = "weapon"
    for key,value in parse.weapons_dictionary.items():
        if fuzz.token_set_ratio(name, key) > max_score:
            max_score = fuzz.token_set_ratio(name, key)
            max_value = value
    
    for key,value in parse.targets_dictionary.items():
        if fuzz.token_set_ratio(name, key) > max_score:
            max_score = fuzz.token_set_ratio(name, key)
            max_value = value
            type = "target"
    if max_score < 75:
        raise bot.EntityNotFoundError(name)
    output = {"max_value":max_value,"type":type}
    return output
