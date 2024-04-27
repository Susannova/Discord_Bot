import dataclasses
from core.config.config_utility import auto_conversion


@dataclasses.dataclass
class UnsortedConfig:
    """Some basic config."""

    admin_id: int = None
    member_id: int = None
    guest_id: int = None
    everyone_id: int = None

    command_prefix: str = "?"

    emoji_join: str = "✅"
    emoji_pass: str = "❎"

    riot_region: str = "euw1"

    play_now_time_add_limit: int = 120
    play_reminder_seconds: int = 60 * 5
    auto_delete_after_seconds: int = 60 * 60 * 10

    # TODO Move this stuff in an own class
    game_selector_id: int = None

    def __post_init__(self):
        """
        Try to convert false types to the right type.

        Raises a `TypeError` if conversion fails.
        """
        for field in dataclasses.fields(self):
            auto_conversion(self, field)
