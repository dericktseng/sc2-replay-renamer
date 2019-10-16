import PySimpleGUIWx as sg
from sc2reader.factories import SC2Factory
import json
import sys
import os, os.path
import src.defaults as defaults
import src.stringmatch as stringmatch

class rename:

    _template = 'template'
    _source_dir = 'source_dir'
    _target_dir = 'target_dir'
    _player_id = 'player_id'
    _operation = 'operation'
    _copy = 'copy'
    _move = 'move'
    _excludes = 'excludes'
    _ai = 'AI'
    _custom = 'Custom'
    _exclude_matchups = 'Exclude_Matchups'
    _exclude_dirs = 'Exclude_Dirs'
    _includes = 'includes'
    _include_matchups = 'Include_Matchups'
    _min_players = 'Min_Players'
    _max_players = 'Max_Players'
    _wol = 'WoL'
    _hots = 'HotS'
    _lotv = 'LotV'
    _tray = 'tray'
    settings_file = 'settings.json'


    def __init__(self, settings):
        self.settings = settings
        self.set_layout()
        self.set_tray_menu()
        
        self.values = None
        self.tray = None
        self.has_tray_running = False
        self.has_window_running = False
    

    def run(self):
        if self.settings[self._tray]:
            self.run_tray()
        else:
            self.run_window()


    def run_window(self):
        if not self.has_window_running:
            self.has_window_running = True
            self.window = sg.Window('SC2 Replay Renamer', self.layout)

            """runs the GUI"""
            self.window = sg.Window('SC2 Replay Renamer', self.layout)
            
            while True:
                event, values = self.window.read()

                # special case, since values are all set to None here
                if event is None or event == "Exit":
                    self.window.close()
                    break
                
                self.values = values
                print(event, self.values)

                if event == 'Detect':
                    self.detect_player_id(self.values[rename._source_dir], excludes=split_string(self.values[rename._exclude_dirs]))
                
                elif event == 'Rename':
                    self.save_settings()

                    if self.values[self._tray]:
                        self.window.Hide()
                        self.run_renamer(in_tray=True)
                        self.run_tray()
                    
                    else:
                        self.run_renamer(in_tray=False)

                elif event == 'Save':
                    self.save_settings()
                    sg.popup_ok('Your settings have been saved!')
                
                elif event == 'Default':
                    self.set_to_default()
                    self.save_settings()
                    sg.popup_ok('Settings reset to default')

                # updates input values in GUI to the most recent by the end of the loop
                self.window.fill(self.values)
        
        else:
            self.window.un_hide()


    def run_tray(self):
        """Runs the tray application"""
        self.tray = sg.SystemTray(menu=self.tray_menu)

        # runs only a single instance of the tray application
        if not self.has_tray_running:
            self.has_tray_running = True
            self.tray.show_message('SC2 Replay Renamer', 'SC2 Replay Renamer Tool is now running', messageicon=sg.SYSTEM_TRAY_MESSAGE_ICON_INFORMATION)

            while True:
                menu_item = self.tray.read()
                print('TRAY:', menu_item)

                if menu_item == 'Exit' or menu_item == 'None':
                    sys.exit()
                    break
                
                elif menu_item == 'Open' or menu_item == sg.EVENT_SYSTEM_TRAY_ICON_ACTIVATED:
                    self.has_tray_running = False
                    self.tray.close()
                    self.run_window()
                    break

        else:
            print('An Instance of Tray is already running!')
            return None

    def detect_player_id(self, source_path, excludes=[]):
        """automagically fills in the player's id after prompting them with popups"""

        # if source path is valid, initialize the sc2reader and load replays
        if source_path and os.path.isdir(source_path):
            sc2 = SC2Factory(directory=source_path, exclude=excludes, depth=1, followlinks=True)
            replays = sc2.load_replays(source_path, load_level=2, load_maps=False, exclude=excludes)
            
            possible_players = []
            number_of_replay_files = len([name for name in os.listdir(source_path) if '.SC2Replay' in name])            
            number_of_replays_to_test = min(150, number_of_replay_files)
            
            # populates possible_players with the list of players detected
            for _ in range(number_of_replays_to_test):
                replay = next(replays)
                possible_players.extend([(player.name, player.toon_id) for player in replay.players if player.is_human])

            # generator to get the next highest player name
            def get_highest(lst):
                while lst:
                    largest = max(lst, key=lambda x: lst.count(x)) if lst else ''
                    lst = list(filter(lambda x: x != largest, lst)) if largest else []
                    yield tuple(largest)


            highest = get_highest(possible_players)
            p = next(highest, None)
            
            # Check if folder is valid and contains replays
            if p:
                popup = sg.popup_yes_no(f'Are you {p[0]} (ID: {str(p[1])})?\n\n(Your ID does not change, even after a name change)', font='Arial 12')
                
                # checks if there are still names remaining
                while p and popup == 'No':
                    p = next(highest, None)
                    popup = sg.popup_yes_no(f'Are you {p[0]} (id={str(p[1])})?\n\n(Your ID does not change, even after a name change)', font='Arial 12') if p else 'No'

                # updates the values to the latest
                if popup == 'Yes':
                    self.values[rename._player_id] = p[1]
                else:
                    sg.popup_ok('Your ID has not been changed')
            else:
                sg.popup_error(f'Cannot detect any SC2Replay files in:\n\n{source_path}')
        else:
            sg.popup_error('Cannot resolve source path (Replay folder)!')
    

    def run_renamer(self, in_tray=False):
        """renames all of the files that passed through the filters"""
        
        print('Not Implemented')


    def set_to_default(self):
        """makes all settings back to default"""
        self.window.fill(defaults.gui_readable_defaults)
        self.values = defaults.gui_readable_defaults

    
    def save_settings(self):
        """saves the settings to file"""
        print('save_settings', self.values)
        self.settings = {
            self._template: self.values[self._template],
            self._source_dir: self.values[self._source_dir],
            self._target_dir: self.values[self._target_dir],
            self._player_id: self.values[self._player_id],
            self._operation: self._move if self.values[self._move] else self._copy,
            self._excludes: {
                self._ai: self.values[self._ai],
                self._custom: self.values[self._custom],
                self._exclude_matchups: self.values[self._exclude_matchups],
                self._exclude_dirs: self.values[self._exclude_dirs]
            },
            self._includes: {
                self._include_matchups: self.values[self._include_matchups],
                self._min_players: self.values[self._min_players],
                self._max_players: self.values[self._max_players],
                self._wol: self.values[self._wol],
                self._hots: self.values[self._hots],
                self._lotv: self.values[self._lotv]
            },
            self._tray: self.values[self._tray]
        }

        with open(rename.settings_file, 'w') as file:
            json.dump(self.settings, file, indent=4)


    def set_tray_menu(self):
        """ sets the layout of the tray application """
        self.tray_menu = ['BLANK', ['&Open', '---', '&Exit']]


    def set_layout(self):
        """sets the layout of the entire GUI"""
        template = self.settings[rename._template]
        source_dir = self.settings[rename._source_dir]
        target_dir = self.settings[rename._target_dir]
        operation = self.settings[rename._operation]
        excludes = self.settings[rename._excludes]
        includes = self.settings[rename._includes]
        player_id = self.settings[rename._player_id]
        tray = self.settings[rename._tray]
        
        first_column_width = 30
        third_column_width = 50
        button_width = 9
        inner_space = 0.6

        radio_copy = sg.Radio('Copy', 'operation_group', key=rename._copy)
        radio_move = sg.Radio('Move', 'operation_group', key=rename._move)

        if operation == rename._move:
            radio_move = sg.Radio('Move', 'operation_group', key=rename._move, default=True)

        self.layout = [

            # Rename Operations
            [sg.Text('Rename Operations', font='Arial 12 bold')],
            [sg.Text('Rename Template', size=(first_column_width, 3)), sg.Multiline(default_text=template, size=(third_column_width, 3), do_not_clear=True, key=rename._template)],
            [sg.Text('Replay Folder', size=(first_column_width, 1)), sg.InputText(default_text=source_dir, key=rename._source_dir, do_not_clear=True, size=(third_column_width - button_width - inner_space, 1), change_submits=True), sg.FolderBrowse("Browse", size=(button_width, 1), initial_folder=source_dir, target=rename._source_dir, auto_size_button=False)],
            [sg.Text('Target Folder', size=(first_column_width, 1)), sg.InputText(default_text=target_dir, key=rename._target_dir, do_not_clear=True, size=(third_column_width - button_width - inner_space, 1), change_submits=True), sg.FolderBrowse("Browse", size=(button_width, 1), initial_folder=target_dir, target=rename._target_dir, auto_size_button=False)],
            [sg.Text('Player ID', size=(first_column_width, 1)), sg.InputText(default_text=player_id, key=rename._player_id, size=(third_column_width - button_width - inner_space, 1)), sg.Button('Detect', target=rename._player_id, size=(button_width, 1), key='Detect', auto_size_button=False)],
            
            
            # File Operation
            [sg.Text('File Operation', size=(first_column_width, 1)), radio_copy, radio_move],

            # divider
            [sg.Text(' ')],

            # Exclusions
            [sg.Text('Exclusions', font='Arial 14 bold')],
            [sg.Checkbox('Exclude Games with AI', default=excludes[rename._ai], key=rename._ai)],
            [sg.Checkbox('Exclude Custom Games', default=excludes[rename._custom], key=rename._custom)],
            [sg.Text('Exclude directories (separate by comma)', size=(first_column_width, 1)), sg.InputText(default_text=excludes[rename._exclude_dirs], size=(third_column_width, 1), key=rename._exclude_dirs)],

            # divider
            [sg.Text(' ')],

            # Inclusions
            [sg.Text('Inclusions', font='Arial 14 bold')],
            [sg.Text('Minimum Number of Players', size=(first_column_width, 1)), sg.InputText(default_text=includes[rename._min_players], key=rename._min_players, size=(third_column_width, 1))],
            [sg.Text('Maximum Number of Players', size=(first_column_width, 1)), sg.InputText(default_text=includes[rename._max_players], key=rename._max_players, size=(third_column_width, 1))],
            [sg.Checkbox('WoL Replays', key=rename._wol, default=includes[rename._wol])],
            [sg.Checkbox('HotS Replays', key=rename._hots, default=includes[rename._hots])],
            [sg.Checkbox('LotV Replays', key=rename._lotv, default=includes[rename._lotv])],

            # divider
            [sg.Text(' ')],

            # Matchups
            [sg.Text('Matchups', font='Arial 14 bold')],
            [sg.Text('Exclude Matchups (separate by comma)', size=(first_column_width, 1)), sg.InputText(default_text=excludes[rename._exclude_matchups], size=(third_column_width, 1), key=rename._exclude_matchups)],
            [sg.Text('Include Matchups (separate by comma)', size=(first_column_width, 1)), sg.InputText(default_text=includes[rename._include_matchups], size=(third_column_width, 1), key=rename._include_matchups)],
        
            # divider
            [sg.Text(' ')],

            # System Tray
            [sg.Checkbox('Run in System Tray', key='tray', default=tray)],

            # divider
            [sg.Text(' ')],

            # Final Buttons
            [sg.Button('Rename', key='Rename'), sg.Save(), sg.Button('Default', key='Default'), sg.Exit()]
        ]


def split_string(s):
    lst = [elem.strip() for elem in s.split(',')]
    return lst