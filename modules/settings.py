"""Settings for the server module."""
from __future__ import annotations

from dataclasses import dataclass

import toml


class Settings:
    """Base settings class."""

    @classmethod
    def fromDict(cls, dictionary: dict) -> ServerSettings:
        """Create a settings object from a dictionary.

        Args:
            dictionary (dict): The dictionary to create the settings object from.

        Returns:
            Settings: The settings object.
        """
        return cls(**dictionary)

    @classmethod
    def fromToml(cls, path: str, class_name: str = None) -> ServerSettings:
        """Create a settings object from a toml file.

        Args:
            path (str): The path to the toml file.
            class_name (str, optional): The name of the class to load from the
                toml file.
                Defaults to None.

        Returns:
            Settings: The settings object.
        """
        try:
            with open(path, "r") as f:
                toml_data = toml.load(f)
                if class_name is not None:
                    return cls(**toml_data[class_name])
                else:
                    return cls(**toml_data)

        except (FileNotFoundError, toml.TomlDecodeError):
            return cls()


@dataclass
class ServerSettings(Settings):
    """Settings for the server module."""

    port: int
    gradients_path: str
    links_path: str
    greetings_path: str
    logging_config: str


@dataclass
class WeatherSettings(Settings):
    """Settings for the weather module."""

    api_key: str
    city: str
    language: str
    cache_duration: int


@dataclass
class UnsplashSettings(Settings):
    """Settings for the unsplash module."""

    api_key: str
    query: list[str]
    cache_duration: int
