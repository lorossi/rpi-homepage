from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime

import aiohttp
import toml
from pydantic import BaseModel

from modules.settings import UnsplashSettings


class UnsplashResponse(BaseModel):
    """UnsplashResponse class, used to represent a unsplash response."""

    url: str | None
    blur_hash: str | None
    photographer: str | None
    city: str | None
    country: str | None
    photographer: str | None
    description: str | None
    color: str | None
    light_text: bool | None


@dataclass
class UnsplashPhoto:
    url: str
    color: str
    blur_hash: str
    city: str
    country: str
    photographer: str
    description: str

    def toResponse(self) -> UnsplashResponse:
        return UnsplashResponse(
            url=self.url,
            blur_hash=self.blur_hash,
            city=self.city,
            country=self.country,
            photographer=self.photographer,
            description=self.description,
            color=self.color,
            light_text=self.light_text,
        )

    @property
    def light_text(self) -> str:
        """Get whether the text on top of the image should be light or dark."""
        # Convert the hex color to rgb
        rgb = tuple(int(self.color[i : i + 2], 16) for i in (1, 3, 5))
        # Calculate the luminance
        luminance = (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) / 255
        # If the luminance is greater than 0.5, the background is light
        # and the text is black, otherwise the background is dark and the text
        # is white
        return luminance < 0.5


class UnsplashService:
    _settings_path: str
    _settings: UnsplashSettings
    _cached_photo: UnsplashPhoto
    cached_time: float

    def __init__(
        self, settings_path: str = "settings/settings.toml"
    ) -> UnsplashService:
        """Create a UnsplashService object.

        Args:
            settings_path (str, optional): Path to the settings file.
                Defaults to "settings/settings.toml".

        Returns:
            UnsplashService
        """
        logging.info("Initializing UnsplashService")
        self.settings_path = settings_path
        # the time the photo was cached to 0
        self.cached_time = 0
        self._cached_photo = None

        self._loadSettings()

    def _loadSettings(self) -> None:
        """Load the settings from the settings file."""
        with open(self.settings_path, "r") as f:
            settings_data = toml.load(f)[self.__class__.__name__]

        self._settings = UnsplashSettings.fromDict(settings_data)

    async def _asyncRequest(
        self, url: str, headers: dict = None
    ) -> aiohttp.ClientResponse:
        """Request a response from a url."""
        async with aiohttp.ClientSession() as session:
            return await session.get(url, headers=headers)

    async def _requestPhoto(self) -> UnsplashPhoto:
        """Get a random photo from unsplash."""
        logging.info("Requesting photo from unsplash")
        query = "https://api.unsplash.com/photos/random?topics=textures-patterns"
        headers = {
            "Accept-Version": "v1",
            "Authorization": f"Client-ID {self._settings.api_key}",
        }

        logging.info(f"Sending request to unsplash: {query}")
        response = await self._asyncRequest(query, headers=headers)

        if response.status != 200:
            logging.error(f"Unsplash API returned status code {response.status}")
            return UnsplashResponse(
                url=None,
                blur_hash=None,
                city=None,
                country=None,
                photographer=None,
                description=None,
                color=None,
            )

        logging.info("Awaiting response from unsplash")
        data = await response.json()

        logging.info("Parsing response from unsplash")
        img_data = {
            "color": data["color"],
            "url": data["urls"]["regular"],
            "blur_hash": data["blur_hash"],
            "city": data["location"]["city"],
            "country": data["location"]["country"],
            "photographer": data["user"]["name"],
            "description": data["description"],
        }

        return UnsplashPhoto(**img_data)

    async def getRandomPhoto(self) -> UnsplashPhoto:
        """Get a random photo from unsplash."""
        elapsed_time = datetime.now().timestamp() - self.cached_time
        if elapsed_time > self._settings.cache_duration:
            # if the photo is older than the cache duration, request a new one
            logging.info("Requesting new photo from unsplash")
            # request the photo
            self._cached_photo = await self._requestPhoto()
            # update the cached time
            self.cached_time = datetime.now().timestamp()

        return self._cached_photo
