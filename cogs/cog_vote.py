import logging
import typing
import datetime
import asyncio

import discord
from discord.ext import commands

from core import (
    checks,
    DiscordBot,
    converters
)

logger = logging.getLogger(__name__)

# TODO Most of this is not needed anymore.
class Vote:
    def __init__(self, creator_id: int, end_time: datetime.datetime, title: str):
        self.creator_id = creator_id
        self.end_time = end_time
        self.title = title

        self.options = {}

class VoteCog(commands.Cog, name='Vote Commands'):
    """ Commands and events for the vote command
    """
    def __init__(self, bot: DiscordBot.KrautBot):
        self.bot = bot
        self.votes = {}

        self.number_emoji = {
            1: '1️⃣',
            2: "2️⃣",
            3: "3️⃣",
            4: "4️⃣",
            5: "5️⃣",
            6: "6️⃣",
            7: "7️⃣",
            8: "8️⃣",
            9: "9️⃣"
        }

        self.emoji_number = dict(
            ((value, key) for key, value in self.number_emoji.items())
        )
    
    def get_vote(self, message_id: int) -> Vote:
        return self.votes[message_id]
    
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.Member):
        if reaction.message.id not in self.votes or user == self.bot.user:
            return
        
        # if reaction.count == 1:
        if self.bot.user not in await reaction.users().flatten():
            logger.warning("Removing a new reaction in vote %i", reaction.message.id)
            await reaction.remove(user)
    
    async def end_vote(self, message: discord.Message):
        if message.id not in self.votes:
            return
        
        vote = self.get_vote(message.id)
        
        counts = {}
        participants = []
        for reaction in message.reactions:
            async for user in reaction.users():
                if user not in participants and user != self.bot.user:
                    participants.append(user)
            
            count = reaction.count - 1
            if count in counts:
                counts[count].append(reaction.emoji)
            else:
                counts[count] = [reaction.emoji]
        
        counts_list = list(counts.keys())
        counts_list.sort(reverse=True)

        embed = discord.Embed(
            title=f"Results: {vote.title}"
        )

        for count in counts_list:
            embed.add_field(
                name=f"Votes: {count}",
                value="\n".join(
                    (f"- {vote.options[self.emoji_number[emoji]]}" for emoji in counts[count])
                ),
                inline=False
            )
        
        await message.channel.send(" ".join((participant.mention for participant in participants)), embed=embed)
    
    @commands.command()
    async def vote(self, ctx: commands.Context, time: converters.StrToTime, *, title_and_options: converters.LinesToList):
        """ Start a vote
        
        TODO Needs to be updated!
        Options are seperated by lines. If no options are given a yes-no vote is started.

        Args:
            ctx (commands.Context): The context
            options (typing.Optional[converters.LinesToList]): The vote options seperated by lines
        """
        
        title = title_and_options[0]
        title_and_options.remove(title)

        number_of_options = len(title_and_options)
        
        options_text = (f"**{option+1}**: {title_and_options[option]}" for option in range(0, number_of_options))

        embed = discord.Embed(
            title=title,
            description="\n".join(options_text)
        )

        # TODO Not that nice...
        embed.set_footer(text=f"Ends: {time.isoformat()}")

        if len(title_and_options) > len(self.number_emoji):
            logger.error("Guild: %i: Vote started with too much options.", ctx.guild.id)
            raise RuntimeError("Too much options")

        if len(embed) > 5000: # Max would be 6000 but the conclusion needs space too
            await ctx.send("The text is too long. PLease try again with shorter options")
            raise RuntimeError()

        new_vote = Vote(ctx.author.id, time, title)

        # message = discord.Message()
        message = await ctx.send(embed=embed)
        for number in range(0, number_of_options):
            emoji = self.number_emoji[number+1]
            await message.add_reaction(emoji)
            new_vote.options[number+1] = title_and_options[number]
            

        
        self.votes[message.id] = new_vote

        await asyncio.sleep((time - datetime.datetime.now()).seconds)
        await self.end_vote(await message.channel.fetch_message(message.id))






def setup(bot: DiscordBot.KrautBot):
    bot.add_cog(VoteCog(bot))
    logger.info('Vote cog loaded')