import json

def load_json_to_dict(filename):
    with open(filename) as f:
        dict = json.load(f)
        return dict