import logging

import asyncio, time

import discord
from discord.ext import commands

from core import (
    bot_utility as utility,
    checks,
    exceptions,
    timers,
    help_text
)

from riot import riot_commands

from core.config import CONFIG
from core.state import global_state as gstate

logger = logging.getLogger(__name__)


class UtilityCog(commands.Cog, name='Utility Commands'):
    @commands.command(name='create-team', help = help_text.create_team_HelpText.text, brief = help_text.create_team_HelpText.brief, usage = help_text.create_team_HelpText.usage)
    @checks.is_in_channels(CONFIG.channel_ids.commands)
    async def create_team(self, ctx: commands.Context, *player_names):
        logger.debug('!create-team command called')
        member = await discord.ext.commands.MemberConverter().convert(ctx, ctx.message.author.name)
        voice_channel = discord.utils.find(lambda x: member in x.members, ctx.message.guild.voice_channels)
        voice_channel = voice_channel if voice_channel is not None else utility.get_voice_channel(ctx.message, CONFIG.channel_ids.create_team_voice[0])
        players_list = utility.get_players_in_channel(voice_channel)
        if len(list(player_names)) != 0:
            for player_name in player_names:
                if player_name != 'mv':
                    players_list.append(player_name)
        message, team1, team2 = utility.create_team(players_list)
        await ctx.send(message)

        role = discord.utils.find(lambda x: x.name == 'Wurzel', ctx.message.guild.roles)
        if len(list(player_names)) == 0:
            return

        if player_names[0] == 'mv' and role in ctx.message.author.roles:
            channel_team1 = discord.utils.find(lambda x: x.name == 'Team 1', ctx.message.guild.voice_channels)
            channel_team2 = discord.utils.find(lambda x: x.name == 'Team 2', ctx.message.guild.voice_channels)
            for member in voice_channel.members:
                if member.name in team1:
                    await member.move_to(channel_team1)
                elif member.name in team2:
                    await member.move_to(channel_team2)

    @commands.command(name='link', help = help_text.link_HelpText.text, brief = help_text.link_HelpText.brief, usage = help_text.link_HelpText.usage)
    @checks.is_riot_enabled()
    @checks.is_in_channels(CONFIG.channel_ids.commands + CONFIG.channel_ids.commands_member)
    async def link_(self, ctx, summoner_name):
        try:
            riot_commands.link_account(ctx.message.author.name, summoner_name)
        except Exception as error:
            logger.error("Error linking %s: %s", summoner_name, error)
            #TODO Add a link to our accounts
            await ctx.message.author.send(f'Dein Lol-Account konnte nicht mit deinem Discord Account verbunden werden. Richtiger Umgang mit ``!link`` ist unter ``{ctx.bot.command_prefix}help link`` zu finden. Falls das nicht weiterhilft, wende dich bitte an Jan oder Nick')
            raise error
        else:
            await ctx.message.author.send(f'Dein Lol-Account wurde erfolgreich mit deinem Discord Account verbunden!\nFalls du deinen Account wieder entfernen möchtest benutze das ``{ctx.bot.command_prefix}unlink`` Command.')
            logger.info("%s was linked.", summoner_name)

    @commands.command(name='unlink', help = help_text.unlink_HelpText.text, brief = help_text.unlink_HelpText.brief, usage = help_text.unlink_HelpText.usage)
    @checks.is_in_channels(CONFIG.channel_ids.commands + CONFIG.channel_ids.commands_member)
    async def unlink_(self, ctx, *summoner_names):
        logger.debug("!unlink called")
        
        #Todo Why???
        if len(list(summoner_names)) != 0:
            raise commands.CommandInvokeError
        
        riot_commands.unlink_account(ctx.message.author.name)
        await ctx.message.author.send(
            'Dein Lol-Account wurde erfolgreich von deinem Discord Account getrennt!')
        logger.info("%s was unlinked", ctx.message.author.name)

    @commands.command(name='purge', hidden=True)
    @commands.has_role(CONFIG.basic_config.admin_id)
    async def purge_(self, ctx, count: int):
        logger.info("!purge %s called in channel %s", count, ctx.message.channel.name)
        last_count_messages = await ctx.message.channel.history(limit=count + 1).flatten()
        # TODO Bad, it is not neccesary to create a list here if we never use it.
        [await message_.delete() for message_ in last_count_messages if not message_.pinned]

    @commands.command(name='leaderboard-old', hidden=True)
    @commands.has_role(CONFIG.basic_config.admin_id)
    async def test_embed(self, ctx):
        logger.debug("!leaderboard-old called")
        await ctx.send(embed=riot_commands.create_embed(ctx))

    @commands.command(name='leaderboard', help = help_text.leaderboard_HelpText.text, brief = help_text.leaderboard_HelpText.brief, usage = help_text.leaderboard_HelpText.usage)
    @commands.has_role(CONFIG.basic_config.admin_id)
    async def leaderboard_(self, ctx):
        logger.debug("!leaderboard called")
        if False:
            loading_message = await ctx.send("This will take a few seconds. Processing...")
            _embed = riot_commands.create_leaderboard_embed()
            message = await ctx.send(file=discord.File(f'{CONFIG.folders_and_files.folder_champ_spliced}/leaderboard.png'))
            _embed = _embed.set_image(url=message.attachments[0].url)
            await ctx.send(embed=_embed)
            await loading_message.delete()
            await message.delete()
        else:
            await ctx.send("Not available right now. Use ``!plot`` instead.")
        

    # dont use this
    @commands.command(name='game-selector', hidden=True)
    @commands.has_role(CONFIG.basic_config.admin_id)
    async def game_selector(self, ctx):
        message = await ctx.send(CONFIG.messages.game_selector)
        for emoji in ctx.bot.emojis:
            if emoji.name == 'rl' or emoji.name == 'lol' or emoji.name == 'csgo' or emoji.name == 'apex' or emoji.name == 'val':
                await message.add_reaction(emoji)
        gstate.game_selector_id = message.id

    @commands.command(name='create-channel', help = help_text.create_channel_HelpText.text, brief = help_text.create_channel_HelpText.brief, usage = help_text.create_channel_HelpText.usage)
    @checks.is_in_channels(CONFIG.channel_ids.commands_member)
    @discord.ext.commands.cooldown(rate=3, per=30)
    async def create_channel(self, ctx, kind, channel_name, *user_limit):
        logger.debug("!create-channel %s %s called by %s", kind, channel_name, ctx.message.author.name)
        for tmp_channels in gstate.tmp_channel_ids:
            logger.debug("Check if channel %s with id %s is already created by user %s.", gstate.tmp_channel_ids[tmp_channels]["name"], tmp_channels, ctx.message.author.name)
            if not gstate.tmp_channel_ids[tmp_channels]['deleted'] and gstate.tmp_channel_ids[tmp_channels]['author'] == ctx.message.author.id:
                logger.info("%s wanted to create a new temporary channel but already has created channel %s with id %s.", ctx.message.author.name, gstate.tmp_channel_ids[tmp_channels]['name'], tmp_channels)
                raise exceptions.LimitReachedException('Der Autor hat schon einen temprorären Channel erstellt.')
        tmp_channel_category = discord.utils.find(lambda x: x.name == CONFIG.channel_ids.category_temporary, ctx.message.guild.channels)
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
        gstate.tmp_channel_ids[tmp_channel.id] = {
            "timer": timers.start_timer(hrs=12),
            "author": ctx.message.author.id,
            "deleted": False,
            "name": channel_name
        }
        logger.info("Temporary %s-channel %s with id %s created", kind, channel_name, tmp_channel.id)

