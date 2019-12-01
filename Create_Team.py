import discord
import random
import json
import time
import re
import consts
from importlib import reload


# work with time:
#import datetime
#import os
#import time
#os.environ['TZ'] = 'Europe/Amsterdam'
#time.tzset()
#this_morning = datetime.datetime.now()
#last_night = datetime.datetime(2019, 11, 29, 20, 0)
#print(this_morning.time() < last_night.time())



#init functions
def setVersion():
    global consts
    version_file = open("./.git/refs/heads/master", "r")
    consts.VERSION = version_file.read()[:7]

def read_json():
    return json.load(open('configuration.json', 'r'))

# init
client = discord.Client()
bot = json.load(open('bot.json', 'r'))
user_delay_cache = []
user_subscribed = []
time_since_last_msg = 0
time_last_play_request = 0
config = read_json()
setVersion()

# riot api
if config["TOOGLE_RIOT_API"]:
    from riotwatcher import RiotWatcher, ApiError


# functions
def create_team(players):
    global config
    num_players = len(players)  
    team1 = random.sample(players, int(num_players / 2))
    team2 = players

    for player in team1:
        team2.remove(player)
    
    teams_message = config["MESSAGE_TEAM_1"]
    for player in team1:
        teams_message += player + "\n"
    
    teams_message += config["MESSAGE_TEAM_2"]
    for player in team2:
        teams_message += player + "\n"
    
    return teams_message


def create_internal_play_request(play_request_creator, play_request_message):
    global consts
    user_internal = user_subscribed
    user_internal.append(play_request_creator)
    play_request_time = re.findall('\d\d:\d\d', play_request_message)[2:-2]
    intern_message = consts.CREATE_INTERN_PLAY_REQUEST_MESSAGE.format(play_request_creator.name, 10  - (len(user_subscribed) + 1), play_request_time, play_request_creator.name)
    for user in user_subscribed:
        intern_message += user.name + '\n'
    return intern_message

# checks if message should be purged based on if it starts with a specified command cmd
# and is send in a specfied channel name channel and is from a user excepted user
# that should not be purged
def is_purgeable_message(message, cmd, channel, *args):
    if message.content.startswith(tuple(cmd)) == False and message.channel.name == channel:
        if message.author.name in args:
            return False
        return True
    return False

def scheduled_purge_for_notifiy_on_react():
    global config
    time_init = time.time()
    global time_since_last_msg
    global user_delay_cache
    if time_init - time_since_last_msg  >= config["TIMER_NOTIFY_ON_REACT_PURGE"]:
        user_delay_cache = []
    time_since_last_msg =  time.time()

# automatically dms user if a reaction in any channel of args was added with a config["TIMER_NOTIFY_ON_REACT_PURGE"] delay
async def auto_dm_in_channel(reaction, user, user_delay_cache, user_subscribed, *args):
    global consts
    global config
    if user == client.user or user.name == "Secret Kraut9 Leader":
        return
    scheduled_purge_for_notifiy_on_react()
    message_sender_id = int((reaction.message.content.split(None, 1)[1]).split(None,1)[0][3:-1])
    message_sender = client.get_user(message_sender_id)
    message_id = reaction.message.id
    if(config["TOGGLE_AUTO_DM"] and str(reaction.message.channel.name) in args and message_sender != user and user not in user_delay_cache):
        if reaction.message.author.name == config["BOT_DYNO_NAME"]:
            #only works for the specfied message format: '@everyone @user [rest of msg]'
            for user_reacted in user_subscribed:
                await user_reacted.send(consts.MESSAGE_AUTO_DM_SUBSCRIBER.format(user.name, str(reaction.emoji),message_sender.name))
            await message_sender.send(consts.MESSAGE_AUTO_DM_CREATOR.format(user.name, str(reaction.emoji)))
            if(str(reaction.emoji) != consts.EMOJI_PASS) and user not in user_subscribed:
                user_subscribed.append(user)
                if len(user_subscribed) + 1 == 6:
                    channel = discord.utils.get(client.get_all_channels(), guild__name='Kraut9', name=config["CHANNEL_INTERN_PLANING"])
                    await channel.send(create_internal_play_request(message_sender, reaction.message.content))
            elif (str(reaction.emoji) == consts.EMOJI_PASS) and user in user_subscribed:
                user_subscribed.remove(user)
    user_delay_cache.append(user)
    return message_id


# events
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    time_since_last_msg = time.time()

@client.event
async def on_member_join(member):
    global config
    # auto role
    if not member.roles:
        for role in member.guild.roles:
            if role.id == config["ROLE_SETZLING_ID"]:
                await member.edit(role)
        
