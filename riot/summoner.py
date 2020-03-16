from . import timers, riot_utility as utility
from .riot_utility import dict_rank
from datetime import datetime, timedelta


class Summoner():
    """Class representing a League of Legends summoner.
    Contains data retrieved via the Riot API.
    Has several basic methods that make handling the data easier.

    Attributes:
    ---------------
    data_summoner: dict
        json of all basic summononer data from Riot API
    data_mastery: list
        basic mastery data from Riot API
    data_league: list
        basic league data from Riot API
    """
    def __init__(self, name, data_summoner={}, data_mastery=[], data_league=[]):
        self.name = name
        self.data_summoner = data_summoner
        self.data_mastery = data_mastery
        self.data_league = data_league
        self.needs_update_timer = timers.start_timer(hrs=12)

    def __str__(self):
        return f'Summoner: {self.name}, Level: {self.get_level()}, Rank: {self.get_soloq_tier}, Winrate: {self.get_soloq_winrate}'

    def get_level(self):
        return int(self.data_summoner['summonerLevel'])

    def is_smurf(self):
        winrate = self.get_soloq_winrate(self)
        rank = self.get_soloq_tier(self)
        if self.get_level(self) < 40 and winrate >= 58 and self.get_soloq_rank_weight(rank) < 7:
            return True
        else:
            return False

    def get_soloq_data(self):
        for queue_data in self.data_league:
            if queue_data['queueType'] == 'RANKED_SOLO_5x5':
                return queue_data

    def get_soloq_winrate(self):
        soloq_stats = self.get_soloq_data(self)
        games_played = int(soloq_stats['wins']) + int(
            soloq_stats['losses'])
        if games_played != 0 and games_played is not None:
            winrate = round((int(soloq_stats['wins']) / games_played) * 100, 1)
            return winrate
        return 50.0

    def get_soloq_tier(self):
        soloq_stats = self.get_soloq_data(self)
        if soloq_stats['tier'] is not None:
            return soloq_stats['tier']
        return 'SILVER'

    def get_soloq_rank(self):
        soloq_stats = self.get_soloq_data(self)
        if soloq_stats['rank'] is not None:
            return soloq_stats['rank']
        return 'II'

    def get_soloq_lp(self):
        soloq_stats = self.get_soloq_data(self)
        if soloq_stats['leaguePoints'] is not None:
            return soloq_stats['leaguePoints']
        return 0

    def get_soloq_rank_weight(self, rank):
        return dict_rank[rank]

    def get_most_played_champs(self, count):
        i = 0
        while i < count:
            yield utility.get_champion_name_by_id(self.data_mastery[i]['championId'])
            i += 1

    def get_last_time_played_by_id(self, id):
        for value in self.data_mastery:
            if value['championId'] == id:
                timestamp = int(str(value['lastPlayTime'])[:-3])
                return datetime.fromtimestamp(timestamp)

    def get_last_time_played_by_name(self, name):
        id = int(utility.get_champion_id_by_name(name))
        for value in self.data_mastery:
            if value['championId'] == id:
                timestamp = int(str(value['lastPlayTime'])[:-3])
                return datetime.fromtimestamp(timestamp)

    def has_played_champ_by_name_in_last_n_days(self, name, n):
        return self.get_last_time_played_by_name(self, name) \
            > datetime.now() - timedelta(days=n)
