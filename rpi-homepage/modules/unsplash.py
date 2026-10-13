"""Unsplash module, used to get a random photo from unsplash."""

from __future__ import annotations

import logging
import random
import time
from dataclasses import dataclass
from typing import Any

import aiohttp
from pydantic import BaseModel

from modules.settings import UnsplashSettings

logger = logging.getLogger(__name__)

# luminance above which a background is considered light
LIGHT_BACKGROUND_LUMINANCE = 0.5


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
    location: str | None
    description: str | None
    color: str | None

    def to_response(self) -> UnsplashResponse:
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
    def light_text(self) -> bool:
        """Get whether the text on top of the image should be light or dark."""
        if self.color is None:
            return False
        # Convert the hex color to rgb
        rgb = tuple(int(self.color[i : i + 2], 16) for i in (1, 3, 5))
        # Calculate the luminance
        luminance = (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) / 255
        # If the luminance is greater than the threshold, the background is light
        # and the text is black, otherwise the background is dark and the text
        # is white
        return luminance < LIGHT_BACKGROUND_LUMINANCE


class UnsplashService:
    """UnsplashService class, used to get a random photo from unsplash."""

    _settings_path: str
    _settings: UnsplashSettings
    _cached_photo: UnsplashPhoto | None
    _cached_time: float

    def __init__(self, settings_path: str = "settings/settings.toml") -> None:
        """Create a UnsplashService object.

        Args:
            settings_path (str, optional): Path to the settings file.
                Defaults to "settings/settings.toml".
        """
        logger.info("Initializing UnsplashService")
        self._settings_path = settings_path
        # the time the photo was cached, in seconds of the monotonic clock
        self._cached_time = 0
        self._cached_photo = None

        self._settings = UnsplashSettings.from_toml(
            self._settings_path, self.__class__.__name__
        )

    async def _async_request_json(
        self, url: str, headers: dict[str, str] | None = None
    ) -> dict[str, Any]:
        """Request a response from a url."""
        async with (
            aiohttp.ClientSession() as session,
            session.get(url, headers=headers, raise_for_status=True) as response,
        ):
            return await response.json()

    async def _request_photo(self) -> UnsplashPhoto:
        """Get a random photo from unsplash."""
        logger.info("Requesting photo from unsplash")

        # the choice of the query is not security sensitive
        selected_query = random.choice(self._settings.query)  # noqa: S311
        query = f"https://api.unsplash.com/photos/random?query={selected_query}"

        headers = {
            "Accept-Version": "v1",
            "Authorization": f"Client-ID {self._settings.api_key}",
        }

        logger.info("Sending request to unsplash: %s", query)
        json_data = await self._async_request_json(query, headers=headers)

        logger.info("Parsing response from unsplash")
        img_data = {
            "color": json_data["color"],
            "url": json_data["urls"]["regular"],
            "link": json_data["links"]["html"],
            "blur_hash": json_data["blur_hash"],
            "location": json_data["location"]["name"],
            "photographer": json_data["user"]["username"],
            "photographer_url": json_data["user"]["links"]["html"],
            "description": json_data["description"],
        }
        logger.info("Parsed response from unsplash")

        return UnsplashPhoto(**img_data)

    async def get_random_photo(self) -> UnsplashPhoto:
        """Get a random photo from unsplash."""
        photo = self._cached_photo
        elapsed_time = time.monotonic() - self._cached_time
        if photo is None or elapsed_time > self._settings.cache_duration:
            # if the photo is older than the cache duration, request a new one
            logger.info("Requesting new photo from unsplash")
            # save started time for logging purposes
            started_time = time.perf_counter()
            # request the photo
            photo = await self._request_photo()
            # compute elapsed time
            elapsed = time.perf_counter() - started_time
            logger.info("Photo requested in %s seconds", elapsed)
            # update the cache
            self._cached_photo = photo
            self._cached_time = time.monotonic()

        return photo
