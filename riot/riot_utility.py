import json
import logging
import shelve
import time
import requests
import urllib.request
from urllib.error import HTTPError

from core import exceptions, timers
from core.config import GeneralConfig, GuildConfig
from core.state import GeneralState

logger = logging.getLogger(__name__)


def load_json(file_name, folder="config"):
    with open(f"./{folder}/{file_name}.json", encoding="utf8") as all_data:
        return json.load(all_data)


def update_champion_json():
    patch = get_current_patch()
    with urllib.request.urlopen(f"https://ddragon.leagueoflegends.com/cdn/{patch}/data/en_US/champion.json") as url:
        data = json.loads(url.read().decode())
        with open("./config/champion.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)


def get_champion_name_by_id(champ_id):
    update_champion_json()
    data_champ = load_json("champion")
    for value in data_champ["data"].values():
        if int(value["key"]) == champ_id:
            return value["id"]


def get_champion_id_by_name(name):
    update_champion_json()
    data_champ = load_json("champion")
    for value in data_champ["data"].values():
        if value["id"] == name:
            return int(value["key"])


def pretty_print_list(_list):
    output = ""
    for value in _list:
        output += value + ", "
    return output[:-2]


def format_last_time_played(_time):
    return _time.strftime("%d-%m-%Y")


def format_summoner_name(name):
    if name.find("%20") > 0:
        return name.replace("%20", " ")
    return name


def get_current_patch_url(guild_config: GuildConfig):
    current_patch_list = get_current_patch().split(".")
    return guild_config.messages.patch_notes.format(current_patch_list[0], current_patch_list[1])


def get_current_patch() -> str:
    return requests.get("https://ddragon.leagueoflegends.com/api/versions.json").json()[0]


def update_current_patch(state: GeneralState) -> bool:
    """
    Check if the LoL version is equal to `state.lol_patch`.

    If not, return `True` and sets `state.lol_patch` to current patch.
    If `state.lol_patch` is `None`, sets `state.lol_patch` to current patch and return `False`.
    Also save the `GeneralState` to a file if an update was needed.
    """
    current_patch = get_current_patch()
    if state.lol_patch is None:
        state.lol_patch = current_patch
        return False
    elif state.lol_patch == current_patch:
        return False
    else:
        state.lol_patch = current_patch
        state.write_state_to_file()
        return True


def get_average_rank(ranks):
    tmp = 0
    for rank in ranks:
        tmp += rank
    return tmp / len(ranks)


def read_account(discord_user_name, general_config: GeneralConfig, guild_id: int):
    folder_name = general_config.database_directory_summoners.format(guild_id=guild_id)
    with shelve.open(f"{folder_name}/{general_config.database_name_summoners}", "r") as database:
        for key in database.keys():
            if key == str(discord_user_name):
                return database[key]
    raise exceptions.DataBaseException("No lol account linked to this discord account")


def read_all_accounts(general_config: GeneralConfig, guild_id: int):
    dir_name = general_config.database_directory_summoners.format(guild_id=guild_id)
    # TODO I think my database in cogs.task is better. And this fails, if the file does not exists
    with shelve.open(f"{dir_name}/{general_config.database_name_summoners}", "r") as database:
        for key in database.keys():
            yield database[key]


def fetch_summoner(player, watcher, config: GuildConfig):
    region = config.unsorted_config.riot_region
    try:
        data_summoner = watcher.summoner.by_name(region, player)
        data_mastery = watcher.champion_mastery.by_summoner(region, data_summoner["id"])
        data_league_unformated = watcher.league.by_summoner(region, data_summoner["id"])
    except HTTPError as e:
        print(e)

    data_league = {}
    for queue_data in data_league_unformated:
        data_league[queue_data["queueType"]] = queue_data

    return [data_summoner, data_mastery, data_league]


def is_in_need_of_update(summoner):
    if timers.is_timer_done(summoner.needs_update_timer):
        return True
    return False


def get_upcoming_clash_dates(config: GeneralConfig, state: GeneralState):
    riot_token = config.riot_token
    clash_url = f"https://euw1.api.riotgames.com/lol/clash/v1/tournaments?api_key={riot_token}"
    clash_json = json.loads(requests.get(clash_url).text)
    clash_dates = []
    for clash in clash_json:
        tmp_clash_date = time.strftime("%d-%m-%Y", time.localtime(clash["schedule"][0]["registrationTime"] / 1000))
        if tmp_clash_date not in state.clash_dates:
            clash_dates.append(tmp_clash_date)
    return clash_dates


def download_champ_icons(LoL_patch: str, config: GeneralConfig):
    logger.info("Download all champ icons")
    champions = requests.get(f"http://ddragon.leagueoflegends.com/cdn/{LoL_patch}/data/en_US/champion.json").json()
    for champ in champions["data"]:
        logger.debug("Download champ icon for %s", champ)
        image = requests.get(f"http://ddragon.leagueoflegends.com/cdn/{LoL_patch}/img/champion/{champ}.png")
        with open(f"{config.folder_champ_icon}{champ}.png", "wb") as file:
            file.write(image.content)
    logger.info("All champ icons were downloaded.")
