"""Module that interacts with the Riot API
and transforms the received data in 
a user readable way.
"""
import json
import sys
import os
from datetime import datetime, timedelta
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
import urllib.request
import statistics
import shelve
import discord

from riotwatcher import RiotWatcher

from . import image_transformation, timers, consts, exceptions
from .state import Singleton

SEASON_2020_START_EPOCH = timers.convert_human_to_epoch_time(consts.RIOT_SEASON_2020_START)



# === INIT === #
def load_json(file_name, folder='config'):
    with open(f'./{folder}/{file_name}.json',  encoding="utf8") as all_data:
        return json.load(all_data)

data_champ = load_json("champion")
dict_rank = load_json("rank")
bot = load_json("bot")
_timers = []
# === INIT END === #


# === PLAYER LIST MANAGEMENT === #

class Summoner():
    def __init__(self, name, data_summoner={}, data_mastery=[], data_league=[]):
        self.name = name
        self.data_summoner = data_summoner
        self.data_mastery = data_mastery
        self.data_league = data_league

class SummonerManager(Singleton):
    players = []

    def populate_player(self, summoner):
        self.players.append(summoner)

    def update_player(self, player_name, data_set_name, data):
        [setattr(player, data_set_name, data) for player in self.players if player.name == player_name]

    def remove_player(self, player):
        for _player in self.players:
            if _player.name == player:
                self.players.remove(_player)

    def remove_all_players(self):
        self.players = []

summoner_manager = SummonerManager()

def create_summoners(summoner_names):
    riot_token = str(bot["riot_token"])
    watcher = RiotWatcher(riot_token)
    for player in summoner_names:
        with ThreadPoolExecutor() as executor:
            future = executor.submit(fetch_summoner, player, watcher)
            data = future.result()
            yield Summoner(
                player,
                data[0],
                data[1],
                data[2]
                )


def add_player_and_data(summoner_names):
    [summoner_manager.populate_player(summoner) for summoner in create_summoners(summoner_names)]


def fetch_summoner(player, watcher):
    region = consts.RIOT_REGION
    data_summoner = watcher.summoner.by_name(region, player)
    data_league = watcher.league.by_summoner(region, data_summoner['id'])
    data_mastery = watcher.champion_mastery.by_summoner(
        region, data_summoner['id'])
    return [data_summoner, data_mastery, data_league]

# === PLAYER LIST MANAGEMENT END === #

# === DATA TRANSFORMATION === #
def get_most_played_champs(idx, count):
    i = 0
    while i < count:
        yield get_champion_name_by_id(summoner_manager.players[idx].data_mastery[i]['championId'])
        i += 1

def get_last_time_played_by_id(idx, id):
    for value in summoner_manager.players[idx].data_mastery:
        if value['championId'] == id:
            timestamp = int(str(value['lastPlayTime'])[:-3])
            return datetime.fromtimestamp(timestamp)

def get_last_time_played_by_name(idx, name):
    id = int(get_champion_id_by_name(name))
    for value in summoner_manager.players[idx].data_mastery:
        if value['championId'] == id:
            timestamp = int(str(value['lastPlayTime'])[:-3])
            return datetime.fromtimestamp(timestamp)

def has_played_champ_by_name_in_last_n_days(idx, name, n):
    return get_last_time_played_by_name(idx, name) \
        > datetime.now() - timedelta(days=n)

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
    ranks = []
    best_bans_for_i = []
    for i in range(0, len(summoner_manager.players)):
        _, rank = get_soloq_data(i)
        ranks.append(get_soloq_rank_weight(rank))
        best_bans_for_i.append(get_best_ban(i))
    median_rank = get_median_rank_for_team(ranks)
    for i in range(0, len(summoner_manager.players)):
        if ranks[i] <= median_rank:
            ban_list.append(best_bans_for_i[0])
        elif ranks[i] >= median_rank + 3:
            ban_list.append(best_bans_for_i[0])
            ban_list.append(best_bans_for_i[1])
            ban_list.append(best_bans_for_i[2])
        elif ranks[i] > median_rank:
            ban_list.append(best_bans_for_i[0])
            ban_list.append(best_bans_for_i[1])
    return list(OrderedDict.fromkeys(ban_list))

