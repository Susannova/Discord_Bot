raise RuntimeError("Can't work right now because of an update of config")

# import requests
# import urllib
# import concurrent.futures
# import json

# from core.config import CONFIG
# from . import riot_utility as utility
# from .riot_utility import data_champ

# url = 'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-icons/'
# urls = []


# def read_json():
#     return json.load(open('./config/configuration.json', 'r'))


# config = read_json()


# def fill_urls():
#     count = 0
#     for value in data_champ['data'].values():
#         urls.append(url + value['key'] + '.png')

# def download_image(url):
#     img_bytes = requests.get(url).content
#     name = utility.get_champion_name_by_id(int(url[101:-4]))
#     with open(f'./{CONFIG.folders_and_files.folder_champ_icon}/{name}.png', 'wb') as img_file:
#         img_file.write(img_bytes)
#         print(f'{name} Icon was downloaded...')


# def start_download():
#     with concurrent.futures.ThreadPoolExecutor() as executor:
#         executor.map(download_image, urls)


# if __name__ == "__main__":
#     fill_urls()
#     start_download()
