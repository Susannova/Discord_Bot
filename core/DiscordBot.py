""" Class for the bot """

import logging
logger = logging.getLogger(__name__)

import discord
from discord.ext import commands

from core.config import BotConfig


class KrautBot(commands.Bot):
    """The actual bot.
    """

    config = BotConfig()
    BOT_TOKEN = config.general_config.discord_token

    exit_status = 1

    def __init__(self):
        """ Sets the Command Prefix and then
        call the __init__ method of the commands.Bot
        class.
        """
        super().__init__(command_prefix=get_command_prefix)
        
        help_command_ = commands.DefaultHelpCommand()
        help_command_.verify_checks = False
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

def get_command_prefix(bot: KrautBot, msg: discord.Message):
    """ Returns the command prefix for the guild in that the message is in """
    return bot.config.get_guild_config(msg.id).unsorted_config.command_prefix
