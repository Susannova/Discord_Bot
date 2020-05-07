import time
from enum import Enum

import discord


class PlayRequestCategory(Enum):
    LOL = 1
    CLASH = 2
    INTERN = 3
    APEX = 4
    CSGO = 5
    RL = 6
    VAL = 7


class PlayRequest():
    subscribers = []

    def __init__(self, message_id: int, author_id: int, category=PlayRequestCategory.LOL):
        self.message_id = message_id
        self.author_id = author_id
        self.timestamp_ = time.time()
        self.category = category
        self.clash_date = ''

    def add_clash_date(self, clash_date):
        if self.category == PlayRequestCategory.CLASH:
            self.clash_date = clash_date

    def add_subscriber_id(self, user_id: int):
        self.subscriber_ids.append(user_id)

    def remove_subscriber_id(self, user_id: int):
        self.subscriber_ids.remove(user_id)

    def generate_all_players(self):
        for subscriber in self.subscriber_ids:
            yield subscriber
        yield self.author
