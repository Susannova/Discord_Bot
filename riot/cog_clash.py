import logging

logger = logging.getLogger(__name__)

import dataclasses

from discord.ext import commands

from core import (
    DiscordBot,
    converters
)


@dataclasses.dataclass
class Ban_Pick:
    prio: int = None
    champ: str = None
    pos: str = None
    pick_at: int = None

class ClashCog(commands.Cog, name='Utility Commands'):
    def __init__(self, bot: DiscordBot.KrautBot):
        self.bot = bot

        self.__bans_list = []
        self.__picks_list = []

    
    @commands.group()
    async def clash(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send('Picking:')
            for pick in self.__picks_list:
                await ctx.send(str(dataclasses.asdict(pick)))
            await ctx.send('Baning:')
            for ban in self.__bans_list:
                await ctx.send(str(dataclasses.asdict(ban)))
    
    @clash.group()
    async def bans(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            for ban in self.__bans_list:
                await ctx.send(str(dataclasses.asdict(ban)))
    
    @bans.command(name="add")
    async def add_ban(self, ctx: commands.Context, *, ban_dict: converters.ArgsToDict):
        self.__bans_list.append(Ban_Pick(**ban_dict))
    
    @clash.group()
    async def picks(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            for pick in self.__picks_list:
                await ctx.send(str(dataclasses.asdict(pick)))
    
    @picks.command(name="add")
    async def add_pick(self, ctx: commands.Context, *, pick_dict: converters.ArgsToDict):
        self.__picks_list.append(Ban_Pick(**pick_dict))
    
    @clash.command()
    async def reset(self, ctx: commands.Context):
        for ban in self.__bans_list:
            del ban
        self.__bans_list = []

        for pick in self.__picks_list:
            del pick
        self.__picks_list = []


def setup(bot: DiscordBot.KrautBot):
    bot.add_cog(ClashCog(bot))
    logger.info('Clash cog loaded')
