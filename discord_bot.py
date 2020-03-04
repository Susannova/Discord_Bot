import sys
import os
import json
import time
import asyncio
import ast
from importlib import reload
import discord
from discord.ext import commands

sys.path.append(os.path.join(sys.path[0], 'modules'))

from modules import (
    consts as CONSTS_,
    riot,
    bot_utility as utility,
    reminder,
    ocr,
    checks
)


####################################################################
#                   === init functions ===                         #
####################################################################

def set_version(consts):
    version_file = open("./.git/refs/heads/master", "r")
    consts.VERSION = version_file.read()[:7]
    return consts


def read_config_json(filename):
    return json.load(open(f'./config/{filename}.json', 'r'))


def write_config_json(filename, data):
    with open(f'./config/{filename}.json', 'w', encoding='utf-8') as file_:
        json.dump(data, file_, ensure_ascii=False, indent=4)


####################################################################
#                        === init variables  ===                   #
####################################################################

bot = commands.Bot(command_prefix='!')

BOT_TOKENS = read_config_json('bot')

CONSTS_ = set_version(CONSTS_)

CONFIG_ = read_config_json('configuration')
bot._play_requests = {}
bot._tmp_message_author = None
bot._message_cache = []

check_handler = checks.CheckHandler()
check_handler._CONFIG_ = CONFIG_
check_handler.debug_bool = False


####################################################################
#                       === commands ===                           #
####################################################################

@bot.command(name='create-team')
@check_handler.is_in_channels([CONSTS_.CHANNEL_INTERN_PLANING, CONSTS_.CHANNEL_BOT])
async def create_team(ctx):
    voice_channel = utility.get_voice_channel(ctx.message, CONSTS_.CHANNEL_CREATE_TEAM_VOICE)
    players_list = utility.get_players_in_channel(voice_channel)
    await ctx.message.channel.send(utility.create_team(players_list))

@bot.command(name='play-now')
@check_handler.is_in_channels([CONSTS_.CHANNEL_PLAY_REQUESTS, CONSTS_.CHANNEL_BOT])
async def play_now(ctx):
    bot.tmp_message_author = ctx.message.author
    await ctx.send(CONSTS_.MESSAGE_PLAY_NOW.format(ctx.message.author.mention))


@bot.command(name='play-lol')
@check_handler.is_in_channels([CONSTS_.CHANNEL_PLAY_REQUESTS, CONSTS_.CHANNEL_BOT])
async def play_lol(ctx, _time):
    bot.tmp_message_author = ctx.message.author
    await ctx.send(CONSTS_.MESSAGE_PLAY_LOL.format(
        ctx.message.author.mention, _time))

@bot.command(name='clash')
@check_handler.is_in_channels([CONSTS_.CHANNEL_BOT, CONSTS_.CHANNEL_MEMBER_ONLY])
@check_handler.has_n_attachments(1)
async def clash_(ctx):
    attached_image = ctx.message.attachments[0]
    attached_image_file_name = attached_image.filename
    await attached_image.save(attached_image_file_name)
    ocr.set_image_file_name(attached_image_file_name)
    await ctx.send(ocr.run_ocr())
    ocr.clean_up_image(attached_image_file_name)
    await ctx.send(
        f'If you want to receive the best bans \
        for the scoutet team copy the following Command:\n?bans \
        {ocr.get_formatted_summoner_names()}')

@bot.command(name='player')
@check_handler.is_riot_enabled()
async def player_(ctx):
    await ctx.send(riot.riot_command(ctx.message))

@bot.command(name='smurf')
@check_handler.is_riot_enabled()
async def smurf_(ctx):
    await ctx.send(riot.riot_command(ctx.message))

@bot.command(name='bans')
@check_handler.is_riot_enabled()
async def bans_(ctx):
    await ctx.send(
            riot.riot_command(ctx.message), file=discord.File(
                f'./{CONSTS_.FOLDER_CHAMP_SPLICED}/image.jpg'))

@bot.command(name='version')
@check_handler.is_in_channels([CONSTS_.CHANNEL_BOT])
async def version_(ctx):
    await ctx.send(CONSTS_.VERSION)

@bot.command(name='reload-config')
@check_handler.is_in_channels([CONSTS_.CHANNEL_BOT])
async def reload_config(ctx):
    global CONSTS_
    global CONFIG_
    global check_handler
    await ctx.send("Reload configuration.json:")
    CONFIG_ = read_config_json('configuration')
    check_handler._CONFIG_ = CONFIG_
    CONSTS_ = reload(CONSTS_)
    CONSTS_ = set_version(CONSTS_)
    await ctx.send("Done.")

@bot.command(name='enable-debug')
@check_handler.is_in_channels([CONSTS_.CHANNEL_BOT])
@check_handler.is_debug_config_enabled()
async def enable_debug(ctx):
    global CONFIG_
    global check_handler
    check_handler._debug_bool = True
    await ctx.send("Debugging is activated for one hour.")
    await asyncio.sleep(3600)
    check_handler._debug_bool = False
    CONFIG_["TOGGLE_DEBUG"] = False
    write_config_json('configuration', CONFIG_)
    await ctx.send("Debugging is deactivated.")

