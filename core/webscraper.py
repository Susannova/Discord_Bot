import requests
import re
#r = requests.get('https://euw.op.gg/summoner/champions/userName=Maxteria')


with open('tmp.txt', 'w',  encoding="utf8") as all_data:
    all_data.write(r.text)

text = ""
with open('tmp.txt', 'r', encoding="utf8") as all_data:
    text = all_data.read()

top_six_played = re.findall('\<tr class="Row TopRanker">(.*)\<tr class="Row TopRanker">',text,  re.DOTALL)

win_rates = re.findall('<span class="WinRatio ((.|\n)*?)<\/span>', top_six_played[0])
kills = re.findall('<span class="Kills">((.|\n)*?)<\/span>', top_six_played[0])
deaths = re.findall('<span class="Deaths">((.|\n)*?)<\/span>', top_six_played[0])
assists = re.findall('<span class="Assists">((.|\n)*?)<\/span>', top_six_played[0])
win_rates = re.findall('<span class="Kills">((.|\n)*?)<\/span>', top_six_played[0])
wins = re.findall('<div class="Text Left">((.|\n)*?)<\/div>', top_six_played[0])
loses = re.findall('<div class="Text Right">((.|\n)*?)<\/div>', top_six_played[0])
names = re.findall('<td class="ChampionName Cell" data-value="((.|\n)*?)">', top_six_played[0])


winrates = []
for winrate in win_rates:
    re3 = re.findall('\d*%', winrate[0])
    winrates.append(re3[0])

print(winrates)