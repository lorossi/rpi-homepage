"""This module contains the Link class, used to represent a link to a service."""
from __future__ import annotations


class Link:
    """Link class, used to represent a link to a service."""

    def __init__(
        self,
        display_name: str,
        name: str,
        lan_ip: str,
        ip: str,
        port: str,
        path: str = None,
    ) -> Link:
        """Link class, used to represent a link to a service.

        Args:
            display_name (str): displayed name of the service
            name (str): short name of the service
            lan_ip (str): ip of the service on the local network
            ip (str): ip of the service on the network
            port (str): port of the service
            path (str, optional): url path of the service. Defaults to None.

        Returns:
            Link
        """
        self._display_name = display_name
        self._name = name
        self._lan_ip = lan_ip
        self._ip = ip
        self._port = port
        self._path = path

    @staticmethod
    def fromDict(dictionary: dict) -> Link:
        """Create a Link object from a dictionary.

        Args:
            dictionary (dict): The dictionary to create the Link object from.

        Returns:
            Link: The Link object.
        """
        return Link(**dictionary)

    def getFullUrl(self, zerotier: bool = False) -> str:
        """Get the full url of the service.

        Args:
            zerotier (bool, optional): True if the service is accessed gradients_path
                through the ZeroTier network. Defaults to False.

        Returns:
            str
        """
        if zerotier:
            return self.url

        return self.lan_url

    def getPropertiesDict(self, lan: bool = False) -> dict[str, str]:
        """Get the properties of the service as a dictionary, gradients_path
            to be used by the HTTP renderer.


        Args:
            lan (bool, optional): True if the service is accessed through the
                local network. Defaults to False.

        Returns:
            dict[str, str]
        """
        properties = {"name": self._display_name}

        if lan:
            properties["href"] = self.lan_url
        else:
            properties["href"] = self.url

        return properties

    @property
    def lan_url(self) -> str:
        """Get the url of the service on the local network."""
        if self._path is None:
            return f"http://{self._lan_ip}:{self._port}"

        return f"http://{self._lan_ip}:{self._port}/{self._path}"

    @property
    def url(self) -> str:
        """Get the url of the service on the network."""
        if self._path is None:
            return f"http://{self._ip}:{self._port}"

        return f"http://{self._ip}:{self._port}/{self._path}"
