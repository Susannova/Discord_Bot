import logging
import dataclasses
import json
from typing import List

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class Game:
    """ Represents a game. A game has a long and a short name, belongs to a discord role and category and an emoji """
    name_short: str
    name_long: str
    role_id: int
    emoji: str
    category_id: int


@dataclasses.dataclass
class Toggles:
    auto_delete: bool = False
    command_only: bool = False
    auto_react: bool = False
    auto_dm: bool = False
    riot_api: bool = False
    debug: bool = False
    game_selector: bool = False
    summoner_rank_history: bool = False
    check_LoL_patch: bool = False


@dataclasses.dataclass
class Messages_Config:
    """ Configuration data of the messages from the bot """
    create_internal_play_request: str = '@everyone Das Play-Request von {creator} hat 6 oder mehr Mitspieler. Ein **__internes Match__** wird aufgebaut!\nEs sind noch **__{free_places}__** Plätze frei. \nUhrzeit: {time} Uhr \nSpieler:\n'
    auto_dm_creator: str = '{player} hat auf dein Play-Request reagiert: {reaction} '
    auto_dm_subscriber: str = '{player} hat auch auf das Play-Request von {creator} reagiert: {reaction} '
    play_now: str = '{role_mention}\n{creator} spielt **__jetzt gerade__** **{game}** und sucht noch nach weiteren Spielern!'
    play_at: str = '{role_mention}\n{player} will **{game}** spielen. Kommt gegen **__{time}__** Uhr online!'
    play_request_reminder: str = 'REMINDER: Der abonnierte Play-Request geht in 5 Minuten los!'
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
    """ Some basic config """

    admin_id: int = None
    member_id: int = None
    guest_id: int = None
    everyone_id: int = None

    lol_patch: str = ''  # TODO Move to global state

    guild_id: int = None

    command_prefix: str = '?'

    emoji_join: str = '✅'
    emoji_pass: str = '❎'

    riot_region: str = 'euw1'

    play_now_time_add_limit: str = 120


@dataclasses.dataclass
class Channel_Ids:
    """ Channel id lists """

    category_temporary: str = None

    create_team_voice: List[str] = dataclasses.field(default_factory=list)
    play_request: List[str] = dataclasses.field(default_factory=list)
    bot: List[str] = dataclasses.field(default_factory=list)
    member_only: List[str] = dataclasses.field(default_factory=list)
    commands_member: List[str] = dataclasses.field(default_factory=list)
    commands: List[str] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class Folders_and_Files:
    """ Global folder and files for the guild. Some needs to be formated with the guild_id! """

    folder_champ_icon: str = './data/{guild_id}/champ-icon/'
    folder_champ_spliced: str = './data/{guild_id}/champ-spliced/'

    database_directory_summoners: str = './db/{guild_id}/summoners'
    database_name_summoners: str = 'summoner_db'
    database_directory_global_state: str = './db/{guild_id}/global_state'
    database_name_global_state: str = 'global_state_db'

