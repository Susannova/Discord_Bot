# === IMPORTS === #
import json
import time
from datetime import datetime, timedelta, date
from riotwatcher import RiotWatcher, ApiError
from collections import OrderedDict
# === IMPORTS END === #

# === INIT === #
def load_json(file_name):
    with open(f'./config/{file_name}.json',  encoding="utf8") as all_data:
        return json.load(all_data)

players = []
data_champ = load_json("champion")
dict_rank = load_json("rank")
# === INIT END === #

# === PLAYER LIST MANAGEMENT === #
def populate_player(player, data_mastery, data_summoner, data_league):
    players.append({"name":     player,
                    "mastery":  data_mastery,
                    "summoner": data_summoner,
                    "league":   data_league})


def updatePlayer(player, data_set_name, data):
    for _player in players:
        if _player["name"] == player:
            _player[data_set_name] = data

def removePlayer(player):
    for _player in players:
        if _player["name"] == player:
            players.remove(_player)

def removeAllPlayers():
    players = []
# === PLAYER LIST MANAGEMENT END === #

# === DATA TRANSFORMATION === #
def get_most_played_champs(idx, count):
    i = 0
    while i < count:
        yield get_champion_name_by_id(players[idx]["mastery"][i]['championId'])
        i += 1

def get_last_time_played_by_id(idx, id):
     for value in players[idx]["mastery"]:
        if value['championId'] == id:
            timestamp = int(str(value['lastPlayTime'])[:-3])
            
            return datetime.fromtimestamp(timestamp)

def get_last_time_played_by_name(idx, name):
    id = int(get_champion_id_by_name(name))
    for value in players[idx]["mastery"]:
        if value['championId'] == id:
            timestamp = int(str(value['lastPlayTime'])[:-3])
            return datetime.fromtimestamp(timestamp)

def has_played_champ_by_name_in_last_n_days(idx, name, n):
    return get_last_time_played_by_name(idx,name) > datetime.now() - timedelta(days=n)

def get_best_ban(idx):
    ban_list = []
    most_played_champs = list(get_most_played_champs(idx, 10))
    for champ in most_played_champs:
        if has_played_champ_by_name_in_last_n_days(idx, champ, 30):
            ban_list.append(champ)
        if len(ban_list) == 5:
            return ban_list
    return ban_list

def get_best_bans_for_team():
    ban_list = []
    for i in range(0,len(players)):
        _, rank = get_soloq_data(i)
        ban_list += get_best_ban(i)[:-4]
    return list(OrderedDict.fromkeys(ban_list))

def get_level(idx):
    return int(players[idx]["summoner"]['summonerLevel'])

def isSmurf(idx):
    winrate, rank = get_soloq_data(idx)
    if get_level(idx) < 40 and winrate >= 58 and get_soloq_rank_weight(rank) < 7:
        return True
    else:
        return False

def get_soloq_data(idx):
    for queue in players[idx]["league"]:
        if queue['queueType'] == 'RANKED_SOLO_5x5':
            soloq_stats = queue
            games_played = int(soloq_stats['wins']) + int(soloq_stats['losses'])
            winrate = round((int(soloq_stats['wins'])/ games_played) *100,1)
            return winrate, '{}-{}'.format(soloq_stats['tier'], soloq_stats['rank'])
    return 'no rank found'    

def get_soloq_rank_weight(rank):
    return dict_rank[rank]
# === DATA TRANSFORMATION END === #

# === UTILITY FUNCTIONS === #
def get_champion_name_by_id(id):
    for value in data_champ['data'].values():
            if int(value["key"]) == id:
               return value['id']

def get_champion_id_by_name(name):
    for value in data_champ['data'].values():
            if value["id"] == name:
               return int(value['key'])

def pretty_print_list(_list):
    output = ''
    for value in _list:
        output += value + ', '
    return output[:-2]

def format_last_time_played(time):
    return time.strftime('%d-%m-%Y')
# === UTILITY FUNCTIONS END === #

# === TESTS === #
def populate_with_debug_data():
    with open('./debug/riot-json/champ_mastery.json',  encoding="utf8") as all_data:
        data_mastery = json.load(all_data)
    with open('./debug/riot-json/summoner.json',  encoding="utf8") as all_data:
        data_summoner = json.load(all_data)
    with open('./debug/riot-json/league.json',  encoding="utf8") as all_data:
        data_league = json.load(all_data)

    populate_player("Thyanin", data_mastery, data_summoner, data_league)
    populate_player("Thya", data_mastery, data_summoner, data_league)

def testModule():
    populate_with_debug_data()
    assert(len(players) == 2)
    removePlayer("Thya")
    assert(len(players) == 1)
    assert(get_champion_id_by_name("Pyke") == 555)
    assert(get_champion_name_by_id(555) == "Pyke")
    assert(list(get_most_played_champs(0, 2)) == ['Pyke', 'Blitzcrank'])
    assert(format_last_time_played(get_last_time_played_by_id(0, 555)) == "20-11-2019")
    assert(format_last_time_played(get_last_time_played_by_name(0, "Pyke")) == "20-11-2019")
    assert(has_played_champ_by_name_in_last_n_days(0, "Pyke",30) == True)
    winrate, rank = get_soloq_data(0)
    assert(winrate == 52.8)
    assert(rank == 'DIAMOND-IV')
    assert(get_soloq_rank_weight(rank) == 7)
    assert(isSmurf(0) == False)
    assert(get_level(0)== 119)
    assert(get_best_ban(0) == ['Pyke', 'Blitzcrank', 'Caitlyn', 'Zoe', 'Kaisa'])
    populate_with_debug_data()
    assert(get_best_bans_for_team() == ['Pyke'])


#testModule()
# === TESTS END === #


