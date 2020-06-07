""" Checks used as decorators for Commands.
Note: Only works on Commands (needs a ctx parameter).
"""

import dataclasses

from discord.ext import commands

from . import (
    exceptions as _exceptions,
    DiscordBot
)


def has_any_role(*role_names):
    async def wrapper(ctx: commands.Context):
        bot = ctx.bot
        roles_to_check = bot.config.get_guild_config(ctx.guild.id).get_role_ids(*role_names).values()

        role_ids_author = [role.id for role in ctx.message.author.roles]
        
        # if list is empty the condition is false
        if ctx.guild.owner == ctx.author or [role_id for role_id in role_ids_author if role_id in roles_to_check]:
            return True
        else:
            raise commands.MissingAnyRole(roles_to_check)
    
    return commands.check(wrapper)


def is_in_channels(*channel_names):
    """ Decorator to check if ctx is in one of the channels """
    async def wrapper(ctx: commands.Context):
        bot = ctx.bot

        guild_config = bot.config.get_guild_config(ctx.guild.id)

        channels_dict = dataclasses.asdict(guild_config.channel_ids)
        
        # TODO Can be None!!
        category_temp = bot.get_channel(channels_dict["category_temporary"])
        
        channels_dict["temporary_channels"] = []
        
        if category_temp is not None:
            for temp_channel in category_temp.channels:
                channels_dict["temporary_channels"].append(temp_channel.id)
        
        channels_to_check = []
        for channel_name in channel_names:
            if channel_name in channels_dict:
                channels_to_check += channels_dict[channel_name]
        channels_to_check += guild_config.get_category_ids(channel_names)
        channels_to_check += channels_dict["bot"]
        
        # if list is empty the condition is false
        if ctx.message.channel.id in channels_to_check:
            return True
        else:
            raise commands.CheckFailure("Command is used in false channel")
    return commands.check(wrapper)


def has_n_attachments(n):
    async def predicate(ctx):
        if len(ctx.message.attachments) == n:
            return True
        else:
            try:
                raise _exceptions.MissingRequiredAttachment()
            except _exceptions.MissingRequiredAttachment:
                await ctx.send(
                    'Es fehlt ein Attachment. (z.B. das Bild bei ?clash)')
    return commands.check(predicate)


def is_riot_enabled(func):
    """ Checks if the riot API is enabled """
    async def inner(obj: DiscordBot.KrautBot, *args):
        if obj.config.general_config.riot_api:
            return await func(obj, *args)
        else:
            raise commands.CheckFailure("Riot-API is disabled")
    return inner

# def is_debug_config_enabled():
#     async def predicate(ctx):
#         if not gstate.CONFIG['TOGGLE_DEBUG']:
#             return False
#         return True
#     return commands.check(predicate)

def is_debug_enabled(func):
    """ Checks if the debug toggle is enabled """
    async def inner(obj: DiscordBot.KrautBot, ctx: commands.Context, *args):
        if obj.config.get_guild_config(ctx.guild.id).toggles.debug:
            return await func(obj, ctx, *args)
        else:
            raise commands.CheckFailure("Debug toggle is false")
    return inner
