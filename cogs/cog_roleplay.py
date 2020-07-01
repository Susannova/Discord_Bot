import logging
import random


import discord
from discord.ext import commands

from core import (
    checks,
    DiscordBot
)

from riot import riot_commands

logger = logging.getLogger(__name__)


class RoleplayCog(commands.Cog, name='Roleplay Commands'):
    def __init__(self, bot: DiscordBot.KrautBot):
        self.bot = bot

    def parse_dice_string(self, dice_string):
        dice_string = dice_string.split('d')
        return dice_string[0], dice_string[1]

    @commands.command(name='r')
    @checks.has_any_role("admin_id", "member_id")
    async def roll_dice(self, ctx: commands.Context, dice_string: str):
        logger.debug('!r command called')
        dice_amount, dice_faces = parse_dice_string(dice_string)
        dice_roll_summed_value = 0
        for i in range(dice_amount):
            dice_roll_summed_value += random.randint(0, dice_faces)
        await ctx.send(f'{ctx.message.author.mention} I rolled {dice_string} for you wish resulted in {dice_roll_summed_value}.')

def setup(bot: DiscordBot.KrautBot):
    bot.add_cog(RoleplayCog(bot))
    logger.info('Debug cogs loaded')