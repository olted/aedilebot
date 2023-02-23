# import discord
from discord.ext import commands
import re
import json
from fuzzywuzzy import fuzz
import discord.app_commands
import math
from dotenv import load_dotenv
import os
import utils

# load_dotenv()
DEPLOYMENT_TOKEN = os.getenv("DEPLOYMENT_TOKEN")
DEV_SERVER_TOKEN = os.getenv("DEV_SERVER_TOKEN")

utils.debugging = True

# NOT USED

class EntityNotFoundError(Exception):
    def __init__(self, name, message="I could not process a request because the entity was not found. Please try again."):
        self.name= name
        self.message = message
        super().__init__(self.message)
    def show_message(self):
        return self.message

class TargetNotFoundError(EntityNotFoundError):
    def __init__(self, name, message="I could not process a request because the target was not found. Please try again."):
        super().__init__(name,message)

class WeaponNotFoundError(EntityNotFoundError):
    def __init__(self,name, message=f"I could not process a request because the weapon was not found. Please try again."):
        super().__init__(name,message)

class LocationNotFoundError(EntityNotFoundError):
    def __init__(self,name,message="I could not process a request because the town/relic was not found. Please try again."):
        super().__init__(name,message)

# NOT USED

with open('th_relic_types.json') as f:
    th_relic_types_dict = json.load(f)

# Structure Json parser
with open('Structures.json') as f:
    StructuresArray = json.load(f)
    structures_dict = {}
for structure in StructuresArray:
    structures_dict[structure['Name']] = structure

# Weapon Json parser
with open('Weapons.json') as f:
    WeaponsArray = json.load(f)
    weapons_dict = {}
for weapon in WeaponsArray:
    name = weapon['Informalname']
    weapons_dict[name] = weapon

# Mitigation json parser
with open('Damage.json') as f:
    DamageArray = json.load(f)
    damages_dict = {}
for damage in DamageArray:
    type = damage['Damagetypes']
    damages_dict[type] = damage

# Slang Dictionary json parser
with open('Dictionary.json') as f:
    DictionaryArray = json.load(f)
    Dictionary_dict = {}
for slang in DictionaryArray:
    Dictionary_dict.update(slang)


# text processing functions
def clean_capitalize(str):
    result = ""
    list_of_words = str.split()
    for elem in list_of_words:
        if len(result) > 0:
            result = result + " " + elem.strip().capitalize()
        else:
            result = elem.capitalize()
    if not result:
        return str
    else:
        return result


def move_string_to_rear(string, tier_string):
    res = string.replace(tier_string, "") + " " + str(tier_string)
    return res


def unslangify(name):
    name_parsed = name.split(' ')
    for word in name_parsed:
        if word == "t1" or word == "t2" or word == "t3":
            tier_string = word
            name = move_string_to_rear(name, tier_string)
            break
    if name in Dictionary_dict:
        return Dictionary_dict[name]
        # if entire input detects as a specific slang piece, itll return it and wont continue past here in the method
    for word in name_parsed:
        if word in Dictionary_dict:
            name = name.replace(word, Dictionary_dict[word])
    return name


# fuzzy stuff
# If they return true, they need to return proper location/vehicle/structure name.

#
def fuzzy_match_th_relic_name(name):
    max_score = 0
    max_key = None
    for key in th_relic_types_dict.keys():
        if fuzz.token_set_ratio(name, key) > max_score:
            max_score = fuzz.token_set_ratio(name, key)
            max_key = key
    if max_score < 90:
        raise LocationNotFoundError(name)
    return max_key


def fuzzy_match_structure_name(name):
    name = unslangify(name)
    max_score = 0
    max_key = None
    perfect_score_list = []
    for key in structures_dict.keys():
        if fuzz.token_set_ratio(name, key) > max_score:
            max_score = fuzz.token_set_ratio(name, key)
            max_key = key
        if fuzz.token_set_ratio(name, key) > 60:
            perfect_score_list.append(key)
    if max_score < 50:
        raise TargetNotFoundError(name)
    if len(perfect_score_list) >= 1:
        harsh_max_score = 0
        harsh_max_key = None
        for key in perfect_score_list:
            if fuzz.ratio(name, key) > harsh_max_score:
                harsh_max_score = fuzz.ratio(name, key)
                harsh_max_key = key
        return harsh_max_key
    else:
        return max_key


def fuzzy_match_weapon_name(name):
    name = unslangify(name)
    max_score = 0
    max_key = None
    for key in weapons_dict.keys():
        if fuzz.token_set_ratio(name, key) > max_score:
            max_score = fuzz.token_set_ratio(name, key)
            max_key = key
            
    if max_score < 45:
        raise WeaponNotFoundError(name)
    utils.debug(max_key)
    return max_key


# Damage Calculator Functions
# They require proper names. If they dont get proper structure/vehicle/whatever names, they will throw exceptions.

# Arguments are structures: weapon and target
# Returns true damage
def calculate_damage(weapon, target):
    mitigation_type = target['MitigationType']
    damage_type = weapon['DamageType']
    mitigation_type_damage = damages_dict[damage_type]
    mitigation_value = mitigation_type_damage[mitigation_type]
    real_damage = float(weapon['Damage']) * float((1 - float(mitigation_value)))
    return math.ceil(real_damage)

