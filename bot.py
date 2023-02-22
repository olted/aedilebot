import discord
import string
from discord.ext import commands
import re
import json
from fuzzywuzzy import fuzz
import discord.app_commands
import math
from dotenv import load_dotenv
import os


load_dotenv()
DEPLOYMENT_TOKEN = os.getenv("DEPLOYMENT_TOKEN")
DEV_TOKEN = os.getenv("DEV_SERVER_TOKEN")
BUNKERTOOLLINK = os.getenv("ARCHIVEDBUNKERTOOLLINK")
SESHIENDAMAGECALCULATORLINK=os.getenv("SESHIENDAMAGECALCULATORLINK")
SIGILWINDGIF=os.getenv("SIGILWINDGIF")
RELICSHEETLINK=os.getenv("RELICSHEETLINK")
#{my faction} is awesome and cool and {your faction} is sux and bad!!111!!!11!
collie_server_ids = [977592440355700816]
# load db into data structures
th_relic_types_dict = {}

with open('th_relic_types.json') as f:
    th_relic_types_dict = json.load(f)

#Structure Json parser
with open('Structures.json') as f:
    StructuresArray = json.loads(f.read())
    structures_dict = {}
for structure in StructuresArray:
    name = structure['Name']
    structures_dict[name] = structure

#Weapon Json parser
with open('Weapons.json') as f:
    WeaponsArray = json.loads(f.read())
    weapons_dict = {}
for weapon in WeaponsArray:
    name = weapon['Informalname']
    weapons_dict[name] = weapon

#Mitigation json parser
with open('Damage.json') as f:
    DamageArray = json.loads(f.read())
    damages_dict = {}
for damage in DamageArray:
    type = damage['Damagetypes']
    damages_dict[type] = damage

#Vehicles Parser
with open('Vehicles.json') as f:
    VehiclesArray = json.loads(f.read())
    vehicles_dict = {}
for vehicle in VehiclesArray:
    name = vehicle['Name']
    vehicles_dict[name] = vehicle

#Slang Dictionary json parser
with open('Dictionary.json') as f:
    DictionaryArray = json.loads(f.read())
    Dictionary_dict = {}
for slang in DictionaryArray:
    Dictionary_dict.update(slang)


print("start")



def damage_handler(weapon,structure):
    mitigation_type = structure['MitigationType']
    damage_type = weapon['DamageType']
    mitigation_type_damage = damages_dict[damage_type]
    mitigation_value = mitigation_type_damage[mitigation_type]
    real_damage = float(weapon['Damage']) * float((1 - float(mitigation_value)))
    return math.ceil(real_damage)

def calculate_hits_to_kill_raw(weapon, structure):
    weapon_name = fuzzy_match_weapon_name(weapon)
    structure_name = fuzzy_match_structure_name(structure)
    structure = structures_dict[structure_name]
    weapon = weapons_dict[weapon_name]
    dmgholder = float(structure['Health']) / damage_handler(weapon,structure)
    return str(math.ceil(dmgholder))

def general_h2k_handler(weapon, structure):
    weapon_name = fuzzy_match_weapon_name(weapon)
    structure_name = fuzzy_match_structure_name(structure)
    structure = structures_dict[structure_name]
    weapon = weapons_dict[weapon_name]
    htk = math.ceil(float(structure['Health']) / damage_handler(weapon,structure))
    output= (f"It takes {htk} {weapon_name} to kill a {structure_name}")
    print("Struc. hp: ", structure['Health'], "Weapon dmg: ", weapon['Damage'], "Real damage: ", damage_handler(weapon,structure))
    return (output)





def handle_response(message) -> str:
    p_message = message.lower()

    if re.search("how (many|much)", p_message) and re.search("to (kill|destroy)", p_message):
        token_pair = re.findall('how (many|much)(.*) to (kill|destroy) (.*)', p_message)
        if relic_th_h2k_handler(token_pair[0][1], token_pair[0][3]) != "Target name not found. Try again with the full name of your target.":
            return relic_th_h2k_handler(token_pair[0][1], token_pair[0][3])
        else:
            return general_h2k_handler(token_pair[0][1],token_pair[0][3])
    
    
def handle_response_collie(message) -> str:
    p_message = message.lower()
    if re.search("how (many|much)", p_message) and re.search("to (kill|destroy)", p_message):
        token_pair = re.findall('how (many|much)(.*) to (kill|destroy) (.*)', p_message)
        if relic_th_h2k_handler(token_pair[0][1], token_pair[0][3]) != "Target name not found. Try again with the full name of your target.":
            return relic_th_h2k_handler(token_pair[0][1], token_pair[0][3])
        else:
            return general_h2k_handler(token_pair[0][1],token_pair[0][3])
        
    if re.search("damage calculator", p_message):
        return f"A legionary has requested Seshien's calculator. {SESHIENDAMAGECALCULATORLINK} "
    if re.search("bunker tool", p_message):
        return f'A legionary has requested the bunker tool. {BUNKERTOOLLINK}'
    if re.search("facility tool", p_message):
        return 'A legionary has requested the facility tool. https://foxholeplanner.com/'
    if re.search("support ticket", p_message):
        return 'A legionary has requested the link for Siege Camp Support Tickets. To get your Steam64 ID simply find the URL to your steam profile and copy+paste the long set of numbers. https://siegecamp.freshdesk.com/support/tickets/new'
    if re.search("timezone tool", p_message) or re.search("time calculator", p_message):
        return 'A legionary has requested the timezone tool. https://hammertime.djdavid98.art/en-GB/'
    if re.search("wind gif", p_message):
        return f'{SIGILWINDGIF}'
    if (re.search("relic size", p_message) or re.search("th size", p_message) or re.search("town hall size", p_message)):
        return f"A legionary wants to know a town or relic size. {RELICSHEETLINK}"

