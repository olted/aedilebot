
from functools import lru_cache
import re
import inflect
inflector = inflect.engine()

debugging = False
def debug(message):
    if debugging:
        print(message)

def debug_summary(weapon, target, damage, h2k):
    if debugging:
        print(f"Weapon = {weapon}, Target = {target}, Damage = {damage}, Hits Required={h2k} ")

def debug_fuzzy(input , key_list, key):
    if debugging:
        print(f"User input: {input}, Good Guesses: {key_list}, Final Guess: {key}")

# canonicalizing synonymous phrases for tiers
move_to_rear_string_list = [ "t1","t2","t3","unemplaced","unentrenched","emplaced", "entrenched","tier 1", "tier 2","tier 3","concrete"]
tier_dictionary = { "tier 1":"t1","tier 2":"t2","tier 3":"t3","concrete":"t3"}
def move_string_to_rear(string):
    for replacement_string in move_to_rear_string_list:
        if replacement_string in string:
            if replacement_string in ["tier 1","tier 2","tier 3","concrete"]:
                new_string = tier_dictionary[replacement_string]
                return string.replace(replacement_string, "") + " " + str(new_string)
            if replacement_string in ["unemplaced","unentrenched"]:
                return string.replace(replacement_string, "")
            if replacement_string in ["emplaced","entrenched"]:
                return string.replace(replacement_string, "") + " " + str("emplaced")
            if replacement_string in ["t1","t2","t3"]:
                return string.replace(replacement_string, "") + " " + str(replacement_string)
    return string

# shrink space, all lowercase, singular only, strip leading "a" or "an"
STOPWORDS = {"a", "an", "the"}
@lru_cache(maxsize=128)
def normalize(text: str) -> str:
    text = re.sub(r"[^\w\s]", "", text.lower().strip())  # drop punctuation
    text = re.sub(r"\s+", " ", text)
    words = text.split()
    if words and words[0] in STOPWORDS:
        words = words[1:]
    words = [singularize(w) for w in words]
    return " ".join(words)

def singularize(word: str) -> str:
    result = inflector.singular_noun(word)
    return result if result else word