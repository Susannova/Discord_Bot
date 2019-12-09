import os
from PIL import Image
import riot

def get_files(champs):
    files = []
    for champ in champs:
        files.append(f'./champ-emoji/{champ}.png')
    return files

def create_new_image(champs):
    files = get_files(champs)
    result = Image.new("RGB", (600, 120))
    for index, file in enumerate(files):
        path = os.path.expanduser(file)
        img = Image.open(path)
        img.thumbnail((120, 120), Image.ANTIALIAS)
        x = index * 120
        y = index %  120
        w, h = img.size
        result.paste(img, (x, y, x + w, y + h))
    result.save(os.path.expanduser('./champ-spliced/image.jpg'))
