""" Used for the bot configarution. If not imported, this can also be used to generate
a config file. Therefore you need to modify the code at the bottom of the file and run
this file"""

import logging
import dataclasses
import json
import typing
import os
from typing import List, Tuple

logger = logging.getLogger(__name__)

def update_recursive(old_dict: dict, update_dict: dict):
    """ Updates old_dict with update_dict

    old_dict -- The dict that will be updated
    update_dict -- The dict to update from
    """
    for key in update_dict:
        if key in old_dict and isinstance(update_dict[key], dict):
            update_recursive(old_dict[key], update_dict[key])
        else:
            old_dict[key] = update_dict[key]

def auto_conversion(obj, field: dataclasses.Field):
    """ Tries to convert the field to the right type

    Raises a TypeError if conversion fails.

    obj -- The obj the field belongs to
    field -- The field to check
    """
    field_val = getattr(obj, field.name)
    if not field_val is None and not isinstance(field_val, field.type):
        try:
            setattr(obj, field.name, field.type(field_val))
        except TypeError as error:
            error_handling_auto_conversion(obj, field, error)

def error_handling_auto_conversion(obj, field: dataclasses.Field, error: Exception):
    """ Logs a error during the conversion of a field and raises a TypeError with an explaination """
    error_message = f"{field.name} is a {type(getattr(obj, field.name))} but should be a {field.type}. Not all settings are set."
    logger.error("%s. Python error text: %s", error_message, error)
    raise TypeError(error_message)

def check_if_channel_id_valid(channel_id: int, valid_ids: List) -> bool:
    """ Checks if a channel_id is valid

    Returns True if channel_id is valid and false otherwise.
    """

    if channel_id is not None and channel_id not in valid_ids:
        return False
    else:
        return True

@dataclasses.dataclass
class Command:
    """Represent a command

    Used for command specific options like the channel that the command is allowed in
    """

    allowed_in_channel_ids: Tuple[int] = dataclasses.field(default_factory=tuple)
    allowed_in_channels: Tuple[str] = dataclasses.field(default_factory=tuple) # Must be a name of the lists in channel_ids
    allowed_from_role_ids: Tuple[int] = dataclasses.field(default_factory=tuple)
    allowed_from_roles: Tuple[str] = dataclasses.field(default_factory=tuple) #  Must be the name of a role in unsorted config or a game role
    enabled: bool = True

    # TODO Does not work!!!
    # def __post_init__(self):
    #     """ Checks if the types are valid and tries to convert the fields if not

    #     Raises an TypeError if conversion fails """
        
    #     for field in dataclasses.fields(self):
    #         auto_conversion(self, field)


@dataclasses.dataclass
class Game:
    """ Represents a game.

    A game has a long and a short name,
    belongs to a discord role and category and an emoji. It also can have its own cog! """
    name_short: str
    name_long: str
    role_id: int
    emoji: int
    category_id: int
    cog: str = None

    def __post_init__(self):
        """ Checks if the types are valid and tries to convert the fields if not

        Raises an TypeError if conversion fails """
        
        for field in dataclasses.fields(self):
            auto_conversion(self, field)


@dataclasses.dataclass
class Toggles:
    """ A class for toggles
    
    A post init function checks if the toggles are booleans or not
    """

    auto_delete: bool = False
    command_only: bool = False
    auto_react: bool = False
    auto_dm: bool = False
    debug: bool = False
    game_selector: bool = False
    summoner_rank_history: bool = False
    leaderboard_loop: bool = False
    check_LoL_patch: bool = False
    highlights: bool = False

    def __post_init__(self):
        """ Checks if the type of the fields are valid and converts them if not.

        Raises a TypeError if conversion fails """
        for field in dataclasses.fields(self):
            auto_conversion(self, field)


