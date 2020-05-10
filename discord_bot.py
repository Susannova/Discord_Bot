"""Main module. Stars and defines the Discord Bot (KrautBot).
"""
import logging
import sys
import pickle

import discord
from discord.ext import commands

from core import (
    bot_utility as utility,
    consts,
    state
)

from cogs import (
    cog_debug,
    cog_play_requests,
    cog_riot,
    cog_utility,
    cog_tasks,
    events
)

logging.basicConfig(
    filename=consts.LOG_FILE,
    filemode='a',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    level=logging.INFO
)
logger = logging.getLogger('main')

discord.voice_client.VoiceClient.warn_nacl = False
BOT_TOKENS = utility.read_config_file('bot')
help_command_ = discord.ext.commands.DefaultHelpCommand()
help_command_.verify_checks = False

class KrautBot(commands.Bot):
    """The actual bot.
    """
    BOT_TOKEN = str(BOT_TOKENS['token'])

    exit_status = 1

    def __init__(self):
        """ Sets the Command Prefix and then
        call the __init__ method of the commands.Bot
        class.
        """
        super().__init__(command_prefix=consts.COMMAND_PREFIX)
        self.help_command = help_command_

    def run(self):
        """ Runs the Bot using the Token defined
        in BOT_TOKEN.
        """
        try:
            super().run(self.BOT_TOKEN)
        except KeyboardInterrupt:
            logger.exception('Stopped Bot due to Keyboard Interrupt.')
            self.exit_status = 2

    async def logout(self, exit_status_input):
        """Aborts the bot and sets exit_status to exit_status_input"""
        await super().logout()
        logger.info('Logout')
        self.exit_status = exit_status_input


if __name__ == '__main__':
    bot = KrautBot()
    try:
        logger.info("Start Bot")

        bot.load_extension('cogs.cog_debug')
        bot.load_extension('cogs.cog_play_requests')
        bot.load_extension('cogs.cog_riot')
        bot.load_extension('cogs.cog_utility')
        bot.load_extension('cogs.events')
        bot.load_extension('cogs.cog_tasks')
        
        bot.run()
        logger.info("End")
    except discord.LoginFailure:
        logger.exception('Failed to login due to improper Token.')
        bot.exit_status = 2

    state.global_state.write_state_to_file()
    sys.exit(bot.exit_status)