@client.event
async def on_message(message):
    global config
    global consts
    if message.author == client.user:
        return

    # auto react command - reacts to all patterns in consts.PATTERN_LIST_AUTO_REACT
    if config["TOGGLE_AUTO_REACT"]:
        for pattern in consts.PATTERN_LIST_AUTO_REACT:
            if message.content.find(pattern) > -1:
                for emoji_iterator in consts.EMOJI_ID_LIST:
                    await message.add_reaction(client.get_emoji(emoji_iterator))
                await message.add_reaction(consts.EMOJI_PASS)

    #delete subscriber if new request is created
    if message.content.startswith(config["COMMAND_PLAY_LOL"]) and message.channel.name == config["CHANNEL_PLAY_REQUESTS"]:
        global user_subscribed
        user_subscribed = []

    # create team command
    elif message.content.startswith(config["COMMAND_CREATE_TEAM"]) and (str(message.channel.name) == str(config["CHANNEL_INTERN_PLANING"]) or str(message.channel.name) == 'bot'):
        for voice_channel_iterator in message.guild.voice_channels:
            if voice_channel_iterator.name == config["CHANNEL_CREATE_TEAM_VOICE"]:
                voice_channel = voice_channel_iterator

        players_list = []
        for member in voice_channel.members:
            players_list.append(member.name)

        await message.channel.send("\nTeams:\n" + create_team(players_list))
      #  if(config["TOGGLE_AUTO_DELETE"]):
       #     await message.delete() 

    # player command
    elif message.content.startswith('?player'):
        if config["TOGGLE_RIOT_API"]:
            riot_token = str(config["riot_token"])
            watcher = RiotWatcher(riot_token)
            my_region = 'euw1'
            me = watcher.summoner.by_name(my_region, message.content.split(None,1)[1])
            my_ranked_stats = watcher.league.by_summoner(my_region, me['id'])
            games_played = int(my_ranked_stats[0]['wins']) + int(my_ranked_stats[0]['losses'])
            winrate = round((int(my_ranked_stats[0]['wins'])/ games_played) *100,1)
            await message.channel.send('Played: {4}, Rank: {0} {1} {2}LP, Winrate: {3}%'.format(my_ranked_stats[0]['tier'], my_ranked_stats[0]['rank'], my_ranked_stats[0]['leaguePoints'], winrate, games_played))
        else:
            await message.channel.send('Sorry, der Befehl ist aktuell nicht verfügbar.')

    if message.channel.name == "bot":
        # testmsg command for debugging; can be deleted
        if message.content.startswith("?testmsg"):
                await message.channel.send("test")
                await message.add_reaction(consts.EMOJI_PASS)

        elif message.content.startswith("?version"):
                print("test:" + consts.VERSION)
                await message.channel.send(consts.VERSION)

        elif message.content.startswith("?reload_config"):
                await message.channel.send("Reload configuration.json:")
                config = read_json()
                consts = reload(consts)
                await message.channel.send("Done.")

     
     # deletes all messages that are not commands (consts.COMMAND_LIST_ALL)  except bot responses in all cmd channels (consts.CHANNEL_LIST_COMMANDS)
    if config["TOGGLE_AUTO_DELETE"] and is_purgeable_message(message, consts.COMMAND_LIST_PLAY_REQUEST, config["CHANNEL_PLAY_REQUESTS"], config["BOT_DYNO_NAME"]):
            await message.delete()
    if config["TOGGLE_AUTO_DELETE"] and is_purgeable_message(message, consts.COMMAND_LIST_INTERN_PLANING, config["CHANNEL_INTERN_PLANING"], config["BOT_DYNO_NAME"], client.user.name):
            await message.delete()

# delete subscribers if old play-request gets deleted
@client.event
async def on_message_delete(message):
    global consts
    global user_subscribed
    for pattern in consts.PATTERN_LIST_AUTO_REACT:
            if message.content.find(pattern) > -1:
                user_subscribed = []
    
@client.event
async def on_reaction_add(reaction, user):
    global config
    if user == client.user or user.name == "Secret Kraut9 Leader":
        return
    auto_dm_channels = []
    auto_dm_channels.append(config["CHANNEL_PLAY_REQUESTS"])
    auto_dm_channels.append(config["CHANNEL_INTERN_PLANING"])
    auto_dm_in_channel(reaction, user, auto_dm_channels)
    


# run
print("Start Client")
client.run(str(bot["token"]))
print("End")
