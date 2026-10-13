"""Settings for the server module."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Self

import toml


class Settings:
    """Base settings class."""

    @classmethod
    def from_dict(cls, dictionary: dict) -> Self:
        """Create a settings object from a dictionary.

        Args:
            dictionary (dict): The dictionary to create the settings object from.

        Returns:
            Settings: The settings object.
        """
        return cls(**dictionary)

    @classmethod
    def from_toml(cls, path: str, class_name: str | None = None) -> Self:
        """Create a settings object from a toml file.

        Args:
            path (str): The path to the toml file.
            class_name (str, optional): The name of the class to load from the
                toml file.
                Defaults to None.

        Returns:
            Settings: The settings object.

        Raises:
            FileNotFoundError: If the toml file does not exist.
            toml.TomlDecodeError: If the toml file is not valid.
        """
        with Path(path).open() as f:
            toml_data = toml.load(f)

        if class_name is not None:
            return cls.from_dict(toml_data[class_name])

        return cls.from_dict(toml_data)


@dataclass
class SystemSettings(Settings):
    """Settings for the system module."""

    disks: list[str] = field(default_factory=lambda: ["/"])
    sample_interval: int = 10
    history_length: int = 30


@dataclass
class IconSettings(Settings):
    """Settings for the icons module.

    Attributes:
        url (str): url template of the icons, `{name}` is replaced with the
            name of the icon
        cache_path (str): folder where the downloaded icons are stored
        retry_interval (int): seconds between two attempts at downloading
            the missing icons
    """

    url: str = "https://cdn.jsdelivr.net/npm/lucide-static@1.56.0/icons/{name}.svg"
    cache_path: str = "cache/icons"
    retry_interval: int = 3600


@dataclass(frozen=True, kw_only=True)
class Link:
    """Link class, used to represent a link to a service.

    Attributes:
        display_name (str): displayed name of the service
        name (str): short name of the service
        lan_ip (str): ip of the service on the local network
        vpn_ip (str): ip of the service on the VPN
        port (str): port of the service
        path (str, optional): url path of the service. Defaults to None.
        category (str, optional): category of the service, links with the
            same category are grouped together. Defaults to None (grouped
            with the other uncategorized links).
        icon (str, optional): name of the icon of the service, from the
            Lucide set (https://lucide.dev/icons). Defaults to None (generic icon).
    """

    display_name: str
    name: str
    lan_ip: str
    vpn_ip: str
    port: str
    path: str | None = None
    category: str | None = None
    icon: str | None = None

    @staticmethod
    def from_dict(dictionary: dict) -> Link:
        """Create a Link object from a dictionary.

        Args:
            dictionary (dict): The dictionary to create the Link object from.

        Returns:
            Link: The Link object.
        """
        return Link(**dictionary)

    def get_url(self, *, lan: bool = False) -> str:
        """Get the url of the service.

        Args:
            lan (bool, optional): True if the service is accessed through
                the local network, False if through the VPN. Defaults to False.

        Returns:
            str
        """
        if lan:
            return self.lan_url

        return self.vpn_url

    def get_properties_dict(
        self, *, lan: bool = False, icon_markup: str | None = None
    ) -> dict[str, str]:
        """Get the properties as a dictionary.

        Args:
            lan (bool, optional): True if the link is accessed through
                the local network. Defaults to False.
            icon_markup (str, optional): inner svg markup of the icon.
                Defaults to None (generic icon).

        Returns:
            dict[str, str]
        """
        return {
            "name": self.display_name,
            "href": self.get_url(lan=lan),
            "icon": icon_markup or "",
        }

    @property
    def lan_url(self) -> str:
        """Get the url of the service on the local network."""
        if not self.path:
            return f"http://{self.lan_ip}:{self.port}"

        return f"http://{self.lan_ip}:{self.port}/{self.path}"

    @property
    def vpn_url(self) -> str:
        """Get the url of the service on the VPN."""
        if not self.path:
            return f"http://{self.vpn_ip}:{self.port}"

        return f"http://{self.vpn_ip}:{self.port}/{self.path}"


@dataclass
class ServerSettings(Settings):
    """Settings for the server module.

    Attributes:
        port (int): port the server listens on
        local_networks (list[str]): networks (in CIDR notation) whose clients
            get the LAN urls of the links
        forwarded_allow_ips (list[str]): ips of the reverse proxies trusted to
            set the X-Forwarded-For header. Empty to ignore the header.
        categories (list[str]): order of the link categories. Categories
            not listed follow in order of first appearance.
    """

    port: int
    local_networks: list[str] = field(
        default_factory=lambda: ["192.168.1.0/24", "127.0.0.0/8", "::1/128"]
    )
    forwarded_allow_ips: list[str] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)
    system: SystemSettings = field(default_factory=SystemSettings)
    icons: IconSettings = field(default_factory=IconSettings)
    links: list[Link] = field(default_factory=list)

    @classmethod
    def from_toml(cls, path: str, class_name: str | None = None) -> Self:
        """Create a server settings object from a toml file.

        The server options are read from the `class_name` table, the system
        and icon options from the optional `System` and `Icons` tables and the
        links from the `Links` array of tables.

        Args:
            path (str): The path to the toml file.
            class_name (str, optional): The name of the table containing the
                server options. Defaults to None (top level of the file).

        Returns:
            ServerSettings: The settings object.

        Raises:
            FileNotFoundError: If the toml file does not exist.
            toml.TomlDecodeError: If the toml file is not valid.
        """
        with Path(path).open() as f:
            toml_data = toml.load(f)

        server_data = toml_data if class_name is None else toml_data[class_name]
        optional = {
            key: server_data[key]
            for key in ("local_networks", "forwarded_allow_ips", "categories")
            if key in server_data
        }
        return cls(
            port=server_data["port"],
            **optional,
            system=SystemSettings.from_dict(toml_data.get("System", {})),
            icons=IconSettings.from_dict(toml_data.get("Icons", {})),
            links=[Link.from_dict(link) for link in toml_data.get("Links", [])],
        )

    def grouped_links(self) -> dict[str, list[Link]]:
        """Group the links by category.

        The categories listed in the settings come first, in the given order,
        followed by the others in order of first appearance. Uncategorized
        links go last, in a group named "Other" (or unnamed, if no link has
        a category). Empty groups are omitted.

        Returns:
            dict[str, list[Link]]: The links, grouped by category name.
        """
        groups: dict[str, list[Link]] = {name: [] for name in self.categories}
        for link in self.links:
            groups.setdefault(link.category or "", []).append(link)

        uncategorized = groups.pop("", [])
        groups = {name: links for name, links in groups.items() if links}
        if uncategorized:
            groups["Other" if groups else ""] = uncategorized

        return groups
