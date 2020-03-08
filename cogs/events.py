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

        # auto react
        if gstate.CONFIG["TOGGLE_AUTO_REACT"] and utility.has_any_pattern(message):
            await message.add_reaction(self.bot.get_emoji(consts.EMOJI_ID_LIST[5]))
            await message.add_reaction(consts.EMOJI_PASS)

            gstate.play_requests[message.id] = PlayRequest(message, gstate.tmp_message_author)

            for deletable_message in utility.process_deleteables(message):
                await deletable_message.delete()

            # auto reminder
            if utility.has_pattern(message, consts.PATTERN_PLAY_REQUEST):
                time_difference = reminder.get_time_difference(message.content)
                if time_difference > 0:
                    await asyncio.sleep(time_difference)
                    for player in gstate.play_requests[message.id].generate_all_players():
                        await player.send(consts.MESSAGE_PLAY_REQUEST_REMINDER)

        # auto delete
        if gstate.CONFIG["TOGGLE_AUTO_DELETE"] \
        and utility.is_in_channel(message, consts.CHANNEL_PLAY_REQUESTS):
            gstate.message_cache = utility.update_message_cache(message, gstate.message_cache)

        # command only
        if gstate.CONFIG["TOGGLE_COMMAND_ONLY"] \
        and utility.is_no_play_request_command(message, self.bot):
            await message.delete()


    @commands.Cog.listener()
    async def on_message_delete(self, message):
        utility.clear_play_requests(message)
        utility.clear_message_cache(message)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        # auto dm

        if not gstate.CONFIG["TOGGLE_AUTO_DM"]:
            return

        if not utility.is_auto_dm_subscriber(reaction.message, self.bot, user):
            return

        play_request = gstate.play_requests[message_id]
        message_id = reaction.message.id
        play_request_author = play_request.message_author
        utility.add_subscriber_to_play_request(user, play_request)
        # if reaction is 'EMOJI_PASS' delete player from play_request and return
        if str(reaction.emoji) == consts.EMOJI_PASS:
            for player in play_request.generate_all_players():
                if user == player:
                    play_request.remove_subscriber(user)
            return

        # send auto dms to subscribers and author
        for player in play_request.generate_all_players():
            if player == play_request_author and player != user:
                await play_request_author.send(
                    consts.MESSAGE_AUTO_DM_CREATOR.format(user.name, str(reaction.emoji)))
            elif player != user:
                await player.send(
                    consts.MESSAGE_AUTO_DM_SUBSCRIBER.format(
                        user.name, play_request_author.name, str(reaction.emoji)))
        # switch to internal play request
        # if more than 6 players(author + 5 players_known) are subscribed
        if len(play_request.subscribers) + 1 == 6:
            await reaction.channel.send(
                utility.switch_to_internal_play_request(reaction.message, play_request))
