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

logger = logging.getLogger(consts.LOG_NAME)


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
        logger.info('We have logged in as {0.user}'.format(self.bot))
        game_selection_channel = discord.utils.find(lambda x: x.name == 'game-selection', self.bot.guilds[0].channels)
        game_selector_message_list = await game_selection_channel.history(limit=1).flatten()
        self.game_selection_message_id = game_selector_message_list[0].id

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Automatically assigns lowest role to
        anyone that joins the server.
        """
        logger.info(f'New member joined: {member.name}')
        await member.edit(roles=utility.get_auto_role_list(member))

    @commands.Cog.listener()
    async def on_message(self, message):
        # # TODO Moved to tasks
        # # checks if a new lol patch is out and posts it if it is
        # if riot_utility.update_current_patch():
        #     logger.info('Posted new Patch notes')
        #     annoucement_channel = discord.utils.find(lambda m: m.name == 'announcements', message.channel.guild.channels)
        #     await annoucement_channel.send(consts.MESSAGE_PATCH_NOTES_FORMATTED.format(message.guild.get_role(consts.ROLE_LOL_ID).mention, riot_utility.get_current_patch_url()))

        if isinstance(message.channel, discord.DMChannel):
            return

        # add all messages in channel to gstate.message_cache
        if gstate.CONFIG["TOGGLE_AUTO_DELETE"] and utility.is_in_channel(message, consts.CHANNEL_PLAY_REQUESTS):
            utility.insert_in_message_cache(self.message_cache, message.id, message.channel.id)

        # # TODO Moved to tasks
        # # auto delete all purgeable messages
        # purgeable_message_list = utility.get_purgeable_messages_list(message, self.message_cache)
        # for purgeable_message in purgeable_message_list:
        #     utility.clear_message_cache(purgeable_message, self.message_cache)
        #     await purgeable_message.delete()


    @commands.Cog.listener()
    async def on_message_delete(self, message):
        # TODO Also triggered when a purgeable message is deleted automatically!
        logger.info(f'Maually deleted a message')
        utility.clear_play_requests(message)
        if message.id in self.message_cache:
            utility.clear_message_cache(message.id, self.message_cache)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        # auto dm

        if utility.is_user_bot(user, self.bot):
            return
        
        if not gstate.CONFIG["TOGGLE_AUTO_DM"]:
            return

        if reaction.message.id not in self.play_requests:
            return
        
        play_request = self.play_requests[reaction.message.id]

        if utility.is_play_request_author(user.id, play_request):
            await reaction.remove(user)
            return

        if str(reaction.emoji) == consts.EMOJI_PASS:
            for player_id in play_request.generate_all_players():
                if user.id == player_id:
                    play_request.remove_subscriber(user.id)
            return

        if utility.is_already_subscriber(user, play_request):
            return
        
        utility.add_subscriber_to_play_request(user, play_request)

        author = self.bot.get_user(play_request.author_id)
        # send auto dms to subscribers and author
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
            await reaction.channel.send(consts.MESSAGE_CLASH_FULL.format(
                author, play_request.clash_date, utility.pretty_print_list([self.bot.get_user(player_id) for player_id in play_request.subscriber_ids], author)
            ))

        if len(play_request.subscriber_ids) + 1 > 5 and play_request.category == PlayRequestCategory.CLASH:
            await reaction.remove(user)
            await user.send('Das Clash Team ist zur Zeit leider schon voll.')

        if len(play_request.subscriber_ids) + 1 == 6 and play_request.category == PlayRequestCategory.INTERN:
            await reaction.channel.send(
                utility.switch_to_internal_play_request(reaction.message, play_request))



    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id == self.game_selection_message_id:
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
        if payload.message_id == self.game_selection_message_id:
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
            del gstate.tmp_channel_ids[channel.id]

