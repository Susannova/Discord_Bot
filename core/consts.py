""" Used for global variables that cant be used in json(lists, format strings, emoji)
and constant strings. Dont change any variables from outside.
"""


EMOJI_ID_LIST = [644252873672359946, 644254018377482255, 644252861827514388, 644252853644296227, 644252146023530506, 644575356908732437]
EMOJI_PASS = '❌'
MESSAGE_CREATE_INTERN_PLAY_REQUEST = '@everyone Das Play-Request von {0} hat 6 oder mehr Mitspieler. Ein **__internes Match__** wird aufgebaut!\nEs sind noch **__{1}__** Plätze frei. \nUhrzeit: {2} Uhr \nSpieler:\n'
MESSAGE_AUTO_DM_CREATOR = '{0} hat auf dein Play-Request reagiert: {1} '
MESSAGE_AUTO_DM_SUBSCRIBER = '{0} hat auch auf das Play-Request von {1} reagiert: {2} '
MESSAGE_PLAY_NOW = '@everyone\n{0} spielt **__jetzt gerade__** League of Legends und sucht noch nach weiteren Spielern!'
MESSAGE_PLAY_LOL = '@everyone\n{0} will League of Legends spielen. Kommt gegen **__{1}__** Uhr online!'
MESSAGE_PLAY_REQUEST_REMINDER = 'REMINDER: Der abonnierte Play-Request geht in 5 Minuten los!'
MESSAGE_TEAM_HEADER = '\n@here\n**__===Teams===__**\n'
MESSAGE_TEAM_1 = 'Team 1:\n'
MESSAGE_TEAM_2 = '\nTeam 2:\n'
MESSAGE_SERVER_WELCOME = ( 
    'Hallo {0} und herzlich willkommen auf dem Discord Server von Kraut9!\n \
    Hier ist eine kleine Erklärung zu unserem Server:\n \
    https://discordapp.com/channels/564481310417092629/647752522764648448/647752549411061791 \
    Viel Spaß auf dem Server von Kraut9!' 
)
MESSAGE_BANS = (
    'If you want to receive the best bans \
    for the scouted team copy the following Command: \n \
    ?bans {0}'
)

COMMAND_LIST_INTERN_PLANING = ["?create-team", "?play-internal"]
COMMAND_LIST_PLAY_REQUEST = ["?play-lol", "?play-now"]
COMMAND_LIST_ALL = ["?create-team", "?play-internal", "?play-lol", "?play-now", "?player", "?bans"]


PATTERN_LIST_AUTO_REACT = [" will League of Legends spielen. Kommt gegen ", "hat 6 oder mehr Mitspieler. Ein **__internes Match__** wird aufgebaut!", " spielt **__jetzt gerade__** League of Legends und sucht noch nach weiteren Spielern!"]
PATTERN_PLAY_REQUEST = " will League of Legends spielen. Kommt gegen "

COMMAND_PREFIX = '!'
COMMAND_CREATE_TEAM = f'{COMMAND_PREFIX}create-team'
COMMAND_PLAY_LOL = f'{COMMAND_PREFIX}play-lol'
COMMAND_PLAY_NOW = f'{COMMAND_PREFIX}play-now'
COMMAND_CLASH = f'{COMMAND_PREFIX}clash'
COMMAND_BANS = f'{COMMAND_PREFIX}bans'
COMMAND_PLAYER = f'{COMMAND_PREFIX}player'
COMMAND_SMURF = f'{COMMAND_PREFIX}smurf'

COMMAND_LIST_RIOT = [COMMAND_PLAYER, COMMAND_SMURF]

CHANNEL_CREATE_TEAM_VOICE = 'InHouse Planing'
CHANNEL_INTERN_PLANING = 'intern-planing'
CHANNEL_PLAY_REQUESTS = 'play-requests'
CHANNEL_BOT = 'bot'
CHANNEL_MEMBER_ONLY = 'member-only'

BOT_DYNO_NAME = 'Dyno'

TIMER_NOTIFY_ON_REACT_PURGE = 15.0
TIMER_LAST_PLAY_REQUEST_DELETE = 86400.0


ROLE_SETZLING_ID = 643169161236840449
ROLE_EVERYONE_ID = 564481310417092629

FOLDER_CHAMP_ICON = './data/champ-icon/'
FOLDER_CHAMP_SPLICED = './data/champ-spliced/'