class GuildConfig():
    """Configuration for the guild """

    def __init__(self, guild_id: int):
        self.unsorted_config = UnsortedConfig()
        self.messages = Messages_Config()
        self.channel_ids = Channel_Ids()
        self.folders_and_files = Folders_and_Files()
        self.toggles = Toggles()

    # Dict of classes Game. Use the add and get functions to modify this.
        self.__games = {}

        self.unsorted_config.guild_id = guild_id

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

    def fromdict(self, config_dict):
        """ Sets the settings given by a dict. The format of the dictionary must be like in self.asdict().
        Settings not given in the dict are set to default """
        if "unsorted_config" in config_dict:
            self.unsorted_config = UnsortedConfig(**config_dict["unsorted_config"])
        if "messages" in config_dict:
            self.messages = Messages_Config(**config_dict["messages"])
        if "channel_ids" in config_dict:
            self.channel_ids = Channel_Ids(**config_dict["channel_ids"])
        if "folder_and_files" in config_dict:
            self.folders_and_files = Folders_and_Files(**config_dict["folder_and_files"])
        if "toggles" in config_dict:
            self.toggles = Toggles(**config_dict["toggles"])
        if "games" in config_dict:
            self.__games = config_dict["games"]

    def get_game(self, game_short_name: str) -> Game:
        """ Returns a Game class that belongs to the short name of a game """
        if game_short_name in self.__games:
            game_dict = self.__games[game_short_name]
            return Game(name_short=game_short_name, **game_dict)
        else:
            raise LookupError("Game not found")

    def add_game(self, game: str, long_name: str, role_id: int, emoji: str, category_id: int):
        """ Adds a new game to the bot """

        # The asdict prevents one from create a dict that is invalid to Game
        self.__games[game] = dataclasses.asdict(Game(game, long_name, role_id, emoji, category_id))
    
    def emoji_to_game(self, emoji: str) -> Game:
        for game in self.__games:
            if game.emoji == emoji:
                return game
        
        raise LookupError("Game not found")

    def get_all_category_ids(self, *role_names) -> list:
        return [game["category_id"] for game in self.__games if game in role_names]
    
    def get_role_ids(self, *role_names) -> dict:
        role_ids = {
            "guest": self.unsorted_config.guest_id,
            "member": self.unsorted_config.member_id,
            "admin": self.unsorted_config.admin_id
        }

        for game in self.__games:
            role_ids[game] = self.get_game(game).role_id
        
        for role_name in role_names:
            del role_ids[role_name]
        return role_ids


@dataclasses.dataclass
class GeneralConfig:
    discord_token: str = ''
    riot_token: str = ''

    log_file: str = './log/log'
    config_file: str = './config/configuration.json'


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
        """ Sets the settings given by a dict. The format of the dictionary must be like in self.asdict().
        Settings not given in the dict are set to default """
        self.general_config = GeneralConfig(**config_dict["general_config"])
        for guild in config_dict["guilds_config"]:
            if guild not in self.__guilds_config:
                self.add_new_guild_config(guild)
            self.get_guild_config(guild).fromdict(config_dict)

    def write_config_to_file(self, filename: str = None):
        """ Write the config to the config file """
        if filename is None:
            filename = self.general_config.config_file

        with open(filename, 'w') as json_file:
            json.dump(self.asdict(), json_file)
        logger.info("Saved the config to %s",
                    filename)  

    def update_config_from_file(self):
        try:
            config_dict = json.load(open(self.general_config.config_file, 'r'))
            self.fromdict(config_dict)
        except FileNotFoundError:
            logger.warning("File '%s' does not exist. All settings are set to default.", self.general_config.config_file)

    def add_new_guild_config(self, guild_id: str):
        """ Adds a new guild config """ 
        if guild_id in self.__guilds_config:
            raise LookupError("Guild already has a config!")
        else:
            self.__guilds_config[guild_id] = GuildConfig(guild_id)

    def get_guild_config(self, guild_id: str) -> GuildConfig:
        return self.__guilds_config[guild_id]

    def check_if_guild_exists(self, guild_id: str) -> bool:
        return True if guild_id in self.__guilds_config else False

if __name__ == "__main__":
    general_config = GeneralConfig(config_file="./test_config.json")
    bot_config = BotConfig(general_config)
    test_guild_id = "1234"
    if not bot_config.check_if_guild_exists(test_guild_id):
        bot_config.add_new_guild_config(test_guild_id)
    else:
        print("Guild does exist!")
    print(bot_config.get_guild_config(test_guild_id))
    bot_config.write_config_to_file()

    bot_config2 = BotConfig(general_config)
    bot_config2.get_guild_config(test_guild_id).unsorted_config.command_prefix = "!"
    bot_config2.write_config_to_file("./test_config2.json")
