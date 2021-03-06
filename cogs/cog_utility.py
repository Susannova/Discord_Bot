import logging
import typing
import random

import asyncio, time

import discord
from discord.ext import commands

from core import (
    checks,
    exceptions,
    timers,
    help_text,
    DiscordBot,
    config
)

from riot import riot_commands

logger = logging.getLogger(__name__)

def create_team(players: typing.List[typing.Union[discord.Member, str]], guild_config: config.GuildConfig):
    """ Creates two teams and returns a string, and the two teams as lists. """
    num_players = len(players)
    team1 = random.sample(players, int(num_players / 2))
    team2 = players.copy()

    for player in team1:
        team2.remove(player)

    teams_message = guild_config.messages.team_header
    teams_message += guild_config.messages.team_1
    for player in team1:
        name = player.mention if isinstance(player, discord.Member) else player
        teams_message += name + "\n"

    teams_message += guild_config.messages.team_2
    for player in team2:
        name = player.mention if isinstance(player, discord.Member) else player
        teams_message += name + "\n"

    return teams_message, team1, team2

class UtilityCog(commands.Cog, name='Utility Commands'):
    def __init__(self, bot: DiscordBot.KrautBot):
        self.bot = bot
        self.team1 = []
        self.team2 = []
    
    async def cog_check(self, ctx: commands.Context):
        return await checks.command_is_allowed(ctx)

    @commands.group(name='team')
    async def team(self, ctx: commands.Context):
        """ Creates random teams
        
            The teams are created with the subcommand create and can be moved afterwards with move
        """


        logger.debug('!team command called')
        if ctx.invoked_subcommand is None:
            await ctx.send_help(self.team)

    @team.command(name='create')
    async def create_team(self, ctx: commands.Context, players_list: commands.Greedy[typing.Union[discord.Member, str]]):
        """ Creates two random teams

        The player of the team are all the members of your current voice channel and every given player. The bot tries to find a discord user for the given names and will mentions all discord users.
        """
        if ctx.author.voice is not None:
            current_voice_channel = ctx.author.voice.channel
            players_list += current_voice_channel.members

        guild_config = self.bot.config.get_guild_config(ctx.guild.id)

        message, self.team1, self.team2 = create_team(players_list, guild_config)
        await ctx.send(message)
        self.bot.state.get_guild_state(ctx.guild.id).last_team = players_list


    @team.command(name='move')
    async def move_team_members(self, ctx: commands.Context):
        """ Moves the last created team
        
            First a team has to be created with the subcommand create otherwise an error message will be send
        """
        guild_config = self.bot.config.get_guild_config(ctx.guild.id)
        channel_team1 = self.bot.get_channel(guild_config.channel_ids.team_1)
        channel_team2 = self.bot.get_channel(guild_config.channel_ids.team_2)

        last_team = self.bot.state.get_guild_state(ctx.guild.id).last_team

        if not last_team:
            await ctx.send(f"Team is empty. Please use ``{self.bot.get_command_prefix(ctx.guild.id)}team create`` first.")
            return

        for member in last_team:
            if isinstance(member, discord.Member) and member.voice is not None:
                if member in self.team1:
                    await member.move_to(channel_team1)
                elif member in self.team2:
                    await member.move_to(channel_team2)
        self.bot.state.get_guild_state(ctx.guild.id).last_team = []

    @commands.command(name='link', help = help_text.link_HelpText.text, brief = help_text.link_HelpText.brief, usage = help_text.link_HelpText.usage)
    @commands.check(checks.is_riot_enabled)
    async def link_(self, ctx, summoner_name):
        try:
            riot_commands.link_account(ctx.message.author.name, summoner_name, self.bot.config.get_guild_config(ctx.guild.id), general_config=self.bot.config.general_config, guild_id=ctx.guild.id)
        except Exception as error:
            logger.error("Error linking %s: %s", summoner_name, error)
            #TODO Add a link to our accounts
            await ctx.message.author.send(f'Dein Lol-Account konnte nicht mit deinem Discord Account verbunden werden. Richtiger Umgang mit ``!link`` ist unter ``{ctx.bot.command_prefix}help link`` zu finden. Falls das nicht weiterhilft, wende dich bitte an Jan oder Nick')
            raise error
        else:
            await ctx.message.author.send(f'Dein Lol-Account wurde erfolgreich mit deinem Discord Account verbunden!\nFalls du deinen Account wieder entfernen möchtest benutze das ``{ctx.bot.command_prefix}unlink`` Command.')
            logger.info("%s was linked.", summoner_name)

    @commands.command(name='unlink', help = help_text.unlink_HelpText.text, brief = help_text.unlink_HelpText.brief, usage = help_text.unlink_HelpText.usage)
    @commands.check(checks.is_riot_enabled)
    async def unlink_(self, ctx, *summoner_names):
        logger.debug("!unlink called")
        
        #Todo Why???
        if len(list(summoner_names)) != 0:
            raise commands.CommandInvokeError
        
        riot_commands.unlink_account(ctx.message.author.name, self.bot.config.get_guild_config(ctx.guild.id), ctx.guild.id)
        await ctx.message.author.send(
            'Dein Lol-Account wurde erfolgreich von deinem Discord Account getrennt!')
        logger.info("%s was unlinked", ctx.message.author.name)

    # @commands.command(name='leaderboard', help = help_text.leaderboard_HelpText.text, brief = help_text.leaderboard_HelpText.brief, usage = help_text.leaderboard_HelpText.usage)
    # @checks.has_any_role("admin_id")
    # async def leaderboard_(self, ctx):
    #     logger.debug("!leaderboard called")
    #     if False:
    #         loading_message = await ctx.send("This will take a few seconds. Processing...")
    #         _embed = riot_commands.create_leaderboard_embed(self.bot.config.get_guild_config(ctx.guild.id), self.bot.config.general_config, ctx.guild.id)
    #         guild_config = self.bot.config.get_guild_config(ctx.guild.id)
    #         folder_name = guild_config.folders_and_files.folders_and_files.folder_champ_spliced.format(guild_id=ctx.guild.id)
    #         message = await ctx.send(file=discord.File(f'{folder_name}/leaderboard.png'))
    #         _embed = _embed.set_image(url=message.attachments[0].url)
    #         await ctx.send(embed=_embed)
    #         await loading_message.delete()
    #         await message.delete()
    #     else:
    #         await ctx.send("Not available right now. Use ``!plot`` instead.")
        

    @commands.command(name='create-channel', help = help_text.create_channel_HelpText.text, brief = help_text.create_channel_HelpText.brief, usage = help_text.create_channel_HelpText.usage)
    @discord.ext.commands.cooldown(rate=3, per=30)
    async def create_channel(self, ctx, kind, channel_name, *user_limit):
        logger.debug("!create-channel %s %s called by %s", kind, channel_name, ctx.message.author.name)
        guild_state = self.bot.state.get_guild_state(ctx.guild.id)
        for tmp_channels in guild_state.tmp_channel_ids:
            logger.debug("Check if channel %s with id %s is already created by user %s.", guild_state.tmp_channel_ids[tmp_channels]["name"], tmp_channels, ctx.message.author.name)
            if not guild_state.tmp_channel_ids[tmp_channels]['deleted'] and guild_state.tmp_channel_ids[tmp_channels]['author'] == ctx.message.author.id:
                logger.info("%s wanted to create a new temporary channel but already has created channel %s with id %s.", ctx.message.author.name, guild_state.tmp_channel_ids[tmp_channels]['name'], tmp_channels)
                raise exceptions.LimitReachedException('Der Autor hat schon einen temprorären Channel erstellt.')
        
        tmp_channel_category = self.bot.get_channel(self.bot.config.get_guild_config(ctx.guild.id).channel_ids.category_temporary)
        
        tmp_channel = None
        if channel_name is None:
            logger.error("!create-channel is called by user %s without a name.", ctx.message.author.name)
            return
        elif kind == 'text':
            tmp_channel = await ctx.message.guild.create_text_channel(channel_name, category=tmp_channel_category)
        elif kind == 'voice':
            if len(user_limit) > 0 and int(user_limit[0]) > 0 and int(user_limit[0]) <= 99:
                tmp_channel = await ctx.message.guild.create_voice_channel(channel_name, category=tmp_channel_category, user_limit=int(user_limit[0]))
            else:
                tmp_channel = await ctx.message.guild.create_voice_channel(channel_name, category=tmp_channel_category)
        else:
            logger.error("!create-channel is called by user %s with invalid type %s.", ctx.message.author.name, kind)
            return
        guild_state.tmp_channel_ids[tmp_channel.id] = {
            "timer": timers.start_timer(hrs=12),
            "author": ctx.message.author.id,
            "deleted": False,
            "name": channel_name
        }
        logger.info("Temporary %s-channel %s with id %s created", kind, channel_name, tmp_channel.id)

    @checks.is_activated("highlights")
    @commands.command()
    async def highlights(self, ctx: commands.Context):
        """ Prints the best highlights.

        Vote for your favorite highlight with adding a reaction to the highlight.
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
            type="rich",
            description=guild_config.messages.highlight_leaderboard_description.format(
                highlight_channel_mention=", ".join(
                    (self.bot.get_channel(channel).mention for channel in guild_config.channel_ids.highlights)
                    )
            )
        )

        embed.set_footer(text=guild_config.messages.highlight_leaderboard_footer.format(limit=limit))

        text_too_long = False

        max_standing = 3 if len(counts) >=3 else len(counts)
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
            await ctx.send("There were too many highlights so some older highlights were not taken in account.", delete_after=10)

def setup(bot: DiscordBot.KrautBot):
    bot.add_cog(UtilityCog(bot))
    logger.info('Utility cogs loaded')
