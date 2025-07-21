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
move_to_rear_string_list = [ "t1","t2","t3","unemplaced","unentrenched","emplaced", "entrenched","tier 1", "tier 2","tier 3","concrete"]
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
    

    
def move_string_to_rear(string):
    tier_dictionary = { "tier 1":"t1","tier 2":"t2","tier 3":"t3","concrete":"t3"}
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


async def message_handler(message_, user_message):
    response = bot.handle_response(user_message)
    if response:
        await message_.reply(response, mention_author = False)

def list_guilds(client): 
    print("Current discords: ")
    for guild in client.guilds:
        print(guild, end=" \n")

# main bot funcion

if __name__ == '__main__':
    # run
    #message = "how much 40mm to kill trench"
    #print(parse.slang_dict)
    #implement move string to rear
    #print(move_string_to_rear("how many 40 to kill entrenched bb 3x2"))
    #print(bot.handle_response(message))
    bot.run_discord_bot()