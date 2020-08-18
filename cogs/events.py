import logging

import discord
from discord.ext import commands

from core import (
    bot_utility as utility,
    timers,
    play_requests,
    DiscordBot,
    config
)

from riot import riot_utility

logger = logging.getLogger(__name__)


class EventCog(commands.Cog):
    """Cog that handles all events. Used for
    features like Auto-React, Auto-DM etc.
    """
    def __init__(self, bot: DiscordBot.KrautBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info('We have logged in as %s', self.bot.user)
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
                        await self.bot.get_channel(bot_channel).send(f"I have removed the bot channels {removed_channels} because they don't exists.")
                    else:
                        bot_channels.remove(bot_channel)

            # Check for invalid channel ids
            await self.bot.check_channels_id_in_config(guild_id)

        logger.debug("on_ready finished")
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("The command was not found. Avaible commands are:")
            await ctx.send_help()
        
        raise error


    
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
    async def on_member_join(self, member):
        """Automatically assigns lowest role to
        anyone that joins the server.
        """
        logger.info('New member joined: %s', member.name)
        await member.edit(roles=utility.get_auto_role_list(member, self.bot.config.get_guild_config(member.guild.id)))

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        if isinstance(message.channel, discord.DMChannel) and message.author != self.bot.user:
            message_info = 'Got a message from: {user}. Content: {content}'.format(user=message.author, content=message.content.replace("\n", "\\n"))
            logger.info(message_info)
            for super_user in self.bot.config.general_config.super_user:
                await self.bot.get_user(super_user).send(message_info)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        guild_state = self.bot.state.get_guild_state(message.guild.id)
        
        if guild_state.is_play_request(message.id):
            guild_state.remove_play_request(message.id)

        logger.info('message %s deleted', message.id)



    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        guild_config = self.bot.config.get_guild_config(payload.guild_id)
        
        if guild_config.toggles.game_selector and payload.message_id == self.bot.config.get_guild_config(payload.guild_id).unsorted_config.game_selector_id:
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
        if guild_config.toggles.game_selector and payload.message_id == self.bot.config.get_guild_config(payload.guild_id).unsorted_config.game_selector_id:
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
            guild_id = channel.guild.id
            guild_config = self.bot.config.get_guild_config(channel.guild.id)
            guild_config.channel_ids.bot.remove(channel.id)
            if not guild_config.channel_ids.bot:
                bot_channel = await self.bot.create_bot_channel(channel.guild)
                await bot_channel.send("This channel was created because the old one was deleted.")
            



    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        guild_config = self.bot.config.get_guild_config(member.guild.id)
        # Checks if the user changed the channel and returns if the user didn't
        if before.channel == after.channel:
            return
        else:
            everyone_role = member.guild.get_role(guild_config.unsorted_config.everyone_id)
            await update_channels_visibility(everyone_role, before.channel, guild_config, False)
            await update_channels_visibility(everyone_role, after.channel, guild_config, True)

async def update_channels_visibility(role: discord.Role, channel: discord.VoiceChannel, guild_config: config.GuildConfig, bool_after_channel=False):
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
        logger.info("Channel category %s is %s visible for everybody", category_channel.name, "" if bool_make_visible else "not")


def setup(bot: DiscordBot.KrautBot):
    bot.add_cog(EventCog(bot))
    logger.info('Event cogs loaded')
