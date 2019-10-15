import PySimpleGUIWx as sg
from sc2reader.factories import SC2Factory
import json
import os, os.path
import defaults

class rename:

    template_name = 'template'
    source_dir_name = 'source_dir'
    target_dir_name = 'target_dir'
    player_id_name = 'player_id'
    operation_name = 'operation'
    copy_name = 'copy'
    move_name = 'move'
    excludes_name = 'excludes'
    ai_name = 'AI'
    custom_name = 'Custom'
    exclude_matchups_name = 'Exclude_Matchups'
    exclude_dirs_name = 'Exclude_Dirs'
    includes_name = 'includes'
    include_matchups_name = 'Include_Matchups'
    min_players_name = 'Min_Players'
    max_players_name = 'Max_Players'
    expansions_name = 'Expansions'
    wol_name = 'WoL'
    hots_name = 'HotS'
    lotv_name = 'LotV'
    tray_name = 'tray'
    settings_file = 'settings.json'


    def __init__(self, settings):
        self.settings = settings
        self.template = settings[rename.template_name]
        self.source_dir = settings[rename.source_dir_name]
        self.target_dir = settings[rename.target_dir_name]
        self.operation = settings[rename.operation_name]
        self.excludes = settings[rename.excludes_name]
        self.includes = settings[rename.includes_name]
        self.player_id = settings[rename.player_id_name]
        self.tray = settings[rename.tray_name]
        
        self.set_layout()
    
    def run(self):      
        self.window = sg.Window('SC2 Replay Renamer', self.layout)
        
        while True:
            event, values = self.window.Read()
            print(event, values)

            if event is None or event == "Exit":
                break
            
            elif event == 'Detect':
                self.save_settings(values)
                self.detect_player_id(values[rename.source_dir_name], excludes=split_string(values[rename.exclude_dirs_name]))
            
            elif event == 'rename':
                self.save_settings(values)
                self.run_renamer()

            elif event == 'Save':
                self.save_settings(values)
                sg.popup_ok('Your settings have been saved!')
            
            elif event == 'Default':
                self.set_to_default(values)
        
        self.window.Close()

    
    def detect_player_id(self, source_path, excludes=[]):
        """automagically fills in the player's id after prompting them with popups"""

        if source_path:
            sc2 = SC2Factory(directory=source_path, exclude=excludes, depth=1, followlinks=True)
            replays = sc2.load_replays(source_path, load_level=2, load_maps=False, exclude=excludes)
            
            possible_players = []
            number_of_replay_files = len([name for name in os.listdir(source_path) if '.SC2Replay' in name])            
            number_of_replays_to_test = min(150, number_of_replay_files)
            
            for _ in range(number_of_replays_to_test):
                replay = next(replays)
                possible_players.extend([(player.name, player.toon_id) for player in replay.players if player.is_human])

            # function to get the next highest player name
            def get_next_highest():
                nonlocal possible_players
                largest = max(possible_players, key=lambda x: possible_players.count(x)) if possible_players else ''
                possible_players = list(filter(lambda x: x != largest, possible_players)) if largest else []
                return tuple(largest)
            # end function

            p = get_next_highest()
            popup = None
            
            # Check if folder is valid and contains replays
            if p:
                popup = sg.popup_yes_no(f'Are you {p[0]} (id={str(p[1])})?\n\n(Your ID does not change, even after a name change)', font='Arial 12')
                
                # checks if there are still names remaining
                while p and popup == 'No':
                    p = get_next_highest()
                    popup = sg.popup_yes_no(f'Are you {p[0]} (id={str(p[1])})?\n\n(Your ID does not change, even after a name change)', font='Arial 12') if p else 'No'

                if popup == 'Yes':
                    self.window.Element(rename.player_id_name).Update(p[1])
                else:
                    sg.popup_ok('Your ID has not been changed')
            else:
                sg.popup_error(f'Cannot detect any SC2Replay files in:\n\n{source_path}')
        
        else:
            sg.popup_error('Source Path cannot be empty!')
    

    def run_renamer(self):
        """renames all of the files that passed through the filters"""
        
        print('Not Implemented')


    def set_to_default(self, values):
        """makes all settings back to default"""
        
        self.window.fill(defaults.gui_readable_defaults)
        sg.popup_ok('Settings reset to default')

    
    def save_settings(self, values):
        """saves the settings to file"""

        self.template = values[rename.template_name]
        self.source_dir = values[rename.source_dir_name]
        self.target_dir = values[rename.target_dir_name]
        self.player_id = values[rename.player_id_name]
        self.operation = rename.move_name if values[rename.move_name] else rename.copy_name

        self.excludes = dict([
            get_pair(rename.ai_name, values),
            get_pair(rename.custom_name, values),
            get_pair(rename.exclude_matchups_name, values),
            get_pair(rename.exclude_dirs_name, values)
        ])

        self.includes = dict([
            get_pair(rename.include_matchups_name, values),
            get_pair(rename.min_players_name, values),
            get_pair(rename.max_players_name, values),
            get_pair(rename.wol_name, values),
            get_pair(rename.hots_name, values),
            get_pair(rename.lotv_name, values)
        ])

        self.tray = values[rename.tray_name]

        self.settings = {
            rename.template_name: self.template,
            rename.source_dir_name: self.source_dir,
            rename.target_dir_name: self.target_dir,
            rename.player_id_name: self.player_id,
            rename.operation_name: self.operation,
            rename.excludes_name: self.excludes,
            rename.includes_name: self.includes,
            rename.tray_name: self.tray
        }

        with open(rename.settings_file, 'w') as file:
            json.dump(self.settings, file, indent=4)

    
    def set_layout(self):
        first_column_width = 30
        third_column_width = 50
        button_width = 9
        inner_space = 0.6

        radio_copy = sg.Radio('Copy', 'operation_group', key=rename.copy_name)
        radio_move = sg.Radio('Move', 'operation_group', key=rename.move_name)

        if self.operation == rename.move_name:
            radio_move = sg.Radio('Move', 'operation_group', key=rename.move_name, default=True)

        self.layout = [

            # Rename Operations
            [sg.Text('Rename Operations', font='Arial 12 bold')],
            [sg.Text('Rename Template', size=(first_column_width, 3)), sg.Multiline(default_text=self.template, size=(third_column_width, 3), do_not_clear=True, key=rename.template_name)],
            [sg.Text('Replay Folder', size=(first_column_width, 1)), sg.InputText(default_text=self.source_dir, key=rename.source_dir_name, do_not_clear=True, size=(third_column_width - button_width - inner_space, 1), change_submits=True), sg.FolderBrowse("Browse", size=(button_width, 1), initial_folder=self.source_dir, target=rename.source_dir_name, auto_size_button=False)],
            [sg.Text('Target Folder', size=(first_column_width, 1)), sg.InputText(default_text=self.target_dir, key=rename.target_dir_name, do_not_clear=True, size=(third_column_width - button_width - inner_space, 1), change_submits=True), sg.FolderBrowse("Browse", size=(button_width, 1), initial_folder=self.target_dir, target=rename.target_dir_name, auto_size_button=False)],
            [sg.Text('Player ID', size=(first_column_width, 1)), sg.InputText(default_text=self.player_id, key=rename.player_id_name, size=(third_column_width - button_width - inner_space, 1)), sg.Button('Detect', target=rename.player_id_name, size=(button_width, 1), key='Detect', auto_size_button=False)],
            
            
            # File Operation
            [sg.Text('File Operation', size=(first_column_width, 1)), radio_copy, radio_move],

            # divider
            [sg.Text(' ')],

            # Exclusions
            [sg.Text('Exclusions', font='Arial 14 bold')],
            [sg.Checkbox('Exclude Games with AI', default=self.excludes[rename.ai_name], key=rename.ai_name)],
            [sg.Checkbox('Exclude Custom Games', default=self.excludes[rename.custom_name], key=rename.custom_name)],
            [sg.Text('Exclude directories (separate by comma)', size=(first_column_width, 1)), sg.InputText(default_text=self.excludes[rename.exclude_dirs_name], size=(third_column_width, 1), key=rename.exclude_dirs_name)],

            # divider
            [sg.Text(' ')],

            # Inclusions
            [sg.Text('Inclusions', font='Arial 14 bold')],
            [sg.Text('Minimum Number of Players', size=(first_column_width, 1)), sg.InputText(default_text=self.includes[rename.min_players_name], key=rename.min_players_name, size=(third_column_width, 1))],
            [sg.Text('Maximum Number of Players', size=(first_column_width, 1)), sg.InputText(default_text=self.includes[rename.max_players_name], key=rename.max_players_name, size=(third_column_width, 1))],
            [sg.Checkbox('WoL Replays', key=rename.wol_name, default=self.includes[rename.wol_name])],
            [sg.Checkbox('HotS Replays', key=rename.hots_name, default=self.includes[rename.hots_name])],
            [sg.Checkbox('LotV Replays', key=rename.lotv_name, default=self.includes[rename.lotv_name])],

            # divider
            [sg.Text(' ')],

            # Matchups
            [sg.Text('Matchups', font='Arial 14 bold')],
            [sg.Text('Exclude Matchups (separate by comma)', size=(first_column_width, 1)), sg.InputText(default_text=self.excludes[rename.exclude_matchups_name], size=(third_column_width, 1), key=rename.exclude_matchups_name)],
            [sg.Text('Include Matchups (separate by comma)', size=(first_column_width, 1)), sg.InputText(default_text=self.includes[rename.include_matchups_name], size=(third_column_width, 1), key=rename.include_matchups_name)],
        
            # divider
            [sg.Text(' ')],

            # System Tray
            [sg.Checkbox('Run in System Tray', key='tray', default=self.tray)],

            # divider
            [sg.Text(' ')],

            # Final Buttons
            [sg.Button('Rename', key='rename'), sg.Save(), sg.Button('Default', key='Default'), sg.Exit()]
        ]


def get_pair(key, dictionary):
    for k, v in dictionary.items():
        if k == key:
            return (k, v)
    return None


def split_string(s):
    lst = [elem.strip() for elem in s.split(',')]
    return lst