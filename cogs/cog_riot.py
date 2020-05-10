import logging

import discord
from discord.ext import commands

from core import (
    consts,
    checks,
    ocr,
    help_text
)

from riot import riot_commands

logger = logging.getLogger('cog_riot')


class RiotCog(commands.Cog, name='Riot Commands'):
    @commands.command(name='player', help = help_text.player_HelpText.text, brief = help_text.player_HelpText.brief, usage = help_text.player_HelpText.usage)
    @checks.is_riot_enabled()
    @checks.is_in_channels([consts.CHANNEL_COMMANDS, consts.CHANNEL_COMMANDS_MEMBER])
    async def player_(self, ctx, *summoner_name):
        logger.debug('!player command called')
        if len(list(summoner_name)) == 0:
            arg = None
        else:
            arg = summoner_name[0]
        await ctx.send(riot_commands.get_player_stats(ctx.message.author.name, arg))

    @commands.command(name='smurf', help = help_text.smurf_HelpText.text, brief = help_text.smurf_HelpText.brief, usage = help_text.smurf_HelpText.usage)
    @checks.is_riot_enabled()
    @checks.is_in_channels([consts.CHANNEL_COMMANDS, consts.CHANNEL_COMMANDS_MEMBER])
    async def smurf_(self, ctx, *summoner_name):
        logger.debug('!smurf command called')
        if len(list(summoner_name)) == 0:
            arg = None
        else:
            arg = summoner_name[0]
        await ctx.send(riot_commands.get_smurf(ctx.message.author.name, arg))

    @commands.command(name='bans', help = help_text.bans_HelpText.text, brief = help_text.bans_HelpText.brief, usage = help_text.bans_HelpText.usage)
    @checks.is_riot_enabled()
    @discord.ext.commands.cooldown(rate=1, per=5)
    @checks.is_in_channels([consts.CHANNEL_COMMANDS, consts.CHANNEL_COMMANDS_MEMBER])
    async def bans_(self, ctx, *team_names):
        logger.debug('!bans command called')
        await ctx.send(
            riot_commands.calculate_bans_for_team(team_names), file=discord.File(
                f'./{consts.FOLDER_CHAMP_SPLICED}/image.jpg'))

    @commands.command(name='clash', help = help_text.clash_HelpText.text, brief = help_text.clash_HelpText.brief, usage = help_text.clash_HelpText.usage)
    @checks.is_in_channels([consts.CHANNEL_COMMANDS_MEMBER])
    @checks.has_n_attachments(1)
    async def clash_(self, ctx):
        logger.debug('!clash command called')
        attached_image = ctx.message.attachments[0]
        attached_image_file_name = attached_image.filename
        await attached_image.save(attached_image_file_name)
        ocr.set_image_file_name(attached_image_file_name)
        await ctx.send(ocr.run_ocr())
        ocr.clean_up_image(attached_image_file_name)
        await ctx.send(
            consts.MESSAGE_BANS.format(ocr.get_formatted_summoner_names()))
