import discord
import random
import json
import time

# constants
CREATE_TEAM_VOICE_CHANNEL = "InHouse Planing"
CREATE_TEAM_TEXT_CHANNEL = 'intern-planing'
COMMAND_CREATE_TEAM = '?create-team'
AUTO_REACT_PATTERN = ' will League of Legends spielen. Kommt gegen '
AUTO_REACT_PASS_EMOJI = '❌'
TEAM_1_MESSAGE = "Blue Side:\n"
TEAM_2_MESSAGE = "Red Side:\n"
NOTIFY_ON_REACT_CHANNEL= 'play-requests'
NOTIFY_ON_REACT_PURGE_TIMER = 15.0
# order: top, jgl, mid, adc, supp, fill
EMOJI_ID_LIST = [644252873672359946, 644254018377482255, 644252861827514388, 644252853644296227, 644252146023530506, 644575356908732437]


#init
client = discord.Client()
user_cache = []
time_since_last_msg = 0

#functions
def create_team(players):
    num_players = len(players)  

    team1 = random.sample(players, int(num_players / 2))
    team2 = players

    for player in team1:
        team2.remove(player)
    
    teams_message = "Blue Side:\n"
    for player in team1:
        teams_message += player + "\n"
    
    teams_message += "\nRed Side:\n"
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
    if message.content.startswith(COMMAND_CREATE_TEAM) and (str(message.channel) == str(CREATE_TEAM_CHANNEL) or str(message.channel) == 'bot'):
        for voiceChannel in kraut9.voice_channels:
            if voiceChannel.name == VOICE_CHANNEL_NAME:
                bucht = voiceChannel

        players_list = []
        for mem in bucht.members:
            players_list.append(mem.name)

        await message.channel.send(create_team(players_list))

    # auto react command
    elif message.content.find(AUTO_REACT_PATTERN) > -1:
        for emoji_iterator in EMOJI_ID_LIST:
                await message.add_reaction(client.get_emoji(emoji_iterator))
        
        await message.add_reaction(AUTO_REACT_PASS_EMOJI)
        
    # testmsg command for debugging; can be deleted
    elif message.content.startswith("?testmsg"):
        await message.channel.send("test")
        await message.add_reaction(AUTO_REACT_PASS_EMOJI)

    # elif message.content.startswith('!end'):
    #     await message.channel.send('Bye!')
    #     await client.logout()


# automatically dms user if a reaction in NOTIFIY_ON_REACT_CHANNEL was added with a NOTIFY_ON_REACT_PURGE_TIMER delay
@client.event
async def on_reaction_add(reaction, user):
    global user_cache
    scheduled_purge_for_notifiy_on_react()
    if(str(reaction.message.channel) == NOTIFY_ON_REACT_CHANNEL and user not in user_cache and reaction.message.author != user):
        await user.send('{0} hat auf dein Play-Request reagiert: {1} '.format(reaction.message.author.name, str(reaction.emoji)))
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
client.run(str(constants_input["client_token"]))
print("End")