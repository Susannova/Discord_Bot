"""Main module. Stars and defines the Discord Bot (KrautBot).
"""
import logging
import time
import asyncio

import discord
from discord.ext import commands

from core import (
    bot_utility as utility,
    consts as CONSTS_,
    reminder
)
from core.state import global_state as gstate
from cogs import (
    kraut
)


logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)
discord.voice_client.VoiceClient.warn_nacl = False

BOT_TOKENS = utility.read_config_file('bot')


class KrautBot(commands.Bot):
    """The actual bot.
    """
    BOT_TOKEN = str(BOT_TOKENS['token'])

    def __init__(self):
        """ Sets the Command Prefix and then 
        call the __init__ method of the commands.Bot
        Class.
        """
        super().__init__(command_prefix=CONSTS_.COMMAND_PREFIX)

    def run(self):
        """ Runs the Bot using the Token defined
        in BOT_TOKEN.
        """
        try:
            super().run(self.BOT_TOKEN)
        except KeyboardInterrupt:
            logging.warning('Stopped Bot due to Keyboard Interrupt.')

    async def on_ready(self):
        print('We have logged in as {0.user}'.format(bot))

    async def on_member_join(self, member):
        """Automatically assigns lowest role to
        anyone that joins the server.
        """
        await member.edit(roles=utility.get_auto_role_list(member))

    async def on_message(self, message):
        if isinstance(message.channel, discord.DMChannel):
            return

        # auto react
        if gstate.CONFIG["TOGGLE_AUTO_REACT"] and utility.has_any_pattern(message):
            await message.add_reaction(bot.get_emoji(CONSTS_.EMOJI_ID_LIST[5]))
            await message.add_reaction(CONSTS_.EMOJI_PASS)

            gstate.play_requests[message.id] = [[gstate.tmp_message_author, time.time()]]

            for deletable_message in utility.process_deleteables(message):
                await deletable_message.delete()

            # auto reminder
            if utility.has_pattern(message, CONSTS_.PATTERN_PLAY_REQUEST):
                time_difference = reminder.get_time_difference(message.content)
                if time_difference > 0:
                    await asyncio.sleep(time_difference)
                    for player in gstate.play_requests[message.id]:
                        await player[0].send(CONSTS_.MESSAGE_PLAY_REQUEST_REMINDER)

        # auto delete
        if gstate.CONFIG["TOGGLE_AUTO_DELETE"] \
        and utility.is_in_channel(message, CONSTS_.CHANNEL_PLAY_REQUESTS):
            gstate.message_cache = utility.update_message_cache(message, gstate.message_cache)

        # command only
        if gstate.CONFIG["TOGGLE_COMMAND_ONLY"] \
        and utility.is_no_play_request_command(message, bot):
            await message.delete()

        await super().process_commands(message)

    async def on_message_delete(self, message):
        utility.clear_play_requests(message)
        utility.clear_message_cache(message)

    async def on_reaction_add(self, reaction, user):
        # auto dm

        if not gstate.CONFIG["TOGGLE_AUTO_DM"]:
            return

        if not utility.is_auto_dm_subscriber(reaction.message, bot, user, gstate.play_requests):
            return

        message_id = reaction.message.id
        play_request_author = gstate.play_requests[message_id][0][0]
        utility.add_subscriber_to_play_request(message_id, user, gstate.play_requests)
        # if reaction is 'EMOJI_PASS' delete player from play_request and return
        if str(reaction.emoji) == CONSTS_.EMOJI_PASS:
            for player in gstate.play_requests[message_id]:
                if user == player[0]:
                    gstate.play_requests[message_id].remove(player)
            return

        # send auto dms to subscribers and author
        for player in gstate.play_requests[message_id]:
            if player[0] == play_request_author and player[0] != user:
                await play_request_author.send(
                    CONSTS_.MESSAGE_AUTO_DM_CREATOR.format(user.name, str(reaction.emoji)))
            elif player[0] != user:
                await player[0].send(
                    CONSTS_.MESSAGE_AUTO_DM_SUBSCRIBER.format(
                        user.name, play_request_author.name, str(reaction.emoji)))
        # switch to internal play request
        # if more than 6 players(author + 5 players_known) are subscribed
        if len(gstate.play_requests[message_id]) == 6:
            await reaction.channel.send(
                utility.switch_to_internal_play_request(message, gstate.play_requests))


if __name__ == '__main__':
    bot = KrautBot()
    try:
        print("Start Bot")
        logging.info("Start Bot")
        bot.add_cog(kraut.KrautCogs(bot))
        bot.run()
        print("End Bot")
        logging.info("End")
    except discord.LoginFailure:
        logging.warning('Failed to login due to improper Token.')
