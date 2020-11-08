import discord


class NotInstantiatedException(Exception):
    """Exception raised if something is not yet
    instantiated.
    """
    def __init__(self):
        pass

    def __str__(self):
        return 'Something was called before it was instantiated.'


class DataBaseException(Exception):
    """Exception raised if something goes wrong
    while working with the shelve database.
    """
    def __init__(self, message='No Description'):
        self.message = message

    def __str__(self):
        return f'{self.message}: Something went wrong while handling the database.'

class BadArgumentFormat(Exception):
    """Exception that gets raised if an argument for a command
    is not well formated.
    """
    def __init__(self):
        pass
    
    def __str__(self):
        return 'Das angegebene Argument ist falsch formatiert. (z.B. beim Command: play-lol)'

class LimitReachedException(Exception):
    """Exception that gets raised if a limit is reached. For example gets
    used when a user already created one temporary channel, that still exists.
    """
    def __init__(self, message='Ein Limit wurde erreicht!'):
        self.message = message

    def __str__(self):
        return self.message

class FalseChannel(discord.ext.commands.CheckFailure):
    def __init__(self, *valid_channels):
        self.valid_channels = valid_channels

    def __str__(self) -> str:
        return 'This command can\'t be used here.'

