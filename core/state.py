import json
import pickle
import sys
import logging
from core.config import BotConfig


logger = logging.getLogger(__name__)

class GuildState:
    """State class for one guild that saves all variables that need to have a
    global state at runtime that potentially has to change during
    runtime. 
    """
    def __init__(self):
        self.debug = False
        self.message_cache = {}
        self.play_requests = {}
        self.tmp_channel_ids = {}


class GeneralState:
    """State class that saves all variables that need to have a
    global state at runtime that potentially has to change during
    runtime. 
    """
    def __init__(self, config: BotConfig):
        self.config = config
        self.version = self.get_version()
        self.clash_dates = []
        self.guilds_state = {}

    def get_version(self):
        version_file = open("./.git/refs/heads/master", "r")
        return version_file.read()[:7]

    def write_state_to_file(self):
        filename = f'{self.config.general_config.database_directory_global_state}/{self.config.general_config.database_name_global_state}'
        try:
            with open(filename, 'wb') as file:
                pickle.dump(self, file)
            logger.info('Global state saved')
        except pickle.PicklingError:
            filename_failed = filename + '_failed_content'
            with open(filename_failed, 'w') as file_failed:
                file_failed.write(self)
            logger.error('Global state was not pickable. Content was written to %s', filename_failed)
    
    def add_guild_state(self, guild_id: int):
        if guild_id in self.guilds_state:
            raise KeyError(f"Can't add {guild_id} because guild already exists.")
        else:
            self.guilds_state[guild_id] = GuildState()

    def get_guild_state(self, guild_id: int) -> GuildState:
        if guild_id not in self.guilds_state:
            raise KeyError(f"{guild_id} does not exists!.")
        else:
            return self.guilds_state[guild_id]
    
    def remove_guild_state(self, guild_id: int):
        """ Removes the guild state """
        del self.guilds_state[guild_id]