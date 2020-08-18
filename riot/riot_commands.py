"""Module that interacts with the Riot API
and transforms the received data in
a user readable way.
"""
import shelve
import matplotlib.pyplot as plt
import logging

from discord.ext import commands
import discord

import pandas as pd
from core import (
    timers,
    exceptions,
    config
)
from core.state import GeneralState

from . import (
    image_transformation,
    riot_utility as utility
)


logger = logging.getLogger(__name__)

_timers = []

# FIXME: this is trash
# === BAN CALCULATION === #


def get_best_ban(summoner):
    ban_list = []
    most_played_champs = list(summoner.get_most_played_champs(10))
    for champ in most_played_champs:
        if summoner.has_played_champ_by_name_in_last_n_days(champ, 30):
            ban_list.append(champ)
        if len(ban_list) == 5:
            return ban_list
    return ban_list


def get_best_bans_for_team(team) -> list:
    ban_list = []
    ranks = []
    best_bans_for_player = []
    for player in team:
        ranks.append(player.rank_value['RANKED_SOLO_5x5'])
        best_bans_for_player.append(get_best_ban(player))
    average_rank = utility.get_average_rank(ranks)
    for i in range(0, len(team)):
        if ranks[i] <= average_rank - 500:
            continue
        elif ranks[i] > average_rank - 500 and ranks[i] <= average_rank + 800:
            ban_list.append(best_bans_for_player[i][0])
        elif team[i].is_smurf() or ranks[i] > average_rank + 800:
            ban_list.append(best_bans_for_player[i][0])
            ban_list.append(best_bans_for_player[i][1])
            ban_list.append(best_bans_for_player[i][2])
        while len(ban_list) > 5:
            del ban_list[-1]
    return ban_list


# === INTERFACE === #


def get_player_stats(discord_user_name, summoner_name, guild_config: config.GuildConfig, general_config: config.GeneralConfig, guild_id: int, queue_type='RANKED_SOLO_5x5') -> str:
    summoner = get_or_create_summoner(discord_user_name, summoner_name, guild_config, general_config, guild_id=guild_id)
    return f'Rank: {summoner.get_rank_string(queue_type)}, Winrate {summoner.get_winrate(queue_type)}%.'


def get_smurf(discord_user_name, summoner_name, guild_config: config.GuildConfig, general_config: config.GeneralConfig, guild_id: int) -> str:
    summoner = get_or_create_summoner(discord_user_name, summoner_name, guild_config, general_config, guild_id)
    is_smurf_word = 'kein'
    if summoner.is_smurf():
        is_smurf_word = 'ein'
    return f'Der Spieler **{utility.format_summoner_name(summoner.name)}** ist sehr wahrscheinlich **{is_smurf_word}** Smurf.'


def calculate_bans_for_team(bot_config: config.BotConfig, *names) -> str:
    utility.update_champion_json()
    if len(names[0]) != 5:
        logger.exception('Check Failure')
        raise commands.CheckFailure()
    team = list(utility.create_summoners(list(names[0]), bot_config.general_config))
    output = get_best_bans_for_team(team)
    image_transformation.create_new_image(output, bot_config)
    op_url = f'https://euw.op.gg/multi/query={team[0].name}%2C{team[1].name}%2C{team[2].name}%2C{team[3].name}%2C{team[4].name}'
    return f'Team OP.GG: {op_url}\nBest Bans for Team:\n{utility.pretty_print_list(output)}'


def link_account(discord_user_name, summoner_name, guild_config: config.GuildConfig, general_config: config.GeneralConfig, guild_id: int):
    summoner = utility.create_summoner(summoner_name, general_config, guild_config=guild_config)
    summoner.discord_user_name = discord_user_name
    folder_name = guild_config.folders_and_files.database_directory_summoners.format(guild_id=guild_id)
    with shelve.open(f'{folder_name}/{guild_config.folders_and_files.database_name_summoners}', 'rc') as database:
        for key in database.keys():
            if key == str(discord_user_name):
                logger.exception('DataBaseException')
                raise exceptions.DataBaseException('Your discord account already has a lol account linked to it')
            if database[key] is not None:
                if database[key].name == summoner.name:
                    logger.exception('DataBaseException')
                    raise exceptions.DataBaseException('This lol account already has a discord account that is linked to it')
        database[str(discord_user_name)] = summoner


def update_linked_account_data_by_discord_user_name(discord_user_name, guild_config: config.GuildConfig, general_config: config.GeneralConfig, guild_id: int):
    summoner = utility.create_summoner(utility.read_account(discord_user_name, general_config, guild_id).name, general_config, guild_config=guild_config)
    summoner.discord_user_name = discord_user_name
    folder_name = general_config.database_directory_summoners.format(guild_id=guild_id)
    with shelve.open(f'{folder_name}/{general_config.database_name_summoners}', 'rc') as database:
        database[str(discord_user_name)] = summoner
    return summoner

def update_linked_summoners_data(summoners, guild_config: config.GuildConfig, general_config: config.GeneralConfig, guild_id: int):
    for summoner in summoners:
        yield update_linked_account_data_by_discord_user_name(summoner.discord_user_name, guild_config, general_config, guild_id)

