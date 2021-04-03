import logging
import pickle
import asyncio
from typing import List, Dict

from core.config import BotConfig
from core.play_requests import PlayRequest


logger = logging.getLogger(__name__)


class GuildState:
    """
    State class for one guild.

    Saves all variables that need to have a global state
    at runtime that potentially has to change during runtime.
    """

    def __init__(self):
        self.debug = False
        self.__play_requests = {}
        self.tmp_channel_ids = {}
        self.clash_date: str = None
        self.team1 = []
        self.team2 = []
        self.__remove_teams_task = None
        self.last_channel = None
        self.has_moved = False

    async def __remove_teams_after(self, seconds: int):
        logger.info("Wait %d until teams are removed", seconds)
        await asyncio.sleep(seconds)

        self.team1 = []
        self.team2 = []

    async def timer_remove_teams(self, seconds: int = 2 * 60 * 60):
        """
        Wait and then delete the teams.

        Checks first if the bot already waits to remove the teams.
        If so, the function cancels the waiting first.

        `seconds` is the time to wait before the teams are deleted. Defaults to 2*60*60.

        Raises a `RuntimeError` if the bot already waits to delete the teams and can't cancel that.
        """
        if self.__remove_teams_task is not None:
            logger.info("Try to cancel remove teams task.")
            self.__remove_teams_task.cancel()
            try:
                await self.__remove_teams_task
            except asyncio.CancelledError as ce:
                logger.error(f"{ce}: Can't cancel the remove team coroutine!")
            finally:
                self.__remove_teams_task = None

        self.__remove_teams_task = asyncio.create_task(self.__remove_teams_after(seconds))

        try:
            await asyncio.wait([self.__remove_teams_task])
        except asyncio.CancelledError:
            logger.info("Remove teams task was cancelled.")
            return

        self.__remove_teams_task = None

    def is_play_request(self, message_id: int) -> bool:
        return True if message_id in self.__play_requests else False

    def add_play_request(self, play_request: PlayRequest):
        """
        Add a play request to the state.

        Raises `LookupError` if play request already exists.
        """
        message_id = play_request.message_id

        if not self.is_play_request(message_id):
            self.__play_requests[message_id] = play_request
        else:
            raise LookupError("Play request already exists")

    def remove_play_request(self, message_id: int):
        """
        Remove a play request from the state.

        Does NOT check if the `message_id` belongs to a play request.
        """
        del self.__play_requests[message_id]

    def get_play_request(self, message_id: int) -> PlayRequest:
        """Return the play request given by the `message_id`."""
        return self.__play_requests[message_id]


class GeneralState:
    """
    General state class for the bot.

    Saves all variables that need to have a global state
    at runtime that potentially has to change during runtime.
    """

    def __init__(self, config: BotConfig):
        self.config = config
        self.version = self.get_version()
        self.clash_dates = []
        self.__guilds_state = {}
        self.lol_patch: str = None

    def get_version(self):
        """Return the git master head."""
        version_file = open("./.git/refs/heads/master", "r")
        return version_file.read()[:7]

    def write_state_to_file(self):
        """Pickle the state to a file."""
        filename = f"{self.config.general_config.database_directory_global_state}/ \
            {self.config.general_config.database_name_global_state}"
        try:
            with open(filename, "wb") as file:
                tmp_values = self.__set_futures_and_store_values(["__remove_teams_task"])
                pickle.dump(self, file)
                self.__restore_futures_values(tmp_values)
            logger.info("Global state saved")
        except pickle.PicklingError:
            filename_failed = filename + "_failed_content"
            with open(filename_failed, "w") as file_failed:
                file_failed.write(self)
            logger.error("Global state was not pickable. Content was written to %s", filename_failed)

    def __set_futures_and_store_values(self, attrs: List[str]) -> Dict[GuildState, Dict[str, asyncio.Task]]:
        """
        Set the futures in the all guild_states to `None` to make the state pickleable
        and return a `dict` with the current values.
        """
        current_values = {}
        for guild_state in self.__guilds_state.values():
            current_values[guild_state] = dict
            for attr in attrs:
                current_values[guild_state][attr] = getattr(guild_state, attr, None)
                setattr(guild_state, attr, None)
        return current_values

    def __restore_futures_values(self, values: Dict[GuildState, Dict[str, asyncio.Task]]) -> None:
        """Restores the values of the futures of all guild states."""
        for guild_state, attr_dict in values:
            for attr, value in attr_dict:
                setattr(guild_state, attr, value)

    def add_guild_state(self, guild_id: int):
        """
        Add the guild state.

        Raises a `KeyError` if guild already exists.
        """
        if self.check_if_guild_exists(guild_id):
            raise KeyError(f"Can't add {guild_id} because guild already exists.")
        else:
            self.__guilds_state[guild_id] = GuildState()

    def get_guild_state(self, guild_id: int) -> GuildState:
        """
        Return the guild state.

        Raises a `KeyError` if guild does not exist.
        """
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
        """Remove the guild state."""
        del self.__guilds_state[guild_id]

    def get_all_guild_ids(self) -> list:
        return [guild_id for guild_id in self.__guilds_state]
