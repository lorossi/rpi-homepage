"""This module contains the Link class, used to represent a link to a service."""
from __future__ import annotations


class Link:
    """Link class, used to represent a link to a service."""

    def __init__(
        self,
        display_name: str,
        name: str,
        lan_ip: str,
        zerotier_ip: str,
        port: str,
        path: str = None,
    ) -> Link:
        """Link class, used to represent a link to a service.

        Args:
            display_name (str): displayed name of the service
            name (str): short name of the service
            lan_ip (str): ip of the service on the local network
            zerotier_ip (str): ip of the service on the ZeroTier network
            port (str): port of the service
            path (str, optional): url path of the service. Defaults to None.

        Returns:
            Link
        """
        self._display_name = display_name
        self._name = name
        self._lan_ip = lan_ip
        self._zerotier_ip = zerotier_ip
        self._port = port
        self._path = path

    @staticmethod
    def fromJSON(json: dict[str, str]) -> Link:
        """Create a Link object from a json dictionary."""
        return Link(
            json["display_name"],
            json["name"],
            json["lan_ip"],
            json["zerotier_ip"],
            json["port"],
            json.get("path", None),
        )

    def getFullUrl(self, zerotier: bool = False) -> str:
        """Get the full url of the service.

        Args:
            zerotier (bool, optional): True if the service is accessed \
                through the ZeroTier network. Defaults to False.

        Returns:
            str
        """
        if zerotier:
            return self.zerotier_url

        return self.lan_url

    def getPropertiesDict(self, zerotier: bool = False) -> dict[str, str]:
        """Get the properties of the service as a dictionary, \
            to be used by the Flask renderer.

        Args:
            zerotier (bool, optional): True if the service is accessed \
                through the ZeroTier network. Defaults to False.

        Returns:
            dict[str, str
        """
        properties = {"name": self._display_name}

        if zerotier:
            properties["href"] = self.zerotier_url
        else:
            properties["href"] = self.lan_url

        return properties

    @property
    def lan_url(self) -> str:
        """Get the url of the service on the local network."""
        if self._path is None:
            return f"http://{self._lan_ip}:{self._port}"

        return f"http://{self._lan_ip}:{self._port}/{self._path}"

    @property
    def zerotier_url(self) -> str:
        """Get the url of the service on the ZeroTier network."""
        if self._path is None:
            return f"http://{self._zerotier_ip}:{self._port}"

        return f"http://{self._zerotier_ip}:{self._port}/{self._path}"
