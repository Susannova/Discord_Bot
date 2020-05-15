import time
import datetime
import asyncio
import json
import logging

from discord.ext import tasks, commands
import discord

from matplotlib.ticker import MultipleLocator
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


from riot import (
    riot_commands,
    riot_utility
)

from core.state import global_state as gstate

from core import (
    consts,
    bot_utility as utility,
    timers
)

logger = logging.getLogger('cog_tasks')

def get_summoners_data(update=True, file_path='./data/summoners_data.json'):
    summoners = list(riot_utility.read_all_accounts())
    if update:
        time_updated = time.time()
        summoners = list(riot_commands.update_linked_summoners_data(summoners))

    with open(file_path) as json_file:
        summoners_data = json.load(json_file)

    queue_data_empty_dict = {'date_time': [], 'Rang': [], 'Winrate': []}
    for summoner in summoners:
        # print(summoner.discord_user_name, summoner.data_league)
        if summoner.discord_user_name not in summoners_data:
            summoners_data[summoner.discord_user_name] = {'soloq': queue_data_empty_dict, 'flex': queue_data_empty_dict}

        # TODO Bad copy paste!
        if summoner.has_played_rankeds():
            summoner_soloq_rank = summoner.get_rank_value()
            summoner_soloq_winrate = summoner.get_winrate()
            if len(summoners_data[summoner.discord_user_name]['soloq']['date_time']) == 0 or summoner_soloq_rank != summoners_data[summoner.discord_user_name]['soloq']['Rang'][-1] or summoner_soloq_winrate != summoners_data[summoner.discord_user_name]['soloq']['Winrate'][-1]:
                summoners_data[summoner.discord_user_name]['soloq']['date_time'].append(time_updated)
                summoners_data[summoner.discord_user_name]['soloq']['Rang'].append(summoner_soloq_rank)
                summoners_data[summoner.discord_user_name]['soloq']['Winrate'].append(summoner_soloq_winrate)
        
        if summoner.has_played_rankeds('RANKED_FLEX_SR'):
            summoner_flex_rank = summoner.get_rank_value('RANKED_FLEX_SR')
            summoner_flex_winrate = summoner.get_winrate('RANKED_FLEX_SR')
            if len(summoners_data[summoner.discord_user_name]['flex']['date_time']) == 0 or summoner_flex_rank != summoners_data[summoner.discord_user_name]['flex']['Rang'][-1] or summoner_flex_winrate != summoners_data[summoner.discord_user_name]['flex']['Winrate'][-1]:
                summoners_data[summoner.discord_user_name]['flex']['date_time'].append(time_updated)
                summoners_data[summoner.discord_user_name]['flex']['Rang'].append(summoner_flex_rank)
                summoners_data[summoner.discord_user_name]['flex']['Winrate'].append(summoner_flex_winrate)

    with open(file_path, 'w') as json_file:
        json.dump(summoners_data, json_file, indent=4)

    return summoners_data

def plot_summoners_data(summoners_data, queue_type, data):
    fig1, ax1 = plt.subplots()

    ax1.set_xlabel('Zeit')
    ax1.set_ylabel(data)

    ax1.set_title(queue_type)

    if data == "Rang":
        ax1.set_yticks(list(range(0, 2300, 400)))
        ax1.set_yticks(list(range(0, 2300, 100)), minor=True)
        ranks_string = ["Eisen 4", "Bronze 4", "Silber 4", "Gold 4", "Platin 4", "Diamant 4"]
        ax1.set_yticklabels(ranks_string)
        ax1.grid(axis='y')

    for summoner in summoners_data:
        # TODO Timezone is false
        x_data = [mdates.epoch2num(time) for time in summoners_data[summoner][queue_type]['date_time']]

        ax1.plot_date(x_data, list(summoners_data[summoner][queue_type][data]), label=summoner, ls='-')

    ax1.legend()

    return fig1, ax1

def plot_all_summoners_data(summoners_data, filename):
    # fig, ax = plt.subplots(2, 2)
    # fig[0], ax[0] = plot_summoners_data(summoners_data, 'soloq', 'Rang')
    # fig[1], ax[1] = plot_summoners_data(summoners_data, 'soloq', 'Winrate')
    # fig[2], ax[2] = plot_summoners_data(summoners_data, 'flex', 'Rang')
    # fig[3], ax[3] = plot_summoners_data(summoners_data, 'flex', 'Winrate')

    fig, ax = plt.subplots(2, 2)

    args = (
        ('soloq', 'Rang'),
        ('soloq', 'Winrate'),
        ('flex', 'Rang'),
        ('flex', 'Winrate')
    )

    locator = mdates.AutoDateLocator(minticks=3, maxticks=5)
    # Does not work because is no object of module??? https://matplotlib.org/api/dates_api.html#matplotlib.dates.ConciseDateFormatter
    # formatter = mdates.ConciseDateFormatter(locator)

    for i in range(4):
        row = i % 2
        col = int(i / 2)

        queue_type = args[i][0]
        data = args[i][1]

        ax[row, col].set_xlabel('Datum')
        if col == 0:
            ax[row, col].set_ylabel(data)

        ax[row, col].set_title(queue_type)

        if data == 'Rang':
            ax[row, col].set_yticks(list(range(0, 2300, 400)))
            ax[row, col].set_yticks(list(range(0, 2300, 100)), minor=True)
            ranks_string = ["Eisen 4", "Bronze 4", "Silber 4", "Gold 4", "Platin 4", "Diamant 4"]
            ax[row, col].set_yticklabels(ranks_string)
        
        ax[row, col].grid(axis='y', which='both')            
        ax[row, col].xaxis.set_major_locator(locator)
        ax[row, col].xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.'))

        ax[row, col].xaxis.set_minor_locator(MultipleLocator(1))
        # ax[row, col].xaxis.set_major_locator(locator)
        # ax[row, col].xaxis.set_major_formatter(formatter)

        for summoner in summoners_data:
            # TODO Timezone is false
            x_data = [mdates.epoch2num(time) for time in summoners_data[summoner][queue_type]['date_time']]

            ax[row, col].plot_date(x_data, list(summoners_data[summoner][queue_type][data]), ls='-')

        
    fig.legend(labels=summoners_data.keys(), loc='center right')

    fig.set_size_inches(10, 10)
    fig.subplots_adjust(right=0.8)
    fig.savefig(filename)




