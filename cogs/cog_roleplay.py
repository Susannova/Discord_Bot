import logging
import random
import re
import typing

import discord
from discord.ext import commands

from core import (
    checks,
    DiscordBot
)

from riot import riot_commands

logger = logging.getLogger(__name__)

DICE_REGEX = r"[1-9][0-9]{0,2}(d|w)[1-9][0-9]{0,3}(\+[1-9][0-9]{0,3})?"

class RoleplayCog(commands.Cog, name='Roleplay Commands'):
    def __init__(self, bot: DiscordBot.KrautBot):
        self.bot = bot

    def parse_dice_string(self, dice_string):
        dice_string = dice_string.split('d')
        dice_string_add = 0
        if ('+' in dice_string[1]):
            dice_string_add = (dice_string[1].split('+'))
            dice_string[1] = dice_string_add[0]
            dice_string_add = dice_string_add[1]
        return int(dice_string[0]), int(dice_string[1]), int(dice_string_add)

    @commands.command(name='r')
    @checks.has_any_role("admin_id", "member_id")
    async def roll_dice(self, ctx: commands.Context, dice_string: str, gm_only: typing.Optional[bool]):
        logger.debug('!r command called')
        match = re.match(DICE_REGEX, dice_string)
        if match == None:
            await ctx.send('You did use the right command. The correct command syntax is: !r xdy')
            return
        dice_amount, dice_faces, dice_add = self.parse_dice_string(dice_string)
        dice_roll_summed_value = 0
        for i in range(int(dice_amount)):
            dice_roll_summed_value += random.randint(1, int(dice_faces))
        if dice_add != 0:
            dice_roll_summed_value += dice_add
        await ctx.send(f'{ctx.message.author.mention} I rolled {dice_string} for you wish resulted in {dice_roll_summed_value}.')


def setup(bot: DiscordBot.KrautBot):
    bot.add_cog(RoleplayCog(bot))
    logger.info('Debug cogs loaded')