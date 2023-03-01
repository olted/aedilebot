import discord
from discord.ext import commands
from discord import app_commands
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
load_dotenv()
DEPLOYMENT_TOKEN = os.getenv("DEPLOYMENT_TOKEN")
DEV_SERVER_TOKEN = os.getenv("DEV_SERVER_TOKEN")

class EntityNotFoundError(Exception):
    def __init__(self,name, message="I could not process a request because the entity was not found. Please try again."):
        self.name = name
        self.message = message
        super().__init__(self.message)
    def show_message(self):
        return self.message
    
class InvalidTypeError(EntityNotFoundError):
    def __init__(self, name, message="I could not process a request because the entity was invalid for this operation."):
        super().__init__(name,message)

class TargetNotFoundError(EntityNotFoundError):
    def __init__(self, name, message="I could not process a request because the target was not found. Please try again."):
        super().__init__(name,message)

class WeaponNotFoundError(EntityNotFoundError):
    def __init__(self,name, message=f"I could not process a request because the weapon was not found. Please try again."):
        super().__init__(name,message)

class LocationNotFoundError(EntityNotFoundError):
    def __init__(self,name,message="I could not process a request because the town/relic was not found. Please try again."):
        super().__init__(name,message)



def run_discord_bot():
    intents = discord.Intents.default()
    intents.message_content = True
    client = main.commands.Bot(command_prefix="!", intents=discord.Intents.all())

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
        embed.add_field(name="**Damage Calculator Prompt**", value='``How much|many [weapon] to destroy|kill|disable [target]``\nHere are some examples to try:\n\nHow much 150mm to kill Patridia?\nHow many satchels to kill t3 bunker core husk?\nHow many 68mm to disable HTD?\nHow many satchels to kill Victa?\nHow much 40mm to destroy bt pad?', inline=False)
        embed.set_footer(text="Good luck on the front!", icon_url="https://media.discordapp.net/attachments/884587111624368158/1077553561010982922/g839.png?width=570&height=498")
        await interaction.response.send_message(embed=embed)
       
    @client.tree.command(name="statsheet")
    async def statsheet(interaction: discord.Interaction, entity: str):
        data = calculator.statsheet_handler(entity)
        embed=discord.Embed(title=data[1], color=0x992d22)
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/884587111624368158/1077553561010982922/g839.png?width=570&height=498")
        embed.description=f"Statistics sheet for {data[1]}"
        embed.add_field(name="Name", value=data[1], inline=False)
        if data[0]== "Weapons":
            embed.add_field(name="Raw Damage", value=data[2], inline=True)
            embed.add_field(name="Damage Type", value=data[3], inline=True)
        elif data[0]=="Structures":
            embed.add_field(name="Raw Health", value=data[2], inline=True)
            embed.add_field(name="Mitigation Type", value=data[3], inline=True)
            embed.add_field(name="Repair Cost", value=data[5], inline=True)
            embed.add_field(name="Decay Start", value=data[4], inline=True)
            embed.add_field(name="Time to Decay", value=data[6], inline=True)
        elif data[0] in ["Vehicles","Tripods","Emplacements"]:
            embed.add_field(name="Raw Health", value=data[2], inline=True)
            embed.add_field(name="Mitigation Type", value=data[3], inline=True)
            embed.add_field(name="Max Pen Chance", value=str(data[5])+"%", inline=True)
            embed.add_field(name="Min Pen Chance", value=str(data[4])+"%", inline=True)
            embed.add_field(name="Armour Health", value=data[6], inline=True)
            embed.add_field(name="Reload", value=data[7], inline=True)
            embed.add_field(name="Main Weapon", value=data[8], inline=True)
            embed.add_field(name="Turret Disable Chance", value=str(data[9])+"%", inline=True)
            embed.add_field(name="Tracks Disable Chance", value=str(data[10])+"%", inline=True)
        else:
            raise EntityNotFoundError(data[0])
        embed.set_footer(text="Good luck on the front!", icon_url="https://media.discordapp.net/attachments/884587111624368158/1077553561010982922/g839.png?width=570&height=498")
        await interaction.response.send_message(embed=embed)



    #Name: {name}\nRaw HP: {raw_hp}\nMitigation Type: {mitigation}\nMinimum Penetration Chance (Max Armour): {min_pen}%\nMaximum Penetration Chance (Stripped Armour): {max_pen}%\nArmour HP (Penetration damage to strip): {armour_hp}\nReload Time: {reload}\nTrack Chance: {track_disable}%\nMain Gun Disable Chance: {main_disable}%\nMain Weapon: {main}"
    #Not in use yet, kill command
    
    """@client.tree.command(name="kill")
    async def kill(interaction: discord.Interaction,
                    target: str,
                    weapon: str):
        await interaction.response.send_message(handle_response_inner(weapon,target))
    
    @kill.autocomplete("target")
    async def kill_autocompletion(
        interaction:discord.Interaction,
        current: str
    ) -> typing.List[app_commands.Choice[str]]:
        data = []
        guess = fuzz.fuzzy_match_target_name(current)[0]
        if guess in parse.targets_dictionary.keys():
                    data.append(app_commands.Choice(name=guess, value=guess))
        return data
    
    @kill.autocomplete("weapon")
    async def kill_autocompletion(
        interaction:discord.Interaction,
        current: str
    ) -> typing.List[app_commands.Choice[str]]:
        data = []
        for weapon in (parse.weapons_dictionary.keys()):
                if fuzz.fuzzy_match_weapon_name in weapon.lower():
                    data.append(app_commands.Choice(name=weapon, value=weapon))
        return data
    """
    

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        user_message = str(message.content)
        await main.message_handler(message, user_message)
    

    
    client.run(DEV_SERVER_TOKEN)

# bot logic
def handle_response_inner(weapon,target, operation="kill"):
    try:
        if operation=="kill":
            return calculator.general_kill_handler(weapon, target) #return calculator.relic_th_kill_handler(weapon, target)
        if operation=="disable":
            return calculator.general_disable_handler(weapon,target)
    except ZeroDivisionError as e:
        return "I couldn't process your request because this weapon does no damage to this entity."
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
     # first we are deleting all capitalization
    p_message = message_.lower()
    #if re.search("bunker tool", p_message):
    #    return f'A user has requested the bunker tool. https://404th.ru/bob/'
    
    token_pair = re.findall('how (many|much)(.*) to (kill|destroy) (.*)', p_message)
    if len(token_pair) >= 1:
        weapon, target = token_pair[0][1], token_pair[0][3]
        return handle_response_inner(weapon, target)
    
    token_pair = re.findall('how (many|much)(.*) to disable (.*)', p_message)
    if len(token_pair) >= 1:
        weapon, target = token_pair[0][1], token_pair[0][2]
        return handle_response_inner(weapon, target, operation="disable")


