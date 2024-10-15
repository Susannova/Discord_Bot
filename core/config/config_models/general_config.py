import dataclasses
from typing import List


@dataclasses.dataclass
class GeneralConfig:
    super_user: List[int] = dataclasses.field(default_factory=list)

    discord_token: str = ""
    riot_token: str = ""

    riot_api: bool = False

    directory_temp_files: str = "./temp"

    log_file: str = "./log/log"
    config_file: str = "./config/configuration.json"

    folder_champ_icon: str = "./data/champ-icon/"
    folder_champ_spliced: str = "./data/champ-spliced/"

    database_directory_global_state: str = "./db/global_state"
    database_name_global_state: str = "global_state_db"

    database_directory_summoners: str = "./db/{guild_id}/summoners"
    database_name_summoners: str = "summoner_db"
