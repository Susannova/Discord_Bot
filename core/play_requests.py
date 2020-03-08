import time

import discord

class PlayRequest():
    subscribers = []
    def __init__(self, message: discord.Message, message_author: discord.User):
        self.message = message
        self.message_author = message_author
        self.timestamp_ = time.time()

    def add_subscriber(user: discord.User):
        self.subscribers.append(user)
