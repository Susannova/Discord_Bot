from discord import Emoji, HTTPException


class EmojiManager:
    def __init__(self, ctx) -> None:
        self.ctx = ctx

    async def create_emoji(self, emoji_name) -> int:
        if not self.ctx.message.attachments:
            await self.ctx.send("Please attach an image file to create an emoji.")
            return -1

        attachment = self.ctx.message.attachments[0]
        if attachment.filename.endswith((".png", ".jpg", ".jpeg", ".gif")):
            try:
                image_data = await attachment.read()
                guild = self.ctx.guild
                new_emoji = await guild.create_custom_emoji(name=emoji_name, image=image_data)
                await self.ctx.send(f"Emoji created: <:{new_emoji.name}:{new_emoji.id}>")
                return new_emoji
            except HTTPException as e:
                await self.ctx.send(f"Failed to create emoji: {e}")
                return -1
        else:
            await self.ctx.send("The attachment must be an image file (png, jpg, jpeg, gif).")
            return -1

    def find_emoji(self, emoji):
        if isinstance(emoji, Emoji):
            matched_emoji = next(
                (
                    guild_emoji
                    for guild_emoji in self.ctx.guild.emojis
                    if guild_emoji.name.strip().lower() == emoji.name.strip().lower()
                ),
                None,
            )
        elif isinstance(emoji, str):
            matched_emoji = next(
                (
                    guild_emoji
                    for guild_emoji in self.ctx.guild.emojis
                    if guild_emoji.name.strip().lower() == emoji.strip().lower()
                ),
                None,
            )
        elif isinstance(emoji, int):
            matched_emoji = next(
                (guild_emoji for guild_emoji in self.ctx.guild.emojis if guild_emoji.id == emoji),
                None,
            )
        return matched_emoji

    async def remove_emoji(self, emoji):
        emoji_to_remove = self.find_emoji(emoji)

        if emoji_to_remove:
            try:
                await emoji_to_remove.delete()
                await self.ctx.send(f'Emoji "{emoji}" has been removed.')
            except HTTPException as e:
                await self.ctx.send(f"Failed to remove emoji: {e}")
        else:
            await self.ctx.send(f'Emoji "{emoji}" not found.')
