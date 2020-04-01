# Wiki:

## State:

If you need to have any global state at runtime => 
```
from core.state import global_state
```

and only modifiy global_state attributes.
you can add attributes in the GlobalState class in state.py.

## Commands:

If you want to add a command to the bot use [this](https://discordpy.readthedocs.io/en/latest/ext/commands/commands.html) =>
```
@bot.command()
async def foo(ctx, arg):
    await ctx.send(arg)
````

## Add a new Game:
Steps to add a new game:

1. Create new Role in Discord
2. Add Emoji that has the same name as the role
3. Add Role ID to consts and abbreviation + role_id to game_name_to_role_dict
4. Add category in PlayRequestCategory
5. Add category to get_category in kraut.py
6. Add Emoji to Game-Selector Command
7. Add Game_name and game abbreviation to #play-requests message