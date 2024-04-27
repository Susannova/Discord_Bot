import dataclasses
from typing import List
import logging

from core.config.config_utility import error_handling_auto_conversion

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class Channel_Ids:
    """
    A list of channel ids.

    All attributes have to be ints or list of ints.
    """

    category_temporary: int = None
    plots: int = None
    announcement: int = None
    team_1: int = None
    team_2: int = None
    play_request: int = None
    create_tmp_voice: int = None
    game_category: int = None
    bot: List[int] = dataclasses.field(default_factory=list)
    member_only: List[int] = dataclasses.field(default_factory=list)
    commands_member: List[int] = dataclasses.field(default_factory=list)
    commands: List[int] = dataclasses.field(default_factory=list)
    highlights: List[int] = dataclasses.field(default_factory=list)

    def __post_init__(self):
        """
        Check if the types are valid and tries to convert them if not.

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

                # Check if type is right and tries to convert to the right type if not
                desired_type = field.type if field.type is not List[int] else list
                field_val = getattr(self, field.name)
                if not isinstance(field_val, desired_type):
                    logger.warning(
                        "Type of %s is %s. Try to convert it to %s", field.name, type(field_val), desired_type
                    )
                    if desired_type is list and not isinstance(field_val, list):
                        setattr(self, field.name, [field_val])
                    else:
                        setattr(self, field.name, desired_type(field_val))
            except TypeError as error:
                error_handling_auto_conversion(self, field, error)

        logger.debug("Post_init finished")

    def yield_all_channel_ids(self):
        """Yield all channel ids."""
        for elem in dataclasses.astuple(self):
            if isinstance(elem, list):
                for channel_id in elem:
                    yield channel_id
            else:
                yield elem
