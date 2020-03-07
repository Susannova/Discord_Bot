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


