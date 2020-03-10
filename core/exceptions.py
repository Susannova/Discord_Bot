import discord
class MissingRequiredAttachment(discord.DiscordException):
    """Exception raised if a @has_n_attachments(n) check fails.

    This inherits from :exc:`~discord.DiscordException`.
    """
    def __str__(self):
        return 'Es fehlt ein Attachment. (z.B. das Bild bei ?clash)'


class NotInstantiatedException():
    """Exception raised if something is not yet
    instantiated.
    """
    def __str__(self):
        return 'Something was called before it was instantiated.'