@dataclasses.dataclass
class Messages_Config:
    """ Configuration data of the messages from the bot """
    date_format: str = '{day}.{month}.'
    create_internal_play_request: str = '@everyone Das Play-Request von {creator} hat 6 oder mehr Mitspieler. Ein **__internes Match__** wird aufgebaut!\nEs sind noch **__{free_places}__** Plätze frei. \nUhrzeit: {time} Uhr \nSpieler:\n'
    auto_dm_creator: str = '{player} hat auf dein Play-Request reagiert: {reaction} '
    auto_dm_subscriber: str = '{player} hat auch auf das Play-Request von {creator} reagiert: {reaction} '
    play_now: str = '{role_mention}\n{creator} spielt **__jetzt gerade__** **{game}** und sucht noch nach weiteren Spielern!'
    play_at: str = '{role_mention}\n{player} will **{game}** spielen. Kommt {date_str} um **__{time}__** Uhr online!'
    play_at_date: str = 'am **__{date}__**'
    play_request_reminder: str = 'REMINDER: Der abonnierte Play-Request geht in {minutes} Minuten los!'
    clash_create = '{role_mention}\n{player} sucht nach Mitspielern für den LoL Clash am {date}.'
    clash_full: str = 'Das Clash Team von {creator} für den {time} ist jetzt voll. Das Team besteht aus folgenden Mitgliedern:\n{team}'

    bans: str = (
        'If you want to receive the best bans \
                for the scouted team copy the following Command: \n \
                {command_prefix}bans {team}'
    )

    team_header: str = '\n**__===Teams===__**\n'
    team_1: str = 'Team 1:\n'
    team_2: str = '\nTeam 2:\n'

    patch_notes_formatted: str = '{role_mention}\nEin neuer Patch ist da: {patch_note}'
    patch_notes: str = "https://euw.leagueoflegends.com/en-us/news/game-updates/patch-{0}-{1}-notes/"

    game_selector: str = "@everyone\nWähle hier durch das Klicken auf eine Reaktion aus zu welchen Spielen du Benachrichtungen erhalten willst!"

    highlight_leaderboard_description: str = "Vote for the best highlights in {highlight_channel_mention}."
    highlight_leaderboard_footer: str = "Only the last {limit} highlights can be taken in account."
    place: str = "Place"

@dataclasses.dataclass
class UnsortedConfig:
    """ Some basic config
    
    A post init function checks the types of the fields and tries to convert them.
    """

    admin_id: int = None
    member_id: int = None
    guest_id: int = None
    everyone_id: int = None

    command_prefix: str = '?'

    emoji_join: str = '✅'
    emoji_pass: str = '❎'

    riot_region: str = 'euw1'

    play_now_time_add_limit: int = 120
    play_reminder_seconds: int = 60 * 5
    auto_delete_after_seconds: int = 60 * 60 * 10

    # TODO Move this stuff in an own class
    game_selector_id: int = None

    def __post_init__(self):
        """ Tries to convert false types to the right type
        
        Raises an TypeError if conversion fails """

        for field in dataclasses.fields(self):
            auto_conversion(self, field)



@dataclasses.dataclass
class Channel_Ids:
    """ Channel id lists

    All attributes have to be ints or list of ints
    """

    category_temporary: int = None

    plots: int = None
    announcement: int = None
    team_1: int = None
    team_2: int = None
    play_request: int = None

    create_team_voice: List[int] = dataclasses.field(default_factory=list)
    bot: List[int] = dataclasses.field(default_factory=list)
    member_only: List[int] = dataclasses.field(default_factory=list)
    commands_member: List[int] = dataclasses.field(default_factory=list)
    commands: List[int] = dataclasses.field(default_factory=list)
    highlights: List[int] = dataclasses.field(default_factory=list)

    def __post_init__(self):
        """ Checks if the types are valid and tries to convert them if not

        At first all str or list of str are casted to ints or list of ints.
        After that the atttribute is casted to the right type.
        Raises a TypeError if casting fails.
        """

        for field in dataclasses.fields(self):
            field_val = getattr(self, field.name)
            
            if field_val is None or field_val == []:
                continue

            # Check if field is a str or a list of str and convert it to int or list of ints
            try:
                if isinstance(field_val, str):
                    setattr(self, field.name, int(field_val))
                elif isinstance(field_val, list):
                    for elem in field_val:
                        if isinstance(elem, str):
                            setattr(self, field.name, int(field_val))

                #Check if type is right and tries to convert to the right type if not
                desired_type = field.type if not field.type is List[int] else list
                field_val = getattr(self, field.name)
                if not isinstance(field_val, desired_type):
                    logger.warning("Type of %s is %s. Try to convert it to %s", field.name, type(field_val), desired_type)
                    if desired_type is list and not isinstance(field_val, list):
                        setattr(self, field.name, [field_val])
                    else:
                        setattr(self, field.name, desired_type(field_val))
            except TypeError as error:
                error_handling_auto_conversion(self, field, error)
                
        
        logger.debug("Post_init finished")

    def yield_all_channel_ids(self):
        """ Yields all channel ids """
        for elem in dataclasses.astuple(self):
            if isinstance(elem, list):
                for channel_id in elem:
                    yield channel_id
            else:
                yield elem

