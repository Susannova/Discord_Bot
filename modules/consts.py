# used for global variables that cant be used in json(lists, format strings, emoji) or need to be changed (VERSION) in code

EMOJI_ID_LIST = [644252873672359946, 644254018377482255, 644252861827514388, 644252853644296227, 644252146023530506, 644575356908732437]
EMOJI_PASS = '❌'
MESSAGE_CREATE_INTERN_PLAY_REQUEST ='@everyone Das Play-Request von {0} hat 6 oder mehr Mitspieler. Ein **__internes Match__** wird aufgebaut!\n Es sind noch **__{1}__** Plätze frei. \n Uhrzeit: {2} Uhr \n Spieler:\n {3}\n'
MESSAGE_AUTO_DM_CREATOR = '{0} hat auf dein Play-Request reagiert: {1} '
MESSAGE_AUTO_DM_SUBSCRIBER ='{0} hat auch auf das Play-Request von {2} reagiert: {1} '

VERSION = ""

COMMAND_LIST_INTERN_PLANING = ["?create-team", "?play-internal"]
COMMAND_LIST_PLAY_REQUEST = ["?play-lol", "?play-now"]

PATTERN_LIST_AUTO_REACT = [" will League of Legends spielen. Kommt gegen ", "hat 6 oder mehr Mitspieler. Ein **__internes Match__** wird aufgebaut!", " spielt **__jetzt gerade__** League of Legends und sucht noch nach weiteren Spielern!"]


COMMAND_CREATE_TEAM = 'create-team'
COMMAND_PLAY_LOL = '?play-lol'

CHANNEL_CREATE_TEAM_VOICE = 'InHouse Planing'
CHANNEL_INTERN_PLANING = 'intern-planing'
CHANNEL_PLAY_REQUESTS = 'play-requests'
CHANNEL_BOT = 'bot'

BOT_DYNO_NAME = 'Dyno'

TIMER_NOTIFY_ON_REACT_PURGE = 15.0,
TIMER_LAST_PLAY_REQUEST_DELETE = 86400.0

MESSAGE_TEAM_HEADER = '\n@here\n**__===Teams===__**\n'
MESSAGE_TEAM_1 = 'Team 1:\n'
MESSAGE_TEAM_2 = '\nTeam 2:\n'

ROLE_SETZLING_ID = 643169161236840449
ROLE_EVERYONE_ID =564481310417092629

FOLDER_CHAMP_ICON = './data/champ-icon/'
FOLDER_CHAMP_SPLICED = './data/champ-spliced/'