@bot.command(name='print')
@check_handler.is_in_channels([CONSTS_.CHANNEL_BOT])
@check_handler.is_debug_enabled()
async def print_(ctx):
    return_string = ast.literal_eval(ctx.message.content.split(' ')[1])
    await ctx.send(return_string)
    print(return_string)

@bot.command(name='end')
@check_handler.is_in_channels([CONSTS_.CHANNEL_BOT])
async def end_(ctx):
    await ctx.send('Bot is shut down!')
    await bot.logout()
####################################################################
#                    === error handlers ===                        #
####################################################################

@create_team.error
@play_now.error
@play_lol.error
@clash_.error
async def error_handler(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('Das hat nicht funktioniert. (Überprüfe, ob du im richtigen Channel bist.)')
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Es fehlt ein Parameter. (z.B. der Zeitparameter bei ?play-lol)')


####################################################################
#                        === events ===                            #
####################################################################
@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))


@bot.event
async def on_member_join(member):
    """Automatically assigns lowest role to
    anyone that joins the server.
    """
    await member.edit(roles=utility.get_auto_role_list(member))

####################################################################
#               === on_message event / Dispatcher ===              #
####################################################################
@bot.event
async def on_message(message):
    if isinstance(message.channel, discord.DMChannel):
        return

####################################################################
#                        === auto react ===                        #
#   reacts to all patterns in consts.PATTERN_LIST_AUTO_REACT       #
#   and creates a new play_request                                 #
####################################################################
    if CONFIG_["TOGGLE_AUTO_REACT"] and utility.has_any_pattern(message):
        await message.add_reaction(bot.get_emoji(CONSTS_.EMOJI_ID_LIST[5]))
        await message.add_reaction(CONSTS_.EMOJI_PASS)

        bot._play_requests[message.id] = [[bot._tmp_message_author, time.time()]]
        if CONFIG_["TOGGLE_AUTO_DELETE"]:
            bot._message_cache = utility.update_message_cache(
                message, bot._message_cache)
            bot._message_cache, deleteable_messages = utility.get_purgeable_messages(
                bot._message_cache)
            for deleteable_message in deleteable_messages:
                await deleteable_message.delete()
####################################################################
#                       === auto reminder ===                      #
####################################################################
        if utility.has_pattern(message, CONSTS_.PATTERN_PLAY_REQUEST):
            time_difference = reminder.get_time_difference(message.content)
            if time_difference > 0:
                await asyncio.sleep(time_difference)
                for player in bot._play_requests[message.id]:
                    await player[0].send(CONSTS_.MESSAGE_PLAY_REQUEST_REMINDER)

###################################################################

    # make all messages in play_requests channel auto_deleteable
    if CONFIG_["TOGGLE_AUTO_DELETE"] \
    and utility.is_in_channel(message, CONSTS_.CHANNEL_PLAY_REQUESTS):
        bot._message_cache = utility.update_message_cache(message, bot._message_cache)

        if not utility.contains_any_command(message, CONSTS_.COMMAND_LIST_PLAY_REQUEST) \
        and message.author != bot.user:
            await message.delete()

    await bot.process_commands(message)

##########################################################

    # if CONFIG_["TOGGLE_COMMAND_ONLY"]:
    # """Command only mode.
    # Every message that is not a command gets deleted.
    # """
    #     if not utility.contains_any_command(message, CONSTS_.COMMAND_LIST_PLAY_REQUEST):
    #         await message.delete()

@bot.event
async def on_message_delete(message):
    # delete play_request if old play-request gets deleted
    if utility.has_any_pattern(message):
        del bot._play_requests[message.id]
    for message_tuple in bot._message_cache:
        if message in message_tuple:
            bot._message_cache.remove(message_tuple)

####################################################################
#                        === auto dm ===                           #
####################################################################
@bot.event
async def on_reaction_add(reaction, user):
    # auto dm

    if not CONFIG_["TOGGLE_AUTO_DM"]:
        return

    if not utility.is_auto_dm_subscriber(reaction.message, bot, user, bot._play_requests):
        return

    message_id = reaction.message.id
    play_request_author = bot._play_requests[message_id][0][0]
    utility.add_subscriber_to_play_request(message_id, user, bot._play_requests)
    # if reaction is 'EMOJI_PASS' delete player from play_request and return
    if str(reaction.emoji) == CONSTS_.EMOJI_PASS:
        for player in bot._play_requests[message_id]:
            if user == player[0]:
                bot._play_requests[message_id].remove(player)
        return

    # send auto dms to subscribers and author
    for player in bot._play_requests[message_id]:
        if player[0] == play_request_author and player[0] != user:
            await play_request_author.send(
                CONSTS_.MESSAGE_AUTO_DM_CREATOR.format(user.name, str(reaction.emoji)))
        elif player[0] != user:
            await player[0].send(
                CONSTS_.MESSAGE_AUTO_DM_SUBSCRIBER.format(
                    user.name, play_request_author.name, str(reaction.emoji)))
    # switch to internal play request if more than 6 players(author + 5 players_known) are subscribed
    if len(bot._play_requests[message_id]) == 6:
        await reaction.channel.send(
            utility.switch_to_internal_play_request(bot._play_requests))


####################################################################
#                        === run ===                               #
####################################################################
if __name__ == '__main__':
    print("Start Bot")
    bot.run(str(BOT_TOKENS["token"]))
    print("End")
