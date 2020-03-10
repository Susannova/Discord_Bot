import asyncio

import discord
from discord.ext import commands

from core.state import global_state as gstate
from core import (
    bot_utility as utility,
    consts,
    reminder
)
from core.play_requests import PlayRequest

class EventCog(commands.Cog):
    """Cog that handles all events. Used for
    features like Auto-React, Auto-DM etc.
    """
    def __init__(self, bot):
        self.bot = bot
        self.play_requests = gstate.play_requests

    def update_global_play_requests():
        gstate.play_requests = self.play_requests

    @commands.Cog.listener()
    async def on_ready(self):
            print('We have logged in as {0.user}'.format(self.bot))

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Automatically assigns lowest role to
        anyone that joins the server.
        """
        await member.edit(roles=utility.get_auto_role_list(member))

    @commands.Cog.listener()
    async def on_message(self, message):
        if isinstance(message.channel, discord.DMChannel):
            return

        # add all messages in channel to gstate.message_cache
        if gstate.CONFIG["TOGGLE_AUTO_DELETE"] \
        and utility.is_in_channel(message, consts.CHANNEL_PLAY_REQUESTS):
            utility.update_message_cache(message)

        # auto react
        if gstate.CONFIG["TOGGLE_AUTO_REACT"] and utility.has_any_pattern(message):
            await message.add_reaction(self.bot.get_emoji(consts.EMOJI_ID_LIST[5]))
            await message.add_reaction(consts.EMOJI_PASS)

            self.play_requests[message.id] = PlayRequest(message, gstate.tmp_message_author)

            # auto delete all purgeable messages
            purgeable_message_list = utility.get_purgeable_messages_list(message)
            for purgeable_message in purgeable_message_list:
                utility.clear_message_cache(purgeable_message)
                await purgeable_message.delete()

            # auto reminder
            if utility.has_pattern(message, consts.PATTERN_PLAY_REQUEST):
                time_difference = reminder.get_time_difference(message.content)
                if time_difference > 0:
                    await asyncio.sleep(time_difference)
                    for player in self.play_requests[message.id].generate_all_players():
                        await player.send(consts.MESSAGE_PLAY_REQUEST_REMINDER)


    @commands.Cog.listener()
    async def on_message_delete(self, message):
        utility.clear_play_requests(message, self.play_requests)
        [utility.clear_message_cache(message) for msg in gstate.message_cache if message in msg]

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """ Implements the Auto-DM Feature. If a user reacts to
        a PlayRequest message with a :fill: Emojii the user gets
        added as a subscriber in the PlayRequest. If a new player
        reacts to the message every subscriber and the PlayRequest
        author get notified.
        """
        if not gstate.CONFIG["TOGGLE_AUTO_DM"]:
            return

        if not utility.is_auto_dm_subscriber(reaction.message, self.bot, user, self.play_requests):
            return

        play_request = play_requests[reaction.message.id]
        play_request_author = play_request.author
        utility.add_subscriber_to_play_request(user, play_request)

        if str(reaction.emoji) == consts.EMOJI_PASS:
            for player in play_request.generate_all_players():
                if user == player:
                    play_request.remove_subscriber(user)
            return

        for player in play_request.generate_all_players():
            if player == play_request_author and player != user:
                await play_request_author.send(
                    consts.MESSAGE_AUTO_DM_CREATOR.format(user.name, str(reaction.emoji)))
            elif player != user:
                await player.send(
                    consts.MESSAGE_AUTO_DM_SUBSCRIBER.format(
                        user.name, play_request_author.name, str(reaction.emoji)))

        if len(play_request.subscribers) + 1 == 6:
            await reaction.channel.send(
                utility.switch_to_internal_play_request(reaction.message, play_request))
