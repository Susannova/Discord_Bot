""" Checks used as decorators for Commands.
Note: Only works on Commands (needs a ctx parameter).
"""

import dataclasses

from discord.ext import commands

from . import (
    exceptions as _exceptions,
    DiscordBot
)

def command_is_allowed(ctx: commands.Context) -> bool:
    """ Checks if the command is allowed

    Raises:
        commands.CheckFailure: Raised if the command is not allowed in this channel
        commands.DisabledCommand: Raised if the command is disabled
        commands.MissingAnyRole: Raised if the user is missing a role

    Returns:
        bool: True if the command is allowed
    """
    bot = ctx.bot
    command_name = ctx.command.name
    guild_config = bot.config.get_guild_config(ctx.guild.id)
    
    if not guild_config.command_has_config(command_name):
        if ctx.channel.id in (guild_config.channel_ids.commands + guild_config.channel_ids.commands_member + guild_config.channel_ids.bot):
            return True
        else:
            raise commands.CheckFailure("Command is used in false channel")
    else:
        command_config = guild_config.get_command(command_name)

        # Check the channel
        channel_names = command_config.allowed_in_channels
        channel_ids = command_config.allowed_in_channel_ids
        if channel_names or channel_ids:
            channels_dict = dataclasses.asdict(guild_config.channel_ids)
            
            category_temp = bot.get_channel(channels_dict["category_temporary"])
            
            channels_dict["temporary_channels"] = []
            
            if category_temp is not None:
                for temp_channel in category_temp.channels:
                    channels_dict["temporary_channels"].append(temp_channel.id)
            
            channels_to_check = []
            for channel_name in channel_names:
                if channel_name in channels_dict:
                    channel_to_append = channels_dict[channel_name]
                    if isinstance(channel_to_append, list):
                        channels_to_check += channel_to_append
                    else:
                        channels_to_check.append(channel_to_append)
            channels_to_check += guild_config.get_category_ids(channel_names)
            channels_to_check += channels_dict["bot"]
            channels_to_check += channel_ids            
            
            # if list is empty the condition is false
            if ctx.message.channel.id not in channels_to_check:
                raise commands.CheckFailure("Command is used in false channel")
        
        # Check the role
        role_names = command_config.allowed_from_roles
        role_ids = command_config.allowed_from_role_ids
        if ctx.guild.owner == ctx.author:
            return True
        elif role_names or role_ids:
            roles_to_check = guild_config.get_role_ids(*role_names).values()
            roles_to_check += role_ids

            role_ids_author = [role.id for role in ctx.message.author.roles]
            
            if not [role_id for role_id in role_ids_author if role_id in roles_to_check]:
                raise commands.MissingAnyRole(roles_to_check)

        # Check if the command is enabled
        if not command_config.enabled:
            raise commands.DisabledCommand()
        
        return True

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
                channel_to_append = channels_dict[channel_name]
                if isinstance(channel_to_append, list):
                    channels_to_check += channel_to_append
                else:
                    channels_to_check.append(channel_to_append)
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

def is_activated(*toggles):
    """ Checks if the toggles are activated """
    async def wrapper(ctx: commands.Context):
        bot = ctx.bot
        guild_toggles = bot.config.get_guild_config(ctx.guild.id).toggles
        return all((getattr(guild_toggles, toggle) for toggle in toggles))
    
    return commands.check(wrapper)


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
