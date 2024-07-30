import logging

logger = logging.getLogger(__name__)

import pickle
import sys

import discord
from discord.ext import commands

from core.config.bot_config import BotConfig
from core.state import GeneralState


class KrautBot(commands.Bot):
    """The actual bot."""

    config = BotConfig()
    BOT_TOKEN = config.general_config.discord_token
    exit_status = 1

    sending_message = False

    def __init__(self):
        """
        Set the Command Prefix and then
        call the `__init__` method of the `commands.Bot` class.
        """
        intents = discord.Intents.all()
        intents.members = True
        intents.message_content = True
        super().__init__(command_prefix=get_command_prefix, intents=intents)

        help_command_ = commands.DefaultHelpCommand()
        self.help_command = help_command_
        try:
            with open(
                f"{self.config.general_config.database_directory_global_state}/"
                f"{self.config.general_config.database_name_global_state}",
                "rb",
            ) as file:
                self.state = pickle.load(file)
            self.state.config = self.config
            logger.info("Global State reinitialized.")
        except FileNotFoundError:
            no_global_state_found_text = "No global state found! Create new global state."
            logger.warning(no_global_state_found_text)
            print(no_global_state_found_text, file=sys.stderr)

            self.state = GeneralState(self.config)
            for guild in self.guilds:
                self.state.add_guild_state(guild.id)

    async def setup_hook(self):
        try:
            await self.load_extension("cogs.cog_config")
            await self.load_extension("cogs.cog_debug")
            await self.load_extension("cogs.cog_play_requests")
            await self.load_extension("cogs.cog_vote")
            await self.load_extension("cogs.cog_utility")
            await self.load_extension("cogs.events")
            await self.load_extension("cogs.cog_tasks")
            await self.load_extension("cogs.cog_roleplay")
            await self.load_extension("cogs.cog_games")
            self.tree.remove_command("play")
            # await self.tree.a
            # self.tree.remove_command("test123")
            await self.tree.sync()

            for guild_id in self.config.get_all_guild_ids():
                for cog in self.config.get_guild_config(guild_id=guild_id).yield_game_cogs():
                    try:
                        await self.load_extension(cog)
                    except commands.ExtensionAlreadyLoaded:
                        pass
        except discord.LoginFailure:
            logger.exception("Failed to login due to improper Token.")
            self.exit_status = 2

    async def on_ready(self):
        await self.wait_until_ready()

    def get_command_prefix(self, guild_id: int):
        """Return the command prefix for the guild."""
        return self.config.get_guild_config(guild_id).unsorted_config.command_prefix

    async def create_bot_channel(self, guild: discord.Guild) -> discord.TextChannel:
        """Create the bot channel that is needed to configure the bot."""
        owner = guild.owner

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            guild.me: discord.PermissionOverwrite(read_messages=True),
            owner: discord.PermissionOverwrite(read_messages=True),
        }
        channel = await guild.create_text_channel("KrautBot", overwrites=overwrites)

        self.config.get_guild_config(guild.id).channel_ids.bot.append(channel.id)

        await channel.send(
            f"{owner.mention} I have automatically created this channel because"
            "this channel did not exist or was not found in the config."
            "The channel is invisible for everyone except you."
            f"In this channel you can use ``{self.get_command_prefix(guild.id)}config``"
            f"to configure {guild.me.mention}."
        )

        return channel

    def yield_guild_admin_ids(self, guild: discord.Guild) -> int:
        guild_config = self.config.get_guild_config(guild.id)
        admin_role = guild.get_role(guild_config.unsorted_config.admin_id)
        for member in admin_role.members:
            yield member.id

    async def check_channels_id_in_config(self, guild_id: int):
        """Check if the channels set in the config are part of the guild and removes it if not."""
        guild_channel_ids = [channel.id for channel in self.get_guild(guild_id).channels]
        guild_channel_ids.extend([channel.id for channel in self.get_guild(guild_id).categories])
        guild_config = self.config.get_guild_config(guild_id)
        deleted_channels = [channel for channel in guild_config.check_for_invalid_channel_ids(guild_channel_ids)]

        for bot_channel_id in guild_config.channel_ids.bot:
            for deleted_channel in deleted_channels:
                await self.get_channel(bot_channel_id).send(
                    f"The channel id {deleted_channel[1]} which is a {deleted_channel[0]} channel"
                    " was removed from the config because the channel does not exist."
                )

    def run(self):
        """Run the Bot using the Token defined in `BOT_TOKEN`."""
        try:
            super().run(self.BOT_TOKEN)
        except KeyboardInterrupt:
            logger.exception("Stopped Bot due to Keyboard Interrupt.")
            self.exit_status = 2

    async def logout(self, exit_status_input: int):
        """Abort the bot and sets exit_status to exit_status_input."""
        await super().close()
        logger.info("Logout")
        self.exit_status = exit_status_input


def get_command_prefix(bot: KrautBot, msg: discord.Message):
    """Return the command prefix for the guild in that the message is in."""
    if not isinstance(msg.channel, discord.DMChannel):
        return bot.get_command_prefix(msg.guild.id)
    else:
        return "Some string that is defenitly no command prefix"
