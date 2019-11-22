import discord
import random
import json

#constants
VOICE_CHANNEL_NAME = "Bucht der Liebe"
COMMAND_CREATE_TEAM = '?create_team'
AUTO_REACT_PATTERN = 'will League of Legnds spielen. Kommt gegen'

#init
client_infos = json.load(open('client_infos.json', 'r'))
client = discord.Client()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith(COMMAND_CREATE_TEAM):
        guildList = client.guilds
        kraut9 = guildList.pop(0)
        
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
        
        teams_message = "Team1:\n"
        for player in team1:
            teams_message += player + "\n"
        
        teams_message += "\nTeam2:\n"
        for player in team2:
            teams_message += player + "\n"
        
        await message.channel.send(teams_message)

    if message.content.find(AUTO_REACT_PATTERN) > -1:
        guildList = client.guilds
        kraut9 = guildList.pop(0)
        k9Emojis = kraut9.emojis

        for emoj in k9Emojis:
            if emoj.name == "fill":
                await message.add_reaction(emoj)
            if emoj.name == "jgl":
                await message.add_reaction(emoj)
            if emoj.name == "topp":
                await message.add_reaction(emoj)
            if emoj.name == "mid":
                await message.add_reaction(emoj)
            if emoj.name == "supp":
                await message.add_reaction(emoj)
            if emoj.name == "adc":
                await message.add_reaction(emoj)
            
        
        #await message.add_reaction(client.get_emoji(647439883022893067))

      

       


        
    
    # elif message.content.startswith('!end'):
    #     await message.channel.send('Bye!')
    #     await client.logout()

print("Start Client")
client.run(str(client_infos["client_token"]))
print("End")