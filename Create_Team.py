import discord
import random
import json
import time

# constants
constants_input = json.load(open('configuration.json', 'r'))
#commands
COMMAND_CREATE_TEAM = constants_input["COMMAND_CREATE_TEAM"]
COMMAND_PLAY_LOL = constants_input["COMMAND_PLAY_LOL"]
#channel
CHANNEL_CREATE_TEAM_VOICE =  constants_input["CHANNEL_CREATE_TEAM_VOICE"]
CHANNEL_CREATE_TEAM_TEXT = constants_input["CHANNEL_CREATE_TEAM_TEXT"]
CHANNEL_PLAY_REQUESTS= constants_input["CHANNEL_PLAY_REQUESTS"]
#toggle
TOGGLE_AUTO_DELETE = constants_input["TOGGLE_AUTO_DELETE"]
TOGGLE_COMMAND_ONLY = constants_input["TOGGLE_COMMAND_ONLY"]
TOGGLE_AUTO_REACT = constants_input["TOGGLE_AUTO_REACT"]
TOGGLE_AUTO_DM = constants_input["TOGGLE_AUTO_DM"]
#message
MESSAGE_TEAM_1 = constants_input["MESSAGE_TEAM_1"]
MESSAGE_TEAM_2 = constants_input["MESSAGE_TEAM_2"]
#misc
AUTO_REACT_PATTERN = constants_input["AUTO_REACT_PATTERN"]
VERSION = constants_input["VERSION"]
AUTO_REACT_PASS_EMOJI = '❌'
NOTIFY_ON_REACT_PURGE_TIMER = 15.0
# order: top, jgl, mid, adc, supp, fill
EMOJI_ID_LIST = [644252873672359946, 644254018377482255, 644252861827514388, 644252853644296227, 644252146023530506, 644575356908732437]

# init
client = discord.Client()
user_cache = []
time_since_last_msg = 0
    
# functions
def create_team(players):
    num_players = len(players)  
    team1 = random.sample(players, int(num_players / 2))
    team2 = players

    for player in team1:
        team2.remove(player)
    
    teams_message = MESSAGE_TEAM_1
    for player in team1:
        teams_message += player + "\n"
    
    teams_message += MESSAGE_TEAM_2
    for player in team2:
        teams_message += player + "\n"
    
    return teams_message

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    time_since_last_msg = time.time()

@client.event
async def on_message(message):
    guild_list = client.guilds
    kraut9 = guild_list.pop(0)
    if message.author == client.user:
        return
    # create team command
    elif message.content.startswith(COMMAND_CREATE_TEAM) and (str(message.channel.name) == str(CHANNEL_CREATE_TEAM_TEXT) or str(message.channel.name) == 'bot'):
        for voice_channel_iterator in kraut9.voice_channels:
            if voice_channel_iterator.name == CHANNEL_CREATE_TEAM_VOICE:
                voice_channel = voice_channel_iterator

        players_list = []
        for member in voice_channel.members:
            players_list.append(member.name)

        await message.channel.send(create_team(players_list))
        if(TOGGLE_AUTO_DELETE):
            await message.delete()

    # auto react command
    elif message.content.find(AUTO_REACT_PATTERN) > -1 and TOGGLE_AUTO_REACT:
        for emoji_iterator in EMOJI_ID_LIST:
                await message.add_reaction(client.get_emoji(emoji_iterator))
        
        await message.add_reaction(AUTO_REACT_PASS_EMOJI)
        
    # testmsg command for debugging; can be deleted
    elif message.content.startswith("?testmsg") and message.channel.name == 'bot':
        await message.channel.send("test")
        await message.add_reaction(AUTO_REACT_PASS_EMOJI)

    elif message.content.startswith("?version") and message.channel.name == 'bot':
        await message.channel.send(VERSION)
     
     # deletes messages that are not commands in channel create-play-requests
    elif message.content.startswith(COMMAND_PLAY_LOL) == False and (str(message.channel) == str(CHANNEL_PLAY_REQUESTS)):
        await message.delete()
    # elif message.content.startswith('!end'):
    #     await message.channel.send('Bye!')
    #     await  client.logout()
        
   
# automatically dms user if a reaction in NOTIFIY_ON_REACT_CHANNEL was added with a NOTIFY_ON_REACT_PURGE_TIMER delay
@client.event
async def on_reaction_add(reaction, user):
    if user == client.user or user.name == "Secret Kraut9 Leader":
        return
    global user_cache
    scheduled_purge_for_notifiy_on_react()
    message_sender_id = int((reaction.message.content.split(None, 1)[1]).split(None,1)[0][3:-1])
    message_sender = client.get_user(message_sender_id)
    #or str(reaction.message.channel.name) == 'bot'
    if(TOGGLE_AUTO_DM and str(reaction.message.channel.name) == CHANNEL_PLAY_REQUESTS and message_sender != user and user not in user_cache):
        if reaction.message.author.name == "Dyno":
            #only works for the specfied message format: '@everyone @user [rest of msg]'
            await message_sender.send('{0} hat auf dein Play-Request reagiert: {1} '.format(user.name, str(reaction.emoji)))
    user_cache.append(user)

# NOTIFIY_ON_REACT Delay utility function
def scheduled_purge_for_notifiy_on_react():
    time_init = time.time()
    global time_since_last_msg
    global user_cache
    if time_init - time_since_last_msg  >= NOTIFY_ON_REACT_PURGE_TIMER:
        user_cache = []
    time_since_last_msg =  time.time()

print("Start Client")
bot = json.load(open('bot.json', 'r'))
client.run(str(bot["debug_token"]))
print("End")