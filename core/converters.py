import re
import datetime

from discord.ext import commands

from core.config import Game

class ArgsToDict(commands.Converter):
    async def convert(self, ctx: commands.Context, args: str) -> dict:
        """ Converts args to a dict.
        Important: Spaces in args will be ignored!

        Format of args has to be keys and a value for each key. The assignment is done with a ':' or a '='
        the key values pairs are seperated by ',' or ';'.
        """

        args_formatted = args.replace(" ", "").replace("=", ":").replace("(", "[").replace(";", ",").replace(")", "]")

        # This is a generator that yields generators that yield at first a key and then a value. The value is either a string or a list. Short but really ugly..
        dict_list = (
            (key_val_str if re.fullmatch("[\[].*[\]]", key_val_str) is None else [item for item in re.findall("[^,\[\]]+", key_val_str)] for key_val_str in arg.split(":")) for arg in re.findall("[^,]*?:[\[].*?[\]]|[^,]*?:[^\[\],]*", args_formatted)
        )

        return dict(dict_list)

class StrToTime(commands.Converter):
    async def convert(self, ctx: commands.Context, time_str: str) -> datetime.datetime:
        """ Converts a time str in a datetime.datetime

        Args:
            time_str (str): has to be a time in the format hh:mm or +x followed optionally (default m) by "m", "h" or "d" without spaces

        Raises:
            RuntimeError: Raised if format of time_str is wrong

        Returns:
            datetime.timedelta: The timedelta
        """

        if re.fullmatch("\+\d*([mhd]|$)", time_str) is not None:
            time_unit_str = time_str[-1]
            if time_unit_str == "m":
                time_unit = "minutes"
            elif time_unit_str == "h":
                time_unit = "hours"
            elif time_unit_str == "d":
                time_unit = "days"
            else:
                # No m given
                time_unit = "minutes"
                time_str += "m"
            
            return datetime.datetime.now() + datetime.timedelta(**{time_unit: float(time_str[0:-1])})
        elif re.fullmatch("\d*:\d*", time_str) is not None:
            time_str_splitted = time_str.split(":")
            time = datetime.datetime.now()
            time = time.replace(hour=int(time_str_splitted[0]), minute=int(time_str_splitted[1]))
            if time < datetime.datetime.now():
                time += datetime.timedelta(days=1)
            return time
        else:
            raise RuntimeError("Time can't be converted")

class StrToGame(commands.Converter):
    async def convert(self, ctx: commands.Context, game_name_str: str) -> Game:
        return ctx.bot.config.get_guild_config(ctx.guild.id).get_game(game_name_str.upper())
