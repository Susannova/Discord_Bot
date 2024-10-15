import dataclasses
from typing import Optional

from core.config.config_utility import auto_conversion


@dataclasses.dataclass
class Game:
    """
    Representation of a game.

    A game has a long and a short name,
    belongs to a discord role and category and an emoji.
    It can also have its own cog.
    """

    name_short: str
    name_long: str
    role_id: int
    emoji: int
    category_id: int  # Sets the category to the "Games" category by default
    cog: Optional[str] = None

    def __post_init__(self):
        """
        Check if the types are valid and tries to convert the fields if not.

        Raises a `TypeError` if conversion fails.
        """
        for field in dataclasses.fields(self):
            auto_conversion(self, field)
