import dataclasses
import json
import logging

from core.config.config_models.general_config import GeneralConfig
from core.config.guild_config import GuildConfig

logger = logging.getLogger(__name__)


class BotConfig:
    """Configuration of the bot."""

    def __init__(self, general_config=GeneralConfig(), *, config_file: str = None, update_config: bool = True):
        self.general_config = general_config
        self.__guilds_config = {}

        if config_file:
            general_config.config_file = config_file
        if update_config:
            self.update_config_from_file()

    def asdict(self) -> dict:
        """Return the general configs as a dict."""
        config_dict = {"general_config": dataclasses.asdict(self.general_config), "guilds_config": {}}

        for guild in self.__guilds_config:
            config = self.get_guild_config(guild)
            config_dict["guilds_config"][guild] = config.asdict()
        return config_dict

    def fromdict(self, config_dict: dict):
        """
        Set the settings given by a `dict`.

        The format of the dictionary must be like in `self.asdict()`,
        but the keys can be strings or integers.
        Settings not given in the `dict` are set to default.
        """
        self.general_config = GeneralConfig(**config_dict["general_config"])
        for guild in config_dict["guilds_config"]:
            guild_int = int(guild)
            if guild_int not in self.__guilds_config:
                self.add_new_guild_config(guild_int)
            self.get_guild_config(guild_int).fromdict(config_dict["guilds_config"][guild])

    def write_config_to_file(self, filename: str = None):
        """Write the config to the config file."""
        if filename is None:
            filename = self.general_config.config_file

        with open(filename, "w") as json_file:
            json.dump(self.asdict(), json_file, indent=4)
        logger.info("Saved the config to %s", filename)

    def update_config_from_file(self, filename=None):
        """Update the config from a file using fromdict."""
        if filename is None:
            filename = self.general_config.config_file

        config_dict = BotConfig(update_config=False).asdict()

        try:
            config_dict = json.load(open(filename, "r"))
        except FileNotFoundError:
            logger.warning("File '%s' does not exist. All settings are set to default.", filename)

        self.fromdict(config_dict)
        logger.info("Settings were updated from file %s", filename)

    def add_new_guild_config(self, guild_id: int) -> GuildConfig:
        """Add a new guild config and return the config."""

        if guild_id in self.__guilds_config:
            raise LookupError("Guild already has a config!")
        else:
            self.__guilds_config[guild_id] = GuildConfig()
            logger.info("We have added the guild %s to the config!", guild_id)

        return self.__guilds_config[guild_id]

    def remove_guild_config(self, guild_id: int):
        """Remove a guild config."""
        if guild_id not in self.__guilds_config:
            raise LookupError("Guild does not exists!")
        else:
            del self.__guilds_config[guild_id]
            logger.info("We have removed the guild %s from the config!", guild_id)

    def get_guild_config(self, guild_id: int) -> GuildConfig:
        """
        Get the guild that belongs to the id.

        Raises a `KeyError` if guild does not exists.
        """
        try:
            return self.__guilds_config[guild_id]
        except KeyError:
            logger.warning("Guild %s is unknown", guild_id)
            raise

    def check_if_guild_exists(self, guild_id: int) -> bool:
        """Check if a guild exists in the config."""
        return True if guild_id in self.__guilds_config else False

    def get_all_guild_ids(self) -> list:
        """Return a list with every guild id."""
        return [guild_id for guild_id in self.__guilds_config]
