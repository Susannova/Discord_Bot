
import re
import logging
import asyncio
import datetime
import typing

import discord
from discord.ext import commands

from core import (
    checks,
    exceptions,
    timers,
    help_text,
    DiscordBot
)

from core.play_requests import PlayRequest

logger = logging.getLogger(__name__)



class PlayRequestsCog(commands.Cog, name='Play-Request Commands'):
    def __init__(self, bot: DiscordBot.KrautBot):
        self.bot = bot

    @commands.command(name='play', help = help_text.play_HelpText.text, brief = help_text.play_HelpText.brief, usage = help_text.play_HelpText.usage)
    @checks.is_in_channels("play_request")
    async def play_(self, ctx: commands.Context, game_name, time_string: str, minutes_delta: typing.Optional[int] = 0):
        guild_config = self.bot.config.get_guild_config(ctx.guild.id)
        
        logger.info('Create a play request')
        game_name = game_name.upper()
        message = 'Something went wrong.'
        # if game_name == 'CLASH':
        #     await self.create_clash(ctx, time_string)
        #     return
        
        game = guild_config.get_game(game_name)
        
        is_now = True if time_string == 'now' else False
        
        if is_now:
            is_now = True if minutes_delta == 0 else False
            if minutes_delta < 0 or minutes_delta > guild_config.unsorted_config.play_now_time_add_limit:
                await ctx.send("Bitte benutze für die Zeitdifferenz nur positive Zahlen kleiner als {guild_config.unsorted_config.play_now_time_add_limit}")
                return
            time_delta = datetime.timedelta(minutes=minutes_delta)
            play_time = datetime.datetime.now() + time_delta
        else:
            time_string_splitted = time_string.split(":")
            if len(time_string_splitted) > 2:
                await ctx.send("Bitte benutzte für die Zeit das Format 'hh:mm'.")
                return
            else:
                time_now = datetime.datetime.now()
                play_time = time_now.replace(hour=int(time_string_splitted[0]), minute=int(time_string_splitted[1]))
                
                if time_now > play_time:
                    play_time += datetime.timedelta(days=1)


        message_unformated = guild_config.messages.play_now if is_now else guild_config.messages.play_at
        
        message = message_unformated.format(
                role_mention=ctx.guild.get_role(game.role_id).mention,
                creator=ctx.message.author.mention,
                player=ctx.message.author.mention,
                game=game.name_long,
                time=play_time.strftime("%H:%M")
            )
        
        play_request_message = await ctx.send(message)
        _category = game.name_short
        play_request = PlayRequest(play_request_message.id, ctx.message.author.id, category=_category, play_time=play_time)
        
        self.bot.state.get_guild_state(ctx.guild.id).add_play_request(play_request)
        await self.add_auto_reaction(ctx, play_request_message)

        await ctx.message.delete()

        if not is_now:
            await play_request.auto_reminder(guild_config=guild_config, bot=self.bot)

    async def add_auto_reaction(self, ctx: commands.Context, play_request_message: discord.Message):
        guild_config = self.bot.config.get_guild_config(ctx.guild.id)

        await play_request_message.add_reaction(guild_config.unsorted_config.emoji_join)
        await play_request_message.add_reaction(guild_config.unsorted_config.emoji_pass)


    # async def create_clash(self, ctx, date):
    #     guild_config = self.bot.config.get_guild_config(ctx.guild.id)
    #     logger.debug('Create a clash request')
    #     self.bot.state.get_guild_state(ctx.guild.id).clash_date = date
    #     play_request_message = await ctx.send(guild_config.messages.clash_create.format(
    #         role_mention=ctx.guild.get_role(guild_config.get_game("clash").role_id).mention,
    #         player=ctx.message.author.mention,
    #         date=date
    #         )
    #     )
    #     _category = "clash"
    #     play_request = PlayRequest(play_request_message.id, ctx.message.author.id, category=_category)
    #     await self.add_play_request_to_state(ctx.guild.id, play_request)
    #     await self.add_auto_reaction(ctx, play_request_message)
        

        

def setup(bot: DiscordBot.KrautBot):
    bot.add_cog(PlayRequestsCog(bot))
    logger.info('Play request cogs loaded')
