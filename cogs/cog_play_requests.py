
import re
import logging
import asyncio

from discord.ext import commands

from core import (
    checks,
    exceptions,
    timers,
    help_text,
    DiscordBot
)

from core.config import CONFIG
from core.state import global_state as gstate
from core.play_requests import PlayRequest, PlayRequestCategory

logger = logging.getLogger(__name__)



class PlayRequestsCog(commands.Cog, name='Play-Request Commands'):
    def __init__(self, bot: DiscordBot.KrautBot):
        self.bot = bot

    @commands.command(name='play', help = help_text.play_HelpText.text, brief = help_text.play_HelpText.brief, usage = help_text.play_HelpText.usage)
    @checks.is_in_channels(CONFIG.channel_ids.play_request)
    async def play_(self, ctx, game_name, _time, *args):
        is_not_now = True
        logger.info('Create a play request')
        game_name = game_name.upper()
        message = 'Something went wrong.'
        if game_name == 'CLASH':
            await self.create_clash(ctx, _time)
            return
        game = CONFIG.get_game(game_name)
        if _time == 'now':
            arg = None if len(list(args)) == 0 else args[0]
            if arg != None:
                if int(arg[1:]) > CONFIG.basic_config.play_now_time_add_limit or int(arg[1:]) <= 0:
                    raise exceptions.LimitReachedException()
                play_request_time = timers.add_to_current_time(int(arg[1:]))
                message = CONFIG.messages.play_at.format(
                    role_mention=ctx.guild.get_role(game.role_id).mention,
                    player=ctx.message.author.mention,
                    game=game.name_long,
                    time=play_request_time
                )
            else:
                is_not_now = False
                message = CONFIG.messages.play_now.format(
                    role_mention=ctx.guild.get_role(game.role_id).mention,
                    player=ctx.message.author.mention,
                    game=game.name_long
                )
        else:
            if len(re.findall('([0-2])?[0-9]:[0-5][0-9]', _time)) == 0:
                exception_str = exceptions.BadArgumentFormat()
                logger.error(exception_str)
                raise exception_str
            message = CONFIG.messages.play_at.format(
                role_mention=ctx.guild.get_role(game.role_id).mention,
                player=ctx.message.author.mention,
                game=game.name_long,
                time=_time
            )
        
        play_request_message = await ctx.send(message)
        _category = self.get_category(game_name)
        play_request = PlayRequest(play_request_message.id, ctx.message.author.id, category=_category)
        await self.add_play_request_to_gstate(play_request)
        await self.add_auto_reaction(ctx, play_request_message)

        await ctx.message.delete()

        if is_not_now:
            await self.auto_reminder(play_request_message)

    async def add_auto_reaction(self, ctx, play_request_message):
        await play_request_message.add_reaction(CONFIG.basic_config.emoji_join)
        await play_request_message.add_reaction(CONFIG.basic_config.emoji_pass)


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
                await player.send(CONFIG.messages.play_request_reminder)

    async def create_clash(self, ctx, date):
        logger.debug('Create a clash request')
        gstate.tmp_message_author = ctx.message.author
        gstate.clash_date = date
        play_request_message = await ctx.send(CONFIG.messages.clash_create.format(
            role_mention=ctx.guild.get_role(CONFIG.get_game("clash").role_id).mention,
            player=ctx.message.author.mention,
            date=date
            )
        )
        _category = self.get_category("CLASH")
        play_request = PlayRequest(play_request_message.id, ctx.message.author.id, category=_category)
        await self.add_play_request_to_gstate(play_request)
        await self.add_auto_reaction(ctx, play_request_message)
        

        

def setup(bot: DiscordBot.KrautBot):
    bot.add_cog(PlayRequestsCog(bot))
    logger.info('Play request cogs loaded')
