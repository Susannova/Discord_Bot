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
    """ Checks if the author of the context has any of the roles or is the owner of the guild """
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

def is_play_request(ctx: commands.Context):
    """ Checks if the message is a play request """
    bot = ctx.bot
    guild_state = bot.state.get_guild_state(ctx.guild.id)
    return guild_state.is_play_request(ctx.message.id)


def is_not_the_bot(ctx: commands.Context):
    """ Checks if the user is the bot """
    return ctx.bot.user != ctx.author

def is_in_channels(*channel_names):
    """ Decorator to check if ctx is in one of the channels or in the bot_channel"""
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

def is_super_user(ctx: commands.Context):
    """ Checks if the user is a super user """
    bot = ctx.bot
    return ctx.message.author.id in bot.config.general_config.super_user

def is_riot_enabled(ctx: commands.Context):
    """ Checks if the riot API is enabled """
    bot = ctx.bot
    return bot.config.general_config.riot_api


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
