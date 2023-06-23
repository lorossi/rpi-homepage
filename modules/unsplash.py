"""Unsplash module, used to get a random photo from unsplash."""
from __future__ import annotations

import logging
import random
from dataclasses import dataclass
from datetime import datetime

import aiohttp
import toml
from pydantic import BaseModel

from modules.settings import UnsplashSettings


class UnsplashResponse(BaseModel):
    """UnsplashResponse class, used to represent a unsplash response."""

    url: str | None
    link: str | None
    blur_hash: str | None
    photographer: str | None
    photographer_url: str | None
    location: str | None
    description: str | None
    color: str | None
    light_text: bool | None


@dataclass
class UnsplashPhoto:
    """UnsplashPhoto class, used to represent a unsplash photo."""

    url: str
    link: str
    blur_hash: str
    photographer: str
    photographer_url: str
    location: str
    description: str
    color: str

    def toResponse(self) -> UnsplashResponse:
        """Convert the UnsplashPhoto object to a UnsplashResponse object.

        Returns:
            UnsplashResponse
        """
        return UnsplashResponse(
            url=self.url,
            link=self.link,
            blur_hash=self.blur_hash,
            location=self.location,
            photographer=self.photographer,
            photographer_url=self.photographer_url,
            description=self.description,
            color=self.color,
            light_text=self.light_text,
        )

    @property
    def light_text(self) -> str:
        """Get whether the text on top of the image should be light or dark."""
        if self.color is None:
            return False
        # Convert the hex color to rgb
        rgb = tuple(int(self.color[i : i + 2], 16) for i in (1, 3, 5))
        # Calculate the luminance
        luminance = (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) / 255
        # If the luminance is greater than 0.5, the background is light
        # and the text is black, otherwise the background is dark and the text
        # is white
        return luminance < 0.5


class UnsplashService:
    """UnsplashService class, used to get a random photo from unsplash."""

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

        selected_query = random.choice(self._settings.query)
        query = f"https://api.unsplash.com/photos/random?query={selected_query}"

        headers = {
            "Accept-Version": "v1",
            "Authorization": f"Client-ID {self._settings.api_key}",
        }

        logging.info(f"Sending request to unsplash: {query}")
        response = await self._asyncRequest(query, headers=headers)

        if response.status != 200:
            logging.error(f"Unsplash API returned status code {response.status}")
            raise Exception(f"Unsplash API returned an error: {response.status}")

        logging.info("Awaiting response from unsplash")
        data = await response.json()

        logging.info("Parsing response from unsplash")
        img_data = {
            "color": data["color"],
            "url": data["urls"]["regular"],
            "link": data["links"]["html"],
            "blur_hash": data["blur_hash"],
            "location": data["location"]["name"],
            "photographer": data["user"]["username"],
            "photographer_url": data["user"]["links"]["html"],
            "description": data["description"],
        }
        logging.info("Parsed response from unsplash")

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
