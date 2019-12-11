import consts
import random

message = None

# === functions === #
def set_message(_message):
    message = _message

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
def is_purgeable_message(cmds, channel, excepted_users):
    if contains_command(tuple(cmds)) and is_in_channel(channel):
        if message.author.name in excepted_users:
            return False
        return True
    return False


# creates an internal play_request message
def create_internal_play_request_message(message):
    play_request_time = re.findall('\d\d:\d\d', message.content)
    intern_message = consts.MESSAGE_CREATE_INTERN_PLAY_REQUEST.format(message.author.name, 9  - len(play_requests[str(message.id)][0].players_known), play_request_time, message.author.name)
    for player in play_requests[play_requests[str(message.id)]]:
        intern_message += player.players_known.keys() + '\n'
    return intern_message

#TODO: implement this
def switch_to_internal_play_request(message):
    print(create_internal_play_request_message(message))


# BUG: collides with play_requests and manual deletes
# def get_purgeable_messages(message):
#     message_cache.append((message, start_timer(secs=10)))
#     deleteable_messages = []
#     for msg in message_cache:
#         if is_timer_done(msg[1]):
#             deleteable_messages.append(msg[0])
#             message_cache.remove(msg)
#     return deleteable_messages


def has_pattern(message):
    for pattern in consts.PATTERN_LIST_AUTO_REACT:
        if message.content.find(pattern) > -1:
            return True
    return False


def get_auto_role_list(member):
    global config
    
    # if member already has a role => do nothing
    if len(member.roles) >= 2:
        return

    # fill role_list with the default role(@everyone) and the lowest role(Setzling)
    role_list = []
    for role in member.guild.roles:
        if role.id == config["ROLE_EVERYONE_ID"] or role.id == config["ROLE_SETZLING_ID"]:
            role_list.append(role)
    return role_list

def contains_command(cmd):
    if message.content.startswith(cmd):
        return True
    return False

def is_in_channels(channels):
    for channel in channels:
        if message.channel.name == channel:
            return True
    return False

def is_in_channel(channel):
    if message.channel.name == channel:
        return True
    return False

def get_voice_channel(name):
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