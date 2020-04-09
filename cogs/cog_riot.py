import logging

import discord
from discord.ext import commands

from core import (
    consts,
    checks,
    ocr
)

from riot import riot_commands

logger = logging.getLogger(consts.LOG_NAME)


class RiotCog(commands.Cog, name='Riot Commands'):
    @commands.command(name='player')

    @checks.is_riot_enabled()
    @checks.is_in_channels([consts.CHANNEL_COMMANDS, consts.CHANNEL_COMMANDS_MEMBER])
    async def player_(self, ctx, *summoner_name):
        if len(list(summoner_name)) == 0:
            arg = None
        else:
            arg = summoner_name[0]
        await ctx.send(riot_commands.get_player_stats(ctx.message.author.name, arg))

    @commands.command(name='smurf')
    @checks.is_riot_enabled()
    @checks.is_in_channels([consts.CHANNEL_COMMANDS, consts.CHANNEL_COMMANDS_MEMBER])
    async def smurf_(self, ctx, *summoner_name):
        if len(list(summoner_name)) == 0:
            arg = None
        else:
            arg = summoner_name[0]
        await ctx.send(riot_commands.get_smurf(ctx.message.author.name, arg))

    @commands.command(name='bans')
    @checks.is_riot_enabled()
    @discord.ext.commands.cooldown(rate=1, per=5)
    @checks.is_in_channels([consts.CHANNEL_COMMANDS, consts.CHANNEL_COMMANDS_MEMBER])
    async def bans_(self, ctx, *team_names):
        await ctx.send(
            riot_commands.calculate_bans_for_team(team_names), file=discord.File(
                f'./{consts.FOLDER_CHAMP_SPLICED}/image.jpg'))

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
