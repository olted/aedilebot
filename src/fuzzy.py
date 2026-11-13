
import parse
from fuzzywuzzy import fuzz
import main
import utils
import bot
from fuzzywuzzy import process


_VEHICLE_CANONICAL_NAMES = frozenset(parse.vehicle_dictionary.values())
_HUSK_CANONICAL_NAMES = frozenset(parse.husk_dictionary.values())


def _find_exact_name(name, aliases, canonical_entities, allowed_canonical_names=None):
    """Return an exact canonical/alias match and its normalized query."""
    original_name = name.strip()
    if original_name in canonical_entities and (
        allowed_canonical_names is None
        or original_name in allowed_canonical_names
    ):
        return original_name, original_name

    normalized_name = utils.normalize_alias(original_name)
    return aliases.get(normalized_name), normalized_name


def _allowed_target_names(targets_dictionary):
    if targets_dictionary is parse.targets_dictionary:
        return None
    if targets_dictionary is parse.vehicle_dictionary:
        return _VEHICLE_CANONICAL_NAMES
    if targets_dictionary is parse.husk_dictionary:
        return _HUSK_CANONICAL_NAMES
    return frozenset(targets_dictionary.values())


# fuzzy stuff
# If they return true, they need to return proper location/vehicle/structure name.

 #stygian slang <->
def fuzzy_match_target_name(name, targets_dictionary = parse.targets_dictionary):
        exact_match, normalized_name = _find_exact_name(
            name,
            targets_dictionary,
            parse.targets,
            _allowed_target_names(targets_dictionary),
        )
        if exact_match is not None:
            tokens = {}
            original_name = name.strip()
            if parse.check_if_location_name(original_name):
                tokens["location_name"] = original_name
            elif normalized_name != original_name and parse.check_if_location_name(
                normalized_name
            ):
                tokens["location_name"] = normalized_name
            return exact_match, tokens

        name = normalized_name

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
        if parse.check_if_location_name(name):
            tokens["location_name"] = name
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
    exact_match, name = _find_exact_name(
        name, parse.weapons_dictionary, parse.weapons
    )
    if exact_match is not None:
        return exact_match

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
    exact_match, name = _find_exact_name(
        name, parse.all_dictionary, parse.all
    )
    if exact_match is not None:
        return {
            "max_value": exact_match,
            "type": parse.all[exact_match]["ObjectType"],
        }

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
    name = utils.normalize_alias(name)
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
    name = utils.normalize_alias(name)
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
    name = utils.normalize_alias(name)
    good_score_list = []
    for key,value in parse.all_dictionary.items():
        score = fuzz.token_sort_ratio(name,key)
        if score > 60:
            good_score_list.append(key)
    return good_score_list

def fuzzy_match_target_name_command(name, targets_dictionary = parse.targets_dictionary):
    name = utils.normalize_alias(name)
    good_score_list = []
    num_perfect = 0
    for key, value in targets_dictionary.items():
        score = fuzz.token_set_ratio(name, key)
        if score > 60:
            good_score_list.append(key)
            if score == 100:
                num_perfect += 1
                if num_perfect > 5:
                    return fuzzy_perfect_match_target_name_command(
                        name, targets_dictionary
                    )
    return good_score_list

def fuzzy_perfect_match_target_name_command(name, targets_dictionary = parse.targets_dictionary):
    name = utils.normalize_alias(name)
    good_score_list = []
    for key, value in targets_dictionary.items():
        score = fuzz.token_sort_ratio(name,key)
        if score > 60:
             good_score_list.append(key)
    return good_score_list

def fuzzy_match_weapon_name_command(name):
    name = utils.normalize_alias(name)
    good_score_list = []
    for key, value in parse.weapons_dictionary.items():
        score = fuzz.token_set_ratio(name, key)
        if score > 60:
            good_score_list.append(key)
    return good_score_list

def normalized_partial_ratio_equal(a: str, b: str, c: int = 98) -> bool:
    return fuzz.partial_ratio(utils.normalize(a), utils.normalize(b)) >= c

def normalized_ratio_equal(a: str, b: str, c: int = 98) -> bool:
    return fuzz.ratio(utils.normalize(a), utils.normalize(b)) >= c
