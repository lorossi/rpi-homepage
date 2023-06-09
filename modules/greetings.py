"""This module contains the Greeting class, used to represent a greeting."""
from __future__ import annotations


class Greeting:
    """Greeting class, used to represent a greeting."""

    def __init__(self, from_hour: int, to_hour: int, message: str) -> Greeting:
        """Greeting class, used to represent a greeting.

        Args:
            from_hour (int): starting hour of the greeting
            to_hour (int): ending hour of the greeting
            message (str): the greeting

        Returns:
            Greeting
        """
        self._from_hour = from_hour
        self._to_hour = to_hour
        self._message = message

    def isInTime(self, hour: int) -> bool:
        """Check if the current hour is in the greeting time.

        Args:
            hour (int): the current hour
        """
        return self._from_hour <= hour <= self._to_hour

    @property
    def from_hour(self) -> int:
        """Get the starting hour of the greeting.

        Returns:
            int
        """
        return self._from_hour

    @property
    def to_hour(self) -> int:
        """Get the ending hour of the greeting.

        Returns:
            int
        """
        return self._to_hour

    @property
    def message(self) -> str:
        """Get the greeting.

        Returns:
            str
        """
        return self._message

    @staticmethod
    def fromDict(dictionary: dict) -> Greeting:
        """Create a Greeting object from a dictionary.

        Args:
            dictionary (dict): The dictionary to create the Greeting object from.

        Returns:
            Greeting: The Greeting object.
        """
        return Greeting(**dictionary)
