"""This module contains the Link class, used to represent a link to a service."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class Link:
    """Link class, used to represent a link to a service.

    Attributes:
        display_name (str): displayed name of the service
        name (str): short name of the service
        lan_ip (str): ip of the service on the local network
        ip (str): ip of the service on the network
        port (str): port of the service
        path (str, optional): url path of the service. Defaults to None.
    """

    display_name: str
    name: str
    lan_ip: str
    ip: str
    port: str
    path: str | None = None

    @staticmethod
    def from_dict(dictionary: dict) -> Link:
        """Create a Link object from a dictionary.

        Args:
            dictionary (dict): The dictionary to create the Link object from.

        Returns:
            Link: The Link object.
        """
        return Link(**dictionary)

    def get_full_url(self, *, zerotier: bool = False) -> str:
        """Get the full url of the service.

        Args:
            zerotier (bool, optional): True if the service is accessed
                through the ZeroTier network. Defaults to False.

        Returns:
            str
        """
        if zerotier:
            return self.full_url

        return self.lan_url

    def get_properties_dict(self, *, lan: bool = False) -> dict[str, str]:
        """Get the properties as a dictionary.

        Args:
            lan (bool, optional): True if the link is accessed through
                the local network. Defaults to False.

        Returns:
            dict[str, str]
        """
        properties = {"name": self.display_name}

        if lan:
            properties["href"] = self.lan_url
        else:
            properties["href"] = self.full_url

        return properties

    @property
    def lan_url(self) -> str:
        """Get the url of the service on the local network."""
        if self.path is None:
            return f"http://{self.lan_ip}:{self.port}"

        return f"http://{self.lan_ip}:{self.port}/{self.path}"

    @property
    def full_url(self) -> str:
        """Get the url of the service on the network."""
        if self.path is None:
            return f"http://{self.ip}:{self.port}"

        return f"http://{self.ip}:{self.port}/{self.path}"