@dataclasses.dataclass
class Folders_and_Files:
    # TODO Can be replaced with a class 'message_ids' because this is not needed anymore
    """ Global folder and files for the guild. Some needs to be formated with the guild_id! """
    pass

class GuildConfig():
    """Configuration for the guild """

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
        """ Returns all settings as a dict """
        return {
            "unsorted_config": dataclasses.asdict(self.unsorted_config),
            "messages": dataclasses.asdict(self.messages),
            "channel_ids": dataclasses.asdict(self.channel_ids),
            "folders_and_files": dataclasses.asdict(self.folders_and_files),
            "toggles": dataclasses.asdict(self.toggles),
            "games": self.__games,
            "commands": self.__commands
        }
    
    def fromdict(self, config_dict, update: bool = False):
        """ Sets the settings given by a dict. The format of the dictionary must be like in self.asdict().
        
        config_dict -- The dict to set the config from
        update -- If false, settings not given in the dict are set to default (default)
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
        """ Checks and deletes ids that are not in valid_ids and yields tuples of the deleted id and its category"""

        is_invalid = False
        channel_ids_dict = dataclasses.asdict(self.channel_ids)

        # TODO Rewrite: A lot of copy paste
        for key in channel_ids_dict:
            if isinstance(channel_ids_dict[key], list):
                for channel_id in channel_ids_dict[key]:
                    if not check_if_channel_id_valid(channel_id, valid_ids):
                        is_invalid = True
                        yield (key, channel_id)
                        channel_ids_dict[key].remove(channel_id)
            elif not check_if_channel_id_valid(channel_ids_dict[key], valid_ids):
                is_invalid = True
                yield (key, channel_ids_dict[key])
                channel_ids_dict[key] = None
        
        if is_invalid:
            self.channel_ids = Channel_Ids(**channel_ids_dict)

    def game_exists(self, game_short_name: str) -> bool:
        return game_short_name in self.__games

    def get_game(self, game_short_name: str) -> Game:
        """ Returns a Game class that belongs to the short name of a game """
        if self.game_exists(game_short_name):
            game_dict = self.__games[game_short_name]
            return Game(**game_dict)
        else:
            raise LookupError("Game not found")

    def yield_all_game_role_ids(self):
        for game in self.__games:
            yield Game(**self.__games[game]).role_id

    def add_game(self, game: str, long_name: str, role_id: int, emoji: int, category_id: int, cog: str = None):
        """ Adds a new game to the bot """

        # The asdict prevents one from create a dict that is invalid to Game
        self.__games[game] = dataclasses.asdict(Game(name_short=game, name_long=long_name, role_id=role_id, emoji=emoji, category_id=category_id, cog=cog))
    
    def get_all_game_emojis(self):
        """ Yields all game emojis """
        for game in self.__games:
            yield Game(**self.__games[game]).emoji

    def emoji_to_game(self, emoji: int) -> Game:
        """ Returns the game that belongs to the emoji """
        for game_name in self.__games:
            game = Game(**self.__games[game_name])
            if game.emoji == emoji:
                return game
        
        raise LookupError("Game not found")

    def yield_all_games(self) -> Game:
        """ Yields all games """
        for game in self.__games:
            yield self.get_game(game)
            

    def yield_game_cogs(self):
        """ Yields all game_cogs """
        for game_name in self.__games:
            game = Game(**self.__games[game_name])
            game_cog = game.cog
            if game_cog is not None:
                yield game_cog
    
    def command_has_config(self, command_name: str) -> bool:
        """Checks if the command has a config

        Args:
            command_name (str): The command name

        Returns:
            bool: True if the command has a config
        """
        return command_name in self.__commands

    def add_command_config(self, command_name: str, **kwargs):
        """Adds a new command config

        Args:
            command_name (str): The name of the command
            kwargs: The command options. Must be a class variable of Command
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
        """Return the config for a command

        Args:
            command_name (str): The command name

        Raises:
            LookupError: If the command has no config

        Returns:
            Command: The config for the command
        """
        if self.command_has_config(command_name):
            return Command(**self.__commands[command_name])
        else:
            raise LookupError("Command has no config")

    def get_category_ids(self, *role_names) -> list:
        """ Returns a list of all game channel category ids that matches role_names """
        return [self.__games[game]["category_id"] for game in self.__games if game in role_names]

    def get_all_category_ids(self):
        """ Yields all game channel category ids """
        for game in self.__games:
            yield self.__games[game]["category_id"]
    
    #TODO Rewrite this
    def get_role_ids(self, *role_names) -> dict:
        role_ids = {
            "guest_id": self.unsorted_config.guest_id,
            "member_id": self.unsorted_config.member_id,
            "admin_id": self.unsorted_config.admin_id
        }

        for game in self.__games:
            role_ids[game] = self.get_game(game).role_id
        
        for role_name in [_role_name for _role_name in role_ids]:
            if role_name not in role_names:
                del role_ids[role_name]

        return role_ids


