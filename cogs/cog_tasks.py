import time
import datetime
import asyncio
import json
import logging
import typing
import pathlib

from discord.ext import tasks, commands
import discord

from matplotlib.ticker import MultipleLocator
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from itertools import cycle

from riot import riot_commands, riot_utility

from core import timers, checks
from core.kraut_bot import KrautBot

logger = logging.getLogger(__name__)


def plot_all_summoners_data(summoners_data: dict, filename, enable_xkcd: bool = False):
    # Hacky! But without the with the style is changed globally and there is no default style
    if enable_xkcd:
        with plt.xkcd():
            plot_all_summoners_data(summoners_data=summoners_data, filename=filename, enable_xkcd=False)
        return

    fig, ax = plt.subplots(2, 2, sharex="col", sharey="row")

    args = (("soloq", "Rang"), ("soloq", "Winrate"), ("flex", "Rang"), ("flex", "Winrate"))

    locator = mdates.AutoDateLocator(minticks=3, maxticks=5)
    # Does not work because is no object of module???
    # https://matplotlib.org/api/dates_api.html#matplotlib.dates.ConciseDateFormatter
    # formatter = mdates.ConciseDateFormatter(locator)

    for i in range(4):
        row = i % 2
        col = int(i / 2)

        queue_type = args[i][0]
        data = args[i][1]

        # TODO Not that nice
        colormap = plt.cm.hsv
        colors = {}
        sum_keys = summoners_data.keys()
        sum_num = len(sum_keys)
        for sum_index in range(0, sum_num):
            colors[list(sum_keys)[sum_index]] = colormap(sum_index / sum_num)
        markers = [".", "o", "v", "s", "x", "+"]
        mark_cycler = cycle(markers)

        if col == 0:
            ax[row, col].set_ylabel(data)
        if row == 1:
            ax[row, col].set_xlabel("Datum")
        else:
            ax[row, col].set_title(queue_type)

        if data == "Rang":
            ax[row, col].set_yticks(list(range(0, 2300, 400)))
            ax[row, col].set_yticks(list(range(0, 2300, 100)), minor=True)
            ranks_string = ["Eisen 4", "Bronze 4", "Silber 4", "Gold 4", "Platin 4", "Diamant 4"]
            ax[row, col].set_yticklabels(ranks_string)

        ax[row, col].grid(axis="y", which="both")
        ax[row, col].xaxis.set_major_locator(locator)
        ax[row, col].xaxis.set_major_formatter(mdates.DateFormatter("%d.%m."))

        ax[row, col].xaxis.set_minor_locator(MultipleLocator(1))
        # ax[row, col].xaxis.set_major_locator(locator)
        # ax[row, col].xaxis.set_major_formatter(formatter)

        for summoner in summoners_data:
            # TODO Timezone is false
            x_data = [mdates.epoch2num(time) for time in summoners_data[summoner][queue_type]["date_time"]]

            ax[row, col].plot_date(
                x_data,
                list(summoners_data[summoner][queue_type][data]),
                ls="-",
                marker=next(mark_cycler),
                color=colors[summoner],
            )

    fig.legend(labels=summoners_data.keys(), loc="center right")

    fig.set_size_inches(10, 10)
    fig.subplots_adjust(right=0.8, wspace=0.075, hspace=0.075)
    fig.savefig(filename)


