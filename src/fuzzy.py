
import parse
from fuzzywuzzy import fuzz
import main
import utils
import bot



# fuzzy stuff
# If they return true, they need to return proper location/vehicle/structure name.


 #stygian slang <->
def fuzzy_match_target_name(name):
    #name = main.unslangify(name)
    max_score = 0
    max_value = None
    perfect_score_list = []
    for key,value in parse.targets_dictionary.items():
        if fuzz.token_set_ratio(name, key) > max_score:
            max_score = fuzz.token_set_ratio(name, key)
            max_value = value
        if fuzz.token_set_ratio(name, key) > 60:
            perfect_score_list.append(key)
    if max_score < 50:
        raise bot.TargetNotFoundError(name)
    else:
        utils.debug_fuzzy(name,perfect_score_list,max_value)
        return max_value


def fuzzy_match_weapon_name(name):
    #name = main.unslangify(name)
    max_score = 0
    max_value = None
    for key,value in parse.weapons_dictionary.items():
        if fuzz.token_set_ratio(name, key) > max_score:
            max_score = fuzz.token_set_ratio(name, key)
            max_value = value
            
    if max_score < 45:
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
    if max_score < 60:
        raise bot.EntityNotFoundError(name)
    output = {"max_value":max_value,"type":type}
    return output
