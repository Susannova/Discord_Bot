import logging
import asyncio
from datetime import datetime
from typing import List, Optional

import discord
from discord.ext import commands

from core import checks, DiscordBot, converters
from core.config import Game, GuildConfig

from core.play_requests import PlayRequest

logger = logging.getLogger(__name__)


class PlayRequestsCog(commands.Cog, name="Play-Request Commands"):
    def __init__(self, bot: DiscordBot.KrautBot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context):
        return await checks.command_is_allowed(ctx)

    @commands.group()
    async def play(
        self,
        ctx: commands.Context,
        games: commands.Greedy[converters.StrToGame],
        play_time: Optional[converters.StrToTime],
        player_needed_num: Optional[int] = 0,
        should_be_empty: Optional[str] = None,
    ):
        """
        Creates a play request.

        Other players can react to the play request which will notify the other players.
        Five Minutes before the play time, all players will be notified too.

        Args:
            games: The games to play
            play_time: The time to play.
             Either a time in the format hh:mm or +xm where x are the minutes relative to now
            player_needed_num: The amount of players still needed to fill the play-request.
            should_be_empty: A string to check if everything worked. Leave this always empty please.
        """
        logger.info("Trying to create a play request")
        if ctx.invoked_subcommand is not None:
            return

        if should_be_empty is not None:
            logger.warning("Something went wrong. Was able to interpret the play request until: %s.", should_be_empty)
            await ctx.send(
                f"Something went wrong. I was able to interpret the command until '{should_be_empty}'. \
                  Try `{self.bot.get_command_prefix(ctx.guild.id)}help play`."
            )
            raise ValueError("Was not able to interpret the command")

        guild_config = self.bot.config.get_guild_config(ctx.guild.id)

        if not games:
            logger.debug("Play request created without a game. Create list of games based on author")
            games = self.__get_assinged_games(ctx, guild_config)
            if len(games) == 0:
                raise ValueError("There were no games given in the play request.")
                await ctx.send("There were no games given in the play request.")

        is_now = True if play_time is None else False

        if not is_now:
            if (
                play_time - datetime.now()
            ).total_seconds() / 60 > guild_config.unsorted_config.play_now_time_add_limit:
                logger.warning("Play request denied because of time")
                await ctx.send(
                    f"Play requests that are going more than {guild_config.unsorted_config.play_now_time_add_limit} \
                      minutes in the future are not allowed."
                )
                return
        else:
            play_time = datetime.now()

        message = self.__get_play_request_message(guild_config, games, play_time, is_now, player_needed_num)
        play_request_channel = self.bot.get_channel(guild_config.channel_ids.play_request)
        play_request_message = await play_request_channel.send(
            message, delete_after=guild_config.unsorted_config.auto_delete_after_seconds
        )

        _category = [game.name_short for game in games]
        play_request = PlayRequest(
            play_request_message.id, ctx.message.author.id, category=_category, play_time=play_time
        )

        self.bot.state.get_guild_state(ctx.guild.id).add_play_request(play_request)
        await self.add_auto_reaction(play_request_message, games)
        await ctx.message.delete(delay=3)

        if not is_now:
            await play_request.auto_reminder(guild_config=guild_config, bot=self.bot)

    def __get_assinged_games(self, ctx: commands.Context, guild_config) -> List[Game]:
        """Gets all games that are assinged to the command creator."""
        user_role_ids = [role.id for role in ctx.author.roles]
        games = [game for game in guild_config.yield_all_games() if game.role_id in user_role_ids]
        return games

    def __get_game_name_message(self, games: List[Game]) -> List[str]:
        """Gets the formatted game name string needed for the play-request message."""
        game_names = games[0].name_long
        if len(games) > 1:
            for game in games[1:-1]:
                game_names += f", {game.name_long}"
            game_names += f" oder  {games[-1].name_long}"
        return game_names

    def __get_play_request_message(
        self,
        ctx: commands.Context,
        guild_config: GuildConfig,
        games: List[Game],
        play_time: datetime,
        is_now: bool,
        player_needed_num: int,
    ) -> str:
        """Gets the formatted message string for the given play-request."""
        message_unformated = guild_config.messages.play_now if is_now else guild_config.messages.play_at
        game_names = self.__get_game_name_message(games)

        date_str = ""
        if not play_time.date() == datetime.now().date():
            date = guild_config.messages.date_format.format(
                day=play_time.strftime("%d"), month=play_time.strftime("%m")
            )
            date_str = guild_config.messages.play_at_date.format(date=date)

        message = message_unformated.format(
            role_mention=" ".join((ctx.guild.get_role(game.role_id).mention for game in games)),
            creator=ctx.message.author.mention,
            player=ctx.message.author.mention,
            game=game_names,
            time=play_time.strftime("%H:%M"),
            date_str=date_str,
        )
        if player_needed_num > 0 and player_needed_num < 20:
            message = (
                f"{message} {guild_config.messages.players_needed.format(player_needed_num=player_needed_num)}"
            )
        return message

    async def add_auto_reaction(self, play_request_message: discord.Message, games: List[Game]):
        for game in games:
            await play_request_message.add_reaction(self.bot.get_emoji(game.emoji))

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        Event Listener used to automatically delete
        all messages send after certain delay.
        """
        if isinstance(message.channel, discord.DMChannel):
            return

        guild_id = message.guild.id
        guild_config = self.bot.config.get_guild_config(guild_id)

        if message.channel.id == guild_config.channel_ids.play_request:
            if message.author == self.bot.user:
                seconds_slept = 0
                # FIXME: Do we need this? Where does sending message even get changed?
                while self.bot.sending_message:
                    await asyncio.sleep(1)
                    seconds_slept += 1
                    if seconds_slept > 10:
                        raise RuntimeError("Waited for at least 10 seconds for sending_message to become False")
            if not message.pinned:
                delay = guild_config.unsorted_config.auto_delete_after_seconds
                guild_state = self.bot.state.get_guild_state(message.guild.id)
                if not guild_state.is_play_request(message.id):
                    await message.delete(delay=delay)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.Member):
        """
        Event Listener used to automatically add
        subscribers to a play-request and manage
        which reactions are allowed on play-request.
        """
        guild_id = reaction.message.guild.id
        guild_config = self.bot.config.get_guild_config(guild_id)
        guild_state = self.bot.state.get_guild_state(guild_id)

        if not guild_state.is_play_request(reaction.message.id) or user == self.bot.user:
            return

        play_request = guild_state.get_play_request(reaction.message.id)
        emoji_id = None if isinstance(reaction.emoji, str) else reaction.emoji.id

        if play_request.is_play_request_author(user.id):
            logger.info("Remove reaction from a play_request_author")
            await reaction.remove(user)
        elif (
            emoji_id in guild_config.get_all_game_emojis()
            and guild_config.emoji_to_game(emoji_id).name_short in play_request.category
        ):
            play_request.add_subscriber_id(user.id)
            await self.send_auto_dm(guild_config, play_request, user, reaction)
        else:
            await reaction.remove(user)
            logger.info("Removed new reaction %s from %s", reaction.emoji, user.name)

    async def send_auto_dm(
        self,
        guild_config: GuildConfig,
        play_request: PlayRequest,
        user: discord.Member,
        reaction: discord.Reaction,
    ):
        """
        Sends a message to all player involved in a play-request
        to inform them about new subscribers.
        """
        author = self.bot.get_user(play_request.author_id)
        logger.info("Send auto dms to play_request subscribers")

        for player_id in play_request.generate_all_players():
            if player_id == play_request.author_id and player_id != user.id:
                await author.send(
                    guild_config.messages.auto_dm_creator.format(player=user.name, reaction=str(reaction.emoji))
                )
            elif player_id != user.id:
                player = self.bot.get_user(player_id)
                game = guild_config.emoji_to_game(reaction.emoji.id)

                if game.role_id in [role.id for role in user.roles]:
                    await player.send(
                        guild_config.messages.auto_dm_subscriber.format(
                            player=user.name, creator=author.name, reaction=str(reaction.emoji)
                        )
                    )

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction: discord.Reaction, user: discord.Member):
        """
        Event Listener used to automatically
        remove subscribers from play-requests.
        """
        guild_id = reaction.message.guild.id
        guild_state = self.bot.state.get_guild_state(guild_id)

        if not guild_state.is_play_request(reaction.message.id) or user == self.bot.user:
            return

        play_request = guild_state.get_play_request(reaction.message.id)
        if play_request.author_id == user.id:
            return

        remove_from_subscriber = True
        for other_reaction in reaction.message.reactions:
            if user in await other_reaction.users().flatten() and other_reaction != reaction:
                remove_from_subscriber = False
                break

        if remove_from_subscriber and play_request.is_already_subscriber(user.id):
            play_request.remove_subscriber_id(user.id)


def setup(bot: DiscordBot.KrautBot):
    bot.add_cog(PlayRequestsCog(bot))
    logger.info("Play request cogs loaded")
