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
    client = main.commands.Bot(command_prefix="!", intents=discord.Intents.all(), proxy=HTTPS_PROXY)

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
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/884587111624368158/1077553561010982922/g839.png?width=570&height=498")
        embed.add_field(name="/help", value="Provides you with this message! How neat is that?", inline=False)
        embed.add_field(name="/statsheet [entity]", value="Provides you with a statistics sheet of any entity in the calculator", inline=False)
        embed.add_field(name="/kill [target] [weapon]", value="Fulfills the same purpose as the prompt below with the help of autocomplete.", inline=False)
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
        await interaction.response.send_message(handle_response_inner(weapon1,target, "custom_kill", num1, weapon2))

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
        await interaction.response.send_message(handle_response_inner(weapon,target))
    
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
def handle_response_inner(weapon,target, operation="kill", num1=0, weapon2=None):
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
        return e.show_message()
    except InvalidTypeError as e:
        return e.show_message()
    except WeaponNotFoundError as e:
        return e.show_message()
    except EntityNotFoundError as e:
        return e.show_message()
    except Exception as e:
        print(e)
        traceback.print_tb(e.__traceback__)
        return ("Inner error happened during processing of your request. "
                "Please, contact bot's devs about this.")



def handle_response(message_) -> str:
    p_message = message_.lower()


    token_pair = re.findall('how (many|much)(.*) to (kill|destroy) (.*)', main.move_string_to_rear(p_message) )
    if len(token_pair) >= 1:
        weapon, target = token_pair[0][1], token_pair[0][3]
        if "size" in target:
            return handle_response_inner(weapon, target, operation="bunker")
        return handle_response_inner(weapon, target)
    
    token_pair = re.findall('how (many|much)(.*) to disable (.*)', p_message)
    if len(token_pair) >= 1:
        weapon, target = token_pair[0][1], token_pair[0][2]
        return handle_response_inner(weapon, target, operation="disable")
    
    token_pair = re.findall('how (many|much)(.*) to dehusk (.*)', main.move_string_to_rear(p_message))
    if len(token_pair) >= 1:
        weapon, target = token_pair[0][1], token_pair[0][2]
        return handle_response_inner(weapon, target, operation="dehusk")