# TODO I don't think this should be used like this..
    # @create_team.error
    # async def error_handler(self, ctx, error):
    #     logger.exception('Error handler got called: %s', error)
    #     if isinstance(error, commands.CheckFailure):
    #         if str(ctx.command) == 'enable-debug':
    #             await ctx.send(
    #                 'Der Debug Toggle in der Konfiguration ist nicht eingeschaltet.')
    #         elif str(ctx.command) == 'purge':
    #             await ctx.send(
    #                 'Du hast nicht die benötigten Rechte um dieses Command auszuführen.')
    #         elif str(ctx.command) == 'print':
    #             await ctx.send(
    #                 f'Der Debug Modus ist zur Zeit nicht aktiviert. Versuche es mit {ctx.bot.command_prefix}enable-debug zu aktivieren.')
    #         else:
    #             await ctx.send(
    #                 'Das hat nicht funktioniert. (Überprüfe, ob du im richtigen Channel bist.)')
    #     elif isinstance(error, commands.MissingRequiredArgument):
    #         await ctx.send(
    #             'Es fehlt ein Parameter. (z.B. der Zeitparameter bei ?play-lol)')
    #     else:
    #         await ctx.send(error)

def setup(bot: commands.Bot):
    bot.add_cog(UtilityCog())
    logger.info('Utility cogs loaded')