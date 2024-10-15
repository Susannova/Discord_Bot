from asyncio.log import logger
import dataclasses
from typing import List
from core.config.config_utility import auto_conversion, error_handling_auto_conversion


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

    temp_channel_prefix: List[str] = dataclasses.field(default_factory=list)
    temp_channel_suffix: List[str] = dataclasses.field(default_factory=list)