def get_or_create_summoner(discord_user_name, summoner_name, guild_config: config.GuildConfig, general_config: config.GeneralConfig, guild_id: int):
    if summoner_name is None:
        summoner = utility.read_account(discord_user_name, general_config, guild_id)
        if utility.is_in_need_of_update(summoner):
            update_linked_account_data_by_discord_user_name(discord_user_name, guild_config, general_config, guild_id)
        return summoner
    else:
        return utility.create_summoner(summoner_name, general_config, guild_config=guild_config)

def unlink_account(discord_user_name, guild_config: config.GuildConfig, guild_id: int):
    folder_name = guild_config.folders_and_files.database_directory_summoners.format(guild_id=guild_id)
    with shelve.open(f'{folder_name}/{guild_config.folders_and_files.database_name_summoners}', 'rc') as database:
        for key in database.keys():
            if key == str(discord_user_name):
                del database[key]


# FIXME im still not happy with this
def create_embed(ctx, guild_config: config.GuildConfig, general_config: config.GeneralConfig, guild_id):
    summoners = list(utility.read_all_accounts(general_config, guild_id))
    old_summoners = summoners.copy()
    summoners = list(update_linked_summoners_data(summoners, guild_config, general_config, guild_id))
    summoners.sort(key=lambda x: x.rank_value['RANKED_SOLO_5x5'], reverse=True)



    op_url = 'https://euw.op.gg/multi/query='
    for summoner in summoners:
        op_url = op_url + f'{summoner.name}%2C'
    _embed = discord.Embed(
        title='Kraut9 Leaderboard',
        colour=discord.Color.from_rgb(62, 221, 22),
        url=op_url[:-3])

    rank_strings = []
    white_space_pattern = '\u200b \u200b'
    for summoner in summoners:
        rank_string = summoner.get_rank_string()
        length = len(rank_string)
        rank_string = rank_string + f' %!{summoner.get_winrate()}%'
        rank_string = rank_string.replace('%!', f'{white_space_pattern * (25 - length)}')
        rank_strings.append(rank_string)

    _embed.add_field(name='User', value='\n'.join([summoner.discord_user_name for summoner in summoners]))
    _embed.add_field(name='Summoner', value='\n'.join([summoner.name for summoner in summoners]))
    _embed.add_field(name='Rank \t\t\t\t\t\t\t\t Winrate', value='\n'.join(rank_strings))
    return _embed


def create_leaderboard_embed(guild_config: config.GuildConfig, general_config: config.GeneralConfig, guild_id):
    summoners = list(utility.read_all_accounts(general_config, guild_config.unsorted_config.guild_id))
    old_summoners = summoners.copy()
    summoners = list(update_linked_summoners_data(summoners, guild_config, general_config, guild_id))
    summoners.sort(key=lambda x: x.rank_value['RANKED_SOLO_5x5'], reverse=True)

    for summoner in summoners:
        for old_summoner in old_summoners:
            if old_summoner.name == summoner.name:
                summoner.rank_dt = summoner.rank_value['RANKED_SOLO_5x5'] - old_summoner.rank_value['RANKED_SOLO_5x5']
                if summoner.rank_dt > 0:
                    summoner.rank_dt = f'+{summoner.rank_dt}'
                elif summoner.rank_dt < 0:
                    summoner.rank_dt = f'-{summoner.rank_dt}'
                elif summoner.rank_dt == 0:
                    summoner.rank_dt = f'\u00B1{summoner.rank_dt}'
    data = [[summoner.discord_user_name, summoner.name, summoner.get_rank_string(), f'{summoner.get_winrate()}%', summoner.rank_dt, summoner.get_promo_string() if summoner.get_promo_string() is not None else '-' ] for summoner in summoners if summoner.has_played_rankeds() ]
    fig, ax = plt.subplots()

    # hide axes
    fig.patch.set_visible(False)
    ax.axis('off')
    ax.axis('tight')

    df = pd.DataFrame(data, columns=['Discord User', 'Summoner', 'Rank', 'Winrate', 'Progress in LP', 'Promo Progress'])
    inner_cell_colours = []
    col_colors = []
    for i in range(0, len(df.columns)):
        inner_cell_colours.append('#2c2f33')
        col_colors.append('#23272a')

    outer_cell_colours = []
    for i in range(0, len(data)):
        outer_cell_colours.append(inner_cell_colours)

    table = ax.table(cellText=df.values, colLabels=df.columns, loc='center', cellLoc='center', colColours=col_colors, cellColours=outer_cell_colours)
    table_props = table.properties()
    table_cells = table_props['child_artists']
    for cell in table_cells:
        cell.get_text().set_fontsize(30)
        cell.get_text().set_color('white')

    fig.tight_layout()

    plt.savefig('./temp/leaderboard.png')

    op_url = 'https://euw.op.gg/multi/query='
    for summoner in summoners:
        op_url = op_url + f'{summoner.name}%2C'
    _embed = discord.Embed(
        title='Kraut9 Leaderboard',
        colour=discord.Color.from_rgb(62, 221, 22),
        url=op_url[:-3])
    return _embed



def update_state_clash_dates(state: GeneralState, general_config: config.GeneralConfig):
    clash_dates = utility.get_upcoming_clash_dates(general_config, state)
    for clash_date in clash_dates:
        if clash_date not in state.clash_dates:
            state.clash_dates.append(clash_date)
    return
    
# === INTERFACE END === #
