import logging
import typing

import asyncio, time

import discord
from discord.ext import commands

from core import (
    bot_utility as utility,
    checks,
    exceptions,
    timers,
    help_text,
    DiscordBot
)

from riot import riot_commands

logger = logging.getLogger(__name__)


class UtilityCog(commands.Cog, name='Utility Commands'):
    def __init__(self, bot: DiscordBot.KrautBot):
        self.bot = bot

    @commands.command(name='create-team', help = help_text.create_team_HelpText.text, brief = help_text.create_team_HelpText.brief, usage = help_text.create_team_HelpText.usage)
    @checks.is_in_channels("commands")
    @checks.has_any_role("admin_id", "member_id")
    async def create_team(self, ctx: commands.Context, mv_bool: typing.Optional[bool], players_list: commands.Greedy[typing.Union[discord.Member, str]]):
        logger.debug('!create-team command called')

        if ctx.author.voice is not None:
            current_voice_channel = ctx.author.voice.channel
            players_list += current_voice_channel.members

        guild_config = utility.get_guild_config(self.bot, ctx.guild.id)

        message, team1, team2 = utility.create_team(players_list, guild_config)
        await ctx.send(message)

        if mv_bool:
            channel_team1 = self.bot.get_channel(guild_config.channel_ids.team_1)
            channel_team2 = self.bot.get_channel(guild_config.channel_ids.team_2)
            
            for member in players_list:
                if isinstance(member, discord.Member) and member.voice is not None:
                    if member in team1:
                        await member.move_to(channel_team1)
                    elif member in team2:
                        await member.move_to(channel_team2)

    @commands.command(name='link', help = help_text.link_HelpText.text, brief = help_text.link_HelpText.brief, usage = help_text.link_HelpText.usage)
    @commands.check(checks.is_riot_enabled)
    @checks.is_in_channels("commands", "commands_member")
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
    @checks.is_in_channels("commands", "commands_member")
    async def unlink_(self, ctx, *summoner_names):
        logger.debug("!unlink called")
        
        #Todo Why???
        if len(list(summoner_names)) != 0:
            raise commands.CommandInvokeError
        
        riot_commands.unlink_account(ctx.message.author.name, self.bot.config.get_guild_config(ctx.guild.id), ctx.guild.id)
        await ctx.message.author.send(
            'Dein Lol-Account wurde erfolgreich von deinem Discord Account getrennt!')
        logger.info("%s was unlinked", ctx.message.author.name)

    @commands.command(name='purge', hidden=True)
    @checks.has_any_role("admin_id")
    async def purge_(self, ctx, count: int):
        logger.info("!purge %s called in channel %s", count, ctx.message.channel.name)
        last_count_messages = await ctx.message.channel.history(limit=count + 1).flatten()

        for message_ in last_count_messages:
            if not message_.pinned:
                await message_.delete()

    @commands.command(name='leaderboard-old', hidden=True)
    @checks.has_any_role("admin_id")
    async def test_embed(self, ctx):
        logger.debug("!leaderboard-old called")
        await ctx.send(embed=riot_commands.create_embed(ctx, self.bot.config.get_guild_config(ctx.guild.id), self.bot.config.general_config, ctx.guild.id))

    @commands.command(name='leaderboard', help = help_text.leaderboard_HelpText.text, brief = help_text.leaderboard_HelpText.brief, usage = help_text.leaderboard_HelpText.usage)
    @checks.has_any_role("admin_id")
    async def leaderboard_(self, ctx):
        logger.debug("!leaderboard called")
        if False:
            loading_message = await ctx.send("This will take a few seconds. Processing...")
            _embed = riot_commands.create_leaderboard_embed(self.bot.config.get_guild_config(ctx.guild.id), self.bot.config.general_config, ctx.guild.id)
            guild_config = self.bot.config.get_guild_config(ctx.guild.id)
            folder_name = guild_config.folders_and_files.folders_and_files.folder_champ_spliced.format(guild_id=ctx.guild.id)
            message = await ctx.send(file=discord.File(f'{folder_name}/leaderboard.png'))
            _embed = _embed.set_image(url=message.attachments[0].url)
            await ctx.send(embed=_embed)
            await loading_message.delete()
            await message.delete()
        else:
            await ctx.send("Not available right now. Use ``!plot`` instead.")
        

    # dont use this
    @commands.command(name='game-selector', hidden=True)
    @checks.has_any_role("admin_id")
    async def game_selector(self, ctx: commands.Context):
        guild_config = self.bot.config.get_guild_config(ctx.guild.id)
        message = await ctx.send(self.bot.config.get_guild_config(ctx.guild.id).messages.game_selector)
        for emoji_id in guild_config.get_all_game_emojis():
            emoji = self.bot.get_emoji(emoji_id)
            await message.add_reaction(emoji)
        guild_config.unsorted_config.game_selector_id = message.id

    @commands.command(name='create-channel', help = help_text.create_channel_HelpText.text, brief = help_text.create_channel_HelpText.brief, usage = help_text.create_channel_HelpText.usage)
    @checks.is_in_channels("commands_member")
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
    
    @checks.is_in_channels("commands", "commands_member")
    @commands.command()
    async def highlights(self, ctx: commands.Context):
        ranking = {}
        highlight_channel = self.bot.get_channel(606864764936781837)
        test = await highlight_channel.history().flatten()
        for message in test:
            users = []
            for reaction in message.reactions:
                reaction_users = await reaction.users().flatten()
                for user in reaction_users:
                    if user not in users:
                        users.append(user)
            count = len(users)
            if count in ranking:
                ranking[count].append(message)
            else:
                ranking[count] = [message]
        
        counts = list(ranking.keys())
        counts.sort(reverse=True)

        text = "**The best highlights**\n\n"
        for standing in range(0, 1):
            urls = (message.jump_url for message in ranking[counts[standing]])
            text += f"Platz {standing + 1} ({counts[standing]} votes): {', '.join(urls)}\n"
        
        message = await ctx.send(text)

def setup(bot: DiscordBot.KrautBot):
    bot.add_cog(UtilityCog(bot))
    logger.info('Utility cogs loaded')