import time, datetime
import asyncio
import json

from discord.ext import tasks, commands
import discord

import matplotlib
import matplotlib.pyplot as plt


from riot import (
    riot_commands,
    riot_utility
)

def update_summoners_data(file_path='./data/summoners_data.json'):
    summoners = list(riot_utility.read_all_accounts())
    time_updated = time.time()
    summoners = list(riot_commands.update_linked_summoners_data(summoners))

    with open(file_path) as json_file:
        summoners_data = json.load(json_file)
    
    queue_data_empty_dict = {'date_time': [], 'Rang': [], 'Winrate': []}
    for summoner in summoners:
        # print(summoner.discord_user_name, summoner.data_league)
        if summoner.discord_user_name not in summoners_data:
            summoners_data[summoner.discord_user_name] = {'soloq': queue_data_empty_dict, 'flex': queue_data_empty_dict}
        
        summoner_soloq_rank = summoner.get_rank_value()
        summoner_flex_rank = summoner.get_rank_value('RANKED_FLEX_SR')
        summoner_soloq_winrate = summoner.get_winrate()
        summoner_flex_winrate = summoner.get_winrate('RANKED_FLEX_SR')

        # TODO Bad copy paste!
        if len(summoners_data[summoner.discord_user_name]['soloq']['date_time']) == 0 or summoner_soloq_rank != summoners_data[summoner.discord_user_name]['soloq']['Rang'][-1] or summoner_soloq_winrate != summoners_data[summoner.discord_user_name]['soloq']['Winrate'][-1]:
                summoners_data[summoner.discord_user_name]['soloq']['date_time'].append(time_updated)
                summoners_data[summoner.discord_user_name]['soloq']['Rang'].append(summoner_soloq_rank)
                summoners_data[summoner.discord_user_name]['soloq']['Winrate'].append(summoner_soloq_winrate)
        if len(summoners_data[summoner.discord_user_name]['flex']['date_time']) == 0 or summoner_flex_rank != summoners_data[summoner.discord_user_name]['flex']['Rang'][-1] or summoner_flex_winrate != summoners_data[summoner.discord_user_name]['flex']['Winrate'][-1]:
                summoners_data[summoner.discord_user_name]['flex']['date_time'].append(time_updated)
                summoners_data[summoner.discord_user_name]['flex']['Rang'].append(summoner_flex_rank)
                summoners_data[summoner.discord_user_name]['flex']['Winrate'].append(summoner_flex_winrate)
        
    with open(file_path, 'w') as json_file:
        json.dump(summoners_data, json_file, indent=4)
    
    return summoners_data

def plot_summoners_data(summoners_data, queue_type, data, filename):
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
        x_data = [matplotlib.dates.epoch2num(time) for time in summoners_data[summoner][queue_type]['date_time']]
        
        ax1.plot_date(x_data, list(summoners_data[summoner][queue_type][data]), label=summoner, drawstyle='steps-post', ls='-')
    
    ax1.legend()

    fig1.savefig(filename)




class LoopCog(commands.Cog):
    """A class for background tasks"""

    # @tasks.loop(hours = 24 * 7)
    # @tasks.loop(seconds = 5)
    @tasks.loop(hours=24)
    async def print_leaderboard_weekly(self):
        summoners_data = update_summoners_data()

        rank_plot_filename = 'temp/rank_graph.png'
        plot_summoners_data(summoners_data, 'soloq', 'Rang', rank_plot_filename)
        await self.channel.send(file=discord.File(rank_plot_filename))

        winrate_plot_filename = './temp/winrate_graph.png'
        plot_summoners_data(summoners_data, 'soloq', 'Winrate', winrate_plot_filename)
        await self.channel.send(file=discord.File(winrate_plot_filename))

        flex_rank_plot_filename = 'temp/flex_rank_graph.png'
        plot_summoners_data(summoners_data, 'flex', 'Rang', flex_rank_plot_filename)
        await self.channel.send(file=discord.File(flex_rank_plot_filename))

        flex_winrate_plot_filename = './temp/flex_winrate_graph.png'
        plot_summoners_data(summoners_data, 'flex', 'Winrate', flex_winrate_plot_filename)
        await self.channel.send(file=discord.File(flex_winrate_plot_filename))
    
    @print_leaderboard_weekly.before_loop
    async def before_print_leaderboard_weekly(self):
        datetime_now = datetime.datetime.now()
        datetime_18 = datetime.datetime(datetime_now.year, datetime_now.month, datetime_now.day, 18)
        time_delta = (datetime_18 - datetime_now).total_seconds()

        await asyncio.sleep(time_delta)
        await self.bot.wait_until_ready()

        self.channel = self.bot.get_channel(639889605256019980)


    def __init__(self, bot: commands.bot):
        self.bot = bot
        self.print_leaderboard_weekly.start()