@dataclasses.dataclass
class GeneralConfig:
    super_user: List[int] = dataclasses.field(default_factory=list)

    discord_token: str = ''
    riot_token: str = ''

    riot_api: bool = False

    directory_temp_files: str = "./temp"

    log_file: str = './log/log'
    config_file: str = './config/configuration.json'

    folder_champ_icon: str = './data/champ-icon/'
    folder_champ_spliced: str = './data/champ-spliced/'

    database_directory_global_state: str = './db/global_state'
    database_name_global_state: str = 'global_state_db'

    database_directory_summoners: str = './db/{guild_id}/summoners'
    database_name_summoners: str = 'summoner_db'


class BotConfig:
    """ Configuration of the bot """

    def __init__(self, general_config=GeneralConfig(), *, config_file: str = None, update_config: bool = True):
        self.general_config = general_config
        self.__guilds_config = {}

        if config_file:
            general_config.config_file = config_file
        if update_config:
            self.update_config_from_file()
    
    def asdict(self) -> dict:
        """ Returns the general configs as a dict """
        config_dict = {
            "general_config": dataclasses.asdict(self.general_config),
            "guilds_config": {}
            }

        for guild in self.__guilds_config:
            config = self.get_guild_config(guild)
            config_dict["guilds_config"][guild] = config.asdict()
        return config_dict
    
    def fromdict(self, config_dict: dict):
        """ Sets the settings given by a dict. The format of the dictionary must be like in self.asdict()
        but the keys can be strings or integers.
        Settings not given in the dict are set to default """
        self.general_config = GeneralConfig(**config_dict["general_config"])
        for guild in config_dict["guilds_config"]:
            guild_int = int(guild)
            if guild_int not in self.__guilds_config:
                self.add_new_guild_config(guild_int)
            self.get_guild_config(guild_int).fromdict(config_dict["guilds_config"][guild])

    def write_config_to_file(self, filename: str = None, nice_format: bool = False):
        """ Write the config to the config file """
        if filename is None:
            filename = self.general_config.config_file

        with open(filename, 'w') as json_file:
            intent = "\t" if nice_format else None
            json.dump(self.asdict(), json_file, indent=intent)
        logger.info("Saved the config to %s",
                    filename)

    def update_config_from_file(self, filename = None):
        """ Updates the config from a file using fromdict """
        if filename is None:
            filename = self.general_config.config_file
        
        try:
            config_dict = json.load(open(filename, 'r'))
        except FileNotFoundError:
            logger.warning("File '%s' does not exist. All settings are set to default.", filename)
        
        self.fromdict(config_dict)
        logger.info("Settings were updated from file %s", filename)

    def add_new_guild_config(self,  guild_id: int) -> GuildConfig:
        """ Adds a new guild config and returns the config"""

        if guild_id in self.__guilds_config:
            raise LookupError("Guild already has a config!")
        else:
            self.__guilds_config[guild_id] = GuildConfig()
            logger.info("We have added the guild %s to the config!", guild_id)
        
        return self.__guilds_config[guild_id]
    
    def remove_guild_config(self,  guild_id: int):
        """ Remove a guild config """ 
        if guild_id not in self.__guilds_config:
            raise LookupError("Guild does not exists!")
        else:
            del self.__guilds_config[guild_id]
            logger.info("We have removed the guild %s from the config!", guild_id)
    
    def get_guild_config(self, guild_id: int) -> GuildConfig:
        """ Gets the guild that belongs to the id. Raises an key error if guild does not exists """
        try:
            return self.__guilds_config[guild_id]
        except KeyError:
            logger.warning("Guild %s is unknown", guild_id)
            raise
    
    def check_if_guild_exists(self,  guild_id: int) -> bool:
        """ Checks if a guild exists in the config """
        return True if guild_id in self.__guilds_config else False
    
    def get_all_guild_ids(self) -> list:
        """ Returns a list with every guild id """
        return [guild_id for guild_id in self.__guilds_config]

