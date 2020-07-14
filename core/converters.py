import re
from discord.ext import commands

class ArgsToDict(commands.Converter):
	async def convert(self, ctx: commands.Context, args: str) -> dict:
		""" Converts args to a dict.
		Important: Spaces in args will be ignored!

		Format of args has to be keys and a value for each key. The assignment is done with a ':' or a '='
		the key values pairs are seperated by ',' or ';'.
		"""

		# This is a generator that yields generators that yield at first a key and then a value as a string.
		dict_list = (
			(key_value for key_value in re.split("=|:", arg)) for arg in re.split(",|;", args.replace(" ", ""))
		)

		return dict(dict_list)