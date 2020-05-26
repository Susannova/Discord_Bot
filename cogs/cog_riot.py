import logging

import discord
from discord.ext import commands

from core import (
    checks,
    ocr,
    help_text
)

from core.config import CONFIG
from riot import riot_commands
from core.state import global_state as gstate
logger = logging.getLogger('cog_riot')


class RiotCog(commands.Cog, name='Riot Commands'):
    @commands.command(name='player', help = help_text.player_HelpText.text, brief = help_text.player_HelpText.brief, usage = help_text.player_HelpText.usage)
    @checks.is_riot_enabled()
    @checks.is_in_channels(CONFIG.channel_ids.commands_member + CONFIG.channel_ids.commands)
    async def player_(self, ctx, *summoner_name):
        logger.debug('!player command called')
        if len(list(summoner_name)) == 0:
            arg = None
        else:
            arg = summoner_name[0]
        await ctx.send(riot_commands.get_player_stats(ctx.message.author.name, arg))

    @commands.command(name='smurf', help = help_text.smurf_HelpText.text, brief = help_text.smurf_HelpText.brief, usage = help_text.smurf_HelpText.usage)
    @checks.is_riot_enabled()
    @checks.is_in_channels(CONFIG.channel_ids.commands_member + CONFIG.channel_ids.commands)
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
    @checks.is_in_channels(CONFIG.channel_ids.commands_member + CONFIG.channel_ids.commands)
    async def bans_(self, ctx, *team_names):
        logger.debug('!bans command called')
        await ctx.send(
            riot_commands.calculate_bans_for_team(team_names), file=discord.File(
                f'{CONFIG.folders_and_files.folder_champ_spliced}/image.jpg'))

    @commands.command(name='clash', help = help_text.clash_HelpText.text, brief = help_text.clash_HelpText.brief, usage = help_text.clash_HelpText.usage)
    @checks.is_in_channels(CONFIG.channel_ids.commands_member)
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
            CONFIG.messages.bans.format(ocr.get_formatted_summoner_names()))

    @commands.command(name='clash_dates')
    @checks.is_in_channels(CONFIG.channel_ids.commands_member)
    async def clash_dates(self, ctx):
        riot_commands.update_gstate_clash_dates()
        await ctx.send(gstate.clash_dates)


def setup(bot: commands.Bot):
    bot.add_cog(RiotCog())
    logger.info('Riot cogs loaded')