import discord
from discord.ext import commands
from discord import app_commands
import discord.utils
import main
import dotenv
import os
from dotenv import load_dotenv
import calculator
import re
import parse
import typing
import fuzzy as fuzz
import traceback
import datetime
import string
load_dotenv()
DEPLOYMENT_TOKEN = os.getenv("DEPLOYMENT_TOKEN")
DEV_SERVER_TOKEN = os.getenv("DEV_SERVER_TOKEN")

HTTPS_PROXY = os.getenv("https_proxy")

class EntityNotFoundError(Exception):
    def __init__(self,name, message="The requested entity was not found. Please try again."):
        self.name = name
        self.message = message
        super().__init__(self.message)
    def show_message(self):
        return self.message
    
class InvalidTypeError(EntityNotFoundError):
    def __init__(self, name, message="The entity was invalid for this operation. Please try again."):
        super().__init__(name,message)

class TargetNotFoundError(EntityNotFoundError):
    def __init__(self, name, message=f"The detected target is not found in my data set. Please try again."):
        super().__init__(name,message)

class TargetOfTypeNotFoundError(EntityNotFoundError):
    def __init__(self, name, message=f"The detected target for this operation is not found in my data set. Please try again."):
        super().__init__(name,message)

class WeaponNotFoundError(EntityNotFoundError):
    def __init__(self,name, message=f"The detected weapon is not found in my data set. Please try again."):
        super().__init__(name,message)

class LocationNotFoundError(EntityNotFoundError):
    def __init__(self,name,message="I could not process a request because the town/relic was not found. Please try again."):
        super().__init__(name,message)

class BunkerSpecParseError(TargetNotFoundError):
    def __init__(self,name,message="Invalid bunker specification, please try again with this example format: \n`how many <weapon> to kill size <number> tier <1/2/3> bunker with <numer> <modification> ...`\nEx: `How many tremola to kill a size 15 t3 bunker with 2 mg 3 atg 3 howi 1 ramp`"):
        super().__init__(name,message)