class LoopCog(commands.Cog, name="Plot Commands"):
    """A class for background tasks."""

    def __init__(self, bot: KrautBot):
        self.bot = bot

        if self.bot.config.general_config.riot_api:
            self.update_summoners.start()
            self.print_leaderboard_loop.start()
            self.check_LoL_patch.start()
        self.auto_delete_tmp_channels.start()

    async def cog_check(self, ctx: commands.Context):
        return await checks.command_is_allowed(ctx)

    async def print_leaderboard(self, guild_id: int, channel_to_print=None, update=True, enable_xkcd=False):
        summoners_data = self.get_summoners_data(guild_id, update)

        if channel_to_print is None:
            channel_to_print = self.bot.get_channel(self.bot.config.get_guild_config(guild_id).channel_ids.plots)

        filename = "temp/LoL_plot.png"
        plot_all_summoners_data(summoners_data, filename, enable_xkcd=enable_xkcd)
        await channel_to_print.send(file=discord.File(filename))

    @commands.check(checks.is_riot_enabled)
    @commands.command(name="plot")
    async def print_leaderboard_command(self, ctx, enable_xkcd: typing.Optional[bool]):
        if self.bot.config.get_guild_config(ctx.guild.id).toggles.summoner_rank_history:
            logger.debug("!plot command called")
            await self.print_leaderboard(ctx.guild.id, ctx.channel, False, enable_xkcd=enable_xkcd)
        else:
            logger.error("In guild %s: plot called without toggle summoner_rank_history", ctx.guild.id)

    @tasks.loop(hours=1)
    async def update_summoners(self):
        logger.info("Update the summoners")
        for guild in self.bot.guilds:
            if self.bot.config.get_guild_config(guild.id).toggles.summoner_rank_history:
                self.get_summoners_data(guild.id, True)

    @update_summoners.before_loop
    async def before_update_summoners(self):
        await self.bot.wait_until_ready()

    @tasks.loop(hours=24 * 7)
    async def print_leaderboard_loop(self):
        logger.info("Print the LoL-plot")
        for guild in self.bot.guilds:
            if self.bot.config.get_guild_config(guild.id).toggles.leaderboard_loop:
                await self.print_leaderboard(guild.id)

    @print_leaderboard_loop.before_loop
    async def before_print_leaderboard_loop(self):
        await self.bot.wait_until_ready()

        datetime_now = datetime.datetime.now()
        datetime_mon_18 = datetime_now
        while datetime_mon_18.weekday() != 0:
            datetime_mon_18 = datetime_mon_18 + datetime.timedelta(days=1)

        datetime_mon_18 = datetime_mon_18.replace(hour=18, minute=0, second=0, microsecond=0)

        time_delta = (datetime_mon_18 - datetime_now).total_seconds()

        # Check if it is monday today and after 18:00
        if time_delta < 0:
            time_delta += 7 * 24 * 60 * 60

        logger.info("Wait %s hours to print the LoL-plot", time_delta / 60 / 60)

        try:
            await asyncio.sleep(time_delta)
        except asyncio.CancelledError:
            self.print_leaderboard_loop.cancel()
            return

        await self.bot.wait_until_ready()

    @tasks.loop(hours=24)
    async def check_LoL_patch(self):
        logger.info("Look for new LoL patch")
        if riot_utility.update_current_patch(self.bot.state):
            logger.info("New LoL patch notes")
            for guild in self.bot.guilds:
                guild_config = self.bot.config.get_guild_config(guild.id)

                if guild_config.toggles.check_LoL_patch:
                    annoucement_channel = self.bot.get_channel(guild_config.channel_ids.announcement)

                    text_to_send = guild_config.messages.patch_notes_formatted.format(
                        role_mention=guild.get_role(guild_config.get_game("LOL").role_id).mention,
                        patch_note=riot_utility.get_current_patch_url(self.bot.config.get_guild_config(guild.id)),
                    )

                    await annoucement_channel.send(text_to_send)

        riot_utility.download_champ_icons(self.bot.state.lol_patch, self.bot.config.general_config)

    @check_LoL_patch.before_loop
    async def check_LoL_patch_before_loop(self):
        await self.bot.wait_until_ready()

    @tasks.loop(hours=1)
    async def auto_delete_tmp_channels(self):
        """Delete all tmp_channels automatically."""
        logger.info("Look for expired temp channels")

        for guild in self.bot.guilds:
            guild_state = self.bot.state.get_guild_state(guild.id)

            deleted_channels = []
            for temp_channel_id in guild_state.tmp_channel_ids:
                if timers.is_timer_done(guild_state.tmp_channel_ids[temp_channel_id]["timer"]):
                    temp_channel = self.bot.get_channel(temp_channel_id)
                    temp_channel_name = guild_state.tmp_channel_ids[temp_channel_id]["name"]

                    if guild_state.tmp_channel_ids[temp_channel_id]["deleted"]:
                        logger.debug(
                            "Temporary channel %s with id %s already deleted.", temp_channel_name, temp_channel_id
                        )
                    elif temp_channel is None:
                        logger.error(
                            "Temporary channel %s with id %s not found and can't be deleted.",
                            temp_channel_name,
                            temp_channel_id,
                        )
                    else:
                        await temp_channel.delete(reason="Delete expired temporary channel")
                        logger.info("Temp channel %s is deleted", temp_channel_name)

                    deleted_channels.append(temp_channel_id)

            for channel in deleted_channels:
                logger.debug("Remove temp channel %s from gstate", temp_channel_name)
                del guild_state.tmp_channel_ids[channel]

    # TODO how often? at what time should this trigger
    @tasks.loop(hours=12)
    async def create_clash_play_request(self):
        current_date = ""

        state = self.bot.state

        for date in state.clash_dates:
            if date == current_date:
                # create play request
                # how to not get it back in the before part => dont activate clash thing more than once
                state.clash_dates.remove(date)
                pass

    @create_clash_play_request.before_loop
    async def before_create_clash_play_request(self):
        riot_commands.update_state_clash_dates(self.bot.state, self.bot.config.general_config)

    def get_summoners_data(
        self, guild_id: int, update=True, file_path_unformatted="./data/{guild_id}/summoners_data.json"
    ):
        summoners = list(riot_utility.read_all_accounts(self.bot.config.general_config, guild_id))
        time_updated = time.time()
        if update:
            summoners = list(
                riot_commands.update_linked_summoners_data(
                    summoners, self.bot.config.get_guild_config(guild_id), self.bot.config.general_config, guild_id
                )
            )

        file_path = file_path_unformatted.format(guild_id=guild_id)

        try:
            with open(file_path) as json_file:
                summoners_data = json.load(json_file)
        except FileNotFoundError:
            summoners_data = {}

        queue_data_empty_dict = {"date_time": [], "Rang": [], "Winrate": []}
        for summoner in summoners:
            # print(summoner.discord_user_name, summoner.data_league)
            if summoner.discord_user_name not in summoners_data:
                summoners_data[summoner.discord_user_name] = {
                    "soloq": queue_data_empty_dict,
                    "flex": queue_data_empty_dict,
                }

            # TODO Bad copy paste!
            if summoner.has_played_rankeds():
                summoner_soloq_rank = summoner.get_rank_value()
                summoner_soloq_winrate = summoner.get_winrate()
                if (
                    len(summoners_data[summoner.discord_user_name]["soloq"]["date_time"]) == 0
                    or summoner_soloq_rank != summoners_data[summoner.discord_user_name]["soloq"]["Rang"][-1]
                    or summoner_soloq_winrate != summoners_data[summoner.discord_user_name]["soloq"]["Winrate"][-1]
                ):
                    summoners_data[summoner.discord_user_name]["soloq"]["date_time"].append(time_updated)
                    summoners_data[summoner.discord_user_name]["soloq"]["Rang"].append(summoner_soloq_rank)
                    summoners_data[summoner.discord_user_name]["soloq"]["Winrate"].append(summoner_soloq_winrate)

            if summoner.has_played_rankeds("RANKED_FLEX_SR"):
                summoner_flex_rank = summoner.get_rank_value("RANKED_FLEX_SR")
                summoner_flex_winrate = summoner.get_winrate("RANKED_FLEX_SR")
                if (
                    len(summoners_data[summoner.discord_user_name]["flex"]["date_time"]) == 0
                    or summoner_flex_rank != summoners_data[summoner.discord_user_name]["flex"]["Rang"][-1]
                    or summoner_flex_winrate != summoners_data[summoner.discord_user_name]["flex"]["Winrate"][-1]
                ):
                    summoners_data[summoner.discord_user_name]["flex"]["date_time"].append(time_updated)
                    summoners_data[summoner.discord_user_name]["flex"]["Rang"].append(summoner_flex_rank)
                    summoners_data[summoner.discord_user_name]["flex"]["Winrate"].append(summoner_flex_winrate)

        path = pathlib.Path(file_path).parent
        if not path.exists():
            path.mkdir(parents=True)

        with open(file_path, "w") as json_file:
            json.dump(summoners_data, json_file, indent=4)

        return summoners_data


async def setup(bot: KrautBot):
    await bot.add_cog(LoopCog(bot))
    logger.info("Loop cogs loaded")
