import PySimpleGUIWx as sg
from sc2reader.factories import SC2Factory
import json
import sys
import os, os.path
import src.defaults as defaults
import src.stringmatch as stringmatch

class rename:

    template_ = 'template'
    source_dir_ = 'source_dir'
    target_dir_ = 'target_dir'
    player_id_ = 'player_id'
    operation_ = 'operation'
    copy_ = 'copy'
    move_ = 'move'
    excludes_ = 'excludes'
    ai_ = 'AI'
    custom_ = 'Custom'
    exclude_matchups_ = 'Exclude_Matchups'
    exclude_dirs_ = 'Exclude_Dirs'
    includes_ = 'includes'
    include_matchups_ = 'Include_Matchups'
    min_players_ = 'Min_Players'
    max_players_ = 'Max_Players'
    expansions_ = 'Expansions'
    wol_ = 'WoL'
    hots_ = 'HotS'
    lotv_ = 'LotV'
    tray_ = 'tray'
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
        self.run_window()


    def run_window(self):
        if not self.has_window_running:
            self.has_window_running = True

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
                    self.detect_player_id(self.values[rename.source_dir_], excludes=split_string(self.values[rename.exclude_dirs_]))
                
                elif event == 'Rename':
                    if self.values[self.tray_]:
                        self.window.Hide()
                        self.run_renamer()
                        self.run_tray()
                    else:
                        self.run_renamer()

                elif event == 'Save':
                    self.save_settings()
                    sg.popup_ok('Your settings have been saved!')
                
                elif event == 'Default':
                    self.set_to_default()
                    sg.popup_ok('Settings reset to default')

                # updates input values in GUI to the most recent by the end of the loop
                self.window.fill(self.values)
        
        else:
            print('An Instance of Window is already running!')
            return None


    def run_tray(self):
        """Runs the tray application"""
        self.tray = sg.SystemTray(menu=self.tray_menu)

        # runs only a single instance of the tray application
        if not self.has_tray_running:
            self.has_tray_running = True
            
            while True:
                menu_item = self.tray.read()
                print('TRAY:', menu_item)

                if menu_item == 'Exit':
                    self.window.close()
                    self.tray.close()
                    sys.exit()
                    break
                
                elif menu_item == 'Open' or menu_item == '__ACTIVATED__':
                    self.has_tray_running = False
                    self.window.un_hide()
                    self.tray.close()
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
                    self.values[rename.player_id_] = p[1]
                else:
                    sg.popup_ok('Your ID has not been changed')
            else:
                sg.popup_error(f'Cannot detect any SC2Replay files in:\n\n{source_path}')
        else:
            sg.popup_error('Cannot resolve source path (Replay folder)!')
    

    def run_renamer(self):
        """renames all of the files that passed through the filters"""
        
        print('Not Implemented')


    def set_to_default(self):
        """makes all settings back to default"""
        self.window.fill(defaults.gui_readable_defaults)
        self.values = defaults.gui_readable_defaults

    
    def save_settings(self):
        """saves the settings to file"""
        self.settings = {
            self.template_: self.values[self.template_],
            self.source_dir_: self.values[self.source_dir_],
            self.target_dir_: self.values[self.target_dir_],
            self.player_id_: self.values[self.player_id_],
            self.operation_: self.move_ if self.values[self.move_] else self.copy_,
            self.excludes_: {
                self.ai_: self.values[self.ai_],
                self.custom_: self.values[self.custom_],
                self.exclude_matchups_: self.values[self.exclude_matchups_],
                self.exclude_dirs_: self.values[self.exclude_dirs_]
            },
            self.includes_: {
                self.include_matchups_: self.values[self.include_matchups_],
                self.min_players_: self.values[self.min_players_],
                self.max_players_: self.values[self.max_players_],
                self.wol_: self.values[self.wol_],
                self.hots_: self.values[self.hots_],
                self.lotv_: self.values[self.lotv_]
            },
            self.tray_: self.values[self.tray_]
        }

        with open(rename.settings_file, 'w') as file:
            json.dump(self.settings, file, indent=4)


    def set_tray_menu(self):
        """ sets the layout of the tray application """
        self.tray_menu = ['BLANK', ['&Open', '---', '&Exit']]


    def set_layout(self):
        """sets the layout of the entire GUI"""
        template = self.settings[rename.template_]
        source_dir = self.settings[rename.source_dir_]
        target_dir = self.settings[rename.target_dir_]
        operation = self.settings[rename.operation_]
        excludes = self.settings[rename.excludes_]
        includes = self.settings[rename.includes_]
        player_id = self.settings[rename.player_id_]
        tray = self.settings[rename.tray_]
        
        first_column_width = 30
        third_column_width = 50
        button_width = 9
        inner_space = 0.6

        radio_copy = sg.Radio('Copy', 'operation_group', key=rename.copy_)
        radio_move = sg.Radio('Move', 'operation_group', key=rename.move_)

        if operation == rename.move_:
            radio_move = sg.Radio('Move', 'operation_group', key=rename.move_, default=True)

        self.layout = [

            # Rename Operations
            [sg.Text('Rename Operations', font='Arial 12 bold')],
            [sg.Text('Rename Template', size=(first_column_width, 3)), sg.Multiline(default_text=template, size=(third_column_width, 3), do_not_clear=True, key=rename.template_)],
            [sg.Text('Replay Folder', size=(first_column_width, 1)), sg.InputText(default_text=source_dir, key=rename.source_dir_, do_not_clear=True, size=(third_column_width - button_width - inner_space, 1), change_submits=True), sg.FolderBrowse("Browse", size=(button_width, 1), initial_folder=source_dir, target=rename.source_dir_, auto_size_button=False)],
            [sg.Text('Target Folder', size=(first_column_width, 1)), sg.InputText(default_text=target_dir, key=rename.target_dir_, do_not_clear=True, size=(third_column_width - button_width - inner_space, 1), change_submits=True), sg.FolderBrowse("Browse", size=(button_width, 1), initial_folder=target_dir, target=rename.target_dir_, auto_size_button=False)],
            [sg.Text('Player ID', size=(first_column_width, 1)), sg.InputText(default_text=player_id, key=rename.player_id_, size=(third_column_width - button_width - inner_space, 1)), sg.Button('Detect', target=rename.player_id_, size=(button_width, 1), key='Detect', auto_size_button=False)],
            
            
            # File Operation
            [sg.Text('File Operation', size=(first_column_width, 1)), radio_copy, radio_move],

            # divider
            [sg.Text(' ')],

            # Exclusions
            [sg.Text('Exclusions', font='Arial 14 bold')],
            [sg.Checkbox('Exclude Games with AI', default=excludes[rename.ai_], key=rename.ai_)],
            [sg.Checkbox('Exclude Custom Games', default=excludes[rename.custom_], key=rename.custom_)],
            [sg.Text('Exclude directories (separate by comma)', size=(first_column_width, 1)), sg.InputText(default_text=excludes[rename.exclude_dirs_], size=(third_column_width, 1), key=rename.exclude_dirs_)],

            # divider
            [sg.Text(' ')],

            # Inclusions
            [sg.Text('Inclusions', font='Arial 14 bold')],
            [sg.Text('Minimum Number of Players', size=(first_column_width, 1)), sg.InputText(default_text=includes[rename.min_players_], key=rename.min_players_, size=(third_column_width, 1))],
            [sg.Text('Maximum Number of Players', size=(first_column_width, 1)), sg.InputText(default_text=includes[rename.max_players_], key=rename.max_players_, size=(third_column_width, 1))],
            [sg.Checkbox('WoL Replays', key=rename.wol_, default=includes[rename.wol_])],
            [sg.Checkbox('HotS Replays', key=rename.hots_, default=includes[rename.hots_])],
            [sg.Checkbox('LotV Replays', key=rename.lotv_, default=includes[rename.lotv_])],

            # divider
            [sg.Text(' ')],

            # Matchups
            [sg.Text('Matchups', font='Arial 14 bold')],
            [sg.Text('Exclude Matchups (separate by comma)', size=(first_column_width, 1)), sg.InputText(default_text=excludes[rename.exclude_matchups_], size=(third_column_width, 1), key=rename.exclude_matchups_)],
            [sg.Text('Include Matchups (separate by comma)', size=(first_column_width, 1)), sg.InputText(default_text=includes[rename.include_matchups_], size=(third_column_width, 1), key=rename.include_matchups_)],
        
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