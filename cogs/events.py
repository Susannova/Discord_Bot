import logging

import discord
from discord.ext import commands

from core import exceptions
from core import timers
from core.kraut_bot import KrautBot
from core.config.guild_config import GuildConfig
import random


logger = logging.getLogger(__name__)


class EventCog(commands.Cog):
    """
    Cog that handles all events. Is used for
    features like Auto-React, Auto-DM etc.
    """

    def __init__(self, bot: KrautBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("We have logged in as %s", self.bot.user)
        guilds = [guild.id for guild in self.bot.guilds]

        for guild_id in guilds:
            # Checks if we are in new guilds
            if not self.bot.config.check_if_guild_exists(guild_id):
                self.bot.config.add_new_guild_config(guild_id)
            if not self.bot.state.check_if_guild_exists(guild_id):
                self.bot.state.add_guild_state(guild_id)

        logger.debug("Check if we were removed from a guild")
        for guild_id in self.bot.config.get_all_guild_ids():
            if guild_id not in guilds:
                self.bot.config.remove_guild_config(guild_id)

        for guild_id in self.bot.state.get_all_guild_ids():
            if guild_id not in guilds:
                self.bot.state.remove_guild_state(guild_id)

        logger.debug("Check the channel ids")
        for guild_id in guilds:
            # Check if a bot channel was deleted
            guild = self.bot.get_guild(guild_id)
            guild_channels = [channel.id for channel in guild.channels]
            bot_channels = self.bot.config.get_guild_config(guild_id).channel_ids.bot

            channel_found = False
            removed_channels = []
            for bot_channel in bot_channels:
                if bot_channel in guild_channels:
                    channel_found = True
                else:
                    removed_channels.append(bot_channel)

            if not channel_found:
                await self.bot.create_bot_channel(guild)

            # Second loop is needed because a new bot channel could have beeen created above.
            if removed_channels:
                for bot_channel in bot_channels:
                    if bot_channel not in removed_channels:
                        await self.bot.get_channel(bot_channel).send(
                            f"I have removed the bot channels {removed_channels} because they don't exists."
                        )
                    else:
                        bot_channels.remove(bot_channel)

            # Check for invalid channel ids
            await self.bot.check_channels_id_in_config(guild_id)

        logger.debug("on_ready finished")

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CommandNotFound):
            await ctx.author.send("The command was not found.")
        elif isinstance(error, exceptions.FalseChannel):
            text = "This command is not allowed here."
            if error.valid_channels is not None:
                text += " The command is allowed in "
                text += ", ".join(
                    (
                        self.bot.get_channel(channel_id).mention
                        for channel_id in error.valid_channels
                        if ctx.author in self.bot.get_channel(channel_id).members
                    )
                )
            await ctx.author.send(text)
        elif isinstance(error, commands.DisabledCommand):
            await ctx.author.send("This command is currently disabled.")
        elif isinstance(error, commands.MissingAnyRole):
            await ctx.author.send("Sorry, you are not allowed to use this command.")
        else:
            await ctx.author.send("Sorry, an unknown error has occurred...")
            raise error
        await ctx.author.send(f"Try using ``{self.bot.get_command_prefix(ctx.guild.id)}help`` for available commands.")

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        logger.info("Joined to new server %s with id %s!", guild.name, guild.id)
        self.bot.state.add_guild_state(guild.id)
        self.bot.config.add_new_guild_config(guild.id)

        await self.bot.create_bot_channel(guild)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        logger.info("Removed from server %s with id %s!", guild.name, guild.id)
        self.bot.config.remove_guild_config(guild.id)
        self.bot.state.remove_guild_state(guild.id)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """
        Automatically assign the lowest role to
        anyone that joins the server.
        """
        logger.info("New member joined: %s", member.name)
        guild_config = self.bot.config.get_guild_config(member.guild.id)

        await member.add_roles(
            member.guild.get_role(guild_config.unsorted_config.guest_id), reason="Assign lowest role"
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if isinstance(message.channel, discord.DMChannel) and message.author != self.bot.user:
            message_info = "Got a message from: {user}. Content: {content}".format(
                user=message.author, content=message.content.replace("\n", "\\n")
            )
            logger.info(message_info)
            for super_user in self.bot.config.general_config.super_user:
                await self.bot.get_user(super_user).send(message_info)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        guild_state = self.bot.state.get_guild_state(message.guild.id)

        if guild_state.is_play_request(message.id):
            guild_state.remove_play_request(message.id)

        logger.info("message %s deleted", message.id)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        guild_config = self.bot.config.get_guild_config(payload.guild_id)

        if (
            guild_config.toggles.game_selector
            and payload.message_id
            == self.bot.config.get_guild_config(payload.guild_id).unsorted_config.game_selector_id
        ):
            member = discord.utils.find(lambda x: x.id == payload.user_id, list(self.bot.get_all_members()))
            member_roles = member.roles.copy()
            for role in member_roles:
                if role.id == guild_config.emoji_to_game(payload.emoji.id).role_id:
                    return
            member_roles.append(discord.utils.find(lambda x: x.name == payload.emoji.name.upper(), member.guild.roles))
            await member.edit(roles=member_roles)
            logger.info("Member %s was added to %s", member.name, payload.emoji.name)
        return

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        guild_config = self.bot.config.get_guild_config(payload.guild_id)
        if (
            guild_config.toggles.game_selector
            and payload.message_id
            == self.bot.config.get_guild_config(payload.guild_id).unsorted_config.game_selector_id
        ):
            member = discord.utils.find(lambda x: x.id == payload.user_id, list(self.bot.get_all_members()))
            member_roles = member.roles.copy()
            for role in member_roles:
                if role.id == guild_config.emoji_to_game(payload.emoji.id).role_id:
                    member_roles.remove(role)
            await member.edit(roles=member_roles)
            logger.info("Member %s was removed from %s", member.name, payload.emoji.name)
        return

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        tmp_channel_ids = self.bot.state.get_guild_state(channel.guild.id).tmp_channel_ids
        if channel.id in tmp_channel_ids:
            logger.info("Temporary channel was deleted manually.")
            tmp_channel_ids[channel.id]["deleted"] = True
        elif channel.id in self.bot.config.get_guild_config(channel.guild.id).channel_ids.bot:
            guild_config = self.bot.config.get_guild_config(channel.guild.id)
            guild_config.channel_ids.bot.remove(channel.id)
            if not guild_config.channel_ids.bot:
                bot_channel = await self.bot.create_bot_channel(channel.guild)
                await bot_channel.send("This channel was created because the old one was deleted.")

    @commands.Cog.listener()
    async def on_voice_state_update(
        self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState
    ):
        guild_config = self.bot.config.get_guild_config(member.guild.id)
        # Checks if the user changed the channel and returns if the user didn't
        if after.channel is not None:
            if after.channel.id == self.bot.config.get_guild_config(member.guild.id).channel_ids.create_tmp_voice:
                await self.create_channel(member)
        if before.channel == after.channel:
            return
        else:
            everyone_role = member.guild.get_role(guild_config.unsorted_config.everyone_id)
            await update_channels_visibility(everyone_role, before.channel, guild_config, False)
            await update_channels_visibility(everyone_role, after.channel, guild_config, True)

    async def create_channel(
        self,
        member: commands.Context,
    ):
        """
        Create a temporary channel.
        """
        guild_state = self.bot.state.get_guild_state(member.guild.id)
        for tmp_channels in guild_state.tmp_channel_ids:
            logger.debug(
                "Check if channel %s with id %s is already created by user %s.",
                guild_state.tmp_channel_ids[tmp_channels]["name"],
                tmp_channels,
                member.name,
            )
            if (
                not guild_state.tmp_channel_ids[tmp_channels]["deleted"]
                and guild_state.tmp_channel_ids[tmp_channels]["author"] == member.id
            ):
                logger.info(
                    "%s wanted to create a new temporary channel but already has created channel %s with id %s.",
                    member.name,
                    guild_state.tmp_channel_ids[tmp_channels]["name"],
                    tmp_channels,
                )
                logger.warning(
                    exceptions.LimitReachedException("Der Autor hat schon einen temporären Channel erstellt.")
                )
                return

        tmp_channel_category = self.bot.get_channel(
            self.bot.config.get_guild_config(member.guild.id).channel_ids.category_temporary
        )

        channel_name = self.get_random_channel_name()
        tmp_channel = await member.guild.create_voice_channel(
            channel_name, category=tmp_channel_category, user_limit=99
        )

        guild_state.tmp_channel_ids[tmp_channel.id] = {
            "timer": timers.start_timer(hrs=12),
            "author": member.id,
            "deleted": False,
            "name": channel_name,
        }
        await member.move_to(tmp_channel)

    def get_random_channel_name(self):
        prefix = ["Grotte", "Peninsula", "Archipel", "Mündung", "Höhle"]
        suffix = ["der Freundschaft", "der Begeisterung", "des Danks", "der Güte", "der Passion"]
        channel_name = f"{prefix[random.randint(0, len(prefix) - 1)]} {suffix[random.randint(0, len(suffix) - 1)]}"
        return channel_name


async def update_channels_visibility(
    role: discord.Role,
    channel: discord.VoiceChannel,
    guild_config: GuildConfig,
    bool_after_channel=False,
):
    if channel is not None and channel.category.id in guild_config.get_all_category_ids():
        category_channel = channel.category
        bool_make_visible = False

        if not bool_after_channel:
            for voice_channel in category_channel.voice_channels:
                if len(voice_channel.members) >= 1:
                    bool_make_visible = True
                    break
        else:
            bool_make_visible = True

        await category_channel.set_permissions(role, read_messages=bool_make_visible)
        logger.info(
            "Channel category %s is %s visible for everybody",
            category_channel.name,
            "" if bool_make_visible else "not",
        )


async def setup(bot: KrautBot):
    await bot.add_cog(EventCog(bot))
    logger.info("Event cogs loaded")
