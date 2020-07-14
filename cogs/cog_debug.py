import asyncio
import logging


from discord.ext import commands

from core import (
    checks,
    DiscordBot,
    converters
)

logger = logging.getLogger(__name__)


class DebugCog(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot: DiscordBot.KrautBot):
        self.bot = bot

    @commands.command(name='version')
    @checks.is_in_channels()
    @checks.has_any_role("admin_id")
    async def version_(self, ctx):
        logger.debug('!version called')
        await ctx.send(self.bot.state.version)

    @commands.command(name='reload-ext')
    @checks.is_in_channels()
    @checks.has_any_role("admin_id")
    async def reload_ext_(self, ctx, ext):
        logger.info('!reload-ext called')
        try:
            self.bot.reload_extension(ext)
            log_str = "Extension " + ext + " is reloaded"
            logger.info(log_str)
        except commands.ExtensionNotLoaded:
            log_str = "Extension " + ext + " was not loaded!"
            logger.error(log_str)
        except commands.ExtensionNotFound:
            log_str = "Extension " + ext + " was not found!"
            logger.error(log_str)
        except Exception as error:
            log_str = "Unknown error reloading extension " + ext
            logger.error(log_str)
            await ctx.send(log_str)
            raise error

        await ctx.send(log_str)

    @commands.command(name='status')
    @checks.is_in_channels()
    @checks.has_any_role("admin_id")
    async def status_(self, ctx):
        logger.debug('!status called')
        await ctx.send("Bot is alive.")
    
    @commands.command(name='get_emoji_id')
    @checks.is_in_channels()
    @checks.has_any_role("admin_id")
    async def get_emoji_id_(self, ctx, emoji_name):
        logger.debug('!get_emoji_id called')

        for emoji in ctx.guild.emojis:
            if emoji.name == emoji_name:
                await ctx.send(f"Emoji id is {emoji.id}.")
                break

    @commands.command(name='reload-config')
    @checks.is_in_channels()
    @checks.has_any_role("admin_id")
    async def reload_config(self, ctx):
        logger.info('Try to reload the configuration.')
        await ctx.send("Reload configuration.json:")
        self.bot.config.update_config_from_file()
        self.bot.state.get_version()
        await ctx.send("Done.")
        logger.info('configuration reloaded.')
    
    @commands.command(name='write-config')
    @checks.is_in_channels()
    @checks.has_any_role("admin_id")
    async def write_config(self, ctx):
        logger.info('Try to write the configuration.')
        self.bot.config.write_config_to_file()
        await ctx.send("Done.")

    # @commands.command(name='enable-debug')
    # @checks.is_in_channels()
    # @checks.is_debug_config_enabled()
    # @checks.has_any_role("admin_id")
    # async def enable_debug(self, ctx):
    #     gstate.debug = True
    #     str_debug_activated="Debugging is activated for one hour."
    #     await ctx.send(str_debug_activated)
    #     logger.info(str_debug_activated)
    #     await asyncio.sleep(3600)
    #     gstate.debug = False
    #     self.bot.config.get_guild_config(ctx.guild.id).toggles.debug = False
    #     str_debug_deactivated="Debugging is deactivated."
    #     await ctx.send(str_debug_deactivated)
    #     logger.info(str_debug_deactivated)

    @commands.command(name='print')
    @checks.is_in_channels()
    @checks.is_debug_enabled
    @checks.has_any_role("admin_id")
    async def print_(self, ctx, arg):
        logger.debug('!print %s called', arg)
        # return_string = ast.literal_eval(arg)
        # less safe but more powerful
        return_string = eval(arg)
        await ctx.send(return_string)
        print(return_string)

    @commands.command(name='end')
    @checks.is_in_channels()
    @checks.has_any_role("admin_id")
    @commands.is_owner()
    async def end_(self, ctx, *arg):
        if len(list(arg)) == 0:
            await ctx.send('Goodbye!')
            exit_status = 0
        elif str(arg[0]) == "abort":
            await ctx.send('Bot will be restarted if systemd is configured to restart on failure.')
            exit_status=3
        else:
            await ctx.send('Use "abort" or nothing.')
            return

        logger.info("Try to end bot with exit status %s", exit_status)
        await self.bot.logout(exit_status)


    @commands.command(name='dict')
    @checks.is_in_channels()
    @checks.has_any_role("admin_id")
    async def dict_(self, ctx, *, dictonary: converters.ArgsToDict):
        await ctx.send(str(dictonary))


def setup(bot: DiscordBot.KrautBot):
    bot.add_cog(DebugCog(bot))
    logger.info('Debug cogs loaded')