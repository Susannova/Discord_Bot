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
    
    for summoner in summoners:
        if summoner.discord_user_name not in summoners_data:
            summoners_data[summoner.discord_user_name] = {'date_time': [], 'rank_value': [], 'winrate': []}
        
        summoner_rank = summoner.get_rank_value()
        summoner_winrate = summoner.get_soloq_winrate()

        if summoner_rank != summoners_data[summoner.discord_user_name]['rank_value'][-1] or summoner_winrate != summoners_data[summoner.discord_user_name]['winrate'][-1]:
            summoners_data[summoner.discord_user_name]['date_time'].append(time_updated)
            summoners_data[summoner.discord_user_name]['rank_value'].append(summoner_rank)
            summoners_data[summoner.discord_user_name]['winrate'].append(summoner_winrate)

    with open(file_path, 'w') as json_file:
        json.dump(summoners_data, json_file, indent=4)
    
    return summoners_data


class LoopCog(commands.Cog):
    """A class for background tasks"""

    # @tasks.loop(hours = 24 * 7)
    # @tasks.loop(seconds = 5)
    @tasks.loop(hours=24)
    async def print_leaderboard_weekly(self):
        summoners_data = update_summoners_data()

        fig1, ax1 = plt.subplots()
        fig2, ax2 = plt.subplots()
        
        ax1.set_xlabel('Zeit')
        ax1.set_ylabel('Winrate')
        # ax1.xaxis_date()

        ax2.set_xlabel('Zeit')
        ax2.set_ylabel('Rang')
        # ax2.xaxis_date()
        ax2.set_yticks(list(range(0, 2300, 400)))
        ax2.set_yticks(list(range(0, 2300, 100)), minor=True)
        ranks_string = ["Eisen 4", "Bronze 4", "Silber 4", "Gold 4", "Platin 4", "Diamant 4"]
        ax2.set_yticklabels(ranks_string)
        ax2.grid(axis='y')
        
        for summoner in summoners_data:
            # TODO Timezone is false
            x_data = [matplotlib.dates.epoch2num(time) for time in summoners_data[summoner]['date_time']]
            
            ax1.plot_date(x_data, list(summoners_data[summoner]['winrate']), label=summoner, drawstyle='steps-post', ls='-')
            ax2.plot_date(x_data, list(summoners_data[summoner]['rank_value']), label=summoner, drawstyle='steps-post', ls='-')
        
        ax1.legend()
        ax2.legend()

        fig1.savefig('./temp/winrate_graph.png')
        fig2.savefig('./temp/rank_graph.png')

        await self.channel.send(file=discord.File('temp/rank_graph.png'))
        await self.channel.send(file=discord.File('temp/winrate_graph.png'))
    
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