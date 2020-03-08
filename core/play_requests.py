import time

import discord

class PlayRequest():
    subscribers = []
    message = None

    def __init__(self, message: discord.Message, author: discord.User):
        self.message = message
        self.author = author
        self.timestamp_ = time.time()

    def add_subscriber(user: discord.User):
        self.subscribers.append(user)

    def remove_subscriber(user: discord.User):
        self.subscribers.remove(user)
    
    def generate_all_players():
        for subscriber in self.subscribers:
            yield subscriber
        yield self.author
