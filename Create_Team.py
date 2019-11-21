import discord
import random
import json

client_infos = json.load(open('client_infos.json', 'r'))

client = discord.Client()

voice_channel_id = str(client_infos["voice_channel_id"])

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!create_team'):
        task = message.content

        task_splitted = (task.split())
        task_splitted.pop(0)

        players = task_splitted
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
    
    # elif message.content.startswith('!end'):
    #     await message.channel.send('Bye!')
    #     await client.logout()

print("Start Client")
client.run(str(client_infos["client_token"]))
print("End")