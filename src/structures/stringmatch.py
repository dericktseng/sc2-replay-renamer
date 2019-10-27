id_variables = [
    'myteam',
    'myteamwithmmr'
    'oppteams',
    'myraces',
    'oppraces',
    'mymmr',
    'oppmmr',
    'oppwithmmr',
]

non_id_variables = [
    'team1',
    'team2',
    't1races',
    't1withmmr',
    't2races',
    't2withmmr',
    't1mmr',
    't2mmr',
    'wl', # special case, since implementation will be different if an ID is supplied
    'WL', # special case, since implementation will be different if an ID is supplied
    'durationhours',
    'durationmins',
    'durationsecs',
    'month',
    'year',
    'day',
    'hour',
    'min',
    'sec',
    'map',
    'gametype',
    'expansion',
    'currentname',
    'uniqueID'
]

all_variables = id_variables + non_id_variables