import json
import urllib.request
import statistics
import shelve
from concurrent.futures import ThreadPoolExecutor
from urllib.error import HTTPError
import logging
import requests
import time

from riotwatcher import RiotWatcher

from core import consts, exceptions, timers
from .summoner import Summoner
from core.state import global_state as gstate

def load_json(file_name, folder='config'):
    with open(f'./{folder}/{file_name}.json', encoding="utf8") as all_data:
        return json.load(all_data)


logger = logging.getLogger('riot_utility')
tokens = load_json("bot")
data_champ = load_json("champion")


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


def format_last_time_played(_time):
    return _time.strftime('%d-%m-%Y')


def generate_summoner_names(players):
    for player in players:
        if player.find('%') > 0:
            player = player.replace('%', '%20')
        yield player


def format_summoner_name(name):
    if name.find('%20') > 0:
        return name.replace('%20', ' ')
    return name

def get_current_patch_url():
    current_patch_list = get_current_patch().split('.')
    return consts.MESSAGE_PATCH_NOTES.format(current_patch_list[0], current_patch_list[1])


def get_current_patch():
  with urllib.request.urlopen("https://ddragon.leagueoflegends.com/api/versions.json") as url:
    data = json.loads(url.read().decode())
    return data[0]

def update_current_patch():
    current_patch_list = get_current_patch().split('.')
    current_patch = current_patch_list[0] + '.' + current_patch_list[1]
    if gstate.CONFIG['LOL_PATCH'] == current_patch:
        return False
    gstate.CONFIG['LOL_PATCH'] = current_patch
    gstate.write_and_reload_config(gstate.CONFIG)
    return True


def update_champion_json():
    patch = get_current_patch()
    with urllib.request.urlopen(f'https://ddragon.leagueoflegends.com/cdn/{patch}/data/en_US/champion.json') as url:
        data = json.loads(url.read().decode())
        with open('./config/champion.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)


def is_command_on_cooldown(timer_list):
    timers.remove_finished_timers(timer_list)
    if len(timer_list) != 0:
        return True
    timer_list.append(timers.start_timer(secs=5))
    return False


def get_median_rank(ranks):
    return statistics.median(ranks)

def get_average_rank(ranks):
    tmp = 0
    for rank in ranks:
        tmp += rank
    return tmp / len(ranks)

def read_account(discord_user_name):
    with shelve.open(f'{consts.DATABASE_DIRECTORY}/{consts.DATABASE_NAME}', 'r') as database:
        for key in database.keys():
            if key == str(discord_user_name):
                return database[key]
    raise exceptions.DataBaseException('No lol account linked to this discord account')


def read_all_accounts():
    with shelve.open(f'{consts.DATABASE_DIRECTORY}/{consts.DATABASE_NAME}', 'r') as database:
        for key in database.keys():
            yield database[key]


def create_summoners(summoner_names: list):
    riot_token = str(tokens["riot_token"])
    watcher = RiotWatcher(riot_token)
    for player in summoner_names:
        with ThreadPoolExecutor() as executor:
            future = executor.submit(fetch_summoner, player, watcher)
            data = future.result()
            yield Summoner(
                player,
                data_summoner=data[0],
                data_mastery=data[1],
                data_league=data[2]
            )


def create_summoner(summoner_name: str):
    riot_token = str(tokens["riot_token"])
    watcher = RiotWatcher(riot_token)
    with ThreadPoolExecutor() as executor:
        future = executor.submit(fetch_summoner, summoner_name, watcher)
        data = future.result()
        return Summoner(
            summoner_name,
            data_summoner=data[0],
            data_mastery=data[1],
            data_league=data[2]
            )


def fetch_summoner(player, watcher):
    region = consts.RIOT_REGION
    try:
        data_summoner = watcher.summoner.by_name(region, player)
        data_mastery = watcher.champion_mastery.by_summoner(region, data_summoner['id'])
        data_league_unformated = watcher.league.by_summoner(region, data_summoner['id'])
    except HTTPError as e:
        print(e)
    
    data_league = {}
    for queue_data in data_league_unformated:
        data_league[queue_data['queueType']] = queue_data

    return [data_summoner, data_mastery, data_league]


def is_in_need_of_update(summoner):
    if timers.is_timer_done(summoner.needs_update_timer):
        return True
    return False


def get_upcoming_clash_dates():
    riot_token = str(tokens['riot_token'])
    clash_url = f'https://euw1.api.riotgames.com/lol/clash/v1/tournaments?api_key={riot_token}'
    clash_json = json.loads(requests.get(clash_url).text)
    clash_dates = []
    for clash in clash_json:
        tmp_clash_date = time.strftime('%d-%m-%Y', time.localtime(clash['schedule'][0]['registrationTime']/1000))
        if tmp_clash_date not in gstate.clash_dates:
            clash_dates.append(tmp_clash_date)
    return clash_dates