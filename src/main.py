# import discord
from discord.ext import commands
import re
import json
import discord.app_commands
import math
import os
import utils
import parse
import fuzzy as fuzz
import bot
import calculator

utils.debugging = True
move_to_rear_string_list = [ "t1","t2","t3", "emplaced", "entrenched","tier 1", "tier 2","tier 3"]
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

async def message_handler(message_, user_message):
    response = bot.handle_response(user_message)
    if response:
        await message_.reply(response, mention_author = False)

def list_guilds(client): 
    for guild in client.guilds:
        print("Current discords: ",guild, end=" ")

# main bot funcion

if __name__ == '__main__':
    # run
    message = "how much 40mm to kill svhh"
    #print(parse.slang_dict)

    print(bot.handle_response(message))
    bot.run_discord_bot()