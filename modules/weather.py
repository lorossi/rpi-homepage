"""Module for the WeatherService class."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime

import aiohttp
import toml
from pydantic import BaseModel

from modules.settings import WeatherSettings


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

    def _formatTemperature(self, temperature: float) -> str:
        return f"{round(temperature, 1)}°C"

    @property
    def temperature_formatted(self) -> str:
        """Get the formatted temperature."""
        return self._formatTemperature(self.temperature)

    @property
    def min_temperature_formatted(self) -> str:
        """Get the formatted minimum temperature."""
        return self._formatTemperature(self.min_temperature)

    @property
    def max_temperature_formatted(self) -> str:
        """Get the formatted maximum temperature."""
        return self._formatTemperature(self.max_temperature)

    @property
    def humidity_formatted(self) -> str:
        """Get the formatted humidity."""
        return f"{int(self.humidity)}%"

    def toResponse(self) -> WeatherResponse:
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
    _cached_weather: Weather
    _cached_time: float

    def __init__(self, settings_path: str = "settings/settings.toml") -> WeatherService:
        """Instantiate a new Weather object."""
        logging.info("Initializing WeatherService")
        self._settings_path = settings_path
        # set the time the weather was cached to 0
        self._cached_time = 0
        self._cached_weather = None

        self._loadSettings()

    def _loadSettings(self) -> None:
        with open(self._settings_path, "r") as f:
            settings = toml.load(f)[self.__class__.__name__]

        self._settings = WeatherSettings.fromDict(settings)

    async def _requestJSON(self, url: str) -> dict:
        """Request a JSON object from a url."""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.json()

    async def _requestWeather(self) -> Weather:
        request_url = (
            f"http://api.openweathermap.org/data/2.5/weather?"
            f"q={self._settings.city}"
            f"&appid={self._settings.api_key}"
            f"&units=metric&lang={self._settings.language}"
        )

        json_data = await self._requestJSON(request_url)
        return Weather(
            cod=json_data["cod"],
            city=json_data["name"],
            temperature=json_data["main"]["temp"],
            min_temperature=json_data["main"]["temp_min"],
            max_temperature=json_data["main"]["temp_max"],
            humidity=json_data["main"]["humidity"],
            description=json_data["weather"][0]["description"],
        )

    async def getWeather(self) -> Weather:
        """Get the weather."""
        elapsed_time = datetime.now().timestamp() - self._cached_time
        if elapsed_time > self._settings.cache_duration:
            # if the weather is older than the cache duration, fetch it again
            logging.info("Fetching weather")
            # store the weather in the cache
            self._cached_weather = await self._requestWeather()
            # update the cached time
            self._cached_time = datetime.now().timestamp()

        return self._cached_weather
