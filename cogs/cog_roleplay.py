import logging
import random
import re

from discord.ext import commands

from core import (
    checks,
    DiscordBot
)


logger = logging.getLogger(__name__)

DICE_REGEX = r"[1-9]?[0-9]{0,1}(d|w)[1-9][0-9]{0,3}((\+|\-)[1-9][0-9]{0,3})?!?"
MIN_INFINITE_EXPLOSION_CHAIN_DICE_FACES = 4


class RoleplayCog(commands.Cog, name='Roleplay Commands'):
    def __init__(self, bot: DiscordBot.KrautBot):
        self.bot = bot
    
    async def cog_check(self, ctx: commands.Context):
        return await checks.command_is_allowed(ctx)

    @commands.command(name='r')
    async def dice(self, ctx: commands.Context, dice_string: str):
        logger.debug('!r command called')
        match = self.parse_regex(dice_string)
        if match is None:
            await ctx.send('You did use the right command. The correct command syntax is: !r xdy')
            return
        results, dice_string_summed_value = self.get_dice_rolls(dice_string)
        output = f'{ctx.message.author.mention} I rolled {dice_string} for you which resulted in {dice_string_summed_value}.'
        output = self.format_output(output, results)
        await ctx.send(output)

    def parse_regex(self, dice_string):
        match = re.fullmatch(DICE_REGEX, dice_string)
        return match

    def get_dice_rolls(self, dice_string):
        dice_amount, dice_faces, dice_add, exploding = self.parse_dice_string(dice_string)
        dice_roll_summed_value = 0
        results = []
        for i in range(int(dice_amount)):
            dice_roll_summed_value += self.roll_dice(exploding, dice_faces, results)
        dice_roll_summed_value += dice_add
        dice_roll_summed_value = 1 if dice_roll_summed_value < 1 else dice_roll_summed_value
        return results, dice_roll_summed_value

    def parse_dice_string(self, dice_string):
        dice_string = self.split_dice_string(dice_string)
        exploding = self.parse_explosion(dice_string)
        dice_string_add, dice_string[1] = self.parse_add_substract(dice_string)
        dice_string[0] = self.parse_empty_prefix(dice_string)
        return int(dice_string[0]), int(dice_string[1]), int(dice_string_add), exploding

    def split_dice_string(self, dice_string):
        if 'd' in dice_string:
            dice_string = dice_string.split('d')
        elif 'w' in dice_string:
            dice_string = dice_string.split('w')
        return dice_string

    def parse_explosion(self, dice_string):
        exploding = False
        if '!' in dice_string[1]:
            dice_string[1] = dice_string[1].replace('!', '')
            exploding = True
        return exploding

    def parse_add_substract(self, dice_string):
        dice_string_add = 0
        if '+' in dice_string[1]:
            dice_string_add, dice_string[1] = self.parse_add_subtract_dice_string(dice_string[1], True)
        elif '-' in dice_string[1]:
            dice_string_add, dice_string[1] = self.parse_add_subtract_dice_string(dice_string[1], False)
        return dice_string_add, dice_string[1]

    def parse_add_subtract_dice_string(self, dice_string, is_adding):
        add_symbol = '-'
        if is_adding:
            add_symbol = '+'
        dice_string_add = (dice_string.split(add_symbol))
        dice_string = dice_string_add[0]
        dice_string_add = int(dice_string_add[1])
        if not is_adding:
            dice_string_add = dice_string_add * -1
        return dice_string_add, dice_string

    def parse_empty_prefix(self, dice_string):
        if dice_string[0] == '':
            dice_string[0] = '1'
        return dice_string[0]

    def roll_dice(self, exploding, dice_faces, results):
        local_dice_roll_sum = 0
        dice_roll = random.randint(1, int(dice_faces))
        local_dice_roll_sum += dice_roll
        explosion_string = ''
        if exploding:
            local_dice_roll_sum, explosion_string = self.apply_explosions(dice_faces, dice_roll, local_dice_roll_sum)
        if exploding:
            results.append((local_dice_roll_sum, explosion_string))
        else:
            results.append(local_dice_roll_sum)
        return local_dice_roll_sum

    def apply_explosions(self, dice_faces, dice_roll, dice_roll_summed_value):
        explosion_string = ''
        if dice_faces >= MIN_INFINITE_EXPLOSION_CHAIN_DICE_FACES:
            explosion_string, dice_roll_summed_value = self.apply_multiple_explosions(dice_faces, dice_roll_summed_value, explosion_string, dice_roll)
        else:
            explosion_string, dice_roll_summed_value = self.apply_single_explosion(dice_faces, dice_roll_summed_value, explosion_string, dice_roll)
        if explosion_string != '':
            explosion_string = f'({dice_faces})' + explosion_string
        return dice_roll_summed_value, explosion_string

    def apply_multiple_explosions(self, dice_faces, dice_roll_summed_value, explosion_string, dice_roll):
        while dice_roll == dice_faces:
            dice_roll = random.randint(1, int(dice_faces))
            dice_roll_summed_value += dice_roll
            explosion_string += f'({dice_roll})'
        return explosion_string, dice_roll_summed_value

    def apply_single_explosion(self, dice_faces, dice_roll_summed_value, explosion_string, dice_roll):
        if dice_roll == dice_faces:
            dice_roll = random.randint(1, int(dice_faces))
            dice_roll_summed_value += dice_roll
            explosion_string += f'({dice_roll})'
        return explosion_string, dice_roll_summed_value

    def format_output(self, output, results):
        if len(results) > 1:
            output += '\nResults: '
            for result in results:
                if not isinstance(result, int):
                    output += f'{result[0]}{result[1]}, '
                else:
                    output += f'{result}, '
            output = output[:-2]
        else:
            if not isinstance(results[0], int):
                output += f' {results[0][1]}'
        return output


def setup(bot: DiscordBot.KrautBot):
    bot.add_cog(RoleplayCog(bot))
    logger.info('Debug cogs loaded')
