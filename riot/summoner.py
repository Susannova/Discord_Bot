from datetime import datetime, timedelta
import json
import math

from core import timers


def load_json(file_name, folder='config'):
    with open(f'./{folder}/{file_name}.json', encoding="utf8") as all_data:
        return json.load(all_data)


dict_rank = load_json("rank")
data_champ = load_json("champion")


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
    data_league: dict
        formatted basic league data from Riot API
    """
    def __init__(self, name, data_summoner={}, data_mastery=[], data_league={}):
        self.name = name
        self.discord_user_name = 'None'

        self.data_summoner = data_summoner
        self.data_mastery = data_mastery
        self.data_league = data_league

        self.rank_values = {}
        for queue_type in data_league:
            self.rank_values[queue_type] = self.get_rank_value(queue_type)


    def __str__(self):
        return f'Summoner: {self.name}, Level: {self.get_level()}, Rank: {self.get_rank_string()}, Winrate: {self.get_winrate()}'

    def __repr__(self):
        return self.name

    def get_level(self):
        return int(self.data_summoner['summonerLevel'])

    def is_smurf(self):
        winrate = self.get_winrate()
        
        if self.has_played_rankeds() and self.get_level() < 40 and winrate >= 58 and self.rank_values['RANKED_SOLO_5x5'] < 700:
            return True
        else:
            return False

    def has_played_rankeds(self, queue_type='RANKED_SOLO_5x5'):
        # return queue_type in self.data_league #Doesn't work?
        return True if queue_type in self.data_league else False

    def get_winrate(self, queue_type='RANKED_SOLO_5x5'):
        if self.has_played_rankeds(queue_type):
            data = self.data_league[queue_type]
            games_played = int(data['wins']) + int(data['losses'])
            return round((int(data['wins']) / games_played) * 100, 1)
        else:
            return math.nan

    def get_rank_weight(self, rank):
        return dict_rank[rank]

    def get_rank_value(self, queue_type = 'RANKED_SOLO_5x5'):
        if self.has_played_rankeds(queue_type):
            data = self.data_league[queue_type]
            tier_string = data['tier']
            rank_string = data['rank']
            return self.get_rank_weight(tier_string + '-' + rank_string) * 100 + data['leaguePoints']
        else:
            return math.nan

    def get_rank_string(self, queue_type='RANKED_SOLO_5x5'):
        if self.has_played_rankeds(queue_type):
            data = self.data_league[queue_type]
            tier_string = data['tier']
            rank_string = data['rank']
            lp = data['leaguePoints']
            return f'{tier_string}-{rank_string} {lp}LP'
        else:
            return None

    def get_promo_string(self, queue_type='RANKED_SOLO_5x5'):
        if self.has_played_rankeds(queue_type):
            data = self.data_league[queue_type]
            promo_string = None if 'miniSeries' not in data else data['miniSeries']['progress']
            new_promo_string = ''
            if promo_string is not None:
                for character in promo_string:
                    if character == 'N':
                        new_promo_string += 'N'
                    elif character == 'W':
                        new_promo_string += 'W'
                    elif character == 'F':
                        new_promo_string += 'L'
                    new_promo_string += '-'
            return None if promo_string is None else new_promo_string[:-1]


    def get_most_played_champs(self, count):
        i = 0
        while i < count:
            yield self.get_champion_name_by_id(self.data_mastery[i]['championId'])
            i += 1

    def get_last_time_played_by_id(self, id):
        for value in self.data_mastery:
            if value['championId'] == id:
                timestamp = int(str(value['lastPlayTime'])[:-3])
                return datetime.fromtimestamp(timestamp)

    def get_last_time_played_by_name(self, name):
        id = int(self.get_champion_id_by_name(name))
        for value in self.data_mastery:
            if value['championId'] == id:
                timestamp = int(str(value['lastPlayTime'])[:-3])
                return datetime.fromtimestamp(timestamp)

    def has_played_champ_by_name_in_last_n_days(self, name, n):
        return self.get_last_time_played_by_name(name) \
            > datetime.now() - timedelta(days=n)

    def get_champion_name_by_id(self, id):
        for value in data_champ['data'].values():
            if int(value["key"]) == id:
                return value['id']

    def get_champion_id_by_name(self, name):
        for value in data_champ['data'].values():
            if value["id"] == name:
                return int(value['key'])