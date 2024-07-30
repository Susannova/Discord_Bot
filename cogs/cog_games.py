from calendar import c
from gettext import find
from hashlib import sha1
from imp import reload
import logging
from os import name
from typing import Optional
import json

import discord
from discord.ext import commands

from core import checks, converters, role_manager
from core import emoji_manager
from core.config.guild_config import GuildConfig
from core.kraut_bot import KrautBot
from core.emoji_manager import EmojiManager
from core.role_manager import RoleManager


logger = logging.getLogger(__name__)


class GameCog(commands.Cog, name="Game Commands"):
    def __init__(self, bot: KrautBot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context):
        return await checks.command_in_bot_channel_and_used_by_admin(ctx)

    @commands.command(name="add-game")
    @commands.check(checks.is_super_user)
    async def add_game(
        self,
        ctx: commands.Context,
        name_short: str,
        name_long: str,
        category_id: int = None,
    ) -> None:
        """Adds a game to the games config, creates a role and an emoji.

        Args:
            ctx (commands.Context): discord.Context
            name_short (str): Abbrevation of the game name used as command input.
            name_long (str): Full name of the game.
            category_id (int, optional): Game category. Deprecated. Defaults to default category.
        """
        name_short = name_short.strip().upper()
        emoji_manager = EmojiManager(ctx)
        role_manager = RoleManager(ctx)

        matched_emoji = emoji_manager.find_emoji(name_short)
        if matched_emoji:
            emoji = matched_emoji
            await ctx.send("Emoji already exists.")
        else:
            emoji = await emoji_manager.create_emoji(name_short.lower())
            if not emoji or not isinstance(emoji, discord.Emoji):
                return

        role_id = await role_manager.create_role(name_short)
        if role_id == -1 or not isinstance(role_id, int):
            return

        guild_config = self.bot.config.get_guild_config(ctx.guild.id)
        if not category_id:
            category_id = guild_config.channel_ids.game_category

        if guild_config.game_exists(name_short):
            await ctx.send("Game already exists.")
            return
        guild_config.add_game(name_short, name_long, role_id, emoji.id)
        self.bot.config.write_config_to_file()

        game_selection_message = self.get_game_selection_message(ctx, guild_config)
        await ctx.send(f"Adding reaction to {game_selection_message.channel.mention}.")
        await game_selection_message.add_reaction(emoji)
        await ctx.send(f"Game reaction added.")

    async def get_game_selection_message(self, ctx, guild_config):
        channel = discord.utils.get(ctx.guild.channels, id=guild_config.channel_ids.game_selection)
        if not channel:
            await ctx.send("Game selection channel not found.")
            return None
        pins = await channel.pins()
        if len(pins) > 0:
            return pins[0]
        await ctx.send("Game selection message not found. Please pin it **only**.")
        return None

    @commands.command(name="rm-game")
    @commands.check(checks.is_super_user)
    async def remove_game(self, ctx: commands.Context, game_name: str):
        """Removes the game, its emoji and its role.

        Args:
            ctx (commands.Context): discord.Context
            game_name (str): Abbreviation of the game to be removed.
        """
        await ctx.send("Removing game...")
        game_name = game_name.strip().upper()
        role_manager = RoleManager(ctx)
        emoji_manager = EmojiManager(ctx)
        guild_config: GuildConfig = self.bot.config.get_guild_config(ctx.guild.id)

        if not guild_config.game_exists(game_name):
            await ctx.send("Game does not exist.")
            return

        game = guild_config.get_game(game_name)

        if guild_config.remove_game(game_name):
            game_selection_message = self.get_game_selection_message(ctx, guild_config)
            emoji_to_remove = emoji_manager.find_emoji(game.emoji)
            await game_selection_message.clear_reaction(emoji_to_remove)
            await ctx.send(f"Game reaction removed from channel {game_selection_message.channel.mention}")

            await role_manager.remove_role_by_id(game.role_id)
            await emoji_manager.remove_emoji(game.emoji)

            self.bot.config.write_config_to_file()
            await ctx.send("Game removed.")
            return
        await ctx.send("Unknown error.")


async def setup(bot: KrautBot):
    await bot.add_cog(GameCog(bot))
    logger.info("Debug cogs loaded")
