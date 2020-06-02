""" Class for the bot """

import logging
logger = logging.getLogger(__name__)

from discord.ext import commands

from core.config import Config as ConfigurationClass


class KrautBot(commands.Bot):
    """The actual bot.
    """

    config = ConfigurationClass(None, "./config/configuration.json")
    BOT_TOKEN = config.basic_config.discord_token

    exit_status = 1

    def __init__(self):
        """ Sets the Command Prefix and then
        call the __init__ method of the commands.Bot
        class.
        """
        super().__init__(command_prefix=self.config.basic_config.command_prefix)
        
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