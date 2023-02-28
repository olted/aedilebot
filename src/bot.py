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
        await interaction.response.send_message(
            "Aedile is a discord bot which provides damage calculation and foxhole stats with nothing more than a single prompt or command. To use it try a prompt with the following format\n``How many|much (weapon) to kill|disable (target)``\n\nExample prompts to try:\nHow many 40mm to kill SvH?\nHow many 94.5mm to disable Ares?\nHow much 40mm to kill BT Pad?\nHow many satchels to kill Patridia?\nHow many ATG to kill Chieftain?\nHow many 150 to kill Feirmor?\n\nTo get stats about a specific weapon, vehicle, or structure, do ``/statsheet (entity)``")
    @client.tree.command(name="statsheet")
    async def statsheet(interaction: discord.Interaction, entity: str, hide_output: bool=False):
        if hide_output==True:
            await interaction.response.send_message(calculator.statsheet_handler(entity),ephemeral=True)
        elif hide_output==False:
            await interaction.response.send_message(calculator.statsheet_handler(entity),ephemeral=False)

    #Not in use yet, kill command
    
    @client.tree.command(name="kill")
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
        guess = fuzz.fuzzy_match_target_name(current)
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


