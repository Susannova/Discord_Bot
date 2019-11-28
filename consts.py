# used for global variables that cant be used in json(lists, format strings, emoji) or need to be changed (VERSION) in code

EMOJI_ID_LIST = [644252873672359946, 644254018377482255, 644252861827514388, 644252853644296227, 644252146023530506, 644575356908732437]
EMOJI_PASS = '❌'
MESSAGE_CREATE_INTERN_PLAY_REQUEST ='@everyone Das Play-Request von {0} hat 6 oder mehr Mitspieler. Ein **__internes Match__** wird aufgebaut!\n Es sind noch **__{1}__** Plätze frei. \n Uhrzeit: {2} Uhr \n Spieler:\n {3}\n'
MESSAGE_AUTO_DM_CREATOR = '{0} hat auf dein Play-Request reagiert: {1} '
MESSAGE_AUTO_DM_SUBSCRIBER ='{0} hat auch auf das Play-Request von {2} reagiert: {1} '
VERSION = ""

COMMAND_LIST_INTERN_PLANING = ["?create-team", "?play-internal"]
COMMAND_LIST_PLAY_REQUEST = ["?play-lol", "?play-lol-now"]

PATTERN_LIST_AUTO_REACT = [" will League of Legends spielen. Kommt gegen ", "hat 6 oder mehr Mitspieler. Ein **__internes Match__** wird aufgebaut!\n"]