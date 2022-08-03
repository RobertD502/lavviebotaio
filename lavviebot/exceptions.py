""" Exceptions for Lavviebot Client """

from typing import Any


class LavviebotError(Exception):
    """ Error from PurrSong Api """

    def __init__(self, *args: Any) -> None:
        """Initialize the exception."""
        Exception.__init__(self, *args)

class LavviebotAuthError(Exception):
    """ Authentication Error """

    def __init__(self, *args: Any) -> None:
        """Initialize the exception."""
        Exception.__init__(self, *args)