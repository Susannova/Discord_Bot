from discord.ext import tasks, commands
import discord
from core import (
	consts
)
from riot import riot_commands

class LoopCog(commands.Cog):
	"""A class for background tasks"""

	# @tasks.loop(hours = 24 * 7)
	# @tasks.loop(seconds = 5)
	@tasks.loop(hours = 24)
	async def print_leaderboard_weekly(self):
		await self.channel.send(file=discord.File(f'./{consts.FOLDER_CHAMP_SPLICED}/leaderboard.png'))
	
	@print_leaderboard_weekly.before_loop
	async def before_print_leaderboard_weekly(self):
		await self.bot.wait_until_ready()
		self.channel = self.bot.get_channel(639889605256019980)


	def __init__(self, bot : commands.bot):
		self.bot = bot
		self.print_leaderboard_weekly.start()