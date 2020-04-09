"""Main module. Stars and defines the Discord Bot (KrautBot).
"""
import logging
import sys

import discord
from discord.ext import commands

from core import (
    bot_utility as utility,
    consts
)

from cogs import (
    cog_debug,
    cog_play_requests,
    cog_riot,
    cog_utility,
    events
)

logging.basicConfig(filename=consts.LOG_FILE,
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.INFO)

logger = logging.getLogger(consts.LOG_NAME)
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
        self.exit_status = exit_status_input


if __name__ == '__main__':
    bot = KrautBot()
    try:
        logger.info("Start Bot")
        bot.add_cog(events.EventCog(bot))
        bot.add_cog(cog_debug.DebugCog(bot))
        bot.add_cog(cog_play_requests.PlayRequestsCog())
        bot.add_cog(cog_riot.RiotCog())
        bot.add_cog(cog_utility.UtilityCog())
        bot.run()
        logger.info("End")
    except discord.LoginFailure:
        logger.exception('Failed to login due to improper Token.')
        bot.exit_status = 2
    
    sys.exit(bot.exit_status)
