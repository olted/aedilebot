
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


def _whole_phrase_pattern(phrase: str) -> str:
    escaped_phrase = re.escape(phrase).replace(r"\ ", r"\s+")
    return rf"(?<!\w){escaped_phrase}(?!\w)"


def move_string_to_rear(string):
    for replacement_string in move_to_rear_string_list:
        pattern = _whole_phrase_pattern(replacement_string)
        if re.search(pattern, string, flags=re.IGNORECASE):
            if replacement_string in ["tier 1","tier 2","tier 3","concrete"]:
                new_string = tier_dictionary[replacement_string]
                return re.sub(pattern, "", string, flags=re.IGNORECASE) + " " + new_string
            if replacement_string in ["unemplaced","unentrenched"]:
                return re.sub(pattern, "", string, flags=re.IGNORECASE)
            if replacement_string in ["emplaced","entrenched"]:
                return re.sub(pattern, "", string, flags=re.IGNORECASE) + " emplaced"
            if replacement_string in ["t1","t2","t3"]:
                return re.sub(pattern, "", string, flags=re.IGNORECASE) + " " + replacement_string
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


def normalize_alias(text: str) -> str:
    """Normalize an entity name using the same rules as alias generation."""
    return normalize(move_string_to_rear(text))


def singularize(word: str) -> str:
    result = inflector.singular_noun(word)
    return result if result else word