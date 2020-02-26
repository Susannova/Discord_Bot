from PIL import Image
import PIL.ImageOps    
import sys
import subprocess
import os

opgg = 'https://euw.op.gg/multi/query={}%2C{}%2C{}%2C{}%2C{}'

image_file_name = ''

def set_image_file_name(name):
    global image_file_name
    image_file_name = name

def crop_and_invert_image(i):
    image = Image.open(f'{image_file_name}')
    width, height = image.size
    image = image.crop((0+(i*int(width*.16)),int(height*.3),175+(i*int(width*.16)),int(height*.38)))
    inverted_image = PIL.ImageOps.invert(image)
    inverted_image.save(f'{i}.png')

def run_ocr_on_image(name):
    FNULL = open(os.devnull, 'w')
    subprocess.run(["tesseract", f'{name}.png', f'{name}'], stdout=FNULL, stderr=subprocess.STDOUT)

def get_summoner_name(i):
    text = ''
    with open(f'{i}.txt', 'r') as f:
        text = f.readlines()
    text2 = ''
    for line in text:
        if line != '':
            return line[:-1]

def get_opgg_link(summoners):
    return opgg.format(summoners[0], summoners[1], summoners[2], summoners[3], summoners[4])

def clean_up_tmp_files(name):
        subprocess.run(["rm", f'{name}.png'])
        subprocess.run(["rm", f'{name}.txt'])

def clean_up_image(name):
    subprocess.run(["rm", f'{name}'])

def replace_spaces(summoners):
    new_summoners = []
    for summoner in summoners:
        if ' ' in summoner:
            summoner = summoner.replace(" ", "%20")
        new_summoners.append(summoner)
    return new_summoners

def run_ocr():
    if image_file_name == '':
        print("No image file found.")
        return -1
    summoners = []
    for i in range(0, 5):
        crop_and_invert_image(i)
        run_ocr_on_image(i)
        summoners.append(get_summoner_name(i))
        clean_up_tmp_files(i)
    summoners = replace_spaces(summoners)
    return get_opgg_link(summoners)