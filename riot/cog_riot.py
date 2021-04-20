import logging

import discord
from discord.ext import commands

from core import checks, ocr

from riot import riot_utility, riot_commands

from core import DiscordBot

logger = logging.getLogger(__name__)


class RiotCog(commands.Cog, name="Riot Commands"):
    def __init__(self, bot: DiscordBot.KrautBot):
        self.bot = bot
        if self.bot.state.lol_patch is None:
            riot_utility.update_current_patch(self.bot.state)
            riot_utility.download_champ_icons(self.bot.state.lol_patch, self.bot.config.general_config)

    async def cog_check(self, ctx: commands.Context):
        return checks.is_riot_enabled(ctx) and await checks.command_is_allowed(ctx)

    @commands.command(name="player")
    async def player_(self, ctx, *summoner_name):
        """
        Returns info about lol account.

        Returns the rank and winrate of a player on the EUW server.
        """
        logger.debug("!player command called")
        if len(list(summoner_name)) == 0:
            arg = None
        else:
            arg = summoner_name[0]
        await ctx.send(
            riot_commands.get_player_stats(
                ctx.message.author.name,
                arg,
                self.bot.config.get_guild_config(ctx.guild.id),
                self.bot.config.general_config,
                guild_id=ctx.guild.id,
            )
        )

    @commands.command(name="smurf")
    async def smurf_(self, ctx, summoner_name: str):
        """Checks if a player is a smurf."""
        logger.debug("!smurf command called")
        await ctx.send(
            riot_commands.get_smurf(
                ctx.message.author.name,
                summoner_name,
                self.bot.config.get_guild_config(ctx.guild.id),
                self.bot.config.general_config,
                guild_id=ctx.guild.id,
            )
        )

    @commands.command(name="bans")
    @discord.ext.commands.cooldown(rate=1, per=5)
    async def bans_(self, ctx: commands.Context, team_names: commands.Greedy[str]):
        """Determines the five best champion bans against a 5-man lol team."""
        logger.debug("!bans command called")
        folder_name = self.bot.config.get_guild_config(ctx.guild.id).folders_and_files.folder_champ_spliced.format(
            guild_id=ctx.guild.id
        )
        await ctx.send(
            riot_commands.calculate_bans_for_team(self.bot.config, team_names),
            file=discord.File(f"{folder_name}/image.jpg"),
        )

    @commands.command(name="clash")
    async def clash_(self, ctx: commands.Context):
        """
        Returns the op.gg names of all clash team members.


        Reads a screenshot and returns the names and the op.gg links of all clash team members.
        The screenshot has to be attached to the command messsage.
        """
        logger.debug("!clash command called")

        if len(ctx.message.attachments) == 0:
            logger.error("Clash command called without an attachment")
            await ctx.send("Please attach an image to the command.")
            return
        elif len(ctx.message.attachments) > 1:
            logger.error("Clash command called with multiple attachments")
            await ctx.send("Only one image is needed. I will take the first.")

        attached_image = ctx.message.attachments[0]
        attached_image_file_name = attached_image.filename
        await attached_image.save(attached_image_file_name)
        ocr.set_image_file_name(attached_image_file_name)
        await ctx.send(ocr.run_ocr())
        ocr.clean_up_image(attached_image_file_name)
        await ctx.send(
            self.bot.config.get_guild_config(ctx.guild.id).messages.bans.format(ocr.get_formatted_summoner_names())
        )

    @commands.command(name="clash_dates", hidden=True)
    async def clash_dates(self, ctx):
        riot_commands.update_state_clash_dates(self.bot.state, self.bot.config.general_config)
        await ctx.send(self.bot.state.clash_dates)

    @commands.command()
    async def leaderboard(self, ctx: commands.Context, queue_type: str = "RANKED_SOLO_5x5"):
        """
        Print the LoL leaderboard.

        The `queue_type` is either 'RANKED_SOLO_5x5' or 'flex'. Defaults to 'RANKED_SOLO_5x5'.
        """
        logger.info("Leaderboard called")

        message_wait = await ctx.send("This can take some time...")

        if queue_type == "flex":
            queue_type = "RANKED_FLEX_SR"

        summoners = list(riot_utility.read_all_accounts(self.bot.config.general_config, ctx.guild.id))
        summoners = list(
            riot_commands.update_linked_summoners_data(
                summoners, self.bot.config.get_guild_config(ctx.guild.id), self.bot.config.general_config, ctx.guild.id
            )
        )

        for summoner in summoners:
            if queue_type not in summoner.rank_values.keys():
                summoners.remove(summoner)
        summoners = [summoner for summoner in summoners if summoner.rank_values]
        summoners.sort(key=lambda x: x.rank_values[queue_type], reverse=True)

        op_url = "https://euw.op.gg/multi/query="
        for summoner in summoners:
            op_url = op_url + f"{summoner.name}%2C"

        embed = discord.Embed(
            title=f'Kraut9 Leaderboard: {"Flex" if queue_type == "RANKED_FLEX_SR" else "SoloQ"}',
            colour=discord.Color.from_rgb(62, 221, 22),
            url=op_url[:-3],
        )

        embed.add_field(
            name="User",
            value="\n".join(
                (f"[{summoner.discord_user_name}](https://euw.op.gg/summoner/userName={summoner.name})")
                for summoner in summoners
            ),
            inline=True,
        )
        embed.add_field(
            name="Rank", value="\n".join((summoner.get_rank_string(queue_type) for summoner in summoners)), inline=True
        )
        embed.add_field(
            name="WR", value="\n".join((f"{summoner.get_winrate(queue_type)}%" for summoner in summoners)), inline=True
        )

        embed.set_footer(text=f"To link your account use {self.bot.get_command_prefix(ctx.guild.id)}link")

        await ctx.send(embed=embed)
        await message_wait.delete()


def setup(bot: DiscordBot.KrautBot):
    bot.add_cog(RiotCog(bot))
    logger.info("Riot cogs loaded")
