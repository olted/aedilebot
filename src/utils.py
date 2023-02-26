
debugging = False
def debug(message):
    if debugging:
        print(message)

def debug_summary(weapon, target, damage, h2k):
    if debugging:
        print(f"Weapon = {weapon}, Target = {target}, Damage = {damage}, HitsToKill={h2k} ")

def debug_fuzzy(input , key_list, key):
    if debugging:
        print(f"User input: {input}, Good Guesses: {key_list}, Final Guess: {key}")