def run_discord_bot():
    intents = discord.Intents.default()
    intents.message_content = True
    client = main.commands.Bot(command_prefix="!", intents=intents, proxy=HTTPS_PROXY)

    @client.event
    async def on_ready():
        print(f'{client.user} is now running')
        try:
            synced = await client.tree.sync()
            print(f"Synced {len(synced)} commands")
            main.list_guilds(client)
        except Exception as e:
            print(e)

    @client.tree.command(name="help")
    async def help(interaction: discord.Interaction):
        embed = discord.Embed(title= "__**Help and Commands**__",description="Welcome to the help section. Here you will be provided with a description of how the bot works and its commands.\n",color=0x992d22, timestamp=datetime.datetime.utcnow())
        embed.add_field(name="Version", value="0.8.61 (Up to date with foxhole U61)", inline=False)
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/884587111624368158/1077553561010982922/g839.png?width=570&height=498")
        embed.add_field(name="/help", value="Provides you with this message! How neat is that?", inline=False)
        embed.add_field(name="/statsheet [entity]", value="Provides you with a statistics sheet of any entity in the calculator", inline=False)
        embed.add_field(name="/kill [target] [weapon]", value="Fulfills the same purpose as the prompt below with the help of autocomplete.", inline=False)
        embed.add_field(name="/bunker_kill", value="Specify the bunker island you want to kill with detailed parameters. (If a modification is not an option, it means it has the same stat as a blank bunker such as engine room)", inline=False)
        embed.add_field(name="**Damage Calculator Prompt**", value='``How much|many [weapon] to destroy|kill|disable [target]``\nHere are some examples to try:\n\nHow much 150mm to kill Patridia?\nHow many satchels to kill t3 bunker core husk?\nHow many 68mm to disable HTD?\nHow many satchels to kill Victa?\nHow much 40mm to destroy bt pad?', inline=False)
        embed.set_footer(text="Good luck on the front!", icon_url="https://media.discordapp.net/attachments/884587111624368158/1077553561010982922/g839.png?width=570&height=498")
        await interaction.response.send_message(embed=embed)
       
    '''@client.tree.command(name="rawstats")
    async def rawstats(interaction: discord.Interaction, entity:str):
        data = parse.everything
        embed=discord.Embed(title=data[1], color=0x992d22)
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/884587111624368158/1077553561010982922/g839.png?width=570&height=498")
        embed.description=f"Statistics sheet for {data[entity][1]}"
        embed.add_field(name=data[entity][0])'''
    
    @client.tree.command(name="custom_kill")
    async def custom_kill(interaction: discord.Interaction,
                    target: str,
                    weapon1: str,
                    num1: int,
                    weapon2: str):
        query = f"Custom_kill query: target = {target}, weapon1 = {weapon1}, num1 = {str(num1)}, weapon2 = {weapon2}"
        await interaction.response.send_message(handle_response_inner(weapon1,target, query, "custom_kill", num1, weapon2))
    
    @client.tree.command(name="bunker_kill")
    @app_commands.describe(
    weapon='weapon you are using to kill the bunker',
    total_size='total size of the bunker (including all the garrisons and blanks)',
    tier='tier of the bunker',
    green_dots='number of bunker edges that is not exposed (Optional, will be estimated if not specified)',
    red_dots='number of bunker edges exposed on the outer perimeter (Optional, will be estimated if not specified)',
    rg='rifle garrison number (Optional)',
    mg='machine gun garrison number (Optional)',
    atg='anti-tank garrison number (Optional)',
    howi='howitzer garrison number (Optional)',
    shelter='arty shelter number (Optional)',
    obs='observation bunker number (Optional)',
    core='bunker core number (Optional)',
    ic='intelligence center number (Optional)',
    sc='storm cannon number (Optional)',
    ws='weather station number (Optional)',
    fortress='underground fortress number (Optional)',
    wet='hours since the bunker has been upgraded to T3 (Optional)'
    )
    @app_commands.choices(
    tier=[
        app_commands.Choice(name="Tier 1", value=1),
        app_commands.Choice(name="Tier 2", value=2),
        app_commands.Choice(name="Tier 3", value=3),
    ]
    )
    async def bunker_kill(interaction: discord.Interaction,
                    weapon: str,
                    total_size: int,
                    tier: app_commands.Choice[int],
                    green_dots: int = -1,
                    red_dots: int = -1,
                    rg: int = 0,
                    mg: int = 0,
                    atg: int = 0,
                    howi: int = 0,
                    shelter: int = 0,
                    obs: int = 0,
                    core: int = 0,
                    ic: int = 0,
                    sc: int = 0,
                    ws: int = 0,
                    fortress: int = 0,
                    wet: int = 24
                    ):
        await interaction.response.send_message(handle_bunker_kill_command(weapon, total_size, tier.value, green_dots, red_dots, rg, mg, atg, howi, shelter, obs, core, ic, sc, ws, fortress, wet))

    @client.tree.command(name="statsheet")
    async def statsheet(interaction: discord.Interaction, entity: str):
        data = calculator.statsheet_handler(entity)
        embed=discord.Embed(title=data[1], color=0x992d22)
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/884587111624368158/1077553561010982922/g839.png?width=570&height=498")
        embed.description=f"Statistics sheet for {data[1]}"
        #embed.add_field(name="Name", value=data[1], inline=False)
        if data[0]== "Weapons":
            embed.add_field(name="Raw Damage", value=data[2], inline=True)
            embed.add_field(name="Damage Type", value=data[3], inline=True)
        elif data[0]=="Structures":
            embed.add_field(name="Raw Health", value=data[2], inline=True)
            embed.add_field(name="Mitigation Type", value=data[3], inline=True)
            embed.add_field(name="Repair Cost", value=data[5], inline=True)
            #embed.add_field(name="Decay Start", value=data[4], inline=True)
            #embed.add_field(name="Time to Decay", value=data[6], inline=True)
        elif data[0] in ["Vehicles","Tripods","Emplacements"]:
            embed.add_field(name="Raw Health", value=data[2], inline=True)
            embed.add_field(name="Mitigation Type", value=data[3], inline=True)
            if data[6]!="0":
                embed.add_field(name="Max Pen Chance", value=str(data[5])+"%", inline=True)
                embed.add_field(name="Min Pen Chance", value=str(data[4])+"%", inline=True)
                embed.add_field(name="Armour Health", value=data[6], inline=True)
            if data[7]!="":
                embed.add_field(name="Reload", value=data[7], inline=True)
            if data[8]!="":
                embed.add_field(name="Main Weapon", value=data[8], inline=True)
            if data[9]!="":
                embed.add_field(name="Turret Disable Chance", value=str(data[9])+"%", inline=True)
            if data[10]!="":
                embed.add_field(name="Tracks Disable Chance", value=str(data[10])+"%", inline=True)
        elif data[0] in ["Multitier_structures"]:
            embed.add_field(name="Raw Health", value=data[2], inline=True)
            embed.add_field(name="Bmat Cost", value=data[3], inline=True)
            embed.add_field(name="Repair Cost", value=data[4], inline=True)
            embed.add_field(name="Mitigation Type", value="Tier[x]GarrisonHouse", inline=True)

        else:
            raise EntityNotFoundError(data[0])
        embed.set_footer(text="Good luck on the front!", icon_url="https://media.discordapp.net/attachments/884587111624368158/1077553561010982922/g839.png?width=570&height=498")
        await interaction.response.send_message(embed=embed)

    @statsheet.autocomplete("entity")
    async def statsheet_autocompletion(
        interaction:discord.Interaction,
        current:str
    ) -> typing.List[app_commands.Choice[str]]:
        data = []
        usedlist = []
        if len(current)>1:
            guess = fuzz.fuzzy_match_any_command(current)
            for possible_value in guess:
                if possible_value.lower() != possible_value and len(data)<20:
                    if possible_value not in usedlist:
                        data.append(app_commands.Choice(name=possible_value,value=possible_value))
                        usedlist.append(possible_value)
                elif possible_value.lower() == possible_value and len(data)<20:
                    value = fuzz.fuzzy_match_any(possible_value)["max_value"]
                    if value not in usedlist:
                        data.append(app_commands.Choice(name=value,value=value))
                        usedlist.append(value)
        return data


    @client.tree.command(name="kill")
    async def kill(interaction: discord.Interaction,
                    target: str,
                    weapon: str):
        query = f"kill query: target = {target}, weapon = {weapon}"
        await interaction.response.send_message(handle_response_inner(weapon, target, query))
    
    @kill.autocomplete("target")
    @custom_kill.autocomplete("target")
    async def kill_autocompletion(
        interaction:discord.Interaction,
        current: str
    ) -> typing.List[app_commands.Choice[str]]:
        data = []
        usedlist = {}
        guess = fuzz.fuzzy_match_target_name_command(current)
        value = [fuzz.fuzzy_match_target_name(v) for v in guess if v.lower() == v]
        combined = [v[0] for v in value] + [g for g in guess if g.lower() != g]
        for possible_value in combined:
            if len(data) == 20:
                break
            if possible_value.lower() != possible_value:
                if possible_value not in usedlist:
                    data.append(app_commands.Choice(name=possible_value, value=possible_value))
                    usedlist[possible_value] = True
            else:
                for v in value:
                    if possible_value in v:
                        if v[0] not in usedlist:
                            data.append(app_commands.Choice(name=v[0], value=v[0]))
                            usedlist[v[0]] = True
                        break
        return data
    
    @custom_kill.autocomplete("weapon1")
    @custom_kill.autocomplete("weapon2")
    @kill.autocomplete("weapon")
    async def kill_autocompletion(
        interaction:discord.Interaction,
        current: str
    ) -> typing.List[app_commands.Choice[str]]:
        data = []
        usedlist = []
        if len(current)>1:
            guess = fuzz.fuzzy_match_weapon_name_command(current)
            print(guess)
            for possible_value in guess:
                if possible_value.lower() != possible_value and len(data)<20:
                    if possible_value not in usedlist:
                        data.append(app_commands.Choice(name=possible_value,value=possible_value))
                        usedlist.append(possible_value)
                elif possible_value.lower() == possible_value and len(data)<20:
                    value = fuzz.fuzzy_match_weapon_name(possible_value)
                    if value not in usedlist:
                        data.append(app_commands.Choice(name=value,value=value))
                        usedlist.append(value)
        return data

    

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        user_message = str(message.content)
        await main.message_handler(message, user_message)
    

    
    client.run(DEV_SERVER_TOKEN)

