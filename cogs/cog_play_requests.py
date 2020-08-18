
import re
import logging
import asyncio
import datetime
import typing


import discord
from discord.ext import commands

from core import (
    checks,
    exceptions,
    timers,
    help_text,
    DiscordBot,
    converters,
    config
)

from core.play_requests import PlayRequest

logger = logging.getLogger(__name__)



class PlayRequestsCog(commands.Cog, name='Play-Request Commands'):
    def __init__(self, bot: DiscordBot.KrautBot):
        self.bot = bot

    @checks.is_in_channels("play_request")
    @commands.group()
    async def play(self, ctx: commands.Context, games: commands.Greedy[converters.StrToGame], play_time: typing.Optional[converters.StrToTime], *, should_be_empty: typing.Optional[str]):
        """ Create a play request

        Other players can react to the play request which will notify the other players.
        5 Minutes before the play time, all players will be notified too.

        Args:
            games: The games to play
            play_time: The time to play. Either a time in the format hh:mm or +xm where x are the minutes relative to now
            should_be_empty: A string to check if everything worked. Leave this always empty please.
        """
        if ctx.invoked_subcommand is None:
            logger.info('Create a play request')
            guild_config = self.bot.config.get_guild_config(ctx.guild.id)

            if should_be_empty is not None:
                logger.warning("Something went wrong. Was able to interpret the play request until: %s.", should_be_empty)
                await ctx.send(f"Something went wrong. I was able to interpret the command until '{should_be_empty}'. Try `{self.bot.get_command_prefix(ctx.guild.id)}help play`.")
                raise ValueError("Was not able to interpret the command")

            if not games:
                logger.debug("Play request created without a game. Create list of games based on author")
                user_role_ids = [role.id for role in ctx.author.roles]
                games = [game for game in guild_config.yield_all_games() if game.role_id in user_role_ids]
            
            is_now = True if play_time is None else False

            if not is_now:
                if (play_time - datetime.datetime.now()).total_seconds() / 60 > guild_config.unsorted_config.play_now_time_add_limit:
                    logger.warning("Play request denied because of time")
                    await ctx.send(f"Play requests that are going more than {guild_config.unsorted_config.play_now_time_add_limit} minutes in the future are not allowed.")
                    return
            else:
                play_time = datetime.datetime.now()

            message_unformated = guild_config.messages.play_now if is_now else guild_config.messages.play_at
            
            game_names = games[0].name_long
            if len(games) > 1:
                # TODO Make this more general!
                for game in games[1:-1]:
                    game_names += f", {game.name_long}"
                game_names += f" oder  {games[-1].name_long}"
            message = message_unformated.format(
                    role_mention=" ".join((ctx.guild.get_role(game.role_id).mention for game in games)),
                    creator=ctx.message.author.mention,
                    player=ctx.message.author.mention,
                    game=game_names,
                    time=play_time.strftime("%H:%M")
                )
            
            play_request_message = await ctx.send(message)
            _category = [game.name_short for game in games]
            play_request = PlayRequest(play_request_message.id, ctx.message.author.id, category=_category, play_time=play_time)

            self.bot.state.get_guild_state(ctx.guild.id).add_play_request(play_request)
            await self.add_auto_reaction(play_request_message, games)

            await ctx.message.delete()

            if not is_now:
                await play_request.auto_reminder(guild_config=guild_config, bot=self.bot)


    async def add_auto_reaction(self, play_request_message: discord.Message, games: typing.List[config.Game]):
        for game in games:
            await play_request_message.add_reaction(self.bot.get_emoji(game.emoji))

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.Member):

        guild_id = reaction.message.guild.id
        guild_config = self.bot.config.get_guild_config(guild_id)
        guild_state = self.bot.state.get_guild_state(guild_id)

        if not guild_state.is_play_request(reaction.message.id) or user == self.bot.user:
            return

        play_request = guild_state.get_play_request(reaction.message.id)
        user_id = user.id
        emoji_id = None if isinstance(reaction.emoji, str) else reaction.emoji.id

        if play_request.is_play_request_author(user_id):
            logger.info("Remove reaction from a play_request_author")
            await reaction.remove(user)
        elif emoji_id in guild_config.get_all_game_emojis():
            play_request.add_subscriber_id(user_id)
            await self.send_auto_dm(guild_config, play_request, user, reaction)
        else:
            await reaction.remove()
            logger.info("Removed new reaction %s", reaction.emoji)
    
    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction: discord.Reaction, user: discord.Member):

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
        
        if remove_from_subscriber:
            guild_id = reaction.message.guild.id
            guild_state = self.bot.state.get_guild_state(guild_id)

            play_request = guild_state.get_play_request(reaction.message.id)

            play_request.remove_subscriber_id(user.id)
            



    async def send_auto_dm(self, guild_config: config.GuildConfig, play_request: PlayRequest, user: discord.Member, reaction: discord.Reaction):
        author = self.bot.get_user(play_request.author_id)
        logger.info("Send auto dms to play_request subscribers")
        
        for player_id in play_request.generate_all_players():
            if player_id == play_request.author_id and player_id != user.id:
                await author.send(
                    guild_config.messages.auto_dm_creator.format(
                        player=user.name,
                        reaction=str(reaction.emoji)
                        )
                    )
            elif player_id != user.id:
                player = self.bot.get_user(player_id)
                game = guild_config.emoji_to_game(reaction.emoji.id)

                if game.role_id in [role.id for role in user.roles]:
                    await player.send(
                        guild_config.messages.auto_dm_subscriber.format(
                            player=user.name,
                            creator=author.name,
                            reaction=str(reaction.emoji)))


    # async def create_clash(self, ctx, date):
    #     guild_config = self.bot.config.get_guild_config(ctx.guild.id)
    #     logger.debug('Create a clash request')
    #     self.bot.state.get_guild_state(ctx.guild.id).clash_date = date
    #     play_request_message = await ctx.send(guild_config.messages.clash_create.format(
    #         role_mention=ctx.guild.get_role(guild_config.get_game("clash").role_id).mention,
    #         player=ctx.message.author.mention,
    #         date=date
    #         )
    #     )
    #     _category = "clash"
    #     play_request = PlayRequest(play_request_message.id, ctx.message.author.id, category=_category)
    #     await self.add_play_request_to_state(ctx.guild.id, play_request)
    #     await self.add_auto_reaction(ctx, play_request_message)
        

        

def setup(bot: DiscordBot.KrautBot):
    bot.add_cog(PlayRequestsCog(bot))
    logger.info('Play request cogs loaded')
