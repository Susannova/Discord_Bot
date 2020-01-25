import consts
import random
import time
import discord
import consts
import re
import timers

# === functions === #
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
    
    return teams_message


# checks if message should be purged based on if it starts with a specified command cmd
# and is send in a specfied channel name channel and is from a user excepted user
# that should not be purged
def is_purgeable_message(message, cmds, channel, excepted_users):
    if contains_command(message, tuple(cmds)) and is_in_channel(message, channel):
        if message.author.name in excepted_users:
            return False
        return True
    return False


# creates an internal play_request message
def create_internal_play_request_message(message, play_requests):
    play_request_time = re.findall('\d\d:\d\d', message.content)
    intern_message = consts.MESSAGE_CREATE_INTERN_PLAY_REQUEST.format(play_requests[message.id][0][0].name, 10  - len(play_requests[message.id]),play_request_time)
    for player_tuple in play_requests[message.id]:
        intern_message += player_tuple[0].name + '\n'
    return intern_message

#TODO: implement this
def switch_to_internal_play_request(play_requests):
    return create_internal_play_request_message(play_requests)


#BUG: collides with play_requests and manual deletes
def get_purgeable_messages(message_cache):
    deleteable_messages = []
    for msg in message_cache:
        if timers.is_timer_done(msg[1]):
            deleteable_messages.append(msg[0])
            message_cache.remove(msg)
    return message_cache, deleteable_messages



def has_any_pattern(message):
    for pattern in consts.PATTERN_LIST_AUTO_REACT:
        if message.content.find(pattern) > -1:
            return True
    return False

def has_pattern(message, pattern):
    if message.content.find(pattern) > -1:
        return True
    return False

def get_auto_role_list(member):
    if len(member.roles) >= 2:
        return

    # fill role_list with the default role(@everyone) and the lowest role(Setzling)
    role_list = []
    for role in member.guild.roles:
        if role.id == consts.ROLE_EVERYONE_ID or role.id == consts.ROLE_SETZLING_ID:
            role_list.append(role)
    return role_list

def contains_command(message, command):
    if message.content.startswith(command):
        return True
    return False

def contains_any_command(message, commands):
    for command in commands:
        if message.content.startswith(command):
            return True
    return False

def is_in_channels(message, channels):
    for channel in channels:
        if message.channel.name == channel:
            return True
    return False

def is_in_channel(message, channel):
    return message.channel.name == channel

def get_voice_channel(message, name):
    voice_channel = None
    for voice_channel_iterator in message.guild.voice_channels:
        if voice_channel_iterator.name == name:
            voice_channel = voice_channel_iterator
    return voice_channel

def get_players_in_channel(channel):
    players_list = []
    for member in channel.members:
        players_list.append(member.name)
    return players_list

def get_play_request_creator(message):
    return ''

def add_subscriber_to_play_request(message_id, user, play_requests):
    is_already_in_list = False
    for player_list in play_requests[message_id]:
        if user in player_list:
            is_already_in_list = True

    if not is_already_in_list:
        play_requests[message_id].append((user, time.time()))
    return play_requests

def is_auto_dm_subscriber(message, client, user, play_requests):
    if user.name in (client.user.name, "Secret Kraut9 Leader") or \
     is_in_channels(message, [consts.CHANNEL_INTERN_PLANING, consts.CHANNEL_PLAY_REQUESTS, consts.CHANNEL_BOT]) == False:
        return False

    message_id = message.id
    if message_id not in play_requests:
        return False

    play_request_author = play_requests[message_id][0][0]
    if user == play_request_author:
        return False

    return True

def update_message_cache(message, message_cache, time=18):
    message_cache.append((message, timers.start_timer(hrs=time)))
    return message_cache
