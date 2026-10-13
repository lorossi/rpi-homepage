"""Icons module, used to download and cache the icons of the services."""

import asyncio
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import TYPE_CHECKING

import aiohttp
from loguru import logger

if TYPE_CHECKING:
    from collections.abc import Iterable

    from modules.settings import IconSettings

# icon names are used both in the url and in the cache file name
ICON_NAME = re.compile(r"^[a-z0-9-]+$")
# the markup is rendered unescaped, so only plain shapes are allowed
ALLOWED_TAGS = {"path", "circle", "rect", "line", "polyline", "polygon", "ellipse"}
REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=10)


class IconService:
    """IconService class, used to download, cache and serve the icons.

    Icons are downloaded once and stored in the cache folder, so that they
    are available offline after the first download.
    """

    _settings: IconSettings
    _names: set[str]
    _icons: dict[str, str]

    def __init__(self, settings: IconSettings, names: Iterable[str]) -> None:
        """Create an IconService object.

        Args:
            settings (IconSettings): The icon settings.
            names (Iterable[str]): The names of the icons to provide.
        """
        logger.info("Initializing IconService")
        self._settings = settings
        self._icons = {}
        self._names = set()

        for name in names:
            if ICON_NAME.match(name):
                self._names.add(name)
            else:
                logger.warning("Invalid icon name {}, skipping it", name)

    @property
    def retry_interval(self) -> int:
        """Get the interval between two download attempts, in seconds."""
        return self._settings.retry_interval

    def _cache_file(self, name: str) -> Path:
        """Get the path of the cached icon."""
        return Path(self._settings.cache_path) / f"{name}.svg"

    @staticmethod
    def _parse(svg: str) -> str:
        """Extract the inner markup of an svg icon.

        Args:
            svg (str): The svg file content.

        Returns:
            str: The inner markup, without namespaces.

        Raises:
            ValueError: If the file is not an svg made of plain shapes.
        """
        try:
            root = ET.fromstring(svg)  # noqa: S314 - icons come from a pinned package
        except ET.ParseError as e:
            msg = "not a valid xml file"
            raise ValueError(msg) from e

        for element in root.iter():
            element.tag = element.tag.rpartition("}")[2]

        if root.tag != "svg":
            msg = f"root element is {root.tag}, not svg"
            raise ValueError(msg)

        children = list(root)
        for element in children:
            if element.tag not in ALLOWED_TAGS or len(element):
                msg = f"unsupported element {element.tag}"
                raise ValueError(msg)
            if any(attribute.startswith("on") for attribute in element.attrib):
                msg = f"event handler in element {element.tag}"
                raise ValueError(msg)
            element.tail = None

        return "".join(ET.tostring(e, encoding="unicode") for e in children)

    async def _download(self, session: aiohttp.ClientSession, name: str) -> str:
        """Download an icon.

        Args:
            session (aiohttp.ClientSession): The http session.
            name (str): The name of the icon.

        Returns:
            str: The svg file content.
        """
        url = self._settings.url.format(name=name)
        logger.info("Downloading icon {} from {}", name, url)
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.text()

    async def _load(self, session: aiohttp.ClientSession, name: str) -> None:
        """Load an icon from the cache, downloading it if missing.

        Args:
            session (aiohttp.ClientSession): The http session.
            name (str): The name of the icon.
        """
        cache_file = self._cache_file(name)
        try:
            if cache_file.exists():
                self._icons[name] = self._parse(cache_file.read_text())
                return

            svg = await self._download(session, name)
            self._icons[name] = self._parse(svg)
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            cache_file.write_text(svg)
        except (aiohttp.ClientError, TimeoutError, OSError, ValueError) as e:
            logger.warning("Could not load icon {}: {}", name, e)

    async def prefetch(self) -> None:
        """Load all the icons that are not loaded yet."""
        missing = self._names - self._icons.keys()
        if not missing:
            return

        logger.info("Loading icons: {}", ", ".join(sorted(missing)))
        async with aiohttp.ClientSession(timeout=REQUEST_TIMEOUT) as session:
            await asyncio.gather(*(self._load(session, name) for name in missing))
        logger.info("Loaded {} of {} icons", len(self._icons), len(self._names))

    def get(self, name: str | None) -> str | None:
        """Get the inner svg markup of an icon.

        Args:
            name (str | None): The name of the icon.

        Returns:
            str | None: The markup, or None if the icon is not available.
        """
        if name is None:
            return None

        return self._icons.get(name)
