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
        'Exclude_Matchups': '',
        'Exclude_Dirs': ''
    },
    'includes': {
        'Include_Matchups': 'XvX',
        'Min_Players': "2",
        'Max_Players': "2",
        'WoL': False,
        'HotS': False,
        'LotV': True
    },
    'tray': False
}

gui_readable_defaults = {
    'template': settings['template'],
    'source_dir': settings['source_dir'],
    'target_dir': settings['target_dir'],
    'player_id': settings['player_id'],
    'copy': True if settings['operation'] == 'copy' else False,
    'move': True if settings['operation'] == 'move' else False,
    'AI': settings['excludes']['AI'],
    'Custom': settings['excludes']['Custom'],
    'Exclude_Matchups': settings['excludes']['Exclude_Matchups'],
    'Exclude_Dirs': settings['excludes']['Exclude_Dirs'],
    'Include_Matchups': settings['includes']['Include_Matchups'],
    'Min_Players': settings['includes']['Min_Players'],
    'Max_Players': settings['includes']['Max_Players'],
    'WoL': settings['includes']['WoL'],
    'HotS': settings['includes']['HotS'],
    'LotV': settings['includes']['LotV'],
    'tray': settings['tray']
}