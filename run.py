from src.ReplayRenamer import ReplayRenamer
import json
import sc2reader
import os.path
from src.structures.defaults import settings

if __name__ == '__main__':

    # Load settings from file, if it exists, otherwise, uses the default settings    
    settings_file = "settings.json"
    
    if os.path.isfile(settings_file):
        with open(settings_file, 'r') as file:
            settings = json.load(file)
    else:
        with open(settings_file, 'w') as file:
            json.dump(settings, file, indent=4)

    # initializing and running the GUI
    gui = ReplayRenamer(settings)
    gui.run()