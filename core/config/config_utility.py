"""
Used for the bot configuration.

If not imported, this can also be used to generate a config file.
Therefore, you need to modify the code at the bottom of the file
and run this file.
"""

import logging
import dataclasses

logger = logging.getLogger(__name__)


def auto_conversion(obj, field: dataclasses.Field):
    """
    Try to convert the field to the right type.

    Raise a `TypeError` if conversion fails.
    """
    field_val = getattr(obj, field.name)
    if field_val is not None and not isinstance(field_val, field.type):
        try:
            setattr(obj, field.name, field.type(field_val))
        except TypeError as error:
            error_handling_auto_conversion(obj, field, error)


def error_handling_auto_conversion(obj, field: dataclasses.Field, error: Exception):
    """
    Log an error during the conversion of a field.

    Raises a `TypeError` with an explanation.
    """
    error_message = (
        f"{field.name} is a {type(getattr(obj, field.name))} but should be a {field.type}. Not all settings are set."
    )
    logger.error("%s. Python error text: %s", error_message, error)
    raise TypeError(error_message)
