""" Used for global variables that cant be used in json(lists, format strings, emoji)
and constant strings. Dont change any variables from outside.
"""

COMMAND_PREFIX = '!'
EMOJI_JOIN = '✅'
EMOJI_PASS = '❎'
MESSAGE_CREATE_INTERN_PLAY_REQUEST = '@everyone Das Play-Request von {0} hat 6 oder mehr Mitspieler. Ein **__internes Match__** wird aufgebaut!\nEs sind noch **__{1}__** Plätze frei. \nUhrzeit: {2} Uhr \nSpieler:\n'
MESSAGE_AUTO_DM_CREATOR = '{0} hat auf dein Play-Request reagiert: {1} '
MESSAGE_AUTO_DM_SUBSCRIBER = '{0} hat auch auf das Play-Request von {1} reagiert: {2} '
MESSAGE_PLAY_NOW = '{0}\n{1} spielt **__jetzt gerade__** **{2}** und sucht noch nach weiteren Spielern!'
MESSAGE_PLAY_AT = '{0}\n{1} will **{2}** spielen. Kommt gegen **__{3}__** Uhr online!'
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
    ' + COMMAND_PREFIX + 'bans {0}'
)

MESSAGE_CLASH_CREATE = (
    '{0}\n{1} sucht nach Mitspielern für den LoL Clash am {2}.'
)
MESSAGE_CLASH_FULL = 'Das Clash Team von {0} für den {1} ist jetzt voll. Das Team besteht aus folgenden Mitgliedern:\n{1}'

MESSAGE_PATCH_NOTES_FORMATTED = '{0}\nEin neuer Patch ist da: {1}'
MESSAGE_GAME_SELECTOR = "@everyone\nWähle hier durch das Klicken auf eine Reaktion aus zu welchen Spielen du Benachrichtungen erhalten willst!"

MESSAGE_PLAY_REQUEST_CREATED = '*{0}* hat ein Play-Request für das Spiel **{1}** erstellt. Wenn du interessiert daran bist, klicke hier: <{2}>'

MESSAGE_PATCH_NOTES = "https://oce.leagueoflegends.com/en-us/news/game-updates/patch-{0}-{1}-notes/"



COMMAND_LIST_INTERN_PLANING = ["?create-team", "?play-internal"]
COMMAND_LIST_PLAY_REQUEST = ["?play-lol", "?play-now"]
COMMAND_LIST_ALL = ["?create-team", "?play-internal", "?play-lol", "?play-now", "?player", "?bans"]


PATTERN_LIST_AUTO_REACT = [" spielen. Kommt gegen ",
 "hat 6 oder mehr Mitspieler. Ein **__internes Match__** wird aufgebaut!",
  " und sucht noch nach weiteren Spielern!",
  " sucht nach Mitspielern für den Clash am "]

PATTERN_PLAY_REQUEST = " spielen. Kommt gegen "
PATTERN_CLASH = " sucht nach Mitspielern für den Clash am "


COMMAND_CREATE_TEAM = f'{COMMAND_PREFIX}create-team'
COMMAND_PLAY_LOL = f'{COMMAND_PREFIX}play-lol'
COMMAND_PLAY_NOW = f'{COMMAND_PREFIX}play-now'
COMMAND_CLASH = f'{COMMAND_PREFIX}clash'
COMMAND_BANS = f'{COMMAND_PREFIX}bans'
COMMAND_PLAYER = f'{COMMAND_PREFIX}player'
COMMAND_SMURF = f'{COMMAND_PREFIX}smurf'

COMMAND_LIST_RIOT = [COMMAND_PLAYER, COMMAND_SMURF]

CHANNEL_CREATE_TEAM_VOICE_ID = 564481311432245265
CHANNEL_PLAY_REQUESTS = 'play-requests'
CHANNEL_BOT = 'bot'
CHANNEL_MEMBER_ONLY = 'member-only'
CHANNEL_COMMANDS_MEMBER = 'kraut-commands'
CHANNEL_COMMANDS = 'commands'
CHANNEL_CLASH = 'clash'
CHANNEL_CATEGORY_TEMPORARY = 'TEMPORARY-CHANNELS'
BOT_DYNO_NAME = 'Dyno'

TIMER_NOTIFY_ON_REACT_PURGE = 15.0
TIMER_LAST_PLAY_REQUEST_DELETE = 86400.0


ROLE_SETZLING_ID = 643169161236840449
ROLE_EVERYONE_ID = 564481310417092629
ROLE_ADMIN_ID = 564492616977088532
ROLE_APEX_ID = 693817368937496596
ROLE_CSGO_ID = 693817437623418911
ROLE_LOL_ID = 693817391330623508
ROLE_RL_ID = 693817406883233822
ROLE_VAL_ID = 694873734040780810
FOLDER_CHAMP_ICON = './data/champ-icon/'
FOLDER_CHAMP_SPLICED = './data/champ-spliced/'

GAME_NAME_TO_ROLE_ID_DICT = {
    "LOL" : ROLE_LOL_ID,
    "APEX" : ROLE_APEX_ID,
    "CSGO" : ROLE_CSGO_ID,
    "RL" : ROLE_RL_ID,
    "VAL" : ROLE_VAL_ID
}

# source: https://na.leagueoflegends.com/en-us/news/game-updates/patch-10-1-notes/
RIOT_SEASON_2020_START = '10.01.2020'
RIOT_REGION = 'euw1'

DATABASE_DIRECTORY = './db/summoners'
DATABASE_NAME = 'summoner_db'

DATABASE_DIRECTORY_GLOBAL_STATE = './db/global_state'
DATABASE_NAME_GLOBAL_STATE = 'global_state_db'

LOG_FILE = './log/log'
LOG_NAME = 'kraut.log'

GAME_NAME_DICT = {
    "LOL" : "League of Legends",
    "APEX" : "Apex",
    "CSGO" : "CS:GO",
    "RL" : "Rocket League",
    "VAL" : "Valorant"
}

GAME_SELECTOR_MESSAGE_ID = 693832367521005617
PLAY_NOW_TIME_ADD_LIMIT = 120

#                   LOL,                CSGO,               VAL,                RL,                 APEX                
CATEGORY_IDS = [696776011848613958, 696776901779521536, 696776627786481674, 696776150613098577, 696777095719682073]