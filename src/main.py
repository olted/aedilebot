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
    if name in parse.slang_dict:
        return parse.slang_dict[name]
        # if entire input detects as a specific slang piece, itll return it and wont continue past here in the method
    for word in name_parsed:
        if word in parse.slang_dict:
            name = name.replace(word, parse.slang_dict[word])
    return name

async def message_handler(message_, user_message):
    response = bot.handle_response(user_message)
    if response:
        await message_.reply(response)

def list_guilds(client):
    for guild in client.guilds:
        print("Current discords: ",guild, end=" ")

# main bot funcion

if __name__ == '__main__':
    # run
    message = "how much 40mm to kill Patridia"
    #print(parse.slang_dict)

    #print(handle_response(message))
    bot.run_discord_bot()