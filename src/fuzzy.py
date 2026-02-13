
import parse
from fuzzywuzzy import fuzz
import main
import utils
import bot
from fuzzywuzzy import process
import re



# fuzzy stuff
# If they return true, they need to return proper location/vehicle/structure name.


 #stygian slang <->
def fuzzy_match_target_name(name, targets_dictionary = parse.targets_dictionary):
        max_score = 0
        max_key = None
        max_value = None
        tokens = {}
        good_score_list = []
        for key, value in targets_dictionary.items():
            score = fuzz.token_set_ratio(name,key)
            if score > max_score:
                max_score = fuzz.token_set_ratio(name, key)
                max_key, max_value = key, value
            if score == 100:
                good_score_list.append(key)
        if max_score < 65:
            if targets_dictionary != parse.targets_dictionary:
                raise bot.TargetOfTypeNotFoundError(name)
            else:
                raise bot.TargetNotFoundError(name)
        if parse.check_if_location_name(max_key):
            tokens["location_name"] = max_key
        if len(good_score_list)>1:  #this is INSANELY inefficient and yet I can't find a proper solution to the bug this fixes
                max_score = 0          #in the amount of time I currently have to work on this so it'll have to do. We're not low on processing time anyway.
                max_key = None
                max_value = None
                tokens = {}
                for key, value in targets_dictionary.items():
                    if fuzz.token_sort_ratio(name, key) > max_score:
                        max_score = fuzz.token_sort_ratio(name, key)
                        max_key, max_value = key, value

        utils.debug_fuzzy(name,good_score_list,max_value)
        return max_value, tokens

        
def fuzzy_match_weapon_name(name):
    good_score_list = []
    max_score = 0
    max_value = None
    for key,value in parse.weapons_dictionary.items():
        score = fuzz.token_set_ratio(name, key)
        if score > max_score:
            max_score = score
            max_value = value
        if score == 100:
            good_score_list.append(key)
    if max_score < 65:
        raise bot.WeaponNotFoundError(name)
    if len(good_score_list)>1:  #this is INSANELY inefficient and yet I can't find a proper solution to the bug this fixes
                max_score = 0          #in the amount of time I currently have to work on this so it'll have to do. We're not low on processing time anyway.
                max_key = None
                max_value = None
                tokens = {}
                for key, value in parse.weapons_dictionary.items():
                    if fuzz.token_sort_ratio(name, key) > max_score:
                        max_score = fuzz.token_sort_ratio(name, key)
                        max_key, max_value = key, value
    utils.debug_fuzzy(name,good_score_list,max_value)
    return max_value

def fuzzy_match_any(name):
    max_score = 0
    max_value = None
    num_perfect = 0
    good_score_list = []
    for key,value in parse.all_dictionary.items():
        score = fuzz.token_set_ratio(name, key)
        if score > max_score:
            max_score = score
            max_value = value
            type= parse.all[max_value]["ObjectType"]
        if score==100:
            num_perfect+=1
            good_score_list.append(key)
        if num_perfect>1:
            return fuzzy_perfect_match_any(name)
    if max_score < 75:
        raise bot.EntityNotFoundError(name)
    output = {"max_value":max_value,"type":type}
    return output

def fuzzy_perfect_match_any(name):
    max_score = 0
    max_value = None
    for key,value in parse.all_dictionary.items():
        score = fuzz.token_sort_ratio(name, key)
        if score > max_score:
            max_score = score
            max_value = value
            type = parse.all[max_value]["ObjectType"]
    if max_score < 50:
        raise bot.EntityNotFoundError(name)
    output = {"max_value":max_value,"type":type}
    return output

def fuzzy_match_any_command(name):
    good_score_list = []
    num_perfect = 0
    for key,value in parse.all_dictionary.items():
        score = fuzz.token_set_ratio(name,key)
        if score > 60:
            good_score_list.append(key)
            if score == 100:
                num_perfect+=1
                if num_perfect>1:
                    return fuzzy_perfect_match_any_command(name)
    return good_score_list

def fuzzy_perfect_match_any_command(name):
    good_score_list = []
    for key,value in parse.all_dictionary.items():
        score = fuzz.token_sort_ratio(name,key)
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

# no space, all lowercase, singular only
def normalize(text: str) -> str:
    text = re.sub(r"\s+", " ", text.lower().strip()) 
    words = text.split()
    words = [singularize(w) for w in words]
    return "".join(words)

def singularize(word: str) -> str:
    if word.endswith("ies"):
        return word[:-3] + "y"
    if word.endswith("ses"):
        return word[:-2]  # e.g. classes -> class
    if word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word

def normalized_partial_ratio_equal(a: str, b: str, c: int = 98) -> bool:
    print(fuzz.partial_ratio(normalize(a), normalize(b)))
    return fuzz.partial_ratio(normalize(a), normalize(b)) >= c

def normalized_ratio_equal(a: str, b: str, c: int = 98) -> bool:
    print(fuzz.ratio(normalize(a), normalize(b)))
    return fuzz.ratio(normalize(a), normalize(b)) >= c
