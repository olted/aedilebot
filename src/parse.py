import json

def load_array_to_dict(filename, key):
    with open(filename) as f:
        dataArray = json.load(f)
        data_dict = {}
    for entity in dataArray:
        data_dict[entity[key]]=entity
    return data_dict

def load_json_to_dict(filename):
    with open(filename) as f:
        dict = json.load(f)
        return dict

# Structure Json parser
structures_dict=load_array_to_dict('data\Structures.json','Name')
weapons_dict=load_array_to_dict('data\Weapons.json','Informalname')
damages_dict=load_array_to_dict('data\Damage.json','Damagetypes')
th_relics_dict=load_json_to_dict('data\\th_relic_types.json')

#slang
with open('data\Structure_Dictionary.json') as f:
    DictionaryArray = json.load(f)
    structure_slang_dict = {}
for slang in DictionaryArray:
    structure_slang_dict.update(slang)

with open('data\Weapon_Dictionary.json') as f:
    DictionaryArray = json.load(f)
    weapon_slang_dict = {}
for slang in DictionaryArray:
    weapon_slang_dict.update(slang)