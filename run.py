from src.rename import rename
import json
import sc2reader
import os.path

if __name__ == '__main__':

    # Load settings from file, if it exists, otherwise, uses the default settings    
    settings_file = "settings.json"
    
    # default settings
    settings = {
        'template': '$myracesv$oppraces $mapname $mynames($mymmr) v $oppnames($oppmmr) - $durationminsmins [$month-$day-$year $hour-$min-$sec]',
        'source_dir': '',
        'target_dir': '',
        'player_id': '',
        'operation': 'copy',
        'excludes': {
            'AI': True,
            'Custom': False,
            'Matchups': ''
        },
        'includes': {
            'Matchups': 'XvX',
            'Min_Players': 2,
            'Max_Players': 2,
            'Expansions': {
                'WoL': False,
                'HotS': False,
                'LotV': True,
            }
        },
        'tray': True
    }
    
    if os.path.isfile(settings_file):
        with open(settings_file, 'r') as file:
            settings = json.load(file)
    else:
        with open(settings_file, 'w') as file:
            json.dump(settings, file, indent=4)

    # initializing and running the GUI
    gui = rename(settings)
    gui.run()