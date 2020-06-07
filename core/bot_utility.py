import random
import re
import json
import typing

import discord

from core import (
    timers,
    play_requests
)

from core import config
from core.DiscordBot import KrautBot
from core.state import GuildState


def read_config_file(filename):
    return json.load(open(f'./config/{filename}.json', 'r'))


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

def create_internal_play_request_message(message, play_request, guild_config: config.GuildConfig, state: GuildState):
    """
    Creates an internal play_request message.
    """
    play_request_time = re.findall('\d\d:\d\d', message.content)
    intern_message = guild_config.messages.create_internal_play_request.format(
        creator=play_request.message_author.name,
        free_places=10 - len(state.play_requests[message.id]),
        time=play_request_time
        )
    for player_tuple in state.play_requests[message.id]:
        intern_message += player_tuple[0].name + '\n'
    return intern_message


# TODO: implement this
def switch_to_internal_play_request(message, play_request, guild_config: config.GuildConfig, state: GuildState):
    return create_internal_play_request_message(message, play_request, guild_config, state)


def generate_auto_role_list(member, guild_config: config.GuildConfig):
    if len(member.roles) >= 2:
        return

    for role in member.guild.roles:
        if role.id == guild_config.unsorted_config.everyone_id or role.id == guild_config.unsorted_config.guest_id:
            yield role


def get_auto_role_list(member, guild_config: config.GuildConfig):
    return list(generate_auto_role_list(member, guild_config))



def is_in_channels(message: discord.message, channel_ids: list):
    return message.channel.id in channel_ids


# def is_in_channel(message: discord.message, channel_id: int):
#     return message.channel.id == channel_id


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


def get_purgeable_messages_list(message_cache, guild_config: config.GuildConfig):
    messages_list = []
    if guild_config.toggles.auto_delete:
        messages_list = [msg for msg in message_cache if timers.is_timer_done(message_cache[msg]["timer"])]
    return messages_list


def clear_message_cache(message_id, message_cache):
    if message_id in message_cache:
        del message_cache[message_id]


def clear_play_requests(message_id: int, state: GuildState):
    if message_id in state.play_requests:
        del state.play_requests[message_id]


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

def get_guild_config(bot: KrautBot, guild_id: int) -> config.GuildConfig:
    return bot.config.get_guild_config(guild_id)