import json
import urllib.request
import statistics
import shelve
from concurrent.futures import ThreadPoolExecutor
from urllib.error import HTTPError
import logging
import requests
import time

from riotwatcher import LolWatcher as RiotWatcher

from core import (
    exceptions,
    timers
)

from core.state import (
    GuildState,
    GeneralState
)

from core.config import(
    GeneralConfig,
    GuildConfig
)


from .summoner import Summoner

def load_json(file_name, folder='config'):
    with open(f'./{folder}/{file_name}.json', encoding="utf8") as all_data:
        return json.load(all_data)


logger = logging.getLogger(__name__)
data_champ = load_json("champion")


def get_champion_name_by_id(champ_id):
    for value in data_champ['data'].values():
        if int(value["key"]) == champ_id:
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


def format_summoner_name(name):
    if name.find('%20') > 0:
        return name.replace('%20', ' ')
    return name

def get_current_patch_url(guild_config: GuildConfig):
    current_patch_list = get_current_patch().split('.')
    return guild_config.messages.patch_notes.format(current_patch_list[0], current_patch_list[1])


def get_current_patch():
    with urllib.request.urlopen("https://ddragon.leagueoflegends.com/api/versions.json") as url:
        data = json.loads(url.read().decode())
        return data[0]

def update_current_patch(state: GeneralState):
    current_patch_list = get_current_patch().split('.')
    current_patch = current_patch_list[0] + '.' + current_patch_list[1]
    if state.lol_patch == current_patch:
        return False
    else:
        state.lol_patch = current_patch
        return True


def update_champion_json():
    patch = get_current_patch()
    with urllib.request.urlopen(f'https://ddragon.leagueoflegends.com/cdn/{patch}/data/en_US/champion.json') as url:
        data = json.loads(url.read().decode())
        with open('./config/champion.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)



def get_average_rank(ranks):
    tmp = 0
    for rank in ranks:
        tmp += rank
    return tmp / len(ranks)

def read_account(discord_user_name, general_config: GeneralConfig, guild_id: int):
    folder_name = general_config.database_directory_summoners.format(guild_id=guild_id)
    with shelve.open(f'{folder_name}/{general_config.folders_and_files.database_name_summoners}', 'r') as database:
        for key in database.keys():
            if key == str(discord_user_name):
                return database[key]
    raise exceptions.DataBaseException('No lol account linked to this discord account')


def read_all_accounts(general_config: GeneralConfig, guild_id: int):
    folder_name = general_config.database_directory_summoners.format(guild_id=guild_id)
    # TODO I think my database in cogs.task is better. And this fails, if the file does not exists
    with shelve.open(f'{folder_name}/{general_config.database_name_summoners}', 'r') as database:
        for key in database.keys():
            yield database[key]


def create_summoners(summoner_names: list, config: GeneralConfig):
    riot_token = str(config.riot_token)
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
    riot_token = str()
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


def fetch_summoner(player, watcher, config: GuildConfig):
    region = config.unsorted_config.riot_region
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


def get_upcoming_clash_dates(config: GeneralConfig, state: GeneralState):
    riot_token = config.riot_token
    clash_url = f'https://euw1.api.riotgames.com/lol/clash/v1/tournaments?api_key={riot_token}'
    clash_json = json.loads(requests.get(clash_url).text)
    clash_dates = []
    for clash in clash_json:
        tmp_clash_date = time.strftime('%d-%m-%Y', time.localtime(clash['schedule'][0]['registrationTime']/1000))
        if tmp_clash_date not in state.clash_dates:
            clash_dates.append(tmp_clash_date)
    return clash_dates