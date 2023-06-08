"""Settings for the server module."""
from __future__ import annotations
from dataclasses import dataclass
import tomllib


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
            with open(path, "rb") as f:
                toml_data = tomllib.load(f)
                if class_name is not None:
                    return cls(**toml_data[class_name])
                else:
                    return cls(**toml_data)

        except (FileNotFoundError, tomllib.TOMLDecodeError):
            return cls()


@dataclass
class ServerSettings(Settings):
    """Settings for the server module."""

    gradients_path: str
    links_path: str
    greetings_path: str
    port: int = 8000


@dataclass
class WeatherSettings(Settings):
    """Settings for the weather module."""

    api_key: str
    city: str
    language: str
