from discord.ext import commands
import bot_utility as utility
import exceptions as _exceptions
class CheckHandler():
    def __init__(self):
        self._CONFIG_ = None
        self._debug_bool = False

    @property
    def CONFIG(self):
        return self._CONFIG_

    @CONFIG.setter
    def CONFIG(self, value):
        self._CONFIG_ = value

    @property
    def debug_bool(self):
        return self._debug_bool

    @debug_bool.setter
    def debug_bool(self, value):
        self._debug_bool = value

    def is_in_channels(self, channel_names):
        async def predicate(ctx):
            return utility.is_in_channels(ctx.message, channel_names)
        return commands.check(predicate)

    def has_n_attachments(self, n):
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

    def is_riot_enabled(self):
        async def predicate(ctx):
            if not self._CONFIG_["TOGGLE_RIOT_API"]:
                await ctx.send('Sorry, der Befehl ist aktuell nicht verfügbar.')
                return False
            return True
        return commands.check(predicate)

    def is_debug_config_enabled(self):
        async def predicate(ctx):
            if not self._CONFIG_['TOGGLE_DEBUG']:
                ctx.send("Debugging is not activated in the config file.")
                return False
            return True
        return commands.check(predicate)

    def is_debug_enabled(self):
        async def predicate(ctx):
            if not self._debug_bool:
                ctx.send("Debugging is not activated.")
                return False
            return True
        return commands.check(predicate)
