import logging
import random
import math
from typing import List, Optional, Union

import discord
from discord.ext import commands

from core import checks, exceptions, timers, help_text
from core.kraut_bot import KrautBot
from riot import riot_commands

logger = logging.getLogger(__name__)


class UtilityCog(commands.Cog, name="Utility Commands"):
    def __init__(self, bot: KrautBot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context):
        return await checks.command_is_allowed(ctx)

    @commands.group(name="team")
    async def team(self, ctx: commands.Context):
        """
        Creates random teams.

        The teams are created with the subcommand create
        and can be moved afterwards with move.
        """
        logger.debug("!team command called")
        if ctx.invoked_subcommand is None:
            await ctx.send_help(self.team)

    @team.command(name="create")
    async def create_team(
        self,
        ctx: commands.Context,
        has_roles: Optional[bool] = False,
        players_list: commands.Greedy[Union[discord.Member, str]] = None,
    ):
        """
        Create two random teams.

        The player of the team are all the members of
        your current voice channel and every given player.
        The bot tries to find a discord user for the given names
        and will mentions all discord users.
        """
        if ctx.author.voice is not None:
            current_voice_channel = ctx.author.voice.channel
            players_list += current_voice_channel.members
            self.bot.state.get_guild_state(ctx.guild.id).last_channel = current_voice_channel

        team1_message, team2_message = self.__get_team_messages(ctx, players_list)
        embed = self.__get_create_team_embed(ctx, team1_message, team2_message, has_roles=has_roles)
        await ctx.send(embed=embed)
        self.bot.state.get_guild_state(ctx.guild.id).has_moved = False
        await self.bot.state.get_guild_state(ctx.guild.id).timer_remove_teams()

    def __get_team_messages(self, ctx: commands.Context, players: List[Union[discord.Member, str]]) -> (str, str):
        """
        Create two teams and saves them in the guild state.

        Return an embed, which includes the given teams.
        """
        guild_state = self.bot.state.get_guild_state(ctx.guild.id)

        guild_state.team1 = random.sample(players, math.ceil(len(players) / 2))
        guild_state.team2 = [player for player in players if player not in guild_state.team1]

        team1_message = (
            [player.mention if isinstance(player, discord.Member) else player for player in guild_state.team1]
            if len(guild_state.team1) > 0
            else ["-"]
        )
        team2_message = (
            [player.mention if isinstance(player, discord.Member) else player for player in guild_state.team2]
            if len(guild_state.team2) > 0
            else ["-"]
        )

        return team1_message, team2_message

    def __get_create_team_embed(
        self, ctx: commands.Context, team1_message: str, team2_message: str, has_roles: bool
    ) -> discord.Embed:
        guild_config = self.bot.config.get_guild_config(ctx.guild.id)
        embed_title = guild_config.messages.team_header
        team1_title = guild_config.messages.team_1
        team2_title = guild_config.messages.team_2
        command_prefix = guild_config.unsorted_config.command_prefix

        embed = discord.Embed(title=embed_title, colour=discord.Color.from_rgb(62, 221, 22))

        emoji = [
            self.bot.get_emoji(id=644252873672359946),
            self.bot.get_emoji(id=644254018377482255),
            self.bot.get_emoji(id=644252861827514388),
            self.bot.get_emoji(id=644252853644296227),
            self.bot.get_emoji(id=644252146023530506),
        ]
        if has_roles and (len(team1_message) + len(team2_message)) <= 10:
            team1_message = "\n".join(f"{member} [{emoji[idx]}]" for idx, member in enumerate(team1_message))
            team2_message = "\n".join(f"{member} [{emoji[idx]}]" for idx, member in enumerate(team2_message))
        else:
            team1_message = "\n".join(member for member in team1_message)
            team2_message = "\n".join(member for member in team2_message)

        embed.add_field(name=team1_title, value=team1_message, inline=True)
        embed.add_field(name=team2_title, value=team2_message, inline=True)

        embed.set_footer(text=f"Move teams into their respective channels and back with: '{command_prefix}team move'")
        return embed

    @team.command(name="move")
    async def move_team_members(self, ctx: commands.Context):
        """
        Move the last created team.

        First a team has to be created with the subcommand create,
        otherwise an error message is send.
        """
        guild_config = self.bot.config.get_guild_config(ctx.guild.id)
        guild_state = self.bot.state.get_guild_state(ctx.guild.id)
        channel_team1 = self.bot.get_channel(guild_config.channel_ids.team_1)
        channel_team2 = self.bot.get_channel(guild_config.channel_ids.team_2)

        last_team = guild_state.team1 + guild_state.team2
        has_moved = guild_state.has_moved
        last_channel = guild_state.last_channel

        if not last_team:
            await ctx.send(
                f"Team is empty. Please use ``{self.bot.get_command_prefix(ctx.guild.id)}team create`` first."
            )
            return

        if not has_moved:
            for member in last_team:
                if isinstance(member, discord.Member) and member.voice is not None:
                    if member in guild_state.team1:
                        await member.move_to(channel_team1)
                    elif member in guild_state.team2:
                        await member.move_to(channel_team2)
            guild_state.has_moved = True
        else:
            if not last_channel or len(last_team) == 0:
                await ctx.send("Could not find channel or members to move.")
                guild_state.last_channel = None
                return
            for member in last_team:
                if isinstance(member, discord.Member) and member.voice is not None:
                    await member.move_to(last_channel)
            guild_state.has_moved = False
            guild_state.team1 = []
            guild_state.team2 = []

        await self.bot.state.get_guild_state(ctx.guild.id).timer_remove_teams()

    @team.command(name="leave")
    async def leave_team(self, ctx: commands.Context):
        """Invoking user leaves current teams."""
        guild_state = self.bot.state.get_guild_state(ctx.guild.id)
        user = ctx.message.author

        if user in guild_state.team1:
            guild_state.team1.remove(user)
            await ctx.send(f"{user.mention} left Team 1.")
        elif user in guild_state.team2:
            guild_state.team2.remove(user)
            await ctx.send(f"{user.mention} left Team 2.")
        else:
            await ctx.send(f"{user.mention} was not in any team.")

    @commands.command(
        name="link",
        help=help_text.link_HelpText.text,
        brief=help_text.link_HelpText.brief,
        usage=help_text.link_HelpText.usage,
    )
    @commands.check(checks.is_riot_enabled)
    async def link_(self, ctx: commands.Context, summoner_name: str):
        try:
            riot_commands.link_account(
                ctx.message.author.name,
                summoner_name,
                self.bot.config.get_guild_config(ctx.guild.id),
                general_config=self.bot.config.general_config,
                guild_id=ctx.guild.id,
            )
        except Exception as error:
            logger.error("Error linking %s: %s", summoner_name, error)
            # TODO Add a link to our accounts
            await ctx.message.author.send(
                f"Dein Lol-Account konnte nicht mit deinem Discord Account verbunden werden. \
                  Richtiger Umgang mit ``!link`` ist unter ``{ctx.bot.command_prefix}help link`` zu finden. \
                  Falls das nicht weiterhilft, wende dich bitte an Jan oder Nick"
            )
            raise error
        else:
            await ctx.message.author.send(
                f"Dein Lol-Account wurde erfolgreich mit deinem Discord Account verbunden!\n \
                Falls du deinen Account wieder entfernen möchtest \
                benutze das ``{ctx.bot.command_prefix}unlink`` Command."
            )
            logger.info("%s was linked.", summoner_name)

    @commands.command(
        name="unlink",
        help=help_text.unlink_HelpText.text,
        brief=help_text.unlink_HelpText.brief,
        usage=help_text.unlink_HelpText.usage,
    )
    @commands.check(checks.is_riot_enabled)
    async def unlink_(self, ctx: commands.Context):
        logger.debug("!unlink called")
        riot_commands.unlink_account(
            ctx.message.author.name, self.bot.config.get_guild_config(ctx.guild.id), ctx.guild.id
        )
        await ctx.message.author.send("Dein Lol-Account wurde erfolgreich von deinem Discord Account getrennt!")
        logger.info("%s was unlinked", ctx.message.author.name)

    @commands.group(name="channel")
    async def channel(self, ctx: commands.Context):
        """Manages temporary channels."""
        logger.debug("!channel command called")
        if ctx.invoked_subcommand is None:
            await ctx.send_help(self.channel)

    @channel.command(
        name="create",
        help=help_text.create_channel_HelpText.text,
        brief=help_text.create_channel_HelpText.brief,
        usage=help_text.create_channel_HelpText.usage,
    )
    @discord.ext.commands.cooldown(rate=3, per=30)
    async def create_channel(
        self, ctx: commands.Context, kind: str, channel_name: str, user_limit: Optional[int] = 99
    ):
        logger.debug("!create-channel %s %s called by %s", kind, channel_name, ctx.message.author.name)
        guild_state = self.bot.state.get_guild_state(ctx.guild.id)
        for tmp_channels in guild_state.tmp_channel_ids:
            logger.debug(
                "Check if channel %s with id %s is already created by user %s.",
                guild_state.tmp_channel_ids[tmp_channels]["name"],
                tmp_channels,
                ctx.message.author.name,
            )
            if (
                not guild_state.tmp_channel_ids[tmp_channels]["deleted"]
                and guild_state.tmp_channel_ids[tmp_channels]["author"] == ctx.message.author.id
            ):
                logger.info(
                    "%s wanted to create a new temporary channel but already has created channel %s with id %s.",
                    ctx.message.author.name,
                    guild_state.tmp_channel_ids[tmp_channels]["name"],
                    tmp_channels,
                )
                raise exceptions.LimitReachedException("Der Autor hat schon einen temprorären Channel erstellt.")

        tmp_channel_category = self.bot.get_channel(
            self.bot.config.get_guild_config(ctx.guild.id).channel_ids.category_temporary
        )

        tmp_channel = None
        if channel_name is None:
            logger.error("!create-channel is called by user %s without a name.", ctx.message.author.name)
            return
        elif kind == "text":
            tmp_channel = await ctx.message.guild.create_text_channel(channel_name, category=tmp_channel_category)
        elif kind == "voice":
            if user_limit > 0 and user_limit <= 99:
                tmp_channel = await ctx.message.guild.create_voice_channel(
                    channel_name, category=tmp_channel_category, user_limit=int(user_limit[0])
                )
            else:
                tmp_channel = await ctx.message.guild.create_voice_channel(channel_name, category=tmp_channel_category)
        else:
            logger.error("!create-channel is called by user %s with invalid type %s.", ctx.message.author.name, kind)
            return
        guild_state.tmp_channel_ids[tmp_channel.id] = {
            "timer": timers.start_timer(hrs=12),
            "author": ctx.message.author.id,
            "deleted": False,
            "name": channel_name,
        }
        logger.info("Temporary %s-channel %s with id %s created", kind, channel_name, tmp_channel.id)

    @checks.is_activated("highlights")
    @commands.command()
    async def highlights(self, ctx: commands.Context):
        """Prints the best highlights.

        Vote for your favorite highlight with
        adding a reaction to the highlight.
        """
        ranking = {}
        limit = 300

        guild_config = self.bot.config.get_guild_config(ctx.guild.id)

        for highlight_channel_id in guild_config.channel_ids.highlights:
            highlight_channel = self.bot.get_channel(highlight_channel_id)
            async for message in highlight_channel.history(limit=limit):
                users = []
                for reaction in message.reactions:
                    async for user in reaction.users():
                        if user not in users:
                            users.append(user)
                count = len(users)
                if count in ranking:
                    ranking[count].append(message)
                else:
                    ranking[count] = [message]

        counts = list(ranking.keys())
        counts.sort(reverse=True)

        embed = discord.Embed(
            title="Highlights Leaderboard",
            colour=discord.Color.from_rgb(62, 221, 22),
            type="rich",
            description=guild_config.messages.highlight_leaderboard_description.format(
                highlight_channel_mention=", ".join(
                    (self.bot.get_channel(channel).mention for channel in guild_config.channel_ids.highlights)
                )
            ),
        )

        embed.set_footer(text=guild_config.messages.highlight_leaderboard_footer.format(limit=limit))

        text_too_long = False

        max_standing = 3 if len(counts) >= 3 else len(counts)
        if max_standing == 0:
            if not guild_config.channel_ids.highlights:
                await ctx.send("I found no highlight channel.")
                logger.warning("highlights called but no highlight channel set for guild %i", ctx.guild.id)
            else:
                await ctx.send("Sorry, I found no highlights...")
                logger.warning("highlights called but no highlight were found for guild %i", ctx.guild.id)
            return

        for standing in range(0, max_standing):
            text = f"Votes: **{counts[standing]}**\n"
            for message in ranking[counts[standing]]:
                appended_text = f" - [{message.author.name}]({message.jump_url})\n"
                if len(text) + len(appended_text) > 1024:
                    text_too_long = True
                    logger.warning("Too many highlights. Some were rejected.")
                    break
                text += appended_text

            embed.add_field(name=f"{standing + 1}. {guild_config.messages.place}", value=text, inline=False)

        message = await ctx.send(embed=embed)
        if text_too_long:
            await ctx.send(
                "There were too many highlights so some older highlights were not taken in account.", delete_after=10
            )


def setup(bot: KrautBot):
    bot.add_cog(UtilityCog(bot))
    logger.info("Utility cogs loaded")
