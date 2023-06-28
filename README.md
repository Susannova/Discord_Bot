[![Code Style Check](https://github.com/Susannova/Discord_Bot/actions/workflows/enforce-style.yml/badge.svg?branch=style-black)](https://github.com/Susannova/Discord_Bot/actions/workflows/enforce-style.yml)

# Discord Bot

The discord bot can run on multiple servers at the same time. Every server has it's own config, that can be set with ``config``.

## Features:
Most of the features can be (de)activated. Not all are activated per default.
- Get help messages with ``?help`` _(default if the command_prefix is unchanged)_
- Create two random teams based on the member in the voice channel
  - The teams can then automatically be moved to two voice channels
- Create a request to play a game now or to a given time
  - Other members can react to the play request if they want to join
  - Members that reacted with join get a message if another member joins and 5 minutes before the game starts
- Automations
  - Auto delete non commands (not default)
  - Assign new members to a specific role
  - Members can choose what games they are interested in. The bot assign the member to corresponding roles
  - Channel categories can be set visible if no member is connected to a voice channel of the category
- Integrated riot api
  - LoL player information
  - calculate best bans for a given lol team
  - check if player is a smurf
  - automatically generate op.gg link from scanning clash scouting screen
- Features for server owner or member in the admin role
  - The config can be changed and printed in an automatically created text channel with the ``config`` command
- Features for 'super users'
  - Super users can modify generall settings with additional ``config`` commands
  - Super users can modify the config of other servers
  - End the bot with a successful or unsuccessful exit code

## Using the bot on your server
### Run the bot by me
Just write me a message and I will add the bot to your server
### Run the bot by yourself
First clone the repo. In the folder you can install the required packages by running ``pip install -r requirements.txt``. [Create and invite a bot to your server](https://discordpy.readthedocs.io/en/latest/discord.html#discord-intro).
Update the token in the file ``./config/configuration.json``. Run ``python3 discord_bot.py``. The bot will create a text channel on the server where you can set the server settings of the bot. Type ``?help config`` in the text channel for more infos.

The best way to modify the server settings of the bot is to get the current config as a json file with ``?config json``. Modify this file and attach it to a message with ``?config load``.

## Commands:
() = mandatory
[] = optional

Not all commands are listed here.

### General Commands:
- `?team (move | (create [members]))`: Creates two teams based on the voice channel the user is in. With `move`, the players are moved to the voice channels 'Team 1' and 'Team 2'
- `?play [game...] [time]`: Creates a play-request for the games `game` for now or for the time in the format hh:mm. Other users can react to the request
- `?help [command]`: Prints a list of the availble commands and a short description or a longer description for a given command.

### Riot Commands:
- `?bans summoner x5`: Returns the best bans for the summoners
- `?player summoner`: Gives some basic infos of the summoner.
- `?smurf summoner`: Checks if the summoner is a smurf or not
- `?link summoner`: Links a Riot account to the user.
- `?unlink`: Unlinks the Riot account.
- `?plot`: Plots a time graph of the winrate and rank of the LoL SoloQ and Flex games for the linked users.

### DEBUG/DEV Commands:
- `?version`
- `?reload-ext extension`
- `?end [abort]`

## Docker
You can use the following docker-compose.yaml file:

```yaml
version: '3'
services:
  discordbot:
    container_name: discordbot
    volumes:
      - /etc/Discord_Bot/config:/usr/src/Discord_Bot/config
      - /etc/Discord_Bot/log:/usr/src/Discord_Bot/log
      - /etc/Discord_Bot/db:/usr/src/Discord_Bot/db
      - /etc/localtime:/etc/localtime:ro
    restart: unless-stopped
    build:
      context: https://github.com/Susannova/Discord_Bot.git#Beta
```

In this example, the config of the bot must be copied to the directory /etc/Discord_bot/config/!