def is_Y(input: str) -> bool:
    if input == "Y":
        return True
    elif input == "N":
        return False
    else:
        raise RuntimeError("Enter Y or N")

if __name__ == "__main__":
    config_file = input("Please enter the path to the config file. This is just needed if you want to check new options. The bot will only find the config in the default path. If you enter no path, the default path will be taken. ")
    config_file = config_file if config_file else "../config/configuration.json"

    reset = is_Y(input("Do you want to reset the config? [Y/N] "))
    file_exists = os.path.exists(config_file)
    if not file_exists and not reset:
        if not is_Y(input("The config file does not exists! Do you want to create a new one?")):
            exit(1)
        else:
            reset = True

    bot_config = BotConfig(config_file=config_file, update_config=not reset)

    
    discord_token = input("Please enter your discord token. Leave empty if the config already has an discord token: ")
    if discord_token or reset:
        bot_config.general_config.discord_token = discord_token
    
    riot_api = is_Y(input("Do you want to enable the riot api? You need a riot api key to do so. [Y/N] "))
    if riot_api:
        riot_token = input("Please enter your riot api key. Leave empty to not change the key: ")
        if not riot_token and not bot_config.general_config.riot_token:
            print("No riot api key. Disable riot api")
            riot_api = False
        else:
            bot_config.general_config.riot_api = True
            bot_config.general_config.riot_token = riot_token

    while True:
        new_guild_id_str = input("Please enter a guild id. Enter nothing to stop: ")
        if not new_guild_id_str:
            break
        new_guild_id = int(new_guild_id_str)
        if bot_config.check_if_guild_exists(new_guild_id):
            if is_Y(input("Guild does already exist! Do you want to reset the settings of this guild?")):
                bot_config.remove_guild_config(new_guild_id)
            else:
                continue

        bot_config.add_new_guild_config(new_guild_id)
        guild_config = bot_config.get_guild_config(new_guild_id)

        while True:
            command_prefix = str(input("Please insert a command string to call a command. Leave empty to leave unchanged: "))
            if command_prefix == "<":
                print("Sorry this is forbidden by Discord...")
            else:
                break
        if command_prefix:
            guild_config.unsorted_config.command_prefix = command_prefix
        
        if bot_config.general_config.riot_api:
            guild_config.unsorted_config.riot_region = str(input("Please insert your riot region. Example for Europe west: 'euw1': "))

        everyone_id =  int(input("Please insert the id of the role that belongs to everyone. Leave empty to leave unchanged: "))
        guest_id =  int(input("Please insert the id of the role that belongs to guests of the server. Leave empty to leave unchanged: "))
        member_id =  int(input("Please insert the id of the role that belongs to members of the server. Leave empty to leave unchanged: "))
        admin_id =  int(input("Please insert the id of the role that can configure the bot. Leave empty to leave unchanged: "))
        
        if everyone_id:
            guild_config.unsorted_config.everyone_id
        if guest_id:
            guild_config.unsorted_config.guest_id
        if member_id:
            guild_config.unsorted_config.member_id
        if admin_id:
            guild_config.unsorted_config.admin_id
        

        while True:
            game_name_short = input("Please enter a short name for a game (Example: 'LoL' for 'League of Legends'). Enter nothing to stop: ")
            if not game_name_short:
                break
            elif guild_config.game_exists(game_name_short):
                print("That game already exists!")
                continue
            else:
                long_name = input("\tPlease enter the full name for the game: ")
                role_id = int(input("\tPlease enter the id of the discord role that belongs to the game: "))
                emoji_id = int(input("\tPlease enter the id of the discord emoji that belongs to the game: "))
                category_id = int(input("\tPlease enter the id of a channel (category) of this game. "))
                cog_path = input("\tPlease enter the path to a cog of this game. Leave empty if there is no cog: ")
                cog_path = cog_path if cog_path else None
                guild_config.add_game(
                    game=game_name_short,
                    long_name=long_name,
                    role_id=role_id,
                    emoji=emoji_id,
                    category_id=category_id,
                    cog=cog_path
                )
                print(long_name, "was added to the guild config")
        print("")

        if not guild_config.command_has_config("purge"):
            guild_config.add_command_config(command_name="purge", enabled=True, allowed_from_roles=("admin_id",))

        while True:
            command = input("Please enter a command that should be configured: ")
            if not command:
                break
            elif guild_config.command_has_config(command):
                if is_Y(input("The command already has a config. Do you want to delete the config and create a new one? [Y/N] ")):
                    guild_config.remove_command_config(command)
                else:
                    continue
            game_config = {}
            
            disabled = is_Y(input("Do you want to disable this command? [Y/N] "))
            if disabled:
                game_config["enabled"] = False
            else:
                game_config["enabled"] = True

                print("For the next options, you can leave the option empty to not use the option.")

                valid_channel_names = [field.name for field in dataclasses.fields(Channel_Ids)]
                channel_names = input(
                        f"The config groups some channels. Enter the names for the channel groups in that the command should be allowed. Seperate names by a space character. Valid names are {', '.join(valid_channel_names)}. Invalid names are ignored without a warning: "
                    ).split(" ")
                allowed_in_channels = [
                    str(channel) for channel in channel_names if str(channel) in valid_channel_names
                ]
                if allowed_in_channels:
                    game_config["allowed_in_channels"] = allowed_in_channels

                allowed_in_channel_ids = [int(id) for id in input("Enter additional ids of the channels in that the command is allowed: ")]
                if allowed_in_channel_ids:
                    game_config["allowed_in_channel_ids"] = allowed_in_channel_ids
                
                allowed_from_roles = [str(role) for role in input(f"The config also groups some roles. Enter the names for the channel groups in that the command should be allowed. Valid names are admin_id, member_id, guest_id, everyone_id and the short name of a game: ")]
                if allowed_from_roles:
                    game_config["allowed_from_roles"] = allowed_from_roles

                allowed_from_role_ids = [int(id) for id in input("Enter ids of the roles that the command can use: ")]
                if allowed_from_role_ids:
                    game_config["allowed_from_role_ids"] = allowed_from_role_ids
        
            guild_config.add_command_config(command_name=command, **game_config)
            print("Command added!")
        
        print("\nFinished with guild config\n")

    bot_config.write_config_to_file(nice_format=True)

    print(f"Config was written to:'{bot_config.general_config.config_file}'. You can configure the bot even more  in this file.")