def get_median_rank_for_team(ranks):
    statistics.median(ranks)

def get_level(idx):
    return int(summoner_manager.players[idx].data_summoner['summonerLevel'])

def is_smurf(idx):
    winrate, rank = get_soloq_data(idx)
    if get_level(idx) < 40 and winrate >= 58 and get_soloq_rank_weight(rank) < 7:
        return True
    else:
        return False

def get_soloq_data(idx):
    for queue in summoner_manager.players[idx].data_league:
        if queue['queueType'] == 'RANKED_SOLO_5x5':
            soloq_stats = queue
            games_played = int(soloq_stats['wins']) + int(
                soloq_stats['losses'])
            winrate = round((int(soloq_stats['wins']) / games_played) * 100, 1)
            return winrate, '{}-{}'.format(
                soloq_stats['tier'], soloq_stats['rank'])
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

def generate_summoner_names(players):
    for player in players:
        if player.find('%') > 0:
            player = player.replace('%', '%20')
        yield player

def format_summoner_name(name):
    if name.find('%20') > 0:
        return name.replace('%20', ' ')
    return name

def update_champion_json():
    with urllib.request.urlopen("https://ddragon.leagueoflegends.com/api/versions.json") as url:
        data = json.loads(url.read().decode())
        patch = data[0]
    with urllib.request.urlopen(f'https://ddragon.leagueoflegends.com/cdn/{patch}/data/en_US/champion.json') as url:
        data = json.loads(url.read().decode())
        with open('./config/champion.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

def is_command_on_cooldown():
        timers.remove_finished_timers(_timers)
        if len(_timers) != 0:
            return True
        _timers.append(timers.start_timer(secs=5))
        return False



# === UTILITY FUNCTIONS END === #

# === INTERFACE === #

def riot_command(ctx, *args) -> str:
    return_value = None
    update_champion_json()
    summoner_names = list(generate_summoner_names(list(args[0])))
    if len(summoner_names) == 0:
        summoner_manager.populate_player(read_account(ctx.message.author.name))
    else:
        if is_command_on_cooldown():
            return "Please wait a few seconds before using Riot API commands again!"
        add_player_and_data(summoner_names)
    if(str(ctx.command) == 'player'):
        winrate, rank = get_soloq_data(0)
        return_value = 'Rank: {} , Winrate: {}%'.format(rank, winrate)
    elif(str(ctx.command) == 'bans' and len(summoner_names) == 5):
        output = get_best_bans_for_team()
        image_transformation.create_new_image(output)
        op_url = f'https://euw.op.gg/multi/query={summoner_names[0]}%2C{summoner_names[1]}%2C{summoner_names[2]}%2C{summoner_names[3]}%2C{summoner_names[4]}'
        return_value = "Team OP.GG: " + op_url + "\nBest Bans for Team:\n" + pretty_print_list(output)
    elif (str(ctx.command) == 'smurf'):
        is_smurf_word = 'kein'
        if is_smurf(0):
            is_smurf_word = 'ein'
        return_value = f'Der Spieler **{format_summoner_name(summoner_manager.players[0].name)}** ist sehr wahrscheinlich **{is_smurf_word}** Smurf.'
    summoner_manager.remove_all_players()
    return return_value if return_value is not None else 'Something went wrong.'

def link_account(ctx, summoner_name):
    if is_command_on_cooldown():
        raise exceptions.DataBaseException('Command on cooldown')
    discord_user_name = ctx.message.author.name
    summoner_name = list(generate_summoner_names([summoner_name]))[0]
    summoner = list(create_summoners([summoner_name]))[0]
    with shelve.open(f'{consts.DATABASE_DIRECTORY}/{consts.DATABASE_NAME}', 'rc') as database:
        for key in database.keys():
            if key == str(discord_user_name):
                raise exceptions.DataBaseException('Your discord account already has a lol account linked to it')
            if database[key] is not None:
                if database[key].name == summoner.name:
                    raise exceptions.DataBaseException('This lol account already has a discord account linked to it')
        database[str(discord_user_name)] = summoner
     
def read_account(discord_user_name):
    with shelve.open(f'{consts.DATABASE_DIRECTORY}/{consts.DATABASE_NAME}', 'r') as database:
        for key in database.keys():
            if key == str(discord_user_name):
                return database[key][0]
    raise exceptions.DataBaseException('No lol account linked to this discord account')

def read_all_accounts():
    with shelve.open(f'{consts.DATABASE_DIRECTORY}/{consts.DATABASE_NAME}', 'r') as database:
        for key in database.keys():
            yield database[key]

def unlink_account(ctx):
    with shelve.open(f'{consts.DATABASE_DIRECTORY}/{consts.DATABASE_NAME}', 'rc') as database:
        for key in database.keys():
            if key == str(ctx.message.author.id):
                del database[key]

# FIXME this is super trash
# the whole module needs a rewrite honestly
def create_embed(ctx):
    _embed = discord.Embed(title='Kraut9 Leaderboard',
    colour=discord.Color.from_rgb(62,221,22))
    summoners = list(read_all_accounts())
    users = ''
    with shelve.open(f'{consts.DATABASE_DIRECTORY}/{consts.DATABASE_NAME}', 'rc') as database:
        for key in database.keys():
            users += f'{key}\n'

    summoner_names = ''
    for summoner in summoners:
        summoner_names += f'{summoner.name}\n'

    rank_tier_winrate= ''
    for i in range(0,len(summoners)):
        summoner_manager.populate_player(summoner)
        winrate, rank =  get_soloq_data(i)
        rank_tier_winrate += str(rank) + '      ' + str(winrate) + '\n'
    _embed.add_field(name='User', value=users)
    _embed.add_field(name='Summoner', value=summoner_names)
    _embed.add_field(name='Rank               Winrate', value=rank_tier_winrate)
    return _embed

# === INTERFACE END === #

# === TESTS === #
def populate_with_debug_data():
    with open('./debug/riot-json/champ_mastery.json',  encoding="utf8") as all_data:
        data_mastery = json.load(all_data)
    with open('./debug/riot-json/summoner.json',  encoding="utf8") as all_data:
        data_summoner = json.load(all_data)
    with open('./debug/riot-json/league.json',  encoding="utf8") as all_data:
        data_league = json.load(all_data)

    summoner_manager.populate_player("Thyanin", data_mastery, data_summoner, data_league)
    summoner_manager.populate_player("Thya", data_mastery, data_summoner, data_league)

def testModule():
    update_champion_json()
    populate_with_debug_data()
    assert(len(summoner_manager.players) == 2)
    summoner_manager.remove_player("Thya")
    assert(len(summoner_manager.players) == 1)
    assert(get_champion_id_by_name("Pyke") == 555)
    assert(get_champion_name_by_id(555) == "Pyke")
    assert(list(get_most_played_champs(0, 2)) == ['Pyke', 'Blitzcrank'])
    assert(format_last_time_played(get_last_time_played_by_id(0, 555)) == "20-11-2019")
    assert(format_last_time_played(get_last_time_played_by_name(0, "Pyke")) == "20-11-2019")
    assert(has_played_champ_by_name_in_last_n_days(0, "Pyke", 30) == False)
    winrate, rank = get_soloq_data(0)
    assert(winrate == 52.8)
    assert(rank == 'DIAMOND-IV')
    assert(get_soloq_rank_weight(rank) == 7)
    assert(is_smurf(0) == False)
    assert(get_level(0)== 119)
    # assert(get_best_ban(0) == ['Pyke', 'Blitzcrank', 'Azir', 'Caitlyn', 'Zoe'])
    # populate_with_debug_data()
    # assert(get_best_bans_for_team() == ['Pyke'])
    summoner_manager.remove_all_players()
    add_player_and_data(["Susannova"])
    print(get_soloq_data(0))

    summoner_manager.remove_all_players()
    add_player_and_data(["Thyanin"])
    print(get_best_ban(0)[0])

# testModule()
if __name__ == "__main__":
    try:
        testModule()
    except ValueError as identifier:
        print('Wrong Token.')
    
# === TESTS END === #
