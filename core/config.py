""" Used for the bot configarution. If not imported, this can also be used to generate
a config file. Therefore you need to modify the code at the bottom of the file and run
this file"""

import logging
import dataclasses
import json
import typing
from typing import List

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

    def __post_init__(self):
        """ Checks if the type of the fields are valid and converts them if not.

        Raises a TypeError if conversion fails """
        for field in dataclasses.fields(self):
            auto_conversion(self, field)


@dataclasses.dataclass
class Messages_Config:
    """ Configuration data of the messages from the bot """
    create_internal_play_request: str = '@everyone Das Play-Request von {creator} hat 6 oder mehr Mitspieler. Ein **__internes Match__** wird aufgebaut!\nEs sind noch **__{free_places}__** Plätze frei. \nUhrzeit: {time} Uhr \nSpieler:\n'
    auto_dm_creator: str = '{player} hat auf dein Play-Request reagiert: {reaction} '
    auto_dm_subscriber: str = '{player} hat auch auf das Play-Request von {creator} reagiert: {reaction} '
    play_now: str = '{role_mention}\n{creator} spielt **__jetzt gerade__** **{game}** und sucht noch nach weiteren Spielern!'
    play_at: str = '{role_mention}\n{player} will **{game}** spielen. Kommt gegen **__{time}__** Uhr online!'
    play_request_reminder: str = 'REMINDER: Der abonnierte Play-Request geht in {minutes} Minuten los!'
    clash_create = '{role_mention}\n{player} sucht nach Mitspielern für den LoL Clash am {date}.'
    clash_full: str = 'Das Clash Team von {creator} für den {time} ist jetzt voll. Das Team besteht aus folgenden Mitgliedern:\n{team}'

    bans: str = (
        'If you want to receive the best bans \
                for the scouted team copy the following Command: \n \
                {command_prefix}bans {team}'
    )

    team_header: str = '\n@here\n**__===Teams===__**\n'
    team_1: str = 'Team 1:\n'
    team_2: str = '\nTeam 2:\n'

    patch_notes_formatted: str = '{role_mention}\nEin neuer Patch ist da: {patch_note}'
    patch_notes: str = "https://euw.leagueoflegends.com/en-us/news/game-updates/patch-{0}-{1}-notes/"

    game_selector: str = "@everyone\nWähle hier durch das Klicken auf eine Reaktion aus zu welchen Spielen du Benachrichtungen erhalten willst!"


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

    create_team_voice: List[int] = dataclasses.field(default_factory=list)
    play_request: List[int] = dataclasses.field(default_factory=list)
    bot: List[int] = dataclasses.field(default_factory=list)
    member_only: List[int] = dataclasses.field(default_factory=list)
    commands_member: List[int] = dataclasses.field(default_factory=list)
    commands: List[int] = dataclasses.field(default_factory=list)

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
        
        # Dict of classes Game. Use the add and get functions to modify this.
        self.__games = {}


    def asdict(self) -> dict:
        """ Returns all settings as a dict """
        return {
            "unsorted_config": dataclasses.asdict(self.unsorted_config),
            "messages": dataclasses.asdict(self.messages),
            "channel_ids": dataclasses.asdict(self.channel_ids),
            "folders_and_files": dataclasses.asdict(self.folders_and_files),
            "toggles": dataclasses.asdict(self.toggles),
            "games": self.__games
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

    def get_game(self, game_short_name: str) -> Game:
        """ Returns a Game class that belongs to the short name of a game """
        if game_short_name in self.__games:
            game_dict = self.__games[game_short_name]
            return Game(**game_dict)
        else:
            raise LookupError("Game not found")

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

    def yield_game_cogs(self):
        """ Yields all game_cogs """
        for game_name in self.__games:
            game = Game(**self.__games[game_name])
            game_cog = game.cog
            if game_cog is not None:
                yield game_cog

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

    riot_api: bool = True

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

    def __init__(self, general_config=GeneralConfig()):
        self.general_config = general_config
        self.__guilds_config = {}
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

    def write_config_to_file(self, filename: str = None):
        """ Write the config to the config file """
        if filename is None:
            filename = self.general_config.config_file

        with open(filename, 'w') as json_file:
            json.dump(self.asdict(), json_file)
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
    
    def get_guild_config(self,  guild_id: int) -> GuildConfig:
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

# if __name__ == "__main__":
#     bot_config = BotConfig()

#     bot_config.general_config.discord_token = ""

#     new_guild_id = None
    
#     if not bot_config.check_if_guild_exists(new_guild_id):
#         bot_config.add_new_guild_config(new_guild_id)
#     else:
#         print("Guild does exist!")

#     bot_config.get_guild_config(new_guild_id).channel_ids.bot.append(None)

#     bot_config.write_config_to_file("./configuration.json")