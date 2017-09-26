import os
import json
import arcpy

def get_config():
    config_file = os.path.join(os.path.dirname(__file__),"_config.json")
    with open(config_file,'rb') as f:
        config = json.load(f)
    return config

CONFIG = get_config()
