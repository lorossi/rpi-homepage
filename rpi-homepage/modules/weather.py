"""Module for the WeatherService class."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any

import aiohttp
from pydantic import BaseModel

from modules.settings import WeatherSettings

logger = logging.getLogger(__name__)


class WeatherResponse(BaseModel):
    """WeatherResponse class, used to represent a weather response."""

    cod: int
    city: str
    temperature: str
    min_temperature: str
    max_temperature: str
    humidity: str
    description: str


@dataclass
class Weather:
    """Weather class, used to represent the weather."""

    cod: int
    city: str
    temperature: float
    min_temperature: float
    max_temperature: float
    humidity: float
    description: str

    def _format_temperature(self, temperature: float) -> str:
        return f"{round(temperature, 1)}°C"

    @property
    def temperature_formatted(self) -> str:
        """Get the formatted temperature."""
        return self._format_temperature(self.temperature)

    @property
    def min_temperature_formatted(self) -> str:
        """Get the formatted minimum temperature."""
        return self._format_temperature(self.min_temperature)

    @property
    def max_temperature_formatted(self) -> str:
        """Get the formatted maximum temperature."""
        return self._format_temperature(self.max_temperature)

    @property
    def humidity_formatted(self) -> str:
        """Get the formatted humidity."""
        return f"{int(self.humidity)}%"

    def to_response(self) -> WeatherResponse:
        """Convert the Weather object to a WeatherResponse object."""
        return WeatherResponse(
            cod=self.cod,
            city=self.city,
            temperature=self.temperature_formatted,
            min_temperature=self.min_temperature_formatted,
            max_temperature=self.max_temperature_formatted,
            humidity=self.humidity_formatted,
            description=self.description,
        )


class WeatherService:
    """WeatherService class, used to represent the weather service."""

    _settings_path: str
    _settings: WeatherSettings
    _cached_weather: Weather | None
    _cached_time: float

    def __init__(self, settings_path: str = "settings/settings.toml") -> None:
        """Instantiate a new Weather object."""
        logger.info("Initializing WeatherService")
        self._settings_path = settings_path
        # the time the weather was cached, in seconds of the monotonic clock
        self._cached_time = 0
        self._cached_weather = None

        self._settings = WeatherSettings.from_toml(
            self._settings_path, self.__class__.__name__
        )

    async def _request_json(self, url: str) -> dict[str, Any]:
        """Request a JSON object from a url."""
        async with aiohttp.ClientSession() as session, session.get(url) as response:
            return await response.json()

    async def _request_weather(self) -> Weather:
        request_url = (
            f"http://api.openweathermap.org/data/2.5/weather?"
            f"q={self._settings.city}"
            f"&appid={self._settings.api_key}"
            f"&units=metric&lang={self._settings.language}"
        )

        json_data = await self._request_json(request_url)
        return Weather(
            cod=json_data["cod"],
            city=json_data["name"],
            temperature=json_data["main"]["temp"],
            min_temperature=json_data["main"]["temp_min"],
            max_temperature=json_data["main"]["temp_max"],
            humidity=json_data["main"]["humidity"],
            description=json_data["weather"][0]["description"],
        )

    async def get_weather(self) -> Weather:
        """Get the weather."""
        weather = self._cached_weather
        elapsed_time = time.monotonic() - self._cached_time
        if weather is None or elapsed_time > self._settings.cache_duration:
            # if the weather is older than the cache duration, fetch it again
            logger.info("Fetching weather")
            weather = await self._request_weather()
            # store the weather in the cache
            self._cached_weather = weather
            self._cached_time = time.monotonic()

        return weather
