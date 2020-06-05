import os
from PIL import Image

from core.config import BotConfig


def get_files(champs: tuple, config: BotConfig):
    files = []
    for champ in champs:
        if os.path.isfile(f'./{config.general_config.folder_champ_icon}/{champ}.png'):
            files.append(f'./{config.general_config.folders_and_files.folder_champ_icon}/{champ}.png')
        else:
            files.append(f'./{config.general_config.folders_and_files.folder_champ_icon}/-1.png')
    return files


def create_new_image(champs, config: BotConfig):
    files = get_files(champs, config)
    result = Image.new("RGB", (600, 120))
    for index, file in enumerate(files):
        path = os.path.expanduser(file)
        img = Image.open(path)
        img.thumbnail((120, 120), Image.ANTIALIAS)
        x = index * 120
        y = index % 120
        w, h = img.size
        result.paste(img, (x, y, x + w, y + h))
    result.save(os.path.expanduser(f'./{config.general_config.folder_champ_spliced}/image.jpg'))
    return 0

# === TEST === #
def testModule():
    config = BotConfig()
    assert(len(get_files(['Pyke', 'Blitzcrank', 'Annie', 'Ahri', 'Nautilus'], config)) == 5)
    assert(create_new_image(['Pyke', 'Blitzcrank', 'Annie', 'Ahri', 'Nunu'], config) == 0)
    assert(create_new_image(['Pyke', 'Blitzcrank', 'Annie', 'Ahri', 'Pingu'], config) == 0)
    return "Tests succeded."


if __name__ == "__main__":
    testModule()
