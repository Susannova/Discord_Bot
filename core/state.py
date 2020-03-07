import json

class GlobalState():
    """Global state class that saves all variables that need to have a
    global state at runtime that potentially has to change during
    runtime. Instantiate once and use the instance in all modules that
    need global state. This makes sure that the state is consistent
    throughout all of the modules.
    """
    CONFIG_FILENAME = 'configuration'

    def __init__(self):
        self.CONFIG = self.read_config()
        self.VERSION = self.get_version()
        self.debug = False
        self.play_requests = {}
        self.tmp_message_author = None
        self.message_cache = []

    def get_version(self):
        version_file = open("./.git/refs/heads/master", "r")
        return version_file.read()[:7]

    def read_config(self):
        return json.load(open(f'./config/{self.CONFIG_FILENAME}.json', 'r'))

    def write_and_reload_config(self, data):
        with open(f'./config/{self.CONFIG_FILENAME}.json', 'w', encoding='utf-8') as file_:
            json.dump(data, file_, ensure_ascii=False, indent=4)
        self.CONFIG = read_config_json('configuration')

global_state = GlobalState()

print('Global State initialized.')