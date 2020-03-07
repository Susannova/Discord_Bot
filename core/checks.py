
from discord.ext import commands

from core import (
    bot_utility as utility,
    exceptions as _exceptions
) 

from core.state import global_state as gstate


def is_in_channels(channel_names):
    async def predicate(ctx):
        return utility.is_in_channels(ctx.message, channel_names)
    return commands.check(predicate)

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

def is_riot_enabled():
    async def predicate(ctx):
        if not gstate.CONFIG["TOGGLE_RIOT_API"]:
            await ctx.send('Sorry, der Befehl ist aktuell nicht verfügbar.')
            return False
        return True
    return commands.check(predicate)

def is_debug_config_enabled():
    async def predicate(ctx):
        if not gstate.CONFIG['TOGGLE_DEBUG']:
            return False
        return True
    return commands.check(predicate)

def is_debug_enabled():
    async def predicate(ctx):
        if not gstate.debug:
            return False
        return True
    return commands.check(predicate)
