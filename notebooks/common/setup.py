import os
from os import path
import json
from enum import Enum

config_path = path.expanduser("~/.brite")
config_file = path.join(config_path,"brite_config.json")
print(config_path)

class ValueDefined(Enum):
    decorrelation_path = "Decorrelation Path"

def setup_config():
    if not path.exists(config_path):
        os.makedirs(config_path)

    if not path.exists(config_file):
        with open(config_file,'x') as f:
            json.dump({},f)
    
    with open(config_file,'r') as f:
        config_dict = json.load(f)
    
    while(True):
        brite_path = input(f"Please enter the path for the 'Brite decorrelation summer 2021' folder:")
        
        if not path.exists(brite_path):
            print("Please enter a valid path!")
            continue
            
        if "Decorrelations" not in os.listdir(brite_path):
            print("Folder doesn't contain the Decorrelations path. This is probably not the right folder.")
            continue
        
        break
    
    config_dict[ValueDefined.decorrelation_path.value] = brite_path

    with open(config_file,'w') as f:
        json.dump(config_dict,f)

    print("Thanks! Everything is configured, you can now use the configs.")

def get_config():
    if not path.exists(config_file):
        setup_config()
    
    with open(config_file,'r') as f:
        config_dict = json.load(f)
    
    if ValueDefined.decorrelation_path.value not in config_dict.keys() or not path.exists(config_dict[ValueDefined.decorrelation_path.value]):
        setup_config()
    
    with open(config_file,'r') as f:
        config_dict = json.load(f)
    