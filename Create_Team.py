import discord
import random
import json

client_infos = json.load(open('client_infos.json', 'r'))

client = discord.Client()

voice_channel_id = str(client_infos["voice_channel_id"])

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!create_team'):
        task = message.content
        #TODO mit + und - Namen hinzufügen oder entfernen

        voice_channel = client.get_channel(voice_channel_id)
        members = voice_channel.members
        num_players = len(members)

        team1 = random.sample(members, int(num_players / 2))

        for player in team1:
            members.remove(player)
        
        string_team1 = "Team1: "
        for player in team1:
            string_team1 + str(player.name)
        
        string_team2 = "Team2: "
        for player in team2:
            string_team2 + str(player.name)
        
        await message.channel.send(string_team1)
        await message.channel.send(string_team2)

print("Start Client")
client.run(str(client_infos["client_token"]))
print("End")