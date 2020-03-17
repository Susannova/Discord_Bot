import discord


class MissingRequiredAttachment(discord.DiscordException):
    """Exception raised if a @has_n_attachments(n) check fails.

    This inherits from :exc:`~discord.DiscordException`.
    """
    def __init__(self):
        pass

    def __str__(self):
        return 'Es fehlt ein Attachment. (z.B. das Bild bei ?clash)'


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
