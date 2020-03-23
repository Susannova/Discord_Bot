import asyncio
import ast
from importlib import reload
import re

import discord
from discord.ext import commands

from core import (
    consts,
    bot_utility as utility,
    ocr,
    checks,
    exceptions
)

from riot import riot_commands

from core.state import global_state as gstate


class KrautCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='create-team')
    @checks.is_in_channels([consts.CHANNEL_INTERN_PLANING, consts.CHANNEL_COMMANDS])
    async def create_team(self, ctx: commands.Context):
        voice_channel = utility.get_voice_channel(ctx.message, consts.CHANNEL_CREATE_TEAM_VOICE)
        players_list = utility.get_players_in_channel(voice_channel)
        await ctx.send(utility.create_team(players_list))

    @commands.command(name='create-clash')
    @checks.is_in_channels([consts.CHANNEL_CLASH])
    async def create_clash(self, ctx, arg):
        gstate.tmp_message_author = ctx.message.author
        gstate.clash_date = arg
        await ctx.send(consts.MESSAGE_CLASH_CREATE.format(
            ctx.message.author.mention, arg
        ))

    @commands.command(name='play-now')
    @checks.is_in_channels([consts.CHANNEL_PLAY_REQUESTS])
    async def play_now(self, ctx):
        gstate.tmp_message_author = ctx.message.author
        await ctx.send(consts.MESSAGE_PLAY_NOW.format(gstate.tmp_message_author.mention))

    @commands.command(name='play-lol')
    @checks.is_in_channels([consts.CHANNEL_PLAY_REQUESTS])
    async def play_lol(self, ctx, _time):
        if len(re.findall('[0-2][0-9]:[0-5][0-9]', _time)) == 0:
            raise exceptions.BadArgumentFormat()
        gstate.tmp_message_author = ctx.message.author
        await ctx.send(consts.MESSAGE_PLAY_LOL.format(
            gstate.tmp_message_author.mention, _time))

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
        print(arg)
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
        if len(list(team_names)) != 0:
            raise commands.CheckFailure()
        await ctx.send(
            riot_commands.get_best_bans_for_team(team_names), file=discord.File(
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
    async def unlink_(self, ctx):
        try:
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

    @commands.command(name='test-embed')
    @commands.has_role(consts.ROLE_ADMIN_ID)
    async def test_embed(self, ctx):
        await ctx.send(embed=riot_commands.create_embed(ctx))

    @commands.command(name='test-plt')
    @commands.has_role(consts.ROLE_ADMIN_ID)
    async def test_plt(self, ctx):
        riot_commands.test_matplotlib()
        await ctx.send(file=discord.File(f'./{consts.FOLDER_CHAMP_SPLICED}/leaderboard.png'))


    @create_team.error
    @create_clash.error
    @play_now.error
    @play_lol.error
    @clash_.error
    @enable_debug.error
    @print_.error
    @player_.error
    @smurf_.error
    @bans_.error
    async def error_handler(self, ctx, error):
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

