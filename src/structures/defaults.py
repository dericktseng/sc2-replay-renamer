# Constants
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


# default settings
settings = {
    _template: '$myracesv$oppraces $WL $map $myteamwithmmr v $oppwithmmr - $durationminsm$durationsecss [$month-$day-$year $hour_$min_$sec]',
    _source_dir: '',
    _target_dir: '',
    _player_id: '',
    _operation: _copy,
    _excludes: {
        _ai: True,
        _custom: False,
        _exclude_matchups: '',
        _exclude_dirs: ''
    },
    _includes: {
        _include_matchups: '',
        _min_players: "2",
        _max_players: "2",
        _wol: False,
        _hots: False,
        _lotv: True
    },
    _tray: False
}

gui_readable_defaults = {
    _template: settings[_template],
    _source_dir: settings[_source_dir],
    _target_dir: settings[_target_dir],
    _player_id: settings[_player_id],
    _copy: True if settings[_operation] == _copy else False,
    _move: True if settings[_operation] == _move else False,
    _ai: settings[_excludes][_ai],
    _custom: settings[_excludes][_custom],
    _exclude_matchups: settings[_excludes][_exclude_matchups],
    _exclude_dirs: settings[_excludes][_exclude_dirs],
    _include_matchups: settings[_includes][_include_matchups],
    _min_players: settings[_includes][_min_players],
    _max_players: settings[_includes][_max_players],
    _wol: settings[_includes][_wol],
    _hots: settings[_includes][_hots],
    _lotv: settings[_includes][_lotv],
    _tray: settings[_tray]
}