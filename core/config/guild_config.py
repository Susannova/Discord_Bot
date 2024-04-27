import dataclasses

from core.config.config_models.unsorted_config import UnsortedConfig
from core.config.config_models.messages_config import Messages_Config
from core.config.config_models.channel_ids import Channel_Ids
from core.config.config_models.folders_and_files import Folders_and_Files
from core.config.config_models.toggles import Toggles
from core.config.config_models.game import Game
from core.config.config_models.command import Command


def update_recursive(old_dict: dict, update_dict: dict):
    """Update old_dict with update_dict."""
    for key in update_dict:
        if key in old_dict and isinstance(update_dict[key], dict):
            update_recursive(old_dict[key], update_dict[key])
        else:
            old_dict[key] = update_dict[key]


class GuildConfig:
    """Configuration for the guild."""

    def __init__(self):
        self.unsorted_config = UnsortedConfig()
        self.messages = Messages_Config()
        self.channel_ids = Channel_Ids()
        self.folders_and_files = Folders_and_Files()
        self.toggles = Toggles()

        # Some dicts. Use the add and get functions to modify this.
        self.__games = {}
        self.__commands = {}

    def asdict(self) -> dict:
        """Return all settings as a dict."""
        return {
            "unsorted_config": dataclasses.asdict(self.unsorted_config),
            "messages": dataclasses.asdict(self.messages),
            "channel_ids": dataclasses.asdict(self.channel_ids),
            "folders_and_files": dataclasses.asdict(self.folders_and_files),
            "toggles": dataclasses.asdict(self.toggles),
            "games": self.__games,
            "commands": self.__commands,
        }

    def fromdict(self, config_dict, update: bool = False):
        """
        Set the settings given by a dict.

        The format of the dictionary must be like in `self.asdict()`.
        If `update` is `False`, settings not given in the dict are set to default.
        `update` defaults to `False`.
        """
        new_config = self.asdict() if update else GuildConfig().asdict()
        update_recursive(new_config, config_dict)

        self.unsorted_config = UnsortedConfig(**new_config["unsorted_config"])
        self.messages = Messages_Config(**new_config["messages"])
        self.channel_ids = Channel_Ids(**new_config["channel_ids"])
        self.folders_and_files = Folders_and_Files(**new_config["folders_and_files"])
        self.toggles = Toggles(**new_config["toggles"])
        self.__games = new_config["games"]
        self.__commands = new_config["commands"]

    def check_for_invalid_channel_ids(self, valid_ids: list):
        """
        Check and delete ids that are not in valid_ids
        and yields tuples of the deleted id and its category.
        """
        is_invalid = False
        channel_ids_dict = dataclasses.asdict(self.channel_ids)

        for key, value in channel_ids_dict.items():
            if isinstance(value, list):
                for channel_id in value:
                    if channel_id not in valid_ids:
                        is_invalid = True
                        value.remove(channel_id)
                        yield (key, channel_id)
            elif value not in valid_ids:
                is_invalid = True
                channel_ids_dict[key] = None
                yield (key, value)

        if is_invalid:
            self.channel_ids = Channel_Ids(**channel_ids_dict)

    def game_exists(self, game_short_name: str) -> bool:
        return game_short_name in self.__games

    def get_game(self, game_short_name: str) -> Game:
        """Returns a Game class that belongs to the short name of a game."""
        if self.game_exists(game_short_name):
            game_dict = self.__games[game_short_name]
            return Game(**game_dict)
        else:
            raise LookupError("Game not found")

    def yield_all_game_role_ids(self):
        for game in self.__games:
            yield Game(**self.__games[game]).role_id

    def add_game(self, game: str, long_name: str, role_id: int, emoji: int, category_id: int = None, cog: str = None):
        """Add a new game to the bot."""
        if category_id is None:
            category_id = self.channel_ids.game_category
        # The asdict prevents one from create a dict that is invalid to Game
        self.__games[game] = dataclasses.asdict(
            Game(name_short=game, name_long=long_name, role_id=role_id, emoji=emoji, category_id=category_id, cog=cog)
        )

    def yield_all_game_emojis(self):
        """Yield all game emojis."""
        for game in self.__games:
            yield Game(**self.__games[game]).emoji

    def emoji_to_game(self, emoji: int) -> Game:
        """Return the game that belongs to the emoji."""
        for game_name in self.__games:
            game = Game(**self.__games[game_name])
            if game.emoji == emoji:
                return game
        raise LookupError("Game not found")

    def yield_all_games(self) -> Game:
        """Yield all games."""
        for game in self.__games:
            yield self.get_game(game)

    def yield_game_cogs(self):
        """Yield all game_cogs."""
        for game_name in self.__games:
            game = Game(**self.__games[game_name])
            game_cog = game.cog
            if game_cog is not None:
                yield game_cog

    def command_has_config(self, command_name: str) -> bool:
        """Check if the command has a config."""
        return command_name in self.__commands

    def add_command_config(self, command_name: str, **kwargs):
        """
        Add a new command config.

        `kwargs` are the command options.
        Must be a class variable of `Command`.
        """
        if self.command_has_config(command_name):
            raise LookupError("Command already has a config!")
        else:
            self.__commands[command_name] = dataclasses.asdict(Command(**kwargs))

    def remove_command_config(self, command_name: str):
        if self.command_has_config(command_name):
            del self.__commands[command_name]
        else:
            raise LookupError("Command has no config!")

    def get_command(self, command_name: str) -> Command:
        """
        Return the config for a command.

        Raises `LookupError` if the command has no config.
        """
        if self.command_has_config(command_name):
            return Command(**self.__commands[command_name])
        else:
            raise LookupError("Command has no config")

    def get_category_ids(self, *role_names) -> list:
        """Return a list of all game channel category ids that matches role_names."""
        return [self.__games[game]["category_id"] for game in self.__games if game in role_names]

    def get_all_category_ids(self):
        """Yield all game channel category ids."""
        for game in self.__games:
            yield self.__games[game]["category_id"]

    # TODO Rewrite this
    def get_role_ids(self, *role_names) -> dict:
        role_ids = {
            "guest_id": self.unsorted_config.guest_id,
            "member_id": self.unsorted_config.member_id,
            "admin_id": self.unsorted_config.admin_id,
        }

        for game in self.__games:
            role_ids[game] = self.get_game(game).role_id

        for role_name in role_ids.keys():
            if role_name not in role_names:
                del role_ids[role_name]

        return role_ids
