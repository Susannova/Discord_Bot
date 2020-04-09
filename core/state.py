import json


class SingletonBase(type):
    """Metaclass that changes class to be a Singleton.
    """
    def __init__(self, *args, **kwargs):
        self._instance = None
        super().__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self._instance is None:
            self._instance = super().__call__(*args, **kwargs)
            return self._instance
        else:
            return self._instance


class Singleton(metaclass=SingletonBase):
    """Inhertiable class that provides the Singleton
    property to all heirs.
    """
    pass


class GlobalState(Singleton):
    """Global state class that saves all variables that need to have a
    global state at runtime that potentially has to change during
    runtime. Has the Singleton property, which means that all instances
    created of this class all point to the same region in memory.
    This makes sure that the state stays conistent.
    """
    CONFIG_FILENAME = 'configuration'

    def __init__(self):
        self.CONFIG = self.read_config()
        self.VERSION = self.get_version()
        self.debug = False
        self.play_requests = {}
        self.tmp_message_author = None
        self.message_cache = []
        self.clash_date = ''
        self.game_selector_id = None
        self.tmp_text_channels = []
        self.tmp_voice_channels = []

    def get_version(self):
        version_file = open("./.git/refs/heads/master", "r")
        return version_file.read()[:7]

    def read_config(self):
        return json.load(open(f'./config/{self.CONFIG_FILENAME}.json', 'r'))

    def reload_config(self):
        self.CONFIG = self.read_config()

    def write_and_reload_config(self, data):
        with open(f'./config/{self.CONFIG_FILENAME}.json', 'w', encoding='utf-8') as file_:
            json.dump(data, file_, ensure_ascii=False, indent=4)
        self.reload_config()

   

global_state = GlobalState()

print('Global State initialized.')
