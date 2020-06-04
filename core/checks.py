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
    """ Checks if the author of the context has any of the roles """
    def _has_any_role(func):
        async def wrapper(obj, ctx, *args):
            roles_to_check = obj.cog.bot.config.get_guild_config(ctx.guild.id).get_all_role_ids(*role_names).values()
        
            role_ids_author = [role.id for role in ctx.message.author.roles]
            
            # if list is empty the condition is false
            if [role_id for role_id in role_ids_author if role_id in roles_to_check]:
                return await func(obj, ctx, *args)
            else:
                raise commands.MissingAnyRole(roles_to_check)
        return wrapper
    return _has_any_role


def is_in_channels(*channel_names):
    """ Decorator to check if ctx is in one of the channels. If not an exception is raised, otherwise the decorated function is executed.
    No exception will be raised and the function will always be executed if the ctx is in a bot channel. """
    def _is_in_channels(func):
        async def wrapper(obj, ctx: commands.Context, *args):
            bot = obj.cog.bot
            channels_dict = dataclasses.asdict(bot.config.get_guild_config(ctx.guild.id).channel_ids)
            category_temp = bot.get_channel(channels_dict["category_temporary"])
            
            channels_dict["temporary_channels"] = []
            for temp_channel in category_temp.channels:
                channels_dict["temporary_channels"].append(temp_channel.id)
            
            channels_to_check = []
            for channel_name in channel_names:
                if channel_name in channels_dict:
                    channels_to_check += channels_dict[channel_name]
            channels_to_check += bot.get_all_category_ids(channel_names)
            channels_to_check += channels_dict["bot"]
            
            # if list is empty the condition is false
            if ctx.message.channel.id in channels_to_check:
                return await func(obj, ctx, *args)
            else:
                raise "Member is not in channel"
        return wrapper
    return _is_in_channels

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
    def inner(obj: DiscordBot.KrautBot, *args):
        if obj.config.general_config.riot_api:
            return func(obj, *args)
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
    def inner(obj: DiscordBot.KrautBot, ctx: commands.Context, *args):
        if obj.config.get_guild_config(ctx.guild.id).toggles.debug:
            return func(obj, ctx, *args)
        else:
            raise commands.CheckFailure("Debug toggle is false")
    return inner
