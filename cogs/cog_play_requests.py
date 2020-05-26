
import re
import logging
import asyncio

from discord.ext import commands

from core import (
    consts,
    checks,
    exceptions,
    timers,
    help_text
)

from core.state import global_state as gstate
from core.play_requests import PlayRequest, PlayRequestCategory

logger = logging.getLogger('cog_play_request')



class PlayRequestsCog(commands.Cog, name='Play-Request Commands'):
    def __init__(self, bot: commands.bot):
        self.bot = bot

    @commands.command(name='play', help = help_text.play_HelpText.text, brief = help_text.play_HelpText.brief, usage = help_text.play_HelpText.usage)
    @checks.is_in_channels([consts.CHANNEL_PLAY_REQUESTS])
    async def play_(self, ctx, game_name, _time, *args):
        is_not_now = True
        logger.info('Create a play request')
        game_name = game_name.upper()
        message = 'Something went wrong.'
        if game_name == 'CLASH':
            await self.create_clash(ctx, _time)
            return
        if _time == 'now':
            arg = None if len(list(args)) == 0 else args[0]
            if arg != None:
                if int(arg[1:]) > consts.PLAY_NOW_TIME_ADD_LIMIT or int(arg[1:]) <= 0:
                    raise exceptions.LimitReachedException()
                play_request_time = timers.add_to_current_time(int(arg[1:]))
                message = consts.MESSAGE_PLAY_AT.format(ctx.guild.get_role(consts.GAME_NAME_TO_ROLE_ID_DICT[game_name]).mention, ctx.message.author.mention, consts.GAME_NAME_DICT[game_name], play_request_time)
            else:
                is_not_now = False
                message = consts.MESSAGE_PLAY_NOW.format(ctx.guild.get_role(consts.GAME_NAME_TO_ROLE_ID_DICT[game_name]).mention, ctx.message.author.mention, consts.GAME_NAME_DICT[game_name])
        else:
            if len(re.findall('([0-2])?[0-9]:[0-5][0-9]', _time)) == 0:
                exception_str = exceptions.BadArgumentFormat()
                logger.error(exception_str)
                raise exception_str
            message = consts.MESSAGE_PLAY_AT.format(ctx.guild.get_role(consts.GAME_NAME_TO_ROLE_ID_DICT[game_name]).mention, ctx.message.author.mention, consts.GAME_NAME_DICT[game_name], _time)
        
        play_request_message = await ctx.send(message)
        _category = self.get_category(game_name)
        play_request = PlayRequest(play_request_message.id, ctx.message.author.id, category=_category)
        await self.add_play_request_to_gstate(play_request)
        await self.add_auto_reaction(ctx, play_request_message)

        await ctx.message.delete()

        if is_not_now:
            await self.auto_reminder(play_request_message)

    async def add_auto_reaction(self, ctx, play_request_message):
        await play_request_message.add_reaction(consts.EMOJI_JOIN)
        await play_request_message.add_reaction(consts.EMOJI_PASS)


    async def add_play_request_to_gstate(self, play_request):
        logger.debug("Add the message id %s to the global state", play_request.message_id)
        gstate.play_requests[play_request.message_id] = play_request
    
    def get_category(self, game_name):
        _category = None
        if game_name == 'LOL':
            _category = PlayRequestCategory.LOL
        elif game_name == 'APEX':
            _category = PlayRequestCategory.APEX
        elif game_name == 'CSGO':
            _category = PlayRequestCategory.CSGO
        elif game_name == 'RL':
            _category = PlayRequestCategory.RL
        elif game_name == 'VAL':
            _category = PlayRequestCategory.VAL
        elif game_name == 'CLASH':
            _category = PlayRequestCategory.CLASH
        return _category


    async def auto_reminder(self, message):
        logger.debug("Create an auto reminder for play request with id %s", message.id)
        time_difference = timers.get_time_difference(message.content)
        if time_difference > 0:
            await asyncio.sleep(time_difference)
            for player_id in gstate.play_requests[message.id].generate_all_players():
                player = self.bot.get_user(player_id)
                await player.send(consts.MESSAGE_PLAY_REQUEST_REMINDER)

    async def create_clash(self, ctx, date):
        logger.debug('Create a clash request')
        gstate.tmp_message_author = ctx.message.author
        gstate.clash_date = date
        play_request_message = await ctx.send(consts.MESSAGE_CLASH_CREATE.format(
            ctx.guild.get_role(consts.GAME_NAME_TO_ROLE_ID_DICT["LOL"]).mention, ctx.message.author.mention, date))
        _category = self.get_category("CLASH")
        play_request = PlayRequest(play_request_message.id, ctx.message.author.id, category=_category)
        await self.add_play_request_to_gstate(play_request)
        await self.add_auto_reaction(ctx, play_request_message)
        

        

def setup(bot: commands.Bot):
    bot.add_cog(PlayRequestsCog(bot))
    logger.info('Play request cogs loaded')