#Arguments are health and damage, returns amount of hits to kill vehicle
def calculate_hits_to_kill(health, damage):
    return math.ceil(float(health) / damage)

# Arguments are correct weapon and target names
# Function currently returns dictionary with all the useful data possible. Good idea would be to make it a class
def damage_calculator(weapon_name, target_name):
    weapon = weapons_dict[weapon_name]
    structure = structures_dict[target_name]

    final_damage = calculate_damage(weapon, structure)

    hits_to_kill = calculate_hits_to_kill(structure["Health"], final_damage)
    utils.debug_summary(weapon_name,target_name,final_damage, hits_to_kill)
    return {"htk": hits_to_kill, "final_damage": final_damage}


# general logic functions

def get_th_relic_type(name):
    if name in th_relic_types_dict:
        return th_relic_types_dict[name]
    raise RuntimeError


# Made them return tuple of (boolean, str)
# If boolean is true, result was successful and str contains result.
# If boolean is false, result was unsuccessful and str contains error message
def general_h2k_handler(weapon_fuzzy_name, target_fuzzy_name):
    weapon_name = fuzzy_match_weapon_name(weapon_fuzzy_name)
    structure_name = fuzzy_match_structure_name(target_fuzzy_name)
    data = damage_calculator(weapon_name, structure_name)

    return f"It takes {data['htk']} {weapon_name} to kill a {structure_name}"


def relic_th_h2k_handler(weapon_fuzzy_name, location_fuzzy_name):
    location_name = fuzzy_match_th_relic_name(location_fuzzy_name)
    weapon_name = fuzzy_match_weapon_name(weapon_fuzzy_name)
    target_name = get_th_relic_type(location_name)
    output_string = f"Hits to kill {clean_capitalize(location_name)} ({target_name}) with {weapon_name}: "

    # check if target_name is relic base, should be done better somehow
    if "relic" in target_name:
        return output_string + f"{damage_calculator(weapon_name, target_name)['htk']}"

    # check if damage type is demolition
    if weapons_dict[weapon_name]["DamageType"] == "BPDemolitionDamageType":
        target_name_tiered = f"{target_name} T3"
        return output_string + f"{damage_calculator(weapon_name, target_name_tiered)['htk']}"

    t = []
    for tier in ["T1", "T2", "T3"]:
        t.append(damage_calculator(weapon_name, f"{target_name} {tier}")['htk'])
    return output_string + f"{t[0]} (Tier 1) {t[1]} (Tier 2) {t[2]} (Tier 3)"


# bot logic
def handle_response_inner(message_):
    # first we are deleting all capitalization
    p_message = message_.lower()
    #if re.search("bunker tool", p_message):
    #    return f'A user has requested the bunker tool. https://404th.ru/bob/'
    
    token_pair = re.findall('how (many|much)(.*) to (kill|destroy) (.*)', p_message)
    if len(token_pair) >= 1:
        weapon, target = token_pair[0][1], token_pair[0][3]
        try:
            return relic_th_h2k_handler(weapon, target)
        except LocationNotFoundError as e:
            return general_h2k_handler(weapon,target)
    return ""


def handle_response(message_) -> str:
    try:
        return handle_response_inner(message_)
    except ZeroDivisionError as e:
        return "I couldn't process your request because this weapon does no damage to this entity."
    except TargetNotFoundError as e:
        return e.show_message()
    except WeaponNotFoundError as e:
        return e.show_message()
    except EntityNotFoundError as e:
        return e.show_message()
    except Exception as e:
        print(e)
        return ("Inner error happened during processing of your request. "
                "Please, contact bot's devs about this.")
    

async def message_handler(message_, user_message):
    response = handle_response(user_message)
    if response:
        await message_.channel.send(response)

# main bot funcion
def run_discord_bot():
    intents = discord.Intents.default()
    intents.message_content = True
    client = commands.Bot(command_prefix="!", intents=discord.Intents.all())

    @client.event
    async def on_ready():
        print(f'{client.user} is now running')
        try:
            synced = await client.tree.sync()
            print(f"Synced {len(synced)} commands")
        except Exception as e:
            print(e)

    @client.tree.command(name="help")
    async def help(interaction: discord.Interaction):
        await interaction.response.send_message(
            "I'm currently configured to answer any prompts containing 'How many/much x to kill/destroy y'. This can be vehicles *and* structures, including specific town hall/relics by name. Any values given for vehicles assumes shell penetration. \n \n Try asking me these questions:\n How many 150 to destroy Abandoned Ward \n How much Predator94.5mm to kill Ares \n How much 40mm to kill bt pad \n How many stickies to kill hatchet \n How many satchels to kill Feirmor\n How many satchels to kill t3 bb husk")

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        user_message = str(message.content)
        await message_handler(message, user_message)

    client.run(DEPLOYMENT_TOKEN)


if __name__ == '__main__':
    # run
    message = "how much 40mm to kill Patridia"
    print(handle_response(message))
    run_discord_bot()
