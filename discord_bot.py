import sys, os
sys.path.append(os.path.join(sys.path[0],'modules'))
import discord
import json
import time
from importlib import reload
from modules import consts, riot, timers, bot_utility as utility

# === init functions === #
def setVersion():
    global consts
    version_file = open("./.git/refs/heads/master", "r")
    consts.VERSION = version_file.read()[:7]

def read_json(filename):
    return json.load(open(f'./config/{filename}.json', 'r'))

# === init === #
client = discord.Client()
bot =  read_json('bot')
play_requests = {}
time_since_last_msg = 0
time_last_play_request = 0
config = read_json('configuration')
setVersion()
message_cache = []

# === classes === #
class player_in_play_request:
    discord_user = discord.user
    players_known = {}

    def __init__(self, user):
        self.discord_user = user

# === events === #
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_member_join(member):
    # auto role
    await member.edit(roles=utility.get_auto_role_list())
        
@client.event
async def on_message(message):
    global config
    global consts
    global play_requests
    utility.set_message(message)

    # auto react - reacts to all patterns in consts.PATTERN_LIST_AUTO_REACT
    # and creates a new play_request
    # only reacts with EMOJI_ID_LIST[5] == :fill:
    if config["TOGGLE_AUTO_REACT"] and has_pattern(message):
        await message.add_reaction(client.get_emoji(consts.EMOJI_ID_LIST[5]))
        await message.add_reaction(consts.EMOJI_PASS)
        play_requests[str(message.id)] = [player_in_play_request(message.author)]

    # create team command
    if utility.contains_command(consts.COMMAND_CREATE_TEAM) and utility.is_in_channels([consts.CHANNEL_INTERN_PLANING, consts.CHANNEL_BOT]):
        voice_channel = utility.get_voice_channel(consts.CHANNEL_CREATE_TEAM_VOICE)
        players_list = utility.get_players_in_channel(voice_channel)
        await message.channel.send(utility.create_team(players_list))

    # riot commands
    if config["TOOGLE_RIOT_API"] == False:
        await message.channel.send('Sorry, der Befehl ist aktuell nicht verfügbar.')
    else:
        if message.content.startswith('?player'):
            await message.channel.send(riot.riot_command(message))
        elif message.content.startswith('?bans'):
            await message.channel.send(riot.riot_command(message), file=discord.File(f'./{config["FOLDER_CHAMP_SPLICED"]}/image.jpg'))

    # debug commands
    if message.channel.name == "bot":
        if message.content.startswith("?testmsg"):
            await message.channel.send("test")
            await message.add_reaction(consts.EMOJI_PASS)
        elif message.content.startswith("?version"):
            await message.channel.send(consts.VERSION)
        elif message.content.startswith("?reload_config"):
            await message.channel.send("Reload configuration.json:")
            config = read_json('configuration')
            #consts = reload(modules.consts)
            await message.channel.send("Done.")
        # killswitch
        elif message.content.startswith('!end'):
            await message.channel.send('Bot is shut down!')
            await client.logout()

     # deletes all messages that are not commands (consts.COMMAND_LIST_ALL)  except bot responses in all cmd channels (consts.CHANNEL_LIST_COMMANDS)
    if config["TOGGLE_AUTO_DELETE"]:
        if utility.is_purgeable_message(consts.COMMAND_LIST_PLAY_REQUEST, consts.CHANNEL_PLAY_REQUESTS, [consts.BOT_DYNO_NAME]):
            await message.delete()
        elif utility.is_purgeable_message(consts.COMMAND_LIST_INTERN_PLANING, consts.CHANNEL_INTERN_PLANING, [consts.BOT_DYNO_NAME, client.user.name]):
            await message.delete()


@client.event
async def on_message_delete(message):
    global consts
    global play_requests
    # delete play_request if old play-request gets deleted
    if has_pattern(message):
        del play_requests[str(message.id)]


@client.event
async def on_reaction_add(reaction, user):
    # auto dm
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

        
        #TODO: fix delay timer - dont use time.sleep
        if player.players_known[user.name]["wait_for_notification"] == False:
            if time.time - player.players_known[user.name]["time_since_last_msg"] < config["TIMER_NOTIFY_ON_REACT_PURGE"]:
                player.players_known[user.name]["wait_for_notification"]: "True"

                # time.sleep() is not a good idea in a single threaded bot
                #time.sleep(player.players_known[user.name]["time_since_last_msg"] + config["TIMER_NOTIFY_ON_REACT_PURGE"] - time.time())
   
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