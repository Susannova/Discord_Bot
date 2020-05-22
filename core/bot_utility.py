import random
import re
import json

import discord

from core import consts, timers, play_requests
from core.state import global_state as gstate


def read_config_file(filename):
    return json.load(open(f'./config/{filename}.json', 'r'))


def create_team(players):
    num_players = len(players)
    team1 = random.sample(players, int(num_players / 2))
    team2 = players

    for player in team1:
        team2.remove(player)

    teams_message = consts.MESSAGE_TEAM_HEADER
    teams_message += consts.MESSAGE_TEAM_1
    for player in team1:
        teams_message += player + "\n"

    teams_message += consts.MESSAGE_TEAM_2
    for player in team2:
        teams_message += player + "\n"

    return teams_message, team1, team2

# FIXME: this is bs
def is_purgeable_message(message, cmds, channel, excepted_users):
    """
    Checks if message should be purged based on if it starts with
    a specified command cmd and is send in a specfied channel name
    channel and is from a user excepted user that should not be purged.
    """
    if contains_command(message, tuple(cmds)) and is_in_channel(message, channel):
        if message.author.name in excepted_users:
            return False
        return True
    return False


def create_internal_play_request_message(message, play_request):
    """
    Creates an internal play_request message.
    """
    play_request_time = re.findall('\d\d:\d\d', message.content)
    intern_message = consts.MESSAGE_CREATE_INTERN_PLAY_REQUEST.format(
        play_request.message_author.name, 10 - len(gstate.play_requests[message.id]), play_request_time)
    for player_tuple in gstate.play_requests[message.id]:
        intern_message += player_tuple[0].name + '\n'
    return intern_message


# TODO: implement this
def switch_to_internal_play_request(message, play_request):
    return create_internal_play_request_message(message, play_request)


def has_any_pattern(message):
    for pattern in consts.PATTERN_LIST_AUTO_REACT:
        if message.content.find(pattern) > -1:
            return True
    return False


def has_pattern(message, pattern):
    if message.content.find(pattern) > -1:
        return True
    return False


def generate_auto_role_list(member):
    if len(member.roles) >= 2:
        return

    for role in member.guild.roles:
        if role.id == consts.ROLE_EVERYONE_ID or role.id == consts.ROLE_SETZLING_ID:
            yield role


def get_auto_role_list(member):
    return list(generate_auto_role_list(member))


def contains_command(message, command):
    if message.content.startswith(command):
        return True
    return False


def contains_any_command(message, commands):
    for command in commands:
        if message.content.startswith(command):
            return True
    return False


def is_in_channels(message: discord.message, channels: list):
    return message.channel.id in channels


def is_in_channel(message: discord.message, channel_id: int):
    return message.channel.id == channel_id


#Todo dont use find here
def get_voice_channel(message, id):
    voice_channel = discord.utils.find(lambda x: x.id == id, message.guild.voice_channels)
    return voice_channel if voice_channel is not None else None


def generate_players_in_channel(channel):
    for member in channel.members:
        yield member.name


def get_players_in_channel(channel):
    return list(generate_players_in_channel(channel))


def add_subscriber_to_play_request(user, play_request: play_requests.PlayRequest):
    play_request.add_subscriber_id(user.id)


def is_user_bot(user, bot):
    if user.name in (bot.user.name, "Secret Kraut9 Leader"):
        return True
    return False


def is_already_subscriber(user, play_request: play_requests.PlayRequest):
    if user.id in play_request.subscriber_ids:
        return True
    return False


def is_play_request_author(user_id, play_request: play_requests.PlayRequest):
    if user_id == play_request.author_id:
        return True
    return False


def get_purgeable_messages_list(message_cache):
    messages_list = []
    if gstate.CONFIG["TOGGLE_AUTO_DELETE"]:
        messages_list = [msg for msg in message_cache if timers.is_timer_done(message_cache[msg]["timer"])]
    return messages_list


def clear_message_cache(message_id, message_cache):
    if message_id in message_cache:
        del message_cache[message_id]


def clear_play_requests(message):
    if has_any_pattern(message):
        del gstate.play_requests[message.id]


def pretty_print_list(*players) -> str:
    pretty_print = ''
    player_list = list(players[0])
    for player_object in player_list:
        if isinstance(player_object, list):
            for player in player_object:
                pretty_print += player + '\n'
        elif isinstance(player_object, str):
            pretty_print += player + '\n'
    return pretty_print

def insert_in_message_cache(message_cache, message_id, channel_id, time=10):
    message_cache[message_id] = {
        "timer": timers.start_timer(hrs=time),
        "channel": channel_id
    }
