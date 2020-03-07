import os
from PIL import Image
import json

import core.consts


def get_files(champs):
    files = []
    for champ in champs:
        if os.path.isfile(f'./{consts.FOLDER_CHAMP_ICON}/{champ}.png'):
            files.append(f'./{consts.FOLDER_CHAMP_ICON}/{champ}.png')
        else:
            files.append(f'./{consts.FOLDER_CHAMP_ICON}/-1.png')
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
    result.save(os.path.expanduser(f'./{consts.FOLDER_CHAMP_SPLICED}/image.jpg'))
    return 0


# === TEST === #
def testModule():
    assert(len(get_files(['Pyke', 'Blitzcrank', 'Annie', 'Ahri', 'Nautilus'])) == 5)
    assert(create_new_image(['Pyke', 'Blitzcrank', 'Annie', 'Ahri', 'Nunu']) == 0)
    assert(create_new_image(['Pyke', 'Blitzcrank', 'Annie', 'Ahri', 'Pingu']) == 0)
    return "Tests succeded."

if __name__ == "__main__":
    testModule()
# === TEST END === #