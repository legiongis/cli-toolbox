import os
import json

def get_settings():
    settings_file = os.path.join(os.path.dirname(__file__),"settings.json")
    if not os.path.isfile(settings_file):
        return False
    with open(settings_file,'rb') as f:
        settings = json.load(f)
    return settings

settings = get_settings()