# bot logic
def handle_response_inner(weapon,target, query = None, operation="kill", num1=0, weapon2=None):
    try:
        if operation=="kill":
            return calculator.general_kill_handler(weapon, target) #return calculator.relic_th_kill_handler(weapon, target)
        if operation=="disable":
            return calculator.general_disable_handler(weapon,target)
        if operation =="dehusk":
            return calculator.general_dehusk_handler(weapon, target)
        if operation =="bunker":
            return calculator.general_bunker_kill_handler(weapon, target)
        if operation =="custom_kill":
            return calculator.custom_kill_handler(weapon, num1, weapon2, target)
    except ZeroDivisionError as e:
        return f"This weapon does no damage to this entity"
    except TargetNotFoundError as e:
        log_error(TargetNotFoundError.__name__, query)
        return e.show_message()
    except InvalidTypeError as e:
        log_error(InvalidTypeError.__name__, query)
        return e.show_message()
    except WeaponNotFoundError as e:
        log_error(WeaponNotFoundError.__name__, query)
        return e.show_message()
    except EntityNotFoundError as e:
        log_error(EntityNotFoundError.__name__, query)
        return e.show_message()
    except Exception as e:
        print(e)
        traceback.print_tb(e.__traceback__)
        log_error(Exception.__name__, query)
        return ("Inner error happened during processing of your request. "
                "Please, contact bot's devs about this.")


