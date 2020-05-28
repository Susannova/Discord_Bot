import logging

import discord
from discord.ext import commands

from core.state import global_state as gstate
from core import (
    bot_utility as utility,
    consts,
    timers,
    play_requests
)
from core.play_requests import PlayRequestCategory
from riot import riot_utility

logger = logging.getLogger('events')


class EventCog(commands.Cog):
    """Cog that handles all events. Used for
    features like Auto-React, Auto-DM etc.
    """
    def __init__(self, bot):
        self.bot = bot
        """ Dicts are mutable objects, which means
        that 'self.play_requests = gstate.play_requests'
        makes self.play_requests a pointer to gstate.play_requests
        so every change to play_requests also changes 
        gstate.play_requests. Technically we can make play_requests
        local, but I feel like we might need play_requests in a global
        scope sometime. Same for message_cache.
        """
        self.play_requests = gstate.play_requests
        self.message_cache = gstate.message_cache
        self.game_selection_message_id = None

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info('We have logged in as %s', self.bot.user)
        if gstate.CONFIG["TOGGLE_GAME_SELECTOR"]:
            game_selection_channel = discord.utils.find(lambda x: x.name == 'game-selection', self.bot.guilds[0].channels)
            game_selector_message_list = await game_selection_channel.history(limit=1).flatten()
            self.game_selection_message_id = game_selector_message_list[0].id

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Automatically assigns lowest role to
        anyone that joins the server.
        """
        logger.info('New member joined: %s', member.name)
        await member.edit(roles=utility.get_auto_role_list(member))

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        if isinstance(message.channel, discord.DMChannel):
            bot_channel = self.bot.get_channel(639889605256019980)
            message_info = 'Got a message from: {user}. Content: {content}'.format(user=message.author, content=message.content.replace("\n", "\\n"))
            logger.info(message_info)
            if bot_channel is None:
                logger.error("Can't send message to bot channel! Channel is None")
            
            await bot_channel.send(message_info)
            return

        # add all messages in channel to gstate.message_cache
        if gstate.CONFIG["TOGGLE_AUTO_DELETE"] and utility.is_in_channel(message, consts.CHANNEL_PLAY_REQUESTS):
            utility.insert_in_message_cache(self.message_cache, message.id, message.channel.id)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        utility.clear_play_requests(message)
        if message.id in self.message_cache:
            utility.clear_message_cache(message.id, self.message_cache)
        else:
            logger.info('Manually deleted message %s', message.id)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        # auto dm
        logger.debug("Reaction added to %s by %s", reaction.message.id, user.name)

        if utility.is_user_bot(user, self.bot):
            return
        
        if not gstate.CONFIG["TOGGLE_AUTO_DM"]:
            return

        if reaction.message.id not in self.play_requests:
            logger.debug("Message is not a play request. Ignore reaction")
            return
        
        play_request = self.play_requests[reaction.message.id]

        if utility.is_play_request_author(user.id, play_request):
            logger.info("Remove reaction from a play_request_author")
            await reaction.remove(user)
            return

        if str(reaction.emoji) == consts.EMOJI_PASS:
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
                    consts.MESSAGE_AUTO_DM_CREATOR.format(user.name, str(reaction.emoji))
                    )
            elif player_id != user.id:
                player = self.bot.get_user(player_id)
                await player.send(
                    consts.MESSAGE_AUTO_DM_SUBSCRIBER.format(
                        user.name, author.name, str(reaction.emoji)))

        if len(play_request.subscriber_ids) + 1 == 5 and play_request.category == PlayRequestCategory.CLASH:
            logger.info("Clash has 5 Members")
            await reaction.channel.send(consts.MESSAGE_CLASH_FULL.format(
                author, play_request.clash_date, utility.pretty_print_list([self.bot.get_user(player_id) for player_id in play_request.subscriber_ids], author)
            ))

        if len(play_request.subscriber_ids) + 1 > 5 and play_request.category == PlayRequestCategory.CLASH:
            logger.info("Remove reaction because clash has 5 Members")
            await reaction.remove(user)
            await user.send('Das Clash Team ist zur Zeit leider schon voll.')

        if len(play_request.subscriber_ids) + 1 == 6 and play_request.category == PlayRequestCategory.INTERN:
            logger.info("Create internal play request")
            await reaction.channel.send(
                utility.switch_to_internal_play_request(reaction.message, play_request))



    # TODO no logging
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if gstate.CONFIG["TOGGLE_GAME_SELECTOR"] and payload.message_id == self.game_selection_message_id:
            member = discord.utils.find(lambda x: x.id == payload.user_id, list(self.bot.get_all_members()))
            member_roles = member.roles.copy()
            for role in member_roles:
                if role.id == consts.GAME_NAME_TO_ROLE_ID_DICT[payload.emoji.name.upper()]:
                    return
            member_roles.append(discord.utils.find(lambda x: x.name == payload.emoji.name.upper(), member.guild.roles))
            await member.edit(roles=member_roles)
        return

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if gstate.CONFIG["TOGGLE_GAME_SELECTOR"] and payload.message_id == self.game_selection_message_id:
            member = discord.utils.find(lambda x: x.id == payload.user_id, list(self.bot.get_all_members()))
            member_roles = member.roles.copy()
            for role in member_roles:
                if role.id == consts.GAME_NAME_TO_ROLE_ID_DICT[payload.emoji.name.upper()]:
                    member_roles.remove(role)
            await member.edit(roles=member_roles)
        return

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        if channel.id in gstate.tmp_channel_ids:
            logger.info("Temporary channel was deleted manually.")
            gstate.tmp_channel_ids[channel.id]["deleted"] = True

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        # Checks if the user changed the channel and returns if the user didn't
        if before.channel == after.channel:
            return
        else:
            everyone_role = discord.utils.find(lambda m: m.id == consts.ROLE_EVERYONE_ID, member.guild.roles)
            await update_channels_visibility(everyone_role, before.channel, False)
            await update_channels_visibility(everyone_role, after.channel, True)

async def update_channels_visibility(role, channel: discord.VoiceChannel, bool_after_channel=False):
    if channel is not None and channel.category.id in consts.CATEGORY_IDS:
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


def setup(bot: commands.Bot):
    bot.add_cog(EventCog(bot))
    logger.info('Event cogs loaded')
