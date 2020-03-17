from PIL import Image
import PIL.ImageOps
import os

import pytesseract

opgg = 'https://euw.op.gg/multi/query={}%2C{}%2C{}%2C{}%2C{}'

image_file_name = ''
summoners = []

START_WIDTH_BASE = 0
END_WIDTH_BASE = 175
START_HEIGHT_RATIO = .3
END_HEIGHT_RATIO = .38
WIDTH_RATIO = .16


def set_image_file_name(name):
    global image_file_name
    image_file_name = name


def crop_and_invert_image(i):
    image = Image.open(f'{image_file_name}')
    width, height = image.size
    image = image.crop((
        START_WIDTH_BASE + (i * int(width * WIDTH_RATIO)),
        int(height * START_HEIGHT_RATIO),
        END_WIDTH_BASE + (i * int(width * WIDTH_RATIO)),
        int(height * END_HEIGHT_RATIO)))
    inverted_image = PIL.ImageOps.invert(image)
    inverted_image.save(f'{i}.png')


def run_ocr_on_image(i):
    return pytesseract.image_to_string(Image.open(f'{i}.png'))


def get_opgg_link(summoners):
    return opgg.format(
        summoners[0], summoners[1], summoners[2], summoners[3], summoners[4])


def clean_up_image(name):
    os.remove(name)


def replace_spaces(summoners):
    new_summoners = []
    for summoner in summoners:
        if ' ' in summoner:
            summoner = summoner.replace(" ", "%20")
        new_summoners.append(summoner)
    return new_summoners


def get_summoner_names():
    if image_file_name == '':
        print("No image file found.")
        return -1
    summoners = []
    for i in range(0, 5):
        crop_and_invert_image(i)
        summoners.append(run_ocr_on_image(i))
        clean_up_image(f'{i}.png')
    summoners = replace_spaces(summoners)
    return summoners


def get_formatted_summoner_names():
    if len(summoners) == 0:
        print("Did not run ocr yet.")
        return
    formatted_summoner_names = ''
    for name in summoners:
        if name.find('%20') > 0:
            name = name.replace('%20', '%')
        formatted_summoner_names += f'{name} '
    return formatted_summoner_names[:-1]


def run_ocr():
    global summoners
    summoners = get_summoner_names()
    return get_opgg_link(summoners)
