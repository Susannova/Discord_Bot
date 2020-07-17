import re
from discord.ext import commands

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
            (key_val_str if re.fullmatch("[\[].*[\]]", key_val_str) is None else [item for item in re.findall("[^,\[\]]+", key_val_str)] for key_val_str in arg.split(":")) for arg in re.findall("[^,]:[\[].*?[\]]|[^,]:[^\[\],]", args_formatted)
        )

        return dict(dict_list)