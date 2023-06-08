"""This module contains the Gradient class, used to represent a css gradient."""

from __future__ import annotations
from random import randint


class Gradient:
    """Gradient class, used to represent a css gradient."""

    def __init__(self, color_from: str, color_to: str) -> Gradient:
        """Gradient class, used to represent a css gradient.

        Args:
            color_from (str): starting color of the gradient
            color_to (str): ending color of the gradient

        Returns:
            Gradient
        """
        self._color_from = color_from
        self._color_to = color_to

    def getCSSString(self, angle: int = None) -> str:
        """Get the css string of the gradient.

        Args:
            angle (int, optional): rotation of the gradient. Defaults to None.

        Returns:
            str
        """
        if angle is None:
            angle = randint(0, 360)

        return f"linear-gradient({angle}deg, {self._color_from}, {self._color_to});"

    @staticmethod
    def fromList(array: list[str]) -> Gradient:
        """Create a Gradient object from a list of colors."""
        return Gradient(array[0], array[1])
