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
        self.help_command = help_command_
        try:
            with open(f'{self.config.general_config.database_directory_global_state}/{self.config.general_config.database_name_global_state}', 'rb') as file:
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
    
    def get_command_prefix(self, guild_id: int):
        """ Returns the command prefix for the guild """
        return self.config.get_guild_config(guild_id).unsorted_config.command_prefix
    
    async def create_bot_channel(self, guild: discord.Guild) -> discord.TextChannel:
        """ Creates the bot channel that is needed to configure the bot """
        owner = guild.owner

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            guild.me: discord.PermissionOverwrite(read_messages=True),
            owner: discord.PermissionOverwrite(read_messages=True)
        }        
        channel = await guild.create_text_channel('KrautBot', overwrites=overwrites)

        self.config.get_guild_config(guild.id).channel_ids.bot.append(channel.id)

        await channel.send(f"{owner.mention} I have automatically created this channel because this channel did not exist or was not found in the config. The channel is invisible for everyone except you. In this channel you can use ``{self.get_command_prefix(guild.id)}config`` to configure {guild.me.mention}.")
        
        return channel

    async def check_channels_id_in_config(self, guild_id: int):
        """ Checks if the channels set in the config are part of the guild and removes it if not """
        
        guild_channel_ids = [channel.id for channel in self.get_guild(guild_id).channels]
        guild_config = self.config.get_guild_config(guild_id)
        deleted_channels = [channel for channel in guild_config.check_for_invalid_channel_ids(guild_channel_ids)]

        for bot_channel_id in guild_config.channel_ids.bot:
            for deleted_channel in deleted_channels:
                await self.get_channel(bot_channel_id).send(f"The channel id {deleted_channel[1]} which is a {deleted_channel[0]} channel was removed from the config because the channel does not exist.")





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
    if not isinstance(msg.channel, discord.DMChannel):
        return bot.get_command_prefix(msg.guild.id)
    else:
        return "Some string that is defenitly no command prefix"
