import discord
class MissingRequiredAttachment(discord.DiscordException):
    """Exception raised if a @has_n_attachments(n) check fails.

    This inherits from :exc:`~discord.DiscordException`.
    """
    def __repr__(self):
        print('Es fehlt ein Attachment. (z.B. das Bild bei ?clash)')
    pass

class NotInstantiatedException():
    """Exception raised if something is not yet
    instantiated.
    """
    def __repr__(self):
        print('Something was called before it was instantiated.')