import dataclasses
from typing import Tuple


@dataclasses.dataclass
class Command:
    """
    Representation of a command.

    Used for command specific options like the channel that the command is allowed in.
    """

    allowed_in_channel_ids: Tuple[int] = dataclasses.field(default_factory=tuple)
    allowed_in_channels: Tuple[str] = dataclasses.field(
        default_factory=tuple
    )  # Must be a name of the lists in channel_ids
    allowed_from_role_ids: Tuple[int] = dataclasses.field(default_factory=tuple)
    allowed_from_roles: Tuple[str] = dataclasses.field(
        default_factory=tuple
    )  # Must be the name of a role in unsorted config or a game role
    enabled: bool = True
