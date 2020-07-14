import logging

import discord
from discord.ext import commands

from core import (
    checks,
    ocr,
    help_text
)

from core import DiscordBot
from riot import riot_commands
logger = logging.getLogger(__name__)


class RiotCog(commands.Cog, name='Riot Commands'):
    def __init__(self, bot: DiscordBot.KrautBot):
        self.bot = bot

    @commands.command(name='player', help = help_text.player_HelpText.text, brief = help_text.player_HelpText.brief, usage = help_text.player_HelpText.usage)
    @commands.check(checks.is_riot_enabled)
    @checks.is_in_channels("commands_member", "commands")
    async def player_(self, ctx, *summoner_name):
        logger.debug('!player command called')
        if len(list(summoner_name)) == 0:
            arg = None
        else:
            arg = summoner_name[0]
        await ctx.send(riot_commands.get_player_stats(ctx.message.author.name, arg, self.bot.config.get_guild_config(ctx.guild.id), self.bot.config.general_config))

    @commands.command(name='smurf', help = help_text.smurf_HelpText.text, brief = help_text.smurf_HelpText.brief, usage = help_text.smurf_HelpText.usage)
    @commands.check(checks.is_riot_enabled)
    @checks.is_in_channels("commands_member", "commands")
    async def smurf_(self, ctx, *summoner_name):
        logger.debug('!smurf command called')
        if len(list(summoner_name)) == 0:
            arg = None
        else:
            arg = summoner_name[0]
        await ctx.send(riot_commands.get_smurf(ctx.message.author.name, arg, self.bot.config.get_guild_config(ctx.guild.id), self.bot.config.general_config))

    @commands.command(name='bans', help = help_text.bans_HelpText.text, brief = help_text.bans_HelpText.brief, usage = help_text.bans_HelpText.usage)
    @commands.check(checks.is_riot_enabled)
    @discord.ext.commands.cooldown(rate=1, per=5)
    @checks.is_in_channels("commands_member", "commands")
    async def bans_(self, ctx, *team_names):
        logger.debug('!bans command called')
        folder_name = self.bot.config.get_guild_config(ctx.guild.id).folders_and_files.folder_champ_spliced.format(guild_id=ctx.guild.id)
        await ctx.send(
            riot_commands.calculate_bans_for_team(self.bot.config, team_names), file=discord.File(
                f'{folder_name}/image.jpg'))

    @commands.command(name='clash', help = help_text.clash_HelpText.text, brief = help_text.clash_HelpText.brief, usage = help_text.clash_HelpText.usage)
    @checks.is_in_channels("commands_member")
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
            self.bot.config.get_guild_config(ctx.guild.id).messages.bans.format(ocr.get_formatted_summoner_names()))

    @commands.command(name='clash_dates')
    @checks.is_in_channels("commands_member")
    async def clash_dates(self, ctx):
        riot_commands.update_state_clash_dates(self.bot.state, self.bot.config.general_config)
        await ctx.send(self.bot.state.clash_dates)


def setup(bot: DiscordBot.KrautBot):
    bot.add_cog(RiotCog(bot))
    logger.info('Riot cogs loaded')