def log_error(error_class, log_str):
        timestamp = datetime.datetime.now().isoformat()
        log_entry = f"[{timestamp}] {error_class}: {log_str}\n"
        with open("error_log.txt", "a") as file:
            file.write(log_entry)

def handle_bunker_kill_command(weapon, total_size, tier, green_dots, red_dots, rg, mg, atg, howi, shelter, obs, core, ic, sc, ws, fortress, wet):
    bunker_spec = {}
    bunker_spec["size"] = total_size
    bunker_spec["tier"] = tier
    bunker_spec["green"] = green_dots
    bunker_spec["red"] = red_dots
    bunker_spec["rg"] = rg
    bunker_spec["mg"] = mg
    bunker_spec["atg"] = atg
    bunker_spec["hg"] = howi
    bunker_spec["shelter"] = shelter
    bunker_spec["obs"] = obs
    bunker_spec["core"] = core
    bunker_spec["ic"] = ic
    bunker_spec["sc"] = sc
    bunker_spec["ws"] = ws
    bunker_spec["fortress"] = fortress
    bunker_spec["wet"] = wet
    return calculator.command_bunker_kill_handler(weapon, bunker_spec)

def handle_response(message_) -> str:
    p_message = message_.lower()


    token_pair = re.findall('how (many|much)(.*) to (kill|destroy) (.*)', main.move_string_to_rear(p_message) )
    if len(token_pair) >= 1:
        weapon, target = token_pair[0][1], token_pair[0][3]
        if "size" in target:
            return handle_response_inner(weapon, target, message_, operation="bunker")
        return handle_response_inner(weapon, target, message_)
    
    token_pair = re.findall('how (many|much)(.*) to disable (.*)', p_message)
    if len(token_pair) >= 1:
        weapon, target = token_pair[0][1], token_pair[0][2]
        return handle_response_inner(weapon, target, message_, operation="disable")
    
    token_pair = re.findall('how (many|much)(.*) to dehusk (.*)', main.move_string_to_rear(p_message))
    if len(token_pair) >= 1:
        weapon, target = token_pair[0][1], token_pair[0][2]
        return handle_response_inner(weapon, target, message_, operation="dehusk")

