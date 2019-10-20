import json
import ntpath
import os
import os.path
import shutil
import sys
from os.path import isfile, join
from datetime import datetime
import time

import PySimpleGUIWx as sg
import sc2reader
from sc2reader.factories import SC2Factory

import src.auto_renamer_thread as AutoRenamer
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
            op = shutil.move if self.settings[self._operation] == self._move else shutil.copy
            self.run_renamer(op, in_tray=True, question=False)
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
                    src = self.values[rename._source_dir]
                    directories_to_exclude = split_string(self.values[rename._exclude_dirs])
                    self.detect_player_id(src, excludes=directories_to_exclude)
                
                elif event == 'Rename':
                    self.save_settings()
                    op = shutil.copy if self.values[self._copy] else shutil.move

                    if self.values[self._tray]:
                        self.window.Hide()
                        self.run_renamer(op=op, in_tray=True)
                        self.run_tray()
                    
                    else:
                        self.run_renamer(op=op, in_tray=False, question=True)

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

                elif menu_item == 'Open Replay Folder':
                    if self._source_dir in self.settings and self.settings[self._source_dir]:
                        os.startfile(self.settings[self._source_dir])
                    else:
                        sg.popup_error('No Replay directory specified')

        else:
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
    

    def run_renamer(self, op, in_tray=False, question=True):
        """renames all of the files that passed through the filters"""
        
        # asks user if they would like to rename all of their replays, or just new ones if they run in tray for the first time
        rename_all = 'Yes' if not in_tray else 'No'
        my_id = int(self.settings[self._player_id]) if self.settings[self._player_id] else ''
        
        if in_tray and question:
            rename_all = sg.popup_yes_no("Do you want to rename all replays?\n(If you select no, the tool will only rename newly created replay files)")

        
        source_path = self.settings[self._source_dir]
        dest = self.settings[self._target_dir]
        template = self.settings[self._template]

        # check if template is valid, requires player ID
        if self.template_contains_id_vars(template) and not my_id:
            sg.popup_error('Your template requires you to have Player ID filled in')
            return None

        # checks if source and target dir are the same
        if self.settings[self._source_dir] == self.settings[self._target_dir] and self.settings[self._operation] == self._copy:
            check = sg.popup_yes_no('Your replay directory and your Destination folder are the same. This is not recommended, unless your file operation is Move.\n\nAre you sure you want to proceed?')
            if check == 'No':
                return None
        
        # checks if source and target directories exists
        if not os.path.isdir(self.settings[self._source_dir]):
            sg.popup_error('Your replays folder is invalid!')
            return None
        
        if not os.path.isdir(self.settings[self._target_dir]):
            sg.popup_error('Your destination folder does not exist!')
            return None

        # check if there will be duplicate names
        if self.may_contain_duplicates(template):
            check = sg.popup_yes_no('Your template string may cause different replays to contain the same name. This WILL result in some replays being lost. Are you sure you want to proceed?')
            if check == 'No':
                sg.popup_ok('Your files have not been changed. Please change your template to include the $uniqueID variable')
                return None            
        
        # renames all replays detected
        elif rename_all == 'Yes':
            excluded_directories = split_string(self.settings[self._excludes][self._exclude_dirs])

            # load replays
            sc2 = SC2Factory(directory=source_path, exclude=excluded_directories, depth=1, followlinks=True)
            replays = sc2.load_replays(source_path, load_level=2, load_maps=False, exclude=excluded_directories)
            
            renamed_count = 0
            start_time = time.time()

            for replay in replays:
                
                # exclude AI
                if self.settings[self._excludes][self._ai] and replay.computers:
                    continue
                
                # exclude customs
                if self.settings[self._excludes][self._custom] and not replay.is_ladder:
                    continue

                # exclude all replays that are not within the bounds of number of players
                min_players = int(self.settings[self._includes][self._min_players])
                max_players = int(self.settings[self._includes][self._max_players])
                if not min_players <= len(replay.players) <= max_players:
                    continue

                # exclude WoL
                if replay.expansion == self._wol and not self.settings[self._includes][self._wol]:
                    continue

                # exclude HotS
                if replay.expansion == self._hots and not self.settings[self._includes][self._hots]:
                    continue

                # exclude LotV
                if replay.expansion == self._lotv and not self.settings[self._includes][self._lotv]:
                    continue

                # check to remove by matchups
                exclude_matchups = split_string(self.settings[self._excludes][self._exclude_matchups])
                include_matchups = split_string(self.settings[self._includes][self._include_matchups])

                should_exclude = self.has_matching(replay, exclude_matchups, has_id=True) if self.template_contains_id_vars(template) else self.has_matching(replay, exclude_matchups, has_id=False)
                should_include = self.has_matching(replay, include_matchups, has_id=True) if self.template_contains_id_vars(template) else self.has_matching(replay, include_matchups, has_id=False)
                if should_exclude:
                    continue
                
                # if include_matchups actually contains a string and it does not pass the include filter
                if include_matchups and not should_include:
                    continue
                

                # actually doing the renaming, after the filtering
                renamed_count += 1
                newname = template

                teams = replay.teams[:]
                if self.template_contains_id_vars(template):
                    my_team_list = list(filter(lambda team: my_id in [player.toon_id for player in team.players], teams))
                    
                    # make the first team the team you were on
                    if len(my_team_list) > 0:
                        my_team = my_team_list[0]
                        if teams[0] != my_team:
                            my_team_index = teams.index(my_team)
                            teams[0], teams[my_team_index] = teams[my_team_index], teams[0]

                    # "forward" everything to be non-ID based
                    newname = newname.replace('$myteamwithmmr', '$t1withmmr')
                    newname = newname.replace('$myteam', '$team1')
                    newname = newname.replace('$oppteams', '$team2')
                    newname = newname.replace('$myraces', '$t1races')
                    newname = newname.replace('$oppraces', '$t2races')
                    newname = newname.replace('$mymmr', '$t1mmr')
                    newname = newname.replace('$oppmmr', '$t2mmr')
                    newname = newname.replace('$oppwithmmr', '$t2withmmr')

                    
                # good luck trying to maintain this
                first_team = teams[0]
                teams.remove(first_team)
                team1player = first_team.players[0]
                team1_player_list = [player.name for player in first_team]
                team2_player_list = ['+'.join([player.name for player in team.players]) for team in teams]
                team2_with_mmr = ['+'.join([player.name for player in team.players]) +'('+ (str(max(0, team.players[0].init_data['scaled_rating'])) if replay.is_ladder else "0") + ')' for team in teams]
                opp_races_list = [team.lineup for team in teams]
                
                # variables to fill
                team1 = '+'.join(team1_player_list)
                t1races = first_team.lineup
                t1mmr = str(max(0, team1player.init_data['scaled_rating'])) if replay.is_ladder else '0'
                WL = 'W' if replay.winner == first_team else 'L'
                wl = WL.lower()
                team2 = 'v'.join(team2_player_list)
                t2withmmr = 'v'.join(team2_with_mmr)
                t2races = 'v'.join(opp_races_list)
                t2mmr = 'v'.join([str(team.players[0].init_data['scaled_rating']) if not replay.computers else '0' for team in teams])
                sc2map = replay.map_name
                durationhours = str(replay.game_length.hours)
                durationmins = str(replay.game_length.mins)
                durationsecs = str(replay.game_length.secs)
                date = datetime.fromtimestamp(replay.unix_timestamp)
                month = add_leading_zero(date.month)
                year = add_leading_zero(date.year)
                day = add_leading_zero(date.day)
                hour = add_leading_zero(date.hour)
                minute = add_leading_zero(date.minute)
                sec = add_leading_zero(date.second)
                currentname = ntpath.split(replay.filename)[1].replace('.SC2Replay', '')
                uniqueID = str(day) + str(month) + str(year) + str(hour) + str(minute) + str(sec)

                template_vars = {
                    'team1': team1,
                    't1races': t1races,
                    't1mmr': t1mmr,
                    't1withmmr': f'{team1}({t1mmr})',
                    'wl': wl,
                    'WL': WL,
                    'team2': team2,
                    't2withmmr': t2withmmr,
                    't2races': t2races,
                    't2mmr': t2mmr,
                    'map': sc2map,
                    'durationhours': durationhours,
                    'durationmins': durationmins,
                    'durationsecs': durationsecs,
                    'month': month,
                    'year': year,
                    'day': day,
                    'hour': hour,
                    'min': minute,
                    'sec': sec,
                    'gametype': replay.real_type,
                    'expansion': replay.expansion,
                    'currentname': currentname,
                    'uniqueID': uniqueID
                }

                # fill in everything in the template
                for var in stringmatch.non_id_variables:
                    newname = newname.replace(f'${var}', template_vars[var])
                
                newname += '.SC2Replay'

                # do the renaming operation
                orig_location = replay.filename
                new_location = join(dest, newname)
                print(orig_location, new_location)
                op(orig_location, new_location)
            
            end_time = time.time()
            sg.popup_ok(f'Job Done!\nRenamed {renamed_count} replays in {str(end_time - start_time)[:3]} seconds')
        
        elif rename_all == 'No' and in_tray:
            print('going to implement')
        
        else:
            print('Something went wrong...')
            sys.exit(1)


    def has_matching(self, replay, lst, has_id=False):
        teams = replay.teams[:]
        lineups = []

        if has_id:
            my_id = int(self.settings[self._player_id])
            get_my_team = filter(lambda team: my_id in [player.toon_id for player in team.players], teams)
            
            # the team you are on
            my_team = list(get_my_team)
            my_team_races = ""

            if my_team:
                my_team_races = my_team[0].lineup
                teams.remove(my_team[0])

            # the other teams that you face (this is a list)
            other_teams = teams

            # remove by matchups
            vs_string = my_team_races
            for team in other_teams:
                vs_string += 'v' + team.lineup
            lineups = vs_string.lower().split('v')
        
        else:
            for team in teams:
                lineups.append(team.lineup.lower())
            
        for matchup in lst:
            matchup = matchup.lower().split('v')
            if matchup == lineups:
                return True
        
        return False

    def may_contain_duplicates(self, template):
        template = str(template)
        if '$unique' in template or '$currentname' in template:
            return False
        
        hour = '$hour' in template
        minute = '$min' in template
        sec = '$sec' in template

        return not (hour and minute and sec)


    def template_contains_id_vars(self, template):
        """returns whether the user included a id_variable when he did not fill in player id"""
        for var in stringmatch.id_variables:
            if var in template:
                return True
        return False


    def set_to_default(self):
        """makes all settings back to default"""
        self.window.fill(defaults.gui_readable_defaults)
        self.values = defaults.gui_readable_defaults

    
    def save_settings(self):
        """saves the settings to file"""
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
        self.tray_menu = ['BLANK', ['&Open', 'Open Replay Folder', '---', '&Exit']]


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
            [sg.Text('Destination Folder', size=(first_column_width, 1)), sg.InputText(default_text=target_dir, key=rename._target_dir, do_not_clear=True, size=(third_column_width - button_width - inner_space, 1), change_submits=True), sg.FolderBrowse("Browse", size=(button_width, 1), initial_folder=target_dir, target=rename._target_dir, auto_size_button=False)],
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
            [sg.Checkbox('Automatically rename new replay files', key='tray', default=tray)],

            # divider
            [sg.Text(' ')],

            # Final Buttons
            [sg.Button('Rename', key='Rename'), sg.Save(), sg.Button('Default', key='Default'), sg.Exit()]
        ]


def split_string(s):
    return [elem.strip() for elem in s.split(',')] if s else []


def add_leading_zero(s):
    s = str(s)
    return '0' + s if len(s) == 1 else s