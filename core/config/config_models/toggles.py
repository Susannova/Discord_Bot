import dataclasses

from core.config.config_utility import auto_conversion


@dataclasses.dataclass
class Toggles:
    """A class for toggles."""

    debug: bool = False
    game_selector: bool = False
    summoner_rank_history: bool = False
    leaderboard_loop: bool = False
    check_LoL_patch: bool = False
    highlights: bool = False
    welcome_message: bool = False

    # deprecated but need to be manually deleted from config before deleting from this class
    auto_delete: bool = False
    command_only: bool = False
    auto_react: bool = False
    auto_dm: bool = False

    def __post_init__(self):
        """
        Check if the type of the fields are valid and converts them if not.

        Raises a `TypeError` if conversion fails.
        """
        for field in dataclasses.fields(self):
            auto_conversion(self, field)
