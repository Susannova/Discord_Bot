import asyncio
from importlib import reload
import logging


from discord.ext import commands

from core import (
    consts,
    checks
)

from core.state import global_state as gstate

logger = logging.getLogger(consts.LOG_NAME)


class DebugCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='version')
    @checks.is_in_channels([])
    @commands.has_role(consts.ROLE_ADMIN_ID)
    async def version_(self, ctx):
        await ctx.send(gstate.VERSION)

    @commands.command(name='status')
    @checks.is_in_channels([])
    @commands.has_role(consts.ROLE_ADMIN_ID)
    async def status_(self, ctx):
        await ctx.send("Bot is alive.")

    @commands.command(name='reload-config')
    @checks.is_in_channels([])
    @commands.has_role(consts.ROLE_ADMIN_ID)
    async def reload_config(self, ctx):
        global consts
        await ctx.send("Reload configuration.json:")
        gstate.read_config()
        consts = reload(consts)
        gstate.get_version()
        await ctx.send("Done.")

    @commands.command(name='enable-debug')
    @checks.is_in_channels([])
    @checks.is_debug_config_enabled()
    @commands.has_role(consts.ROLE_ADMIN_ID)
    async def enable_debug(self, ctx):
        gstate.debug = True
        await ctx.send("Debugging is activated for one hour.")
        await asyncio.sleep(3600)
        gstate.debug = False
        gstate.CONFIG["TOGGLE_DEBUG"] = False
        gstate.write_and_reload_config(gstate.CONFIG)
        await ctx.send("Debugging is deactivated.")

    @commands.command(name='print')
    @checks.is_in_channels([])
    @checks.is_debug_enabled()
    @commands.has_role(consts.ROLE_ADMIN_ID)
    async def print_(self, ctx, arg):
        # return_string = ast.literal_eval(arg)
        # less safe but more powerful
        return_string = eval(arg)
        await ctx.send(return_string)
        print(return_string)

    @commands.command(name='end')
    @checks.is_in_channels([])
    @commands.has_role(consts.ROLE_ADMIN_ID)
    @commands.is_owner()
    async def end_(self, ctx):
        await ctx.send('Bot is shut down!')
        await self.bot.logout()
