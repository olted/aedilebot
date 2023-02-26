import discord
import main
import dotenv
import os
from dotenv import load_dotenv
import calculator
import re

load_dotenv()
DEPLOYMENT_TOKEN = os.getenv("DEPLOYMENT_TOKEN")
DEV_SERVER_TOKEN = os.getenv("DEV_SERVER_TOKEN")

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
            "I'm currently configured to answer any prompts containing 'How many/much x to kill/destroy y'. This can be vehicles *and* structures, including specific town hall/relics by name. Any values given for vehicles assumes shell penetration. \n \n Try asking me these questions:\n How many 150 to destroy Abandoned Ward \n How much Predator94.5mm to kill Ares \n How much 40mm to kill bt pad \n How many stickies to kill hatchet \n How many satchels to kill Feirmor\n How many satchels to kill t3 bb husk")
    

    #Not in use yet, kill command
    #@client.tree.command(name="kill")
    #async def kill(interaction: discord.Interaction, target: str="", weapon: str=""):
    #    await interaction.response.send_message(handle_response_inner(weapon,target))


    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        user_message = str(message.content)
        await main.message_handler(message, user_message)
    

    
    client.run(DEV_SERVER_TOKEN)

# bot logic
def handle_response_inner(weapon,target):
    try:
        try:
            return calculator.relic_th_h2k_handler(weapon, target)
        except LocationNotFoundError as e:
            return calculator.general_h2k_handler(weapon,target)
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



def handle_response(message_) -> str:
     # first we are deleting all capitalization
    p_message = message_.lower()
    #if re.search("bunker tool", p_message):
    #    return f'A user has requested the bunker tool. https://404th.ru/bob/'
    
    token_pair = re.findall('how (many|much)(.*) to (kill|destroy) (.*)', p_message)
    if len(token_pair) >= 1:
        weapon, target = token_pair[0][1], token_pair[0][3]
        return handle_response_inner(weapon,target)
    return ""
