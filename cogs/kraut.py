import asyncio
import ast
from importlib import reload
import re
import logging

import discord
from discord.ext import commands

from core import (
    consts,
    bot_utility as utility,
    ocr,
    checks,
    exceptions,
    reminder,
    timers
)

from riot import riot_commands

from core.state import global_state as gstate
from core.play_requests import PlayRequest, PlayRequestCategory

logger = logging.getLogger(consts.LOG_NAME)

class KrautCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='create-team')
    @checks.is_in_channels([consts.CHANNEL_INTERN_PLANING, consts.CHANNEL_COMMANDS])
    async def create_team(self, ctx: commands.Context, *player_names):
        voice_channel = discord.utils.find(lambda x: len(x.members) >= 6, ctx.message.guild.voice_channels)
        voice_channel = voice_channel if voice_channel is not None else utility.get_voice_channel(ctx.message, consts.CHANNEL_CREATE_TEAM_VOICE_ID)
        players_list = utility.get_players_in_channel(voice_channel)
        if len(list(player_names)) != 0:
            for player_name in player_names:
                if player_name == 'mv':
                    continue
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
        
    @commands.command(name='create-clash')
    @checks.is_in_channels([consts.CHANNEL_CLASH])
    async def create_clash(self, ctx, arg):
        gstate.tmp_message_author = ctx.message.author
        gstate.clash_date = arg
        await ctx.send(consts.MESSAGE_CLASH_CREATE.format(
            ctx.message.author.mention, arg))

    @commands.command(name='play')
    @checks.is_in_channels([consts.CHANNEL_PLAY_REQUESTS])
    async def play_(self, ctx, game_name, _time):
        game_name = game_name.upper()
        message = 'Something went wrong.'
        if _time == 'now':
            message = consts.MESSAGE_PLAY_NOW.format(ctx.guild.get_role(consts.GAME_NAME_TO_ROLE_ID_DICT[game_name]).mention, ctx.message.author.mention, consts.GAME_NAME_DICT[game_name])
        else:
            if len(re.findall('[0-2][0-9]:[0-5][0-9]', _time)) == 0:
                raise exceptions.BadArgumentFormat()
            message = consts.MESSAGE_PLAY_AT.format(ctx.guild.get_role(consts.GAME_NAME_TO_ROLE_ID_DICT[game_name]).mention, ctx.message.author.mention, consts.GAME_NAME_DICT[game_name], _time)
        play_request_message = await ctx.send(message)
        _category = self.get_category(game_name)
        gstate.play_requests[play_request_message.id] = PlayRequest(play_request_message, ctx.message.author, category=_category)
        await play_request_message.add_reaction(ctx.bot.get_emoji(consts.EMOJI_ID_LIST[5]))
        await play_request_message.add_reaction(consts.EMOJI_PASS)

        if not utility.is_in_channel(ctx.message, consts.CHANNEL_BOT):
            for member in ctx.message.guild.members:
                for role in member.roles:
                    if role.id == consts.GAME_NAME_TO_ROLE_ID_DICT[game_name]:
                        if member.id != ctx.message.author.id:
                            await member.send(consts.MESSAGE_PLAY_REQUEST_CREATED.format(ctx.message.author.name, consts.GAME_NAME_DICT[game_name], play_request_message.jump_url))

        if _time != 'now':
            await self.auto_reminder(play_request_message)

    def get_category(self, game_name):
        _category = None
        if game_name == 'LOL':
            _category = PlayRequestCategory.LOL
        elif game_name == 'APEX':
            _category = PlayRequestCategory.APEX
        elif game_name == 'CSGO':
            _category = PlayRequestCategory.CSGO
        elif game_name == 'RL':
            _category = PlayRequestCategory.RL
        return _category

    async def auto_reminder(self, message):
        time_difference = reminder.get_time_difference(message.content)
        if time_difference > 0:
            await asyncio.sleep(time_difference)
            for player in gstate.play_requests[message.id].generate_all_players():
                await player.send(consts.MESSAGE_PLAY_REQUEST_REMINDER)


    @commands.command(name='clash')
    @checks.is_in_channels([consts.CHANNEL_COMMANDS_MEMBER])
    @checks.has_n_attachments(1)
    async def clash_(self, ctx):
        attached_image = ctx.message.attachments[0]
        attached_image_file_name = attached_image.filename
        await attached_image.save(attached_image_file_name)
        ocr.set_image_file_name(attached_image_file_name)
        await ctx.send(ocr.run_ocr())
        ocr.clean_up_image(attached_image_file_name)
        await ctx.send(
            consts.MESSAGE_BANS.format(ocr.get_formatted_summoner_names()))

    @commands.command(name='player')
    @checks.is_riot_enabled()
    @checks.is_in_channels([consts.CHANNEL_COMMANDS, consts.CHANNEL_COMMANDS_MEMBER])
    async def player_(self, ctx, *summoner_name):
        if len(list(summoner_name)) == 0:
            arg = None
        else:
            arg = summoner_name[0]
        await ctx.send(riot_commands.get_player_stats(ctx.message.author.name, arg))

    @commands.command(name='smurf')
    @checks.is_riot_enabled()
    @checks.is_in_channels([consts.CHANNEL_COMMANDS, consts.CHANNEL_COMMANDS_MEMBER])
    async def smurf_(self, ctx, *summoner_name):
        if len(list(summoner_name)) == 0:
            arg = None
        else:
            arg = summoner_name[0]
        await ctx.send(riot_commands.get_smurf(ctx.message.author.name, arg))

    @commands.command(name='bans')
    @checks.is_riot_enabled()
    @checks.is_in_channels([consts.CHANNEL_COMMANDS, consts.CHANNEL_COMMANDS_MEMBER])
    async def bans_(self, ctx, *team_names):
        await ctx.send(
            riot_commands.calculate_bans_for_team(team_names), file=discord.File(
                f'./{consts.FOLDER_CHAMP_SPLICED}/image.jpg'))

    @commands.command(name='link')
    @checks.is_riot_enabled()
    @checks.is_in_channels([consts.CHANNEL_COMMANDS, consts.CHANNEL_COMMANDS_MEMBER])
    async def link_(self, ctx, summoner_name):
        try:
            riot_commands.link_account(ctx.message.author.name, summoner_name)
        except commands.CommandInvokeError:
            pass
        else:
            await ctx.message.author.send(
                f'Dein Lol-Account wurde erfolgreich mit deinem Discord Account verbunden!\nFalls du deinen Account wieder entfernen möchtest benutze das {ctx.bot.command_prefix}unlink Command.')

    @commands.command(name='unlink')
    @checks.is_in_channels([consts.CHANNEL_COMMANDS, consts.CHANNEL_COMMANDS_MEMBER])
    async def unlink_(self, ctx, *summoner_names):
        try:
            if len(list(summoner_names)) != 0:
                raise commands.CommandInvokeError
            riot_commands.unlink_account(ctx.message.author.name)
        except commands.CommandInvokeError:
            pass
        else:
            await ctx.message.author.send(
                'Dein Lol-Account wurde erfolgreich von deinem Discord Account getrennt!')

    @commands.command(name='version')
    @checks.is_in_channels([])
    @commands.has_role(consts.ROLE_ADMIN_ID)
    async def version_(self, ctx):
        await ctx.send(gstate.VERSION)

    @commands.command(name='reload-config')
    @checks.is_in_channels([])
    @commands.has_role(consts.ROLE_ADMIN_ID)
    async def reload_config(self, ctx):
        global consts
        await ctx.send("Reload configuration.json:")
        gstate.read_config()
        consts = reload(consts)
        gstate.get_version()
        await ctx.send("Done.")

    @commands.command(name='enable-debug')
    @checks.is_in_channels([])
    @checks.is_debug_config_enabled()
    @commands.has_role(consts.ROLE_ADMIN_ID)
    async def enable_debug(self, ctx):
        gstate.debug = True
        await ctx.send("Debugging is activated for one hour.")
        await asyncio.sleep(3600)
        gstate.debug = False
        gstate.CONFIG["TOGGLE_DEBUG"] = False
        gstate.write_and_reload_config(gstate.CONFIG)
        await ctx.send("Debugging is deactivated.")

    @commands.command(name='print')
    @checks.is_in_channels([])
    @checks.is_debug_enabled()
    @commands.has_role(consts.ROLE_ADMIN_ID)
    async def print_(self, ctx, arg):
        # return_string = ast.literal_eval(arg)
        # less safe but more powerful
        return_string = eval(arg)
        await ctx.send(return_string)
        print(return_string)

    @commands.command(name='end')
    @checks.is_in_channels([])
    @commands.has_role(consts.ROLE_ADMIN_ID)
    @commands.is_owner()
    async def end_(self, ctx):
        await ctx.send('Bot is shut down!')
        await self.bot.logout()

    @commands.command(name='purge')
    @commands.has_role(consts.ROLE_ADMIN_ID)
    async def purge_(self, ctx, count: int):
        last_count_messages = await ctx.message.channel.history(limit=count + 1).flatten()
        [await message_.delete() for message_ in last_count_messages if not message_.pinned]

    @commands.command(name='leaderboard')
    @commands.has_role(consts.ROLE_ADMIN_ID)
    async def test_embed(self, ctx):
        await ctx.send(embed=riot_commands.create_embed(ctx))

    @commands.command(name='test-plt')
    @commands.has_role(consts.ROLE_ADMIN_ID)
    async def test_plt(self, ctx):
        riot_commands.test_matplotlib()
        await ctx.send(file=discord.File(f'./{consts.FOLDER_CHAMP_SPLICED}/leaderboard.png'))

    # dont use this
    @commands.command(name='game-selector')
    @commands.has_role(consts.ROLE_ADMIN_ID)
    async def game_selector(self, ctx):
        message = await ctx.send(consts.MESSAGE_GAME_SELECTOR)
        for emoji in ctx.bot.emojis:
            if emoji.name == 'rl' or emoji.name == 'lol' or emoji.name == 'csgo' or emoji.name == 'apex':
                await message.add_reaction(emoji)
        gstate.game_selector_id = message.id

    @commands.command(name='create-channel')
    @checks.is_in_channels([consts.CHANNEL_COMMANDS_MEMBER])
    async def create_channel(self, ctx, channel_name):
        for tmp_channels in gstate.tmp_text_channels:
            if tmp_channels[2] == ctx.message.author:
                raise exceptions.LimitReachedException('Der Autor hat schon einen temprorären Channel erstellt.')
        tmp_channel_category = discord.utils.find(lambda x: x.name == consts.CHANNEL_CATEGORY_TEMPORARY, ctx.message.guild.channels)
        tmp_channel = await ctx.message0.guild.create_text_channel(channel_name, category=tmp_channel_category)
        gstate.tmp_text_channels.append((tmp_channel, timers.start_timer(hours=12), ctx.message.author))

    @create_team.error
    @create_clash.error
    @play_.error
    @clash_.error
    @enable_debug.error
    @print_.error
    @player_.error
    @smurf_.error
    @bans_.error
    async def error_handler(self, ctx, error):
        logger.exception('Error handler got called.')
        if isinstance(error, commands.CheckFailure):
            if str(ctx.command) == 'enable-debug':
                await ctx.send(
                    'Der Debug Toggle in der Konfiguration ist nicht eingeschaltet.')
            elif str(ctx.command) == 'purge':
                await ctx.send(
                    'Du hast nicht die benötigten Rechte um dieses Command auszuführen.')
            elif str(ctx.command) == 'print':
                await ctx.send(
                    f'Der Debug Modus ist zur Zeit nicht aktiviert. Versuche es mit {ctx.bot.command_prefix}enable-debug zu aktivieren.')
            else:
                await ctx.send(
                    'Das hat nicht funktioniert. (Überprüfe, ob du im richtigen Channel bist.)')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                'Es fehlt ein Parameter. (z.B. der Zeitparameter bei ?play-lol)')
        else: 
            await ctx.send(error)

