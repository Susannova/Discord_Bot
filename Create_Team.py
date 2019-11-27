import discord
import random
import json
import time

# constants
EMOJI_ID_LIST = [644252873672359946, 644254018377482255, 644252861827514388, 644252853644296227, 644252146023530506, 644575356908732437]
AUTO_REACT_PASS_EMOJI = '❌'
NOTIFY_ON_REACT_PURGE_TIMER = 15.0
VERSION  = ""

#init functions
def setVersion():
    global VERSION
    version_file = open("./.git/refs/heads/master", "r")
    VERSION = version_file.read()[:7]

def read_json():
    return json.load(open('configuration.json', 'r'))

# init
client = discord.Client()
bot = json.load(open('bot.json', 'r'))
user_delay_cache = []
user_subscribed = []
time_since_last_msg = 0
bot = json.load(open('bot.json', 'r'))
constants = read_json()
setVersion()

# riot api
if constants["TOOGLE_RIOT_API"]:
    from riotwatcher import RiotWatcher, ApiError


# functions
def create_team(players):
    global constants

    num_players = len(players)  
    team1 = random.sample(players, int(num_players / 2))
    team2 = players

    for player in team1:
        team2.remove(player)
    
    teams_message = constants["MESSAGE_TEAM_1"]
    for player in team1:
        teams_message += player + "\n"
    
    teams_message += constants["MESSAGE_TEAM_2"]
    for player in team2:
        teams_message += player + "\n"
    
    return teams_message

def scheduled_purge_for_notifiy_on_react():
    time_init = time.time()
    global constants
    global time_since_last_msg
    global user_delay_cache
    if time_init - time_since_last_msg  >= constants["NOTIFY_ON_REACT_PURGE_TIMER"]:
        user_delay_cache = []
    time_since_last_msg =  time.time()

# events
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    time_since_last_msg = time.time()

@client.event
async def on_member_join(member):
    # auto role
    if not member.roles:
        for role in member.guild.roles:
            if role.id == constants["ROLE_SETZLING_ID"]:
                await member.edit(role)
        
@client.event
async def on_message(message):
    global constants 
    if message.author == client.user:
        return
    # create team command
    elif message.content.startswith(constants["COMMAND_CREATE_TEAM"]) and (str(message.channel.name) == str(constants["CHANNEL_CREATE_TEAM_TEXT"]) or str(message.channel.name) == 'bot'):
        for voice_channel_iterator in message.guild.voice_channels:
            if voice_channel_iterator.name == constants["CHANNEL_CREATE_TEAM_VOICE"]:
                voice_channel = voice_channel_iterator

        players_list = []
        for member in voice_channel.members:
            players_list.append(member.name)

        await message.channel.send(create_team(players_list))
        if(constants["TOGGLE_AUTO_DELETE"]):
            await message.delete()

    # auto react command
    elif message.content.find(constants["AUTO_REACT_PATTERN"]) > -1 and constants["TOGGLE_AUTO_REACT"]:
        for emoji_iterator in EMOJI_ID_LIST:
                await message.add_reaction(client.get_emoji(emoji_iterator))
        
        await message.add_reaction(AUTO_REACT_PASS_EMOJI)

    # player command
    elif message.content.startswith('?player'):
        if constants["TOOGLE_RIOT_API"]:
            riot_token = str(constants["riot_token"])
            watcher = RiotWatcher(riot_token)
            my_region = 'euw1'
            me = watcher.summoner.by_name(my_region, message.content.split(None,1)[1])
            my_ranked_stats = watcher.league.by_summoner(my_region, me['id'])
            games_played = int(my_ranked_stats[0]['wins']) + int(my_ranked_stats[0]['losses'])
            winrate = round((int(my_ranked_stats[0]['wins'])/ games_played) *100,1)
            await message.channel.send('Played: {4}, Rank: {0} {1} {2}LP, Winrate: {3}%'.format(my_ranked_stats[0]['tier'], my_ranked_stats[0]['rank'], my_ranked_stats[0]['leaguePoints'], winrate, games_played))
        else:
            await message.channel.send('Sorry, der Befehl ist aktuell nicht verfügbar.')

        
    elif message.channel.name == 'bot':
        # testmsg command for debugging; can be deleted
        if message.content.startswith("?testmsg"):
            await message.channel.send("test")
            await message.add_reaction(constants["AUTO_REACT_PASS_EMOJI"])

        elif message.content.startswith("?version"):
            await message.channel.send(VERSION)

        elif message.content.startswith("?reload_config"):
            await message.channel.send("Reload configuration.json:")
            constants = read_json()
            await message.channel.send("Done.")

     
     # deletes all messages that are not commands(except bot responses) in channel create-play-requests
    elif message.content.startswith(constants["COMMAND_PLAY_LOL"]) == False and (str(message.channel) == str(constants["CHANNEL_PLAY_REQUESTS"])):
        if(message.author.name != "Dyno"):
            await message.delete()
        
   
# automatically dms user if a reaction in NOTIFIY_ON_REACT_CHANNEL was added with a NOTIFY_ON_REACT_PURGE_TIMER delay
@client.event
async def on_reaction_add(reaction, user):
    global constants
    if user == client.user or user.name == "Secret Kraut9 Leader":
        return
    global user_delay_cache
    global user_subscribed
    scheduled_purge_for_notifiy_on_react()
    message_sender_id = int((reaction.message.content.split(None, 1)[1]).split(None,1)[0][3:-1])
    message_sender = client.get_user(message_sender_id)
    if(constants["TOGGLE_AUTO_DM"] and str(reaction.message.channel.name) == constants["CHANNEL_PLAY_REQUESTS"] and message_sender != user and user not in user_delay_cache):
        if reaction.message.author.name == "Dyno":
            #only works for the specfied message format: '@everyone @user [rest of msg]'
            for user_reacted in range(0,user_subscribed.count):
                await user_reacted.send('{0} hat auch auf das Play-Request von {2} reagiert: {1} '.format(user.name, str(reaction.emoji),message_sender.name))
            await message_sender.send('{0} hat auf dein Play-Request reagiert: {1} '.format(user.name, str(reaction.emoji)))
            if(str(reaction.emoji) != AUTO_REACT_PASS_EMOJI):
                user_subscribed.append(user)
    user_delay_cache.append(user)


# run
print("Start Client")
client.run(str(bot["token"]))
print("End")
