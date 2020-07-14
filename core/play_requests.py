import logging
import time
import datetime
import asyncio

# from core.DiscordBot import KrautBot
from core.config import GuildConfig

logger = logging.getLogger(__name__)

class PlayRequest():
    def __init__(self, message_id: int, author_id: int, category: str, play_time: datetime.datetime):
        self.message_id = message_id
        self.author_id = author_id
        self.timestamp_ = time.time()
        self.category = category
        self.clash_date = ''
        self.play_time = play_time

        self.subscriber_ids = []


    def add_clash_date(self, clash_date):
        if self.category == "clash":
            self.clash_date = clash_date

    def add_subscriber_id(self, user_id: int):
        self.subscriber_ids.append(user_id)


    def remove_subscriber_id(self, user_id: int):
        self.subscriber_ids.remove(user_id)

    def generate_all_players(self):
        for subscriber in self.subscriber_ids:
            yield subscriber
        yield self.author_id
    
    def is_already_subscriber(self, user_id: int):
        return True if user_id in self.subscriber_ids else False


    def is_play_request_author(self, user_id: int) -> bool:
        return user_id == self.author_id
    
    # async def auto_reminder(self, guild_config: GuildConfig, bot: KrautBot):
    async def auto_reminder(self, guild_config: GuildConfig, bot):
        logger.debug("Create an auto reminder for play request with id %s", self.message_id)

        time_difference = ((self.play_time - datetime.timedelta(seconds=guild_config.unsorted_config.play_reminder_seconds)) - datetime.datetime.now()).total_seconds()

        if time_difference > 0:
            await asyncio.sleep(time_difference)
            for player_id in self.generate_all_players():
                player = bot.get_user(player_id)
                await player.send(guild_config.messages.play_request_reminder.format(minutes=guild_config.unsorted_config.play_reminder_seconds / 60))
