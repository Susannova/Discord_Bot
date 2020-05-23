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


MESSAGE_PATCH_NOTES = "https://euw.leagueoflegends.com/en-us/news/game-updates/patch-{0}-{1}-notes/"


PATTERN_LIST_AUTO_REACT = [" spielen. Kommt gegen ",
 "hat 6 oder mehr Mitspieler. Ein **__internes Match__** wird aufgebaut!",
  " und sucht noch nach weiteren Spielern!",
  " sucht nach Mitspielern für den Clash am "]





CHANNEL_CREATE_TEAM_VOICE_ID = None
CHANNEL_PLAY_REQUESTS_ID = None
CHANNEL_BOT_ID = None
CHANNEL_MEMBER_ONLY_ID = None
CHANNEL_COMMANDS_MEMBER_ID = None
CHANNEL_COMMANDS_ID = None
CHANNEL_CATEGORY_TEMPORARY_ID = None

ROLE_SETZLING_ID = None
ROLE_EVERYONE_ID = None
ROLE_ADMIN_ID = None
ROLE_APEX_ID = None
ROLE_CSGO_ID = None
ROLE_LOL_ID = None
ROLE_RL_ID = None
ROLE_VAL_ID = None
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

GAME_NAME_DICT = {
    "LOL" : "League of Legends",
    "APEX" : "Apex",
    "CSGO" : "CS:GO",
    "RL" : "Rocket League",
    "VAL" : "Valorant"
}

PLAY_NOW_TIME_ADD_LIMIT = 120

#                   LOL,                CSGO,               VAL,                RL,                 APEX                
CATEGORY_IDS = [696776011848613958, 696776901779521536, 696776627786481674, 696776150613098577, 696777095719682073]