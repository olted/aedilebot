
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
        max_score = 0
        max_key = None
        max_value = None
        tokens = {}
        good_score_list = []
        for key, value in parse.targets_dictionary.items():
            score = fuzz.token_set_ratio(name,key)
            if score > max_score:
                max_score = fuzz.token_set_ratio(name, key)
                max_key, max_value = key, value
            if score == 100:
                good_score_list.append(key)
        if max_score < 65:
            raise bot.TargetNotFoundError(name)
        utils.debug_fuzzy(name,good_score_list,max_value)
        if parse.check_if_location_name(max_key):
            tokens["location_name"] = max_key
        if len(good_score_list)>2:  #this is INSANELY inefficient and yet I can't find a proper solution to the bug this fixes
                max_score = 0          #in the amount of time I currently have to work on this so it'll have to do. We're not low on processing time anyway.
                max_key = None
                max_value = None
                tokens = {}
                good_score_list = {}
                for key, value in parse.targets_dictionary.items():
                    if fuzz.token_sort_ratio(name, key) > max_score:
                        max_score = fuzz.token_sort_ratio(name, key)
                        max_key, max_value = key, value


        return max_value, tokens

        
def fuzzy_match_weapon_name(name):
    max_score = 0
    max_value = None
    for key,value in parse.weapons_dictionary.items():
        score = fuzz.token_set_ratio(name, key)
        if score > max_score:
            max_score = score
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
        score = fuzz.token_set_ratio(name, key)
        if score > max_score:
            max_score = score
            max_value = value
    
    for key,value in parse.targets_dictionary.items():
        score = fuzz.token_set_ratio(name, key)
        if score > max_score:
            max_score = score
            max_value = value
            type = "target"
    if max_score < 75:
        raise bot.EntityNotFoundError(name)
    output = {"max_value":max_value,"type":type}
    return output

def fuzzy_match_any_command(name):
    type = "weapon"
    good_score_list = []
    num_perfect = 0
    for key,value in parse.weapons_dictionary.items():
        score = fuzz.token_set_ratio(name, key)
        if score > 60:
            good_score_list.append(key)
            if score ==100:
                num_perfect+=1
                if num_perfect>5:
                    return fuzzy_perfect_match_any_command(name)
        
    for key,value in parse.targets_dictionary.items():
        score = fuzz.token_set_ratio(name, key)
        if score > 60:
            good_score_list.append(key)
            if score ==100:
                num_perfect+=1
                if num_perfect>5:
                    return fuzzy_perfect_match_any_command(name)
    return good_score_list

def fuzzy_perfect_match_any_command(name):
    good_score_list = []
    for key,value in parse.weapons_dictionary.items():
        score = fuzz.token_sort_ratio(name, key)
        if score > 60:
            good_score_list.append(key)
        
    for key,value in parse.targets_dictionary.items():
        score = fuzz.token_sort_ratio(name, key)
        if score > 60:
            good_score_list.append(key)

    return good_score_list

def fuzzy_match_target_name_command(name):
        good_score_list = []
        num_perfect = 0
        for key, value in parse.targets_dictionary.items():
            score = fuzz.token_set_ratio(name,key)
            if score > 60:
                good_score_list.append(key)
                if score == 100:
                 num_perfect+=1
                 if num_perfect>5:
                      return fuzzy_perfect_match_target_name_command(name)
        return good_score_list

def fuzzy_perfect_match_target_name_command(name):
    good_score_list = []
    for key, value in parse.targets_dictionary.items():
        score = fuzz.token_sort_ratio(name,key)
        if score > 60:
             good_score_list.append(key)
    return good_score_list

def fuzzy_match_weapon_name_command(name):
        good_score_list = []
        for key, value in parse.weapons_dictionary.items():
            score = fuzz.token_set_ratio(name,key)
            if score > 60:
                 good_score_list.append(key)
        return good_score_list
        
