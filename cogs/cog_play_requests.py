
import re
import logging
import asyncio

from discord.ext import commands

from core import (
    consts,
    bot_utility as utility,
    ocr,
    checks,
    exceptions,
    timers
)

from core.state import global_state as gstate
from core.play_requests import PlayRequest, PlayRequestCategory

logger = logging.getLogger(consts.LOG_NAME)


class PlayRequestsCog(commands.Cog):
    @commands.command(name='create-clash')
    @checks.is_in_channels([consts.CHANNEL_CLASH])
    async def create_clash(self, ctx, arg):
        gstate.tmp_message_author = ctx.message.author
        gstate.clash_date = arg
        await ctx.send(consts.MESSAGE_CLASH_CREATE.format(
            ctx.message.author.mention, arg))

    @commands.command(name='play')
    @checks.is_in_channels([consts.CHANNEL_PLAY_REQUESTS])
    async def play_(self, ctx, game_name, _time):
        game_name = game_name.upper()
        message = 'Something went wrong.'
        if _time == 'now':
            message = consts.MESSAGE_PLAY_NOW.format(ctx.guild.get_role(consts.GAME_NAME_TO_ROLE_ID_DICT[game_name]).mention, ctx.message.author.mention, consts.GAME_NAME_DICT[game_name])
        else:
            if len(re.findall('[0-2][0-9]:[0-5][0-9]', _time)) == 0:
                raise exceptions.BadArgumentFormat()
            message = consts.MESSAGE_PLAY_AT.format(ctx.guild.get_role(consts.GAME_NAME_TO_ROLE_ID_DICT[game_name]).mention, ctx.message.author.mention, consts.GAME_NAME_DICT[game_name], _time)
        play_request_message = await ctx.send(message)
        _category = self.get_category(game_name)
        gstate.play_requests[play_request_message.id] = PlayRequest(play_request_message, ctx.message.author, category=_category)
        await play_request_message.add_reaction(ctx.bot.get_emoji(consts.EMOJI_ID_LIST[5]))
        await play_request_message.add_reaction(consts.EMOJI_PASS)

        if not utility.is_in_channel(ctx.message, consts.CHANNEL_BOT):
            for member in ctx.message.guild.members:
                for role in member.roles:
                    if role.id == consts.GAME_NAME_TO_ROLE_ID_DICT[game_name]:
                        if member.id != ctx.message.author.id:
                            await member.send(consts.MESSAGE_PLAY_REQUEST_CREATED.format(ctx.message.author.name, consts.GAME_NAME_DICT[game_name], play_request_message.jump_url))

        if _time != 'now':
            await self.auto_reminder(play_request_message)

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
        return _category

    async def auto_reminder(self, message):
        time_difference = timers.get_time_difference(message.content)
        if time_difference > 0:
            await asyncio.sleep(time_difference)
            for player in gstate.play_requests[message.id].generate_all_players():
                await player.send(consts.MESSAGE_PLAY_REQUEST_REMINDER)

    @commands.command(name='clash')
    @checks.is_in_channels([consts.CHANNEL_COMMANDS_MEMBER])
    @checks.has_n_attachments(1)
    async def clash_(self, ctx):
        attached_image = ctx.message.attachments[0]
        attached_image_file_name = attached_image.filename
        await attached_image.save(attached_image_file_name)
        ocr.set_image_file_name(attached_image_file_name)
        await ctx.send(ocr.run_ocr())
        ocr.clean_up_image(attached_image_file_name)
        await ctx.send(
            consts.MESSAGE_BANS.format(ocr.get_formatted_summoner_names()))
