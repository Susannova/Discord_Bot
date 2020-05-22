# Discord Bot

## Features:
- create a team 
- commit/reject play request with auto react
- auto dm
- auto delete non commands
- version 
- auto dm for people that subscribed to play-request (reacted with non :x:)
- integrated riot api
- lol player information
- reload config on command
- auto role
- play requests
- play-now requests
- purges play_requests after 18h if new play_request is made
- calculate best bans for a given lol team
- check if player is a smurf
- automatically generate op.gg link from scanning clash scouting screen

## Using the bot on your server:
_TODO_

## Commands:
() = mandatory
[] = optional

### General Commands:
- `!create-team [mv] [names]`: Creates two teams based on the voice channel the user is in. With `mv`, the players are moved to the voice channels 'Team 1' and 'Team 2'
- `!play game (time | "now" [+minutes])`: Creates a play-request for the game `game` for now or for the time in the format hh:mm. Other users can react to the fame with :fill: or :x:.
- `!help [command]`: Prints a list of the availble commands and a short description or a longer description for a given command.

### Riot Commands:
- `!bans summoner x5`: Returns the best bans for the summoners
- `!player summoner`: Gives some basic infos of the summoner.
- `!smurf summoner`: Checks if the summoner is a smurf or not
- `!link summoner`: Links a Riot account to the user.
- `!unlink`: Unlinks the Riot account.
- `!plot`: Plots a time graph of the winrate and rank of the LoL SoloQ and Flex games for the linked users.

### DEBUG/DEV Commands:
- `!version`
- `!enable-debug`
- `!reload-config`
- `!reload-ext extension`
- `!print command`
- `!end (restart | abort)`

## Known Bugs:

## Developer Wiki:
