import logging
import dataclasses
import json

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
class Basic_Config:
    """ Some basic config """
    lol_patch: str = ''  # Move to global state

    discord_token: str = ''
    riot_token: str = ''

    command_prefix: str = '?'

    emoji_join: str = '✅'
    emoji_pass: str = '❎'

    riot_region: str = 'euw1'

    play_now_time_add_limit: str = 120

    admin_id: int
    member_id: int
    guest_id: int
    everyone_id: int


@dataclasses.dataclass
class Channel_Ids:
    """ Channel id lists """
    create_team_voice: list = dataclasses.field(default_factory=list)
    play_request: list = dataclasses.field(default_factory=list)
    bot: list = dataclasses.field(default_factory=list)
    member_only: list = dataclasses.field(default_factory=list)
    commands_member: list = dataclasses.field(default_factory=list)
    commands: list = dataclasses.field(default_factory=list)
    
    category_temporary: int


@dataclasses.dataclass
class Folders_and_Files:
    """ Global folder and files used by the bot """
    config_file: str = 'config_test.json'
    folder_champ_icon: str = './data/champ-icon/'
    folder_champ_spliced: str = './data/champ-spliced/'

    database_directory_summoners: str = './db/summoners'
    database_name_summoners: str = 'summoner_db'
    database_directory_global_state: str = './db/global_state'
    database_name_global_state: str = 'global_state_db'

    log_file: str = './log/log'


class Config():
    """Configuration of the bot"""
    basic_config: Basic_Config
    messages: Messages_Config
    channel_ids: Channel_Ids
    folders_and_files: Folders_and_Files
    toggles: Toggles
    # Dict of classes Game. Use the add and get functions to modify this.
    __games: dict

    def __init__(self, filename: str):
        self.set_all_settings()

        if filename:
            self.update_config_from_file(filename)

    def __del__(self):
        self.save_config()

    def set_all_settings(self, basic_config=Basic_Config(), messages=Messages_Config(), channel_ids=Channel_Ids(), folders_and_files=Folders_and_Files(), games={}, toggles=Toggles()):
        self.basic_config = basic_config
        self.messages = messages
        self.channel_ids = channel_ids
        self.folders_and_files = folders_and_files
        self.__games = games
        self.toggles = toggles

    def all_settings_as_dict(self) -> dict:
        """ Returns all settings as a dict """
        return {
            "basic_config": dataclasses.asdict(self.basic_config),
            "messages": dataclasses.asdict(self.messages),
            "channel_ids": dataclasses.asdict(self.channel_ids),
            "folders_and_files": dataclasses.asdict(self.folders_and_files),
            "games": self.__games,
            "toggles": dataclasses.asdict(self.toggles)
        }

    def update_config_category(self, config_old: dict, config_new: dict):
        """Replaces settings of the old config with the new. Settings not set in new are left as is"""

        for key in config_new:
            config_old[key] = config_new[key]

    def update_config_from_file(self, filename: str = ""):
        """ Sets all settings to default and updates the settings given in the file """

        if not filename:
            filename = self.folders_and_files.config_file

        reset_class = Config("")

        all_settings_reset_class = reset_class.all_settings_as_dict()
        all_settings_as_dict = self.all_settings_as_dict()

        # Reset all settings
        for category in all_settings_reset_class:
            all_settings_as_dict[category] = all_settings_reset_class[category]

        # Updates settings
        with open(filename, 'r') as config_new_file:
            config_new = json.load(config_new_file)
            for category in config_new:
                if category not in all_settings_as_dict:
                    raise "Category unknown"
                else:
                    self.update_config_category(
                        all_settings_as_dict[category], config_new[category])

        # Set the settings
        self.set_all_settings(
            basic_config=Basic_Config(**all_settings_as_dict["basic_config"]),
            messages=Messages_Config(**all_settings_as_dict["messages"]),
            channel_ids=Channel_Ids(**all_settings_as_dict["channel_ids"]),
            folders_and_files=Folders_and_Files(
                **all_settings_as_dict["folders_and_files"]),
            games=all_settings_as_dict["games"],
            toggles=Toggles(**all_settings_as_dict["toggles"])
        )

    def save_config(self):
        """ Save the config to the config file """
        with open(self.folders_and_files.config_file, 'w') as json_file:
            json.dump(self.all_settings_as_dict(), json_file)
        logger.info("Saved the config to %s",
                    self.folders_and_files.config_file)

    def get_game(self, game_short_name: str) -> Game:
        """ Returns a Game class that belongs to the short name of a game """
        if game_short_name in self.__games:
            game_dict = self.__games[game_short_name]
            return Game(name_short=game_short_name, **game_dict)
        else:
            raise "Game not found"

    def add_game(self, game: str, long_name: str, role_id: int, emoji: str, category_id: int):
        """ Adds a new game to the bot """

        # The asdict prevents one from create a dict that is invalid to Game
        self.__games[game] = dataclasses.asdict(Game(game, long_name, role_id, emoji, category_id))
    
    def emoji_to_game(self, emoji: str) -> Game:
        for game in self.__games:
            if game.emoji == emoji:
                return game
        
        raise "Game not found"

    def get_all_category_ids(self) -> list:
        return [game["category_id"] for game in self.__games]

# Todo Has to be a singleton!
CONFIG = Config("")

# CONFIG.add_game("LoL", "League of Legends", 42)
# CONFIG.save_config()

# CONFIG2 = Config(CONFIG.folders_and_files.config_file)
# CONFIG2.folders_and_files.config_file = "config2.json"
