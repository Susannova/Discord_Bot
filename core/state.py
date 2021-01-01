import pickle
import logging
from core.config import BotConfig
from core.play_requests import PlayRequest


logger = logging.getLogger(__name__)

class GuildState:
    """State class for one guild that saves all variables that need to have a
    global state at runtime that potentially has to change during
    runtime.
    """
    def __init__(self):
        self.debug = False
        self.__play_requests = {}
        self.tmp_channel_ids = {}
        self.clash_date: str = None
        self.last_team = []
        self.team1 = []
        self.team2 = []
    
    def is_play_request(self, message_id: int) -> bool:
        return True if message_id in self.__play_requests else False
    
    def add_play_request(self, play_request: PlayRequest):
        """ Adds a play request to the state. 
        Raises LookupError if play request already exists """

        message_id = play_request.message_id

        if not self.is_play_request(message_id):
            self.__play_requests[message_id] = play_request
        else:
            raise LookupError("Play request already exists")

    def remove_play_request(self, message_id: int):
        """ Removes a play request from the state
        Does NOT check if the message_id belongs to a play request!"""
        
        del self.__play_requests[message_id]
    
    def get_play_request(self, message_id: int) -> PlayRequest:
        """ Returns the play request given by the message_id """
        return self.__play_requests[message_id]



class GeneralState:
    """State class that saves all variables that need to have a
    global state at runtime that potentially has to change during
    runtime. 
    """
    def __init__(self, config: BotConfig):
        self.config = config
        self.version = self.get_version()
        self.clash_dates = []
        self.__guilds_state = {}
        self.lol_patch: str = None

    def get_version(self):
        """ Returns the git master head """
        version_file = open("./.git/refs/heads/master", "r")
        return version_file.read()[:7]

    def write_state_to_file(self):
        """ Pickles the state to a file """
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
        """ Adds the guild state. Raises a KeyError if guild already exists """
        if self.check_if_guild_exists(guild_id):
            raise KeyError(f"Can't add {guild_id} because guild already exists.")
        else:
            self.__guilds_state[guild_id] = GuildState()

    def get_guild_state(self, guild_id: int) -> GuildState:
        """ Returns the guild state. Raises a KeyError if guild does not exist """
        if not self.check_if_guild_exists(guild_id):
            raise KeyError(f"{guild_id} does not exists!.")
        else:
            return self.__guilds_state[guild_id]
    
    def check_if_guild_exists(self, guild_id: int) -> bool:
        if guild_id in self.__guilds_state:
            return True
        else:
            return False
    
    def remove_guild_state(self, guild_id: int):
        """ Removes the guild state """
        del self.__guilds_state[guild_id]
    
    def get_all_guild_ids(self) -> list:
        return [guild_id for guild_id in self.__guilds_state]
