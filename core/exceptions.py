import discord
class MissingRequiredAttachment(discord.DiscordException):
    """Exception raised if a @has_n_attachments(n) check fails.

    This inherits from :exc:`~discord.DiscordException`.
    """
    pass
