# === IMPORTS === #
import json
import time
from datetime import datetime, timedelta, date
from riotwatcher import RiotWatcher, ApiError
from collections import OrderedDict
import image_transformation
import timers
from concurrent.futures import ThreadPoolExecutor
import urllib.request
# === IMPORTS END === #

# === INIT === #
def load_json(file_name):
    with open(f'./config/{file_name}.json',  encoding="utf8") as all_data:
        return json.load(all_data)

players = []
data_champ = load_json("champion")
dict_rank = load_json("rank")
bot = load_json("bot")
_timers = []
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
    global players
    players = []

def add_player_and_data(summoner_names):
    riot_token = str(bot["riot_token"])
    watcher = RiotWatcher(riot_token)
    for player in summoner_names:
        with ThreadPoolExecutor() as executor:
            future = executor.submit(fetch_summoner, player, watcher)
            populate_player(player, future.result()[0], future.result()[1], future.result()[2])

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
        ban_list.append(get_best_ban(i)[0])
    return list(OrderedDict.fromkeys(ban_list))

def get_level(idx):
    return int(players[idx]["summoner"]['summonerLevel'])

def is_smurf(idx):
    winrate, rank = get_soloq_data(idx)
    print(get_level(idx))
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
    # if player is not ranked return default value
    return 50.0, 'SILVER-II'

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


def fetch_summoner(player, watcher):
       my_region = 'euw1'
       data_summoner = watcher.summoner.by_name(my_region, player)
       data_league = watcher.league.by_summoner(my_region, data_summoner['id'])
       data_mastery = watcher.champion_mastery.by_summoner(my_region, data_summoner['id'])
       return [data_mastery, data_summoner, data_league]     

def get_summoner_name_list(message):
    player_names = []
    for player in message.content.split(' ')[1:]:
        if player.find('%') > 0:
            player = player.replace('%', '%20')
        player_names.append(player)
    return player_names

def format_summoner_name(name):
    if name.find('%20') > 0:
            return name.replace('%20', ' ')
    return name
  
def update_champion_json():
    patch = ''
    with urllib.request.urlopen("https://ddragon.leagueoflegends.com/api/versions.json") as url:
        data = json.loads(url.read().decode())
        patch = data[0]
    with urllib.request.urlopen(f'https://ddragon.leagueoflegends.com/cdn/{patch}/data/en_US/champion.json') as url:
        data = json.loads(url.read().decode())
        with open('./config/champion.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)


# === UTILITY FUNCTIONS END === #

# === INTERFACE === #

def riot_command(message):
    update_champion_json()
    timers.remove_finished_timers(_timers)
    if len(_timers) != 0:
        return "Please wait a few seconds before using Riot API commands again!"

    _timers.append(timers.start_timer(secs=5))
    summoner_names = get_summoner_name_list(message)
    add_player_and_data(summoner_names)
    return_value = ''
    if(message.content.split(' ')[0] == "?player"):
        winrate, rank = get_soloq_data(0)
        return_value = 'Rank: {} , Winrate: {}%'.format(rank , winrate)
    elif(message.content.split(' ')[0] == "?bans"):
        output = get_best_bans_for_team()
        image_transformation.create_new_image(output)
        op_url = f'https://euw.op.gg/multi/query={summoner_names[0]}%2C{summoner_names[1]}%2C{summoner_names[2]}%2C{summoner_names[3]}%2C{summoner_names[4]}'
        return_value = "Team OP.GG: " + op_url + "\nBest Bans for Team:\n" + pretty_print_list(output) 
    elif (message.content.split(' ')[0] == "?smurf"):
        is_smurf_word = 'kein'
        if is_smurf(0):
            is_smurf_word = 'ein'
        return_value = f'Der Spieler **{format_summoner_name(summoner_names[0])}** ist sehr wahrscheinlich **{is_smurf_word}** Smurf.'
    removeAllPlayers()
    return return_value
    

# === INTERFACE END === #

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
    assert(has_played_champ_by_name_in_last_n_days(0, "Pyke",30) == False)
    winrate, rank = get_soloq_data(0)
    assert(winrate == 52.8)
    assert(rank == 'DIAMOND-IV')
    assert(get_soloq_rank_weight(rank) == 7)
    # assert(is_smurf(0) == False)
    # assert(get_level(0)== 119)
    # assert(get_best_ban(0) == ['Pyke', 'Blitzcrank', 'Azir', 'Caitlyn', 'Zoe'])
    # populate_with_debug_data()
    # assert(get_best_bans_for_team() == ['Pyke'])
    removeAllPlayers()  
    add_player_and_data(["Susannova"])
    print(get_soloq_data(0))

    removeAllPlayers()
    add_player_and_data(["Thyanin"])
    print(get_best_ban(0)[0])

#testModule()
# === TESTS END === #