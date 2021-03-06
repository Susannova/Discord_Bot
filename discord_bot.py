"""Main module. Stars and defines the Discord Bot (KrautBot).
"""
import logging

logging.basicConfig(
    filename="log/log",
    filemode='a',
    format='%(asctime)s,%(msecs)d %(levelname)s %(name)s %(message)s',
    level=logging.INFO
)
logger = logging.getLogger('main')

import sys
import pickle

import discord
from discord.ext import commands

from core import (
    state,
    DiscordBot
)

discord.voice_client.VoiceClient.warn_nacl = False

if __name__ == '__main__':
    bot = DiscordBot.KrautBot()
    try:
        logger.info("Start Bot")

        bot.load_extension('cogs.cog_config')
        
        bot.load_extension('cogs.cog_debug')
        bot.load_extension('cogs.cog_play_requests')
        bot.load_extension('cogs.cog_vote')
        bot.load_extension('cogs.cog_utility')
        bot.load_extension('cogs.events')
        bot.load_extension('cogs.cog_tasks')

        
        for guild_id in bot.config.get_all_guild_ids():
            for cog in bot.config.get_guild_config(guild_id=guild_id).yield_game_cogs():
                try:
                    bot.load_extension(cog)
                except commands.ExtensionAlreadyLoaded:
                    pass

        bot.load_extension('cogs.cog_roleplay')

        bot.run()
        logger.info("End")
    except discord.LoginFailure:
        logger.exception('Failed to login due to improper Token.')
        bot.exit_status = 2

    bot.state.write_state_to_file()
    bot.config.write_config_to_file()
    
    sys.exit(bot.exit_status)
