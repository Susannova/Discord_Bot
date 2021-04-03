"""
Decorator checks for Commands.

Needs a `ctx` parameter to work.
"""

import dataclasses

from discord.ext import commands

from . import exceptions as _exceptions, DiscordBot


async def command_in_bot_channel_and_used_by_admin(ctx: commands.Context) -> bool:
    """
    Check if the command is used in the bot channel and by an admin.

    Raises `commands.DisabledCommand` if command is disabled.
    """
    bot = ctx.bot
    command_name = ctx.command.name
    guild_config = bot.config.get_guild_config(ctx.guild.id)

    if ctx.channel.id in guild_config.channel_ids.bot and ctx.author.id in bot.yield_guild_admin_ids(ctx.guild):
        try:
            command_config = guild_config.get_command(command_name)
        except LookupError:
            return True

        if not command_config.enabled:
            raise commands.DisabledCommand

        return True
    else:
        return False


async def command_is_allowed(ctx: commands.Context) -> bool:
    """
    Check if the command is allowed.

    Raise `_exceptions.FalseChannel` if the command is not allowed in this channel.
    Raise `commands.DisabledCommand` if the command is disabled.
    Raise `commands.MissingAnyRole` if the user is missing a role.
    """
    bot = ctx.bot
    command_name = ctx.command.name
    guild_config = bot.config.get_guild_config(ctx.guild.id)

    if await command_in_bot_channel_and_used_by_admin(ctx):
        return True

    if not guild_config.command_has_config(command_name):
        valid_channels = (
            guild_config.channel_ids.commands + guild_config.channel_ids.commands_member + guild_config.channel_ids.bot
        )
        if ctx.channel.id in valid_channels:
            return True
        else:
            raise _exceptions.FalseChannel(*valid_channels)
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

            if ctx.message.channel.id not in channels_to_check:
                raise _exceptions.FalseChannel(*channels_to_check)

        # Check the role
        role_names = command_config.allowed_from_roles
        role_ids = command_config.allowed_from_role_ids
        if ctx.guild.owner == ctx.author and command_config.enabled:
            return True
        elif role_names or role_ids:
            roles_to_check = list(guild_config.get_role_ids(*role_names).values())
            roles_to_check += role_ids

            role_ids_author = [role.id for role in ctx.message.author.roles]

            if not [role_id for role_id in role_ids_author if role_id in roles_to_check]:
                raise commands.MissingAnyRole(roles_to_check)

        # Check if the command is enabled
        if not command_config.enabled:
            raise commands.DisabledCommand()

        return True


def is_play_request(ctx: commands.Context):
    """Check if the message is a play request."""
    guild_state = ctx.bot.state.get_guild_state(ctx.guild.id)
    return guild_state.is_play_request(ctx.message.id)


def is_not_the_bot(ctx: commands.Context):
    """Check if the user is the bot."""
    return ctx.bot.user != ctx.author


def is_super_user(ctx: commands.Context):
    """Check if the user is a super user."""
    return ctx.message.author.id in ctx.bot.config.general_config.super_user


def is_riot_enabled(ctx: commands.Context):
    """Check if the riot API is enabled."""
    return ctx.bot.config.general_config.riot_api


def is_activated(*toggles):
    """Check if the toggles are activated."""

    async def wrapper(ctx: commands.Context):
        bot = ctx.bot
        guild_toggles = bot.config.get_guild_config(ctx.guild.id).toggles
        return all((getattr(guild_toggles, toggle) for toggle in toggles))

    return commands.check(wrapper)


def is_debug_enabled(func):
    """Check if the debug toggle is enabled."""

    async def inner(obj: DiscordBot.KrautBot, ctx: commands.Context, *args):
        if obj.config.get_guild_config(ctx.guild.id).toggles.debug:
            return await func(obj, ctx, *args)
        else:
            raise commands.CheckFailure("Debug toggle is false")

    return inner
