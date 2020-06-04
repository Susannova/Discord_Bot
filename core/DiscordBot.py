""" Class for the bot """

import logging
logger = logging.getLogger(__name__)

import pickle
import sys

import discord
from discord.ext import commands

from core.config import BotConfig
from core.state import GeneralState


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
        try:
            with open(f'{self.config.general_config.database_directory_global_state}/{self.config.general_config.name_global_state}', 'rb') as file:
                self.state = pickle.load(file)
            self.state.config = self.config
            logger.info('Global State reinitialized.')
        except FileNotFoundError:
            no_global_state_found_text = "No global state found! Create new global state."
            logger.warning(no_global_state_found_text)
            print(no_global_state_found_text, file=sys.stderr)
            
            self.state = GeneralState(self.config)
            for guild in self.guilds:
                self.state.add_guild_state(guild.id)

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
