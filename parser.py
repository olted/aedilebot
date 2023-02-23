def parse():
    
    with open('th_relic_types.json') as f:
        th_relic_types_dict = json.load(f)

    # Structure Json parser
    with open('Structures.json') as f:
        StructuresArray = json.load(f)
        structures_dict = {}
    for structure in StructuresArray:
        structures_dict[structure['Name']] = structure

    # Weapon Json parser
    with open('Weapons.json') as f:
        WeaponsArray = json.load(f)
        weapons_dict = {}
    for weapon in WeaponsArray:
        name = weapon['Informalname']
        weapons_dict[name] = weapon

    # Mitigation json parser
    with open('Damage.json') as f:
        DamageArray = json.load(f)
        damages_dict = {}
    for damage in DamageArray:
        type = damage['Damagetypes']
        damages_dict[type] = damage

    # Slang Dictionary json parser
    with open('Dictionary.json') as f:
        DictionaryArray = json.load(f)
        Dictionary_dict = {}
    for slang in DictionaryArray:
        Dictionary_dict.update(slang)   