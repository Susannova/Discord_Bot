# Discord Bot

Features:
- create a team 
- commit/reject play request with auto react
- auto dm
- auto delete non commands
- version 
- auto dm for people that subscribed to play-request (reacted with non :x:)
- integrated riot api => waiting for API KEY
- lol player information
- reload config on command
- auto role

Dyno Features used:
- play requests
- play-now requests
- internal play requests
- join message (new users get a dm from dyno with some text)

Commands:
- ?play-lol [Uhrzeit]
- ?play-now

Our Bot:
- ?create-team
- ?player

DEBUG/DEV Commands:
- ?testmsg
- ?version
- ?reload_config
- !end

TODO:
[issues](https://github.com/Susannova/Create_Team/issues)

KNOWN BUGS:
- dyno commands work in every channel as admin
- multiple play-requests or switch from play-request to internal play-request all share same subscribers => map play-request message id to subscribers

Wiki:
-  [player_request](https://drive.google.com/file/d/1hMAPciHA2Yc0a6dnL9igTXTL4uWULiSC/view?usp=sharing)
