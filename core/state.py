import json
import pickle
import sys
import logging

from core import consts

logger = logging.getLogger('state')


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
        self.message_cache = {}
        self.clash_date = ''
        self.game_selector_id = None
        self.tmp_channel_ids = {}

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
    
    def write_state_to_file(self):
        filename = f'{consts.DATABASE_DIRECTORY_GLOBAL_STATE}/{consts.DATABASE_NAME_GLOBAL_STATE}'
        try:
            with open(filename, 'wb') as file:
                pickle.dump(self, file)
            logger.info('Global state saved')
        except pickle.PicklingError:
            filename_failed = filename + '_failed_content'
            with open(filename_failed, 'w') as file_failed:
                file_failed.write(self)
            logger.error('Global state was not pickable. Content was written to %s', filename_failed)
            

    # TODO Doesn't work?
    # def __del__(self):
    #    self.write_state_to_file()

   
try:
    file = open(f'{consts.DATABASE_DIRECTORY_GLOBAL_STATE}/{consts.DATABASE_NAME_GLOBAL_STATE}', 'rb')
    global_state = pickle.load(file)
    logger.info('Global State reinitialized.')
except FileNotFoundError:
    no_global_state_found_text = "No global state found! Create new global state."
    logger.warning(no_global_state_found_text)
    print(no_global_state_found_text, file=sys.stderr)
    global_state = GlobalState()
except:
    unknown_error_global_state_text = "Unknown error reading the global state!"
    logger.error(unknown_error_global_state_text)
    print(unknown_error_global_state_text, file=sys.stderr)
    backuped = False
    for i in range(10):
        try:
            filename = f'{consts.DATABASE_DIRECTORY_GLOBAL_STATE}/{consts.DATABASE_NAME_GLOBAL_STATE}'
            with open(filename, 'x') as file_backup:
                file_backup.write(file)
            logger.info("Old State was backuped to %s", filename)
            backuped = True
            break
        except FileExistsError:
            filename += str(i)
    
    if not backuped:
        logger.error("Failed to backup old global state 10 times. Are there 10 or more backupfiles already?")
    
    global_state = GlobalState()
