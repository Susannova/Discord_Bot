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
from core.play_requests import PlayRequestCategory

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

        # add all messages in channel to gstate.message_cache
        if gstate.CONFIG["TOGGLE_AUTO_DELETE"] \
        and utility.is_in_channel(message, consts.CHANNEL_PLAY_REQUESTS):
            utility.update_message_cache(message)

        # auto react
        if gstate.CONFIG["TOGGLE_AUTO_REACT"] and utility.has_any_pattern(message):
            await message.add_reaction(self.bot.get_emoji(consts.EMOJI_ID_LIST[5]))
            await message.add_reaction(consts.EMOJI_PASS)

            _category = PlayRequestCategory.PLAY

            if utility.has_pattern(message, consts.PATTERN_CLASH):
                _category = PlayRequestCategory.CLASH
                self.play_requests[message.id] = PlayRequest(message, gstate.tmp_message_author, category=_category)
                self.play_requests[message.id].add_clash_date(gstate.clash_date)
            else:
                self.play_requests[message.id] = PlayRequest(message, gstate.tmp_message_author, category=_category)

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
                    for player in gstate.play_requests[message.id].generate_all_players():
                        await player.send(consts.MESSAGE_PLAY_REQUEST_REMINDER)


        # # command only
        # if gstate.CONFIG["TOGGLE_COMMAND_ONLY"] \
        # and utility.is_no_play_request_command(message, self.bot):
        #     await message.delete()

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        utility.clear_play_requests(message)
        [utility.clear_message_cache(message) for msg in gstate.message_cache if message in msg]

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        # auto dm

        if not gstate.CONFIG["TOGGLE_AUTO_DM"]:
            return

        if utility.is_user_bot(user, self.bot):
            return

        play_request = self.play_requests[reaction.message.id]

        if utility.is_play_request_author(user, play_request):
            await reaction.remove(user)
            return

        if str(reaction.emoji) == consts.EMOJI_PASS:
            for player in play_request.generate_all_players():
                if user == player:
                    play_request.remove_subscriber(user)
            return  

        if utility.is_already_subscriber(user, play_request):
            return
        
        utility.add_subscriber_to_play_request(user, play_request)

        # send auto dms to subscribers and author
        for player in play_request.generate_all_players():
            if player == play_request.author and player != user:
                await play_request.author.send(
                    consts.MESSAGE_AUTO_DM_CREATOR.format(user.name, str(reaction.emoji)))
            elif player != user:
                await player.send(
                    consts.MESSAGE_AUTO_DM_SUBSCRIBER.format(
                        use r.name, play_request.author.name, str(reaction.emoji)))

        if len(play_request.subscribers) + 1 == 5 and play_request.category == PlayRequestCategory.CLASH:
            await reaction.channel.send(consts.MESSAGE_CLASH_FULL.format(
                play_request.author, play_request.clash_date, utility.pretty_print_list(play_request.subscribers, play_request.author)
            ))

        if len(play_request.subscribers) + 1 > 5 and play_request.category == PlayRequestCategory.CLASH:
            await reaction.remove(user)
            await user.send('Das Clash Team ist zur Zeit leider schon voll.')

        if len(play_request.subscribers) + 1 == 6 and play_request.category == PlayRequestCategory.INTERN:
            await reaction.channel.send(
                utility.switch_to_internal_play_request(reaction.message, play_request))
