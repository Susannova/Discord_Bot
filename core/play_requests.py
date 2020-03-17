import time
from enum import Enum

import discord


class PlayRequestCategory(Enum):
    PLAY = 1
    CLASH = 2
    INTERN = 3


class PlayRequest():
    subscribers = []

    def __init__(self, message: discord.Message, author: discord.User, category=PlayRequestCategory.PLAY):
        self.message = message
        self.author = author
        self.timestamp_ = time.time()
        self.category = category
        self.clash_date = ''

    def add_clash_date(self, clash_date):
        if self.category == PlayRequestCategory.CLASH:
            self.clash_date = clash_date

    def add_subscriber(self, user: discord.User):
        self.subscribers.append(user)

    def remove_subscriber(self, user: discord.User):
        self.subscribers.remove(user)

    def generate_all_players(self):
        for subscriber in self.subscribers:
            yield subscriber
        yield self.author