class LoopCog(commands.Cog):
    """A class for background tasks"""

    def __init__(self, bot: commands.bot):
        self.bot = bot

        self.message_cache = gstate.message_cache
        
        if gstate.CONFIG['TOGGLE_RIOT_API']:
            if gstate.CONFIG['TOGGLE_SUMONNER_RANK_HISTORY']:
                self.update_summoners.start()
                self.print_leaderboard_loop.start()
            if gstate.CONFIG['TOGGLE_CHECK_LOL_PATCH']:
                self.check_LoL_patch.start()
        
        if gstate.CONFIG['TOGGLE_AUTO_DELETE']:
            self.auto_delete_purgeable_messages.start()
            self.auto_delete_tmp_channels.start()

        self.channel = None

    async def print_leaderboard(self, channel_to_print=None, update=True):
        summoners_data = get_summoners_data(update)

        if channel_to_print is None:
            channel_to_print = self.channel

        filename = 'temp/LoL_plot.png'
        plot_all_summoners_data(summoners_data, filename)
        await channel_to_print.send(file=discord.File(filename))


    @commands.command(name='plot')
    async def print_leaderboard_command(self, ctx):
        logger.debug('!plot command called')
        await self.print_leaderboard(ctx.channel, False)

    @tasks.loop(hours=1)
    async def update_summoners(self):
        logger.info("Update the summoners")
        get_summoners_data(True)
    
    @update_summoners.before_loop
    async def before_update_summoners(self):
        await self.bot.wait_until_ready()

    @tasks.loop(hours = 24 * 7)
    async def print_leaderboard_loop(self):
        logger.info("Print the LoL-plot")
        await self.print_leaderboard()
        

    @print_leaderboard_loop.before_loop
    async def before_print_leaderboard_loop(self):
        await self.bot.wait_until_ready()
        self.channel = self.bot.get_channel(639889605256019980)

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
        # The for loop is not needed right now but if the bot will ever run on multiple servers this is needed.
        for guild in self.bot.guilds:
            if riot_utility.update_current_patch():
                logger.info('New LoL patch notes')
                annoucement_channel = discord.utils.find(lambda m: m.name == 'announcements', guild.channels)
                await annoucement_channel.send(consts.MESSAGE_PATCH_NOTES_FORMATTED.format(guild.get_role(consts.ROLE_LOL_ID).mention, riot_utility.get_current_patch_url()))
    
    # auto delete all purgeable messages
    @tasks.loop(hours=1)
    async def auto_delete_purgeable_messages(self):
        logger.info('Look for purgeable messages')
        purgeable_message_list = utility.get_purgeable_messages_list(self.message_cache)
        for purgeable_message_id in purgeable_message_list:
            channel = self.bot.get_channel(self.message_cache[purgeable_message_id]["channel"])
            utility.clear_message_cache(purgeable_message_id, self.message_cache)
            if channel is None:
                logger.error("Message with id: %s can't be deleted. Channel is None.", purgeable_message_id)
                return
            purgeable_message = await channel.fetch_message(purgeable_message_id)
            await purgeable_message.delete()
            logger.info("Message with id %s was deleted automatically", purgeable_message_id)

    # auto delete all tmp_channels
    @tasks.loop(hours=1)
    async def auto_delete_tmp_channels(self):
        logger.info('Look for expired temp channels')
        deleted_channels = []
        for temp_channel_id in gstate.tmp_channel_ids:
            if timers.is_timer_done(gstate.tmp_channel_ids[temp_channel_id]["timer"]):
                temp_channel = self.bot.get_channel(temp_channel_id)
                temp_channel_name = gstate.tmp_channel_ids[temp_channel_id]["name"]

                if gstate.tmp_channel_ids[temp_channel_id]["deleted"]:
                    logger.debug("Temporary channel %s with id %s already deleted.", temp_channel_name, temp_channel_id)
                elif temp_channel is None:
                    logger.error("Temporary channel %s with id %s not found and can't be deleted.", temp_channel_name, temp_channel_id)
                else:
                    await temp_channel.delete(reason="Delete expired temporary channel")
                    logger.info('Temp channel %s is deleted', temp_channel_name)

                deleted_channels.append(temp_channel_id)
        
        for channel in deleted_channels:
            logger.debug("Remove temp channel %s from gstate", temp_channel_name)
            del gstate.tmp_channel_ids[channel]
    
    @auto_delete_purgeable_messages.before_loop
    async def before_auto_delete_purgeable_messages(self):
        await self.bot.wait_until_ready()

    #how often? at what time should this trigger
    @tasks.loop(hours=12)
    async def create_clash_play_request(self):
        current_date = ''
        for date in gstate.clash_dates:
            if date == current_date:
                # create play request
                gstate.clash_dates.remove(date) # how to not get it back in the before part => dont activate clash thing more than once
                pass

    @create_clash_play_request.before_loop
    async def before_create_clash_play_request(self):
        riot_commands.update_gstate_clash_dates()

def setup(bot: commands.Bot):
    bot.add_cog(LoopCog(bot))
    logger.info('Loop cogs loaded')
