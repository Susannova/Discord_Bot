import requests
import re

from bs4 import BeautifulSoup

def get_soup_for_summoner(summoner_name) -> BeautifulSoup:
    r = requests.get(f'https://euw.op.gg/summoner/champions/userName={summoner_name}')
    return BeautifulSoup(r.text, features="html.parser")

soup = get_soup_for_summoner('Maxteria')

def generate_winrates():
    win_rates = []
    for win_rate in soup.find_all(class_="WinRatio", limit=10):
        win_rates.append(win_rate.text[:-1])
    return win_rates

def generate_names():
    names = []
    for name in soup.find_all(class_="ChampionName", limit=10):
        names.append(name.text[1:-1])
    return names

def generate_games_played():
    games_played = []
    for played in soup.find_all(class_="Graph", limit=10):
        games_played.append(played.text[2:])
    return games_played

def clean_result(result):
    wins = []
    fails = []
    for line in result:
        if line.find('\n') >= 0:
            print(len(line.replace('\n', ' ').split(' ')))
            print(line)
            wins.append(line.replace('\n', ' ').split(' ')[0])
            fails.append(line.replace('\n', ' ').split(' ')[2])
    
    print(wins)
    print(fails)
    return wins, fails



def create_summoner():
    stats = []
    names = generate_names()
    win_rates = generate_winrates()
    wins, fails = clean_result(generate_games_played())

    for i in range(0, len(generate_names())):
        stats.append((names[i], win_rates[i], wins[i], fails[i]))
    
    return stats
stats = create_summoner()

# print(stats)
# with open('tmp.txt', 'w',  encoding="utf8") as all_data:
#     all_data.write(r.text)

# text = ""
# with open('tmp.txt', 'r', encoding="utf8") as all_data:
#     text = all_data.read()

# top_six_played = re.findall('\<tr class="Row TopRanker">(.*)\<tr class="Row TopRanker">',text,  re.DOTALL)

# win_rates = re.findall('<span class="WinRatio ((.|\n)*?)<\/span>', top_six_played[0])
# kills = re.findall('<span class="Kills">((.|\n)*?)<\/span>', top_six_played[0])
# deaths = re.findall('<span class="Deaths">((.|\n)*?)<\/span>', top_six_played[0])
# assists = re.findall('<span class="Assists">((.|\n)*?)<\/span>', top_six_played[0])
# win_rates = re.findall('<span class="Kills">((.|\n)*?)<\/span>', top_six_played[0])
# wins = re.findall('<div class="Text Left">((.|\n)*?)<\/div>', top_six_played[0])
# loses = re.findall('<div class="Text Right">((.|\n)*?)<\/div>', top_six_played[0])
# names = re.findall('<td class="ChampionName Cell" data-value="((.|\n)*?)">', top_six_played[0])


# winrates = []
# for winrate in win_rates:
#     re3 = re.findall('\d*%', winrate[0])
#     winrates.append(re3[0])

# print(winrates)