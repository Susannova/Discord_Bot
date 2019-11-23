import discord
import random
import json
import time

# constants
constants_input = json.load(open('client_infos.json', 'r'))
CREATE_TEAM_VOICE_CHANNEL =  constants_input["CREATE_TEAM_VOICE_CHANNEL"]
CREATE_TEAM_TEXT_CHANNEL = constants_input["CREATE_TEAM_TEXT_CHANNEL"]
COMMAND_CREATE_TEAM = constants_input["COMMAND_CREATE_TEAM"]
AUTO_REACT_PATTERN = constants_input["AUTO_REACT_PATTERN"]
AUTO_REACT_PASS_EMOJI = '❌'
TEAM_1_MESSAGE = constants_input["TEAM_1_MESSAGE"]
TEAM_2_MESSAGE = constants_input["TEAM_2_MESSAGE"]
NOTIFY_ON_REACT_CHANNEL= constants_input["NOTIFY_ON_REACT_CHANNEL"]
NOTIFY_ON_REACT_PURGE_TIMER = constants_input["NOTIFY_ON_REACT_PURGE_TIMER"]
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
    
    teams_message = TEAM_1_MESSAGE
    for player in team1:
        teams_message += player + "\n"
    
    teams_message += TEAM_2_MESSAGE
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
    if message.content.startswith(COMMAND_CREATE_TEAM) and (str(message.channel) == str(CREATE_TEAM_TEXT_CHANNEL) or str(message.channel) == 'bot'):
        for voice_channel_iterator in kraut9.voice_channels:
            if voice_channel_iterator.name == CREATE_TEAM_VOICE_CHANNEL:
                voice_channel = voice_channel_iterator

        players_list = []
        for member in voice_channel.members:
            players_list.append(member.name)

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
    if user == client.user:
        return
    global user_cache
    scheduled_purge_for_notifiy_on_react()
    if(str(reaction.message.channel) == NOTIFY_ON_REACT_CHANNEL  or str(reaction.message.channel) == 'bot' and user not in user_cache and reaction.message.author != user):
        await reaction.message.author.send('{0} hat auf dein Play-Request reagiert: {1} '.format(user.name, str(reaction.emoji)))
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