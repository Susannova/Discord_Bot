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

## Commands:
() = mandatory
[] = optional

### General Commands:
- `!create-team [mv] [names]`
  Creates two teams based on the voice channel the user is in. With ``mv``, the players are moved to the voice channels 'Team 1' and 'Team 2'
- `!play game (time | "now")`
- `!clash`

### Riot Commands:
- `!bans summoner x5`
- `!player summoner`
- `!smurf summoner`
- `!link summoner`
- `!unlink`
- `!leaderboard`

### DEBUG/DEV Commands:
- `!version`
- `!enable-debug`
- `!reload-config`
- `!print command`
- `!end (restart | abort)`

## Known Bugs:

## Developer Wiki:
