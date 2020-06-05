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
from core.play_requests import PlayRequestCategory
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

        # Checks if we are in new guilds
        for guild_id in guilds:

            if not self.bot.config.check_if_guild_exists(guild_id):
                self.bot.config.add_new_guild_config(guild_id)
            
            if not self.bot.state.check_if_guild_exists(guild_id):
                self.bot.state.add_guild_state(guild_id)

        logger.debug("Check if we were removed from a guild")
        # Checks if we were removed from a guild
        for guild_id in self.bot.config.get_all_guild_ids():
            if guild_id not in guilds:
                self.bot.config.remove_guild_config(guild_id)
        
        for guild_id in self.bot.state.get_all_guild_ids():
            if guild_id not in guilds:
                self.bot.state.remove_guild_state(guild_id)
        
        logger.debug("on_ready finished")


    
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        logger.info("Joined to new server %s with id %s!", guild.name, guild.id)
        self.bot.config.add_new_guild_config(guild.id)
        self.bot.state.add_guild_state(guild.id)

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

        if isinstance(message.channel, discord.DMChannel):
            # TODO Is only the first bot channel
            # TODO A DM has no guild...
            # bot_channel = self.bot.get_channel(self.bot.config.get_guild_config(message.guild.id).channel_ids.bot[0])
            message_info = 'Got a message from: {user}. Content: {content}'.format(user=message.author, content=message.content.replace("\n", "\\n"))
            logger.info(message_info)
            # if bot_channel is None:
            #     logger.error("Can't send message to bot channel! Channel is None")
            
            # await bot_channel.send(message_info)
            return

        guild_config = self.bot.config.get_guild_config(message.guild.id)

        # add all messages in channel to gstate.message_cache
        if guild_config.toggles.auto_delete and utility.is_in_channels(message, guild_config.channel_ids.play_request):
            utility.insert_in_message_cache(self.bot.state.get_guild_state(message.guild.id).message_cache, message.id, message.channel.id)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        guild_state = self.bot.state.get_guild_state(message.guild.id)
        utility.clear_play_requests(message.id, guild_state)
        if message.id in guild_state.message_cache:
            utility.clear_message_cache(message.id, guild_state.message_cache)
        else:
            logger.info('Manually deleted message %s', message.id)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        guild_config = utility.get_guild_config(self.bot, user.guild.id)
        guild_state = self.bot.state.get_guild_state(user.guild.id)

        # auto dm
        logger.debug("Reaction added to %s by %s", reaction.message.id, user.name)

        if utility.is_user_bot(user, self.bot):
            return
        
        if not guild_config.toggles.auto_dm:
            return

        if reaction.message.id not in guild_state.play_requests:
            logger.debug("Message is not a play request. Ignore reaction")
            return
        
        play_request = guild_state.play_requests[reaction.message.id]

        if utility.is_play_request_author(user.id, play_request):
            logger.info("Remove reaction from a play_request_author")
            await reaction.remove(user)
            return

        if str(reaction.emoji) == guild_config.unsorted_config.emoji_pass:
            for player_id in play_request.generate_all_players():
                if user.id == player_id:
                    logger.info("Remove %s from play_request %s", user.name, reaction.message.id)
                    play_request.remove_subscriber_id(user.id)
            return

        if utility.is_already_subscriber(user, play_request):
            return
        
        utility.add_subscriber_to_play_request(user, play_request)

        author = self.bot.get_user(play_request.author_id)
        
        # send auto dms to subscribers and author
        logger.info("Send auto dms to play_request subscribers")
        for player_id in play_request.generate_all_players():
            if player_id == play_request.author_id and player_id != user.id:
                await author.send(
                    guild_config.messages.auto_dm_creator.format(
                        player=user.name,
                        reaction=str(reaction.emoji)
                        )
                    )
            elif player_id != user.id:
                player = self.bot.get_user(player_id)
                await player.send(
                    guild_config.messages.auto_dm_subscriber.format(
                        player=user.name,
                        creator=author.name,
                        reaction=str(reaction.emoji)))

        if len(play_request.subscriber_ids) + 1 == 5 and play_request.category == PlayRequestCategory.CLASH:
            logger.info("Clash has 5 Members")
            await reaction.channel.send(guild_config.messages.clash_full.format(
                creator=author,
                time=play_request.clash_date,
                team=utility.pretty_print_list([self.bot.get_user(player_id) for player_id in play_request.subscriber_ids], author)
            ))

        if len(play_request.subscriber_ids) + 1 > 5 and play_request.category == PlayRequestCategory.CLASH:
            logger.info("Remove reaction because clash has 5 Members")
            await reaction.remove(user)
            await user.send('Das Clash Team ist zur Zeit leider schon voll.')

        if len(play_request.subscriber_ids) + 1 == 6 and play_request.category == PlayRequestCategory.INTERN:
            logger.info("Create internal play request")
            await reaction.channel.send(
                utility.switch_to_internal_play_request(reaction.message, play_request, guild_config, guild_state))



    # TODO no logging
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
        return

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        tmp_channel_ids = self.bot.state.get_guild_state(channel.guild.id).tmp_channel_ids
        if channel.id in tmp_channel_ids:
            logger.info("Temporary channel was deleted manually.")
            tmp_channel_ids[channel.id]["deleted"] = True

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        guild_config = self.bot.config.get_guild_config(member.guild.id)
        # Checks if the user changed the channel and returns if the user didn't
        if before.channel == after.channel:
            return
        else:
            everyone_role = discord.utils.find(lambda m: m.id == guild_config.unsorted_config.everyone_id, member.guild.roles)
            await update_channels_visibility(everyone_role, before.channel, guild_config, False)
            await update_channels_visibility(everyone_role, after.channel, guild_config, True)

async def update_channels_visibility(role, channel: discord.VoiceChannel, guild_config: config.GuildConfig, bool_after_channel=False):
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
