import discord
import random
import json
import time
import re
import consts
import asyncio
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
play_requests = {}
time_since_last_msg = 0
time_last_play_request = 0
config = read_json()
setVersion()

# riot api
if config["TOOGLE_RIOT_API"]:
    from riotwatcher import RiotWatcher, ApiError

# classes
class player_in_play_request:
    discord_user = discord.user
    players_known = {}

    def __init__(self, user):
        self.discord_user = user

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


# checks if message should be purged based on if it starts with a specified command cmd
# and is send in a specfied channel name channel and is from a user excepted user
# that should not be purged
def is_purgeable_message(message, cmd, channel, *args):
    if message.content.startswith(tuple(cmd)) == False and message.channel.name == channel:
        if message.author.name in args:
            return False
        return True
    return False


#creates a internal play_request message
def create_internal_play_request_message(message):
    play_request_time = re.findall('\d\d:\d\d', message.content)
    intern_message = consts.MESSAGE_CREATE_INTERN_PLAY_REQUEST.format(message.author.name, 9  - len(play_requests[str(message.id)][0].players_known), play_request_time, message.author.name)
    for player in play_requests[play_requests[str(message.id)]]:
        intern_message += player.players_known.keys() + '\n'
    return intern_message

#TODO: implement this
def switch_to_internal_play_request(message):
    print(create_internal_play_request_message(message))


# events
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

# auto role
@client.event
async def on_member_join(member):
    global config
    
    # if member already has a role => do nothing
    if len(member.roles) >= 2:
        return

    # fill role_list with the default role(@everyone) and the lowest role(Setzling)
    role_list = []
    for role in member.guild.roles:
        if role.id == config["ROLE_EVERYONE_ID"] or role.id == config["ROLE_SETZLING_ID"]:
            role_list.append(role)

    # replace the members role list with the new role list
    await member.edit(roles=role_list)
        
@client.event
async def on_message(message):
    global config
    global consts
    global play_requests

    # auto react command - reacts to all patterns in consts.PATTERN_LIST_AUTO_REACT
    # and creates a new play_request
    # only reacts with EMOJI_ID_LIST[5] == :fill:
    if config["TOGGLE_AUTO_REACT"]:
        for pattern in consts.PATTERN_LIST_AUTO_REACT:
            if message.content.find(pattern) > -1:
                await message.add_reaction(client.get_emoji(consts.EMOJI_ID_LIST[5]))
                await message.add_reaction(consts.EMOJI_PASS)
                play_requests[str(message.id)] = [player_in_play_request(message.author)]

    # create team command
    if message.content.startswith(config["COMMAND_CREATE_TEAM"]) and (str(message.channel.name) == str(config["CHANNEL_INTERN_PLANING"]) or str(message.channel.name) == 'bot'):
        for voice_channel_iterator in message.guild.voice_channels:
            if voice_channel_iterator.name == config["CHANNEL_CREATE_TEAM_VOICE"]:
                voice_channel = voice_channel_iterator

        players_list = []
        for member in voice_channel.members:
            players_list.append(member.name)

        await message.channel.send("\n@here\n**__===Teams===__**\n" + create_team(players_list))
      #  if(config["TOGGLE_AUTO_DELETE"]):
       #     await message.delete() 

    # player command
    elif message.content.startswith('?player'):
        if config["TOOGLE_RIOT_API"]:
            riot_token = str(bot["riot_token"])
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
            await message.channel.send(consts.VERSION)

        elif message.content.startswith("?reload_config"):
            await message.channel.send("Reload configuration.json:")
            config = read_json()
            consts = reload(consts)
            await message.channel.send("Done.")
        #Killswitch
        elif message.content.startswith('!end'):
            await message.channel.send('Bot is shut down!')
            await client.logout()

     
     # deletes all messages that are not commands (consts.COMMAND_LIST_ALL)  except bot responses in all cmd channels (consts.CHANNEL_LIST_COMMANDS)
    if config["TOGGLE_AUTO_DELETE"] and is_purgeable_message(message, consts.COMMAND_LIST_PLAY_REQUEST, config["CHANNEL_PLAY_REQUESTS"], config["BOT_DYNO_NAME"]):
            await message.delete()
    if config["TOGGLE_AUTO_DELETE"] and is_purgeable_message(message, consts.COMMAND_LIST_INTERN_PLANING, config["CHANNEL_INTERN_PLANING"], config["BOT_DYNO_NAME"], client.user.name):
            await message.delete()

# delete play_request if old play-request gets deleted
@client.event
async def on_message_delete(message):
    global consts
    global play_requests
    for pattern in consts.PATTERN_LIST_AUTO_REACT:
            if message.content.find(pattern) > -1:
                del play_requests[str(message.id)]

# auto dm
@client.event
async def on_reaction_add(reaction, user):
    global config
    global play_requests

   
    # if bot reacts or channel is wrong => dont do anything
    if user == client.user or user.name == "Secret Kraut9 Leader" or reaction.message.channel.name != config["CHANNEL_INTERN_PLANING"] or reaction.message.channel.name != config["CHANNEL_PLAY_REQUESTS"] or reaction.message.channel.name != "bot":
        return
    
    message_id = reaction.message.id

    #if message_id is not a play_request => dont do anything
    if str(message_id) not in play_requests:
        return
    
    # if reaction is 'EMOJI_PASS' delete player from play_request and return
    if str(reaction.emoji) == consts.EMOJI_PASS:
        for player in play_requests[str(message_id)]:
            del player.players_known[user.name]
        return
  
    # if player didnt react with EMOJI_PASS
    # if user that reacted is already in play_request => dont do anything
    for player in play_requests[str(message_id)]:
        if user.name not in player.players_known.keys():
            # add new user that reacted to play_request
            player.players_known[user.name] = {"time_since_last_msg": time.time(), "wait_for_notification": False}

        if player.players_known[user.name]["wait_for_notification"] == False:
            if time.time - player.players_known[user.name]["time_since_last_msg"] < config["TIMER_NOTIFY_ON_REACT_PURGE"]:
                player.players_known[user.name]["wait_for_notification"]: "True"

                await asyncio.sleep(player.players_known[user.name]["time_since_last_msg"] + config["TIMER_NOTIFY_ON_REACT_PURGE"] - time.time())
   
        message_author_name = reaction.message.author.name

        # sends message to play_request creator
        if player.discord_user.name == message_author_name:
            await player.discord_user.send(consts.MESSAGE_AUTO_DM_CREATOR.format(user.name, str(reaction.emoji)))
        # sends message to play_request subscriber
        else:
            await player.discord_user.send(consts.MESSAGE_AUTO_DM_SUBSCRIBER.format(user.name, str(reaction.emoji), message_author_name))

        #reset delay timer
        player.players_known[user.name]["time_since_last_msg"] = time.time()
        player.players_known[user.name]["wait_for_notification"] = False

        #switch to internal play request if more than 6 players(author + 5 players_known) are subscribed
        if len(player.players_known) == 5:
            switch_to_internal_play_request(reaction.message)

# run
print("Start Client")
client.run(str(bot["token"]))
print("End")
