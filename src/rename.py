import PySimpleGUIWx as sg

class rename:
    def __init__(self, settings):
        self.settings = settings
        self.template = settings['template']
        self.source_dir = settings['source_dir']
        self.target_dir = settings['target_dir']
        self.operation = settings['operation']
        self.excludes = settings['excludes']
        self.includes = settings['includes']
        self.player_id = settings['player_id']
        self.tray = settings['tray']
        
        self.set_layout()
    
    def run(self):
        print("Not implemented yet")
        
        self.window = sg.Window('SC2 Replay Renamer', self.layout)
        
        while True:
            event, values = self.window.Read()

            # Debugging purposes
            print(event, values)
            if event is None or event == "Exit":
                break
        self.window.Close()

    def set_layout(self):
        first_column_width = 30
        second_column_width = 22
        third_column_width = 50
        button_width = 9
        inner_space = 0.6

        radio_copy = sg.Radio('Copy', 'operation_group', key='copy')
        radio_move = sg.Radio('Move', 'operation_group', key='move')

        if self.operation == 'move':
            radio_move = sg.Radio('Move', 'operation_group', key='move', default=True)

        self.layout = [

            # Rename Operations
            [sg.Text('Rename Operations', font='Arial 12 bold')],
            [sg.Text('Rename Template', size=(first_column_width, 3)), sg.Multiline(default_text=self.template, size=(third_column_width, 3), do_not_clear=True, key='template')],
            [sg.Text('Player ID', size=(first_column_width, 1)), sg.InputText(default_text=self.player_id, key='pid', size=(third_column_width - button_width - inner_space, 1)), sg.Button('Detect', target='pid', size=(button_width, 1), key='pid_button', auto_size_button=False)],
            [sg.Text('Replay Folder', size=(first_column_width, 1)), sg.InputText(default_text=self.source_dir, key="source_path", do_not_clear=True, size=(third_column_width - button_width - inner_space, 1), change_submits=True), sg.FolderBrowse("Browse", size=(button_width, 1), initial_folder=self.source_dir, target="source_path", auto_size_button=False)],
            [sg.Text('Target Folder', size=(first_column_width, 1)), sg.InputText(default_text=self.target_dir, key="target_path", do_not_clear=True, size=(third_column_width - button_width - inner_space, 1), change_submits=True), sg.FolderBrowse("Browse", size=(button_width, 1), initial_folder=self.target_dir, target="target_path", auto_size_button=False)],
            
            # File Operation
            [sg.Text('File Operation', size=(first_column_width, 1)), radio_copy, radio_move],

            # divider
            [sg.Text(' ')],

            # Exclusions
            [sg.Text('Exclusions', font='Arial 14 bold')],
            [sg.Checkbox('Exclude Games with AI', default=self.excludes['AI'], key='ai')],
            [sg.Checkbox('Exclude Custom Games', default=self.excludes['Custom'], key='custom')],

            # divider
            [sg.Text(' ')],

            # Inclusions
            [sg.Text('Inclusions', font='Arial 14 bold')],
            [sg.Text('Minimum Number of Players', size=(first_column_width, 1)), sg.InputText(default_text=self.includes['Min_Players'], key='min_players', size=(third_column_width, 1))],
            [sg.Text('Maximum Number of Players', size=(first_column_width, 1)), sg.InputText(default_text=self.includes['Max_Players'], key='max_players', size=(third_column_width, 1))],
            [sg.Checkbox('WoL', key='WoL', default=self.includes['Expansions']['WoL'])],
            [sg.Checkbox('HotS', key='HotS', default=self.includes['Expansions']['HotS'])],
            [sg.Checkbox('LotV', key='LotV', default=self.includes['Expansions']['LotV'])],

            # divider
            [sg.Text(' ')],

            # Matchups
            [sg.Text('Matchups', font='Arial 14 bold')],
            [sg.Text('Exclude Matchups', size=(first_column_width, 1)), sg.InputText(default_text=self.excludes['Matchups'], size=(third_column_width, 1), key='exclude_matchups')],
            [sg.Text('Include Matchups', size=(first_column_width, 1)), sg.InputText(default_text=self.includes['Matchups'], size=(third_column_width, 1), key='include_matchups')],
        
            # divider
            [sg.Text(' ')],

            # System Tray
            [sg.Checkbox('Run in System Tray', key='tray', default=self.tray)],

            # divider
            [sg.Text(' ')],
            
            # Final Buttons
            [sg.Button('Rename', key='rename'), sg.Exit()]
        ]