async def message_handler(message, user_message, is_private):
    try:
        response = handle_response(user_message)
        
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)

async def message_handler_collie(message, user_message, is_private):
    try:
        response = handle_response_collie(user_message)
        
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)
    
def move_string_to_rear(string, tier_string):
    res = string.replace(tier_string, "") + " " + str(tier_string)
    return res

def unslangify(name):
    name_parsed = name.split(' ')
    for word in name_parsed:
        if word=="t1" or word=="t2" or word=="t3":
            tier_string = word
            name = move_string_to_rear(name,tier_string)
            break
    if name in Dictionary_dict:
        return Dictionary_dict[name]
            #if entire input detects as a specific slang piece, itll return it and wont continue past here in the method
    for word in name_parsed:
        if word in Dictionary_dict:
            name = name.replace(word, Dictionary_dict[word])
    return name


def fuzzy_match_th_relic_name(name):
    max_score = 0
    max_key = None
    for key in th_relic_types_dict.keys():
        if fuzz.token_set_ratio(name, key) > max_score:
            max_score = fuzz.token_set_ratio(name, key)
            max_key = key
    if max_score < 90:
        print("Couldnt find TH or relic name")
        return "Target name not found. Try again with the full name of your target."
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
        print("Couldnt find structure name")
        return "Target name not found. Try again with the full name of your target."
    if len(perfect_score_list)>=1:
        harsh_max_score = 0
        harsh_max_key = None
        for key in perfect_score_list:
            if fuzz.ratio(name,key)>harsh_max_score:
                harsh_max_score = fuzz.ratio(name,key)
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
        print("Couldnt find weapon name")
        return "Target name not found. Try again with the full name of your target."
    return max_key
#### make more efficient^ return weapons_dict[max_key]


def get_th_relic_type(name):
    if name == None:
        return None
    if name in th_relic_types_dict.keys():
        return th_relic_types_dict[name]


def relic_th_h2k_handler(damage_source, target_name):
    damage_source = unslangify(damage_source)
    #delete unslangify SOMEWHERE either here or in other method
    target_name = unslangify(target_name)
    target_name = fuzzy_match_th_relic_name(target_name)
    structure_type = get_th_relic_type(target_name)
    if structure_type == None:
        return "Target name not found. Try again with the full name of your target."
    damage_type = fuzzy_match_weapon_name(damage_source)

    t1=calculate_hits_to_kill_raw(damage_type,str(structure_type+" T1"))
    t2=calculate_hits_to_kill_raw(damage_type,str(structure_type+" T2"))
    t3=calculate_hits_to_kill_raw(damage_type,str(structure_type+" T3"))
    if t1!=t2:
        output_string = f"Hits to kill {clean_capitalize(target_name)} with {damage_type}: {t1} (Tier 1) {t2} (Tier 2) {t3} (Tier 3)"
    else:
        output_string = f"Hits to kill {clean_capitalize(target_name)} with {damage_type}: {calculate_hits_to_kill_raw(damage_type,structure_type)}"
    return output_string

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
def collie_server_checker(message):
    if message.guild.id in collie_server_ids:
        return True
    else:
        return False

def run_discord_bot():
    TOKEN = f'{DEPLOYMENT_TOKEN}'
    #Dev token: DEV_TOKEN
    #Deployment token: DEPLOYMENT_TOKEN
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

    async def is_collie_server(ctx):
        return (ctx.guild.id in collie_server_ids)

    @client.tree.command(name="help")
    async def help(interaction: discord.Interaction):
        await interaction.response.send_message("I'm currently configured to answer any prompts containing 'How many/much x to kill/destroy y'. This can be vehicles *and* structures. Any values given for vehicles assumes shell penetration.")
        
    @client.event
    async def on_message(message):
        if message.author == client.user:
            return 
        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)
        if message.guild.id == 1075090353650143344:
            print("Message in Aedile Dev Server")
        if collie_server_checker(message):
            await message_handler_collie(message, user_message, is_private=False)
        else:
            await message_handler(message, user_message, is_private=False)
    client.run(TOKEN)

general_h2k_handler("HE", "Machine Gun Pillbox")
if __name__ == '__main__':
    # run
    run_discord_bot()
