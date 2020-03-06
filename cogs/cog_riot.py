from discord.ext import commands
from Create_Team.modules import riot, consts as CONSTS_

class RiotCog(commands.Cog):
    def __init__(self, bot, check_handler):
        self.bot = bot
        self.check_handler = check_handler

    @commands.command(name='player')
    @check_handler.is_riot_enabled()
    async def player_(ctx):
        await ctx.send(riot.riot_command(ctx.message))

    @commands.command(name='smurf')
    @check_handler.is_riot_enabled()
    async def smurf_(ctx):
        await ctx.send(riot.riot_command(ctx.message))

    @commands.command(name='bans')
    @check_handler.is_riot_enabled()
    async def bans_(ctx):
        await ctx.send(
                riot.riot_command(ctx.message), file=discord.File(
                    f'./{CONSTS_.FOLDER_CHAMP_SPLICED}/image.jpg'))
