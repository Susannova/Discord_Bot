from discord.ext import commands
from Create_Team.modules import riot, consts as CONSTS_

class PlayRequestCog(commands.Cog):
    def __init__(self, bot, check_handler):
        self.bot = bot
        self.check_handler = check_handler
    
    @commands.command(name='play-now')
    @check_handler.is_in_channels([CONSTS_.CHANNEL_PLAY_REQUESTS, CONSTS_.CHANNEL_BOT])
    async def play_now(ctx):
        bot.tmp_message_author = ctx.message.author
        await ctx.send(CONSTS_.MESSAGE_PLAY_NOW.format(ctx.message.author.mention))
