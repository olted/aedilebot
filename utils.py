import bot

debugging = False
def debug(message):
    if debugging:
        print(message)

def debug_summary(weapon, target, damage, h2k):
    if debugging:
        print(f"Weapon = {weapon}, Target = {target}, Damage = {damage}, HitsToKill={h2k} ")