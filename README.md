# Discord Bot

Features:
- create a team 
- role planning with auto react
- auto dm
- auto delete non commands
- version 
- auto dm for people that reacted to play-request with anything else then :x:
- integrated riot api => waiting for API KEY
- lol player information
- reload config on command

Dyno Features used:
- play requests
- play-now requests
- internal play requests
- auto role

Commands:
?create-team
?player

DEBUG/DEV Commands:
?testmsg
?version
?reload_config

TODO:
- 24h purge in #play-requests 
- redo dyno functions in our bot
- automatically switch from play-request to internal-play-request if more than 5 people  react to a play-request
- reminder for play-request (notify when the time specified in play-requests is in 5min)

KNOWN BUGS:
- dyno auto role doesnt work => create own version
