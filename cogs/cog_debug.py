import logging
from typing import Optional

import discord
from discord.ext import commands

from core import checks, DiscordBot, converters

logger = logging.getLogger(__name__)


class DebugCog(commands.Cog):
    def __init__(self, bot: DiscordBot.KrautBot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context):
        return await checks.command_in_bot_channel_and_used_by_admin(ctx)

    @commands.command(name="version")
    async def version_(self, ctx: commands.Context):
        """Get the current bot version as a commit hash."""
        logger.debug("!version called")
        await ctx.send(self.bot.state.version)

    @commands.command(name="reload-ext")
    @commands.check(checks.is_super_user)
    async def reload_ext_(self, ctx: commands.Context, ext: str):
        logger.info("!reload-ext called")
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

    @commands.command(name="status")
    async def status_(self, ctx: commands.Context):
        """Check if the bot is alive."""
        logger.debug("!status called")
        await ctx.send("Bot is alive.")

    @commands.command(name="get_emoji_id")
    async def get_emoji_id_(self, ctx: commands.Context, emoji_name: str):
        """Get the ID of the given Emoji name(`str`)."""
        logger.debug("!get_emoji_id called")
        for emoji in ctx.guild.emojis:
            if emoji.name == emoji_name:
                await ctx.send(f"Emoji id is {emoji.id}.")
                break

    @commands.command(name="print")
    @commands.check(checks.is_super_user)
    async def print_(self, ctx: commands.Context, arg: str):
        logger.debug("!print %s called", arg)
        # return_string = ast.literal_eval(arg)
        # less safe but more powerful
        return_string = eval(arg)
        await ctx.send(return_string)
        print(return_string)

    @commands.command(name="end")
    @commands.check(checks.is_super_user)
    async def end_(self, ctx: commands.Context, arg: Optional[str] = None):
        """Stops the bot."""
        if arg is None:
            await ctx.send("Goodbye!")
            exit_status = 0
        elif arg == "abort":
            await ctx.send("Bot will be restarted if systemd is configured to restart on failure.")
            exit_status = 3
        else:
            await ctx.send('Use "abort" or nothing.')
            return

        logger.info("Try to end bot with exit status %s", exit_status)
        await self.bot.logout(exit_status)

    @commands.command(name="dict")
    async def dict_(self, ctx: commands.Context, *, dictonary: converters.ArgsToDict):
        await ctx.send(str(dictonary))

    @commands.command()
    async def send_to_channel(
        self, ctx: commands.Context, text_channel: discord.TextChannel, pin: Optional[bool] = True, *, text: str
    ):
        """Send a message to a text channel and pins it per default."""
        logger.info("Send a text to channel %s: %s", text_channel.name, text)
        if text_channel.guild != ctx.guild:
            logger.warning("%s tried to send a text to a channel of another guild!", ctx.author)
            return
        try:
            self.bot.sending_message = True
            message = await text_channel.send(text)
            if pin:
                await message.pin()
        finally:
            self.bot.sending_message = False


def setup(bot: DiscordBot.KrautBot):
    bot.add_cog(DebugCog(bot))
    logger.info("Debug cogs loaded")
