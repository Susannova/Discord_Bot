import discord
import random
import json

#constants
constants_input = json.load(open('client_infos.json', 'r'))
VOICE_CHANNEL_NAME = constants_input["VOICE_CHANNEL_NAME"]
CREATE_TEAM_CHANNEL = constants_input['CREATE_TEAM_CHANNEL']
COMMAND_CREATE_TEAM = constants_input["COMMAND_CREATE_TEAM"]
AUTO_REACT_PATTERN = constants_input["AUTO_REACT_PATTERN"]
EMOJI_ID_LIST = [644252873672359946, 644254018377482255, 644252861827514388, 644252853644296227, 644252146023530506, 644575356908732437]

#init
client = discord.Client()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    guildList = client.guilds
    kraut9 = guildList.pop(0)
    if message.author == client.user:
        return
    if message.content.startswith(COMMAND_CREATE_TEAM) and (str(message.channel) == str(CREATE_TEAM_CHANNEL) or str(message.channel) == 'bot'):
        for voiceChannel in kraut9.voice_channels:
            if voiceChannel.name == VOICE_CHANNEL_NAME:
                bucht = voiceChannel

        players = []
        for mem in bucht.members:
            players.append(mem.name)
        
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
        
        await message.channel.send(teams_message)

    if message.content.find(AUTO_REACT_PATTERN) > -1:
        for emoj in EMOJI_ID_LIST:
                await message.add_reaction(client.get_emoji(emoj))
        
        await message.add_reaction('❌')
    
    # elif message.content.startswith('!end'):
    #     await message.channel.send('Bye!')
    #     await client.logout()

print("Start Client")
client.run(str(constants_input["client_token"]))
print("End")