"""Main module. Stars and defines the Discord Bot (KrautBot).
"""
import logging

import discord
from discord.ext import commands

from core import (
    bot_utility as utility,
    consts
)

from cogs import (
    kraut,
    events
)


logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)
discord.voice_client.VoiceClient.warn_nacl = False

BOT_TOKENS = utility.read_config_file('bot')


class KrautBot(commands.Bot):
    """The actual bot.
    """
    BOT_TOKEN = str(BOT_TOKENS['token'])

    def __init__(self):
        """ Sets the Command Prefix and then 
        call the __init__ method of the commands.Bot
        class.
        """
        super().__init__(command_prefix=consts.COMMAND_PREFIX)

    def run(self):
        """ Runs the Bot using the Token defined
        in BOT_TOKEN.
        """
        try:
            super().run(self.BOT_TOKEN)
        except KeyboardInterrupt:
            logging.warning('Stopped Bot due to Keyboard Interrupt.')

if __name__ == '__main__':
    bot = KrautBot()
    try:
        print("Start Bot")
        logging.info("Start Bot")
        bot.add_cog(kraut.KrautCog(bot))
        bot.add_cog(events.EventCog(bot))
        bot.run()
        print("End Bot")
        logging.info("End")
    except discord.LoginFailure:
        logging.warning('Failed to login due to improper Token.')
