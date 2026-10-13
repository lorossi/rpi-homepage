"""Module for the RPiServer class."""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import toml

from modules.greetings import Greeting
from modules.links import Link
from modules.server import HTTPException, Request, Response, Server
from modules.unsplash import UnsplashResponse, UnsplashService
from modules.weather import WeatherResponse, WeatherService

if TYPE_CHECKING:
    from modules.settings import ServerSettings

logger = logging.getLogger(__name__)


class APIException(HTTPException):
    """APIException class, used to represent an API exception."""

    message: str


class RPiServer(Server):
    """RPiServer class, used to represent the server."""

    _settings: ServerSettings
    _links: list[Link]
    _greetings: list[Greeting]

    _weather: WeatherService
    _unsplash: UnsplashService

    def __init__(self, settings_path: str = "settings/settings.toml") -> None:
        """Create a RPiServer object.

        Args:
            settings_path (str, optional): Path to the settings file.
            Defaults to "settings/settings.toml".
        """
        logger.info("Initializing RPiServer")
        self._settings_path = settings_path

        self._settings = self.load_settings()
        self._links, self._greetings = self.load_attributes()

        logger.info("Initializing RPiServer routes")
        self.add_static_route("/static", "static")
        self.add_template_folder("templates")
        self.add_route("/", self._index_page)
        self.add_route("/get/weather", self._weather_api)
        self.add_route("/get/image", self._unsplash_api)
        self.add_http_exception_route(self._error_page)

        logger.info("Initializing weather")
        self._weather = WeatherService()
        logger.info("Initializing unsplash")
        self._unsplash = UnsplashService()

    def load_attributes(self) -> tuple[list[Link], list[Greeting]]:
        """Load the links from the settings file."""
        logger.info("Loading RPiServer attributes")

        logger.info("Loading links")
        with Path(self._settings.links_path).open() as f:
            links_dict = toml.load(f)

        links = sorted(
            [Link.from_dict(link) for link in links_dict["Links"]],
            key=lambda link: len(link.display_name),
            reverse=True,
        )

        logger.info("Loading greetings")
        with Path(self._settings.greetings_path).open() as f:
            greetings_list = toml.load(f)

        greetings = [
            Greeting.from_dict(greeting) for greeting in greetings_list["Greetings"]
        ]

        return links, greetings

    def _is_local_ip(self, ip: str) -> bool:
        """Check if the ip is local.

        Args:
            ip (str): IP address

        Returns:
            bool
        """
        return ip.startswith(("192.168.1", "127.0.0"))

    def _is_local_request(self, request: Request) -> bool:
        """Check if the request comes from the local network, logging its ip.

        Args:
            request (Request): HTTP request

        Returns:
            bool
        """
        ip = request.client.host if request.client is not None else ""
        local = self._is_local_ip(ip)
        logger.info("Client ip: %s. Local: %s", ip, local)
        return local

    def _get_greeting(self) -> Greeting | None:
        """Get a greeting.

        Returns:
            Greeting | None: the greeting for the current hour, if any
        """
        logger.info("Getting a greeting")
        hour = datetime.now().astimezone().hour
        for greeting in self._greetings:
            if greeting.is_in_time(hour):
                return greeting

        return None

    async def _index_page(self, request: Request) -> Response:
        """Serve the index page.

        Args:
            request (Request): HTTP request

        Returns:
            Response
        """
        logger.info("Serving index page")
        local = self._is_local_request(request)

        # format the links according to the request
        # (either local or remote)
        links = [link.get_properties_dict(lan=local) for link in self._links]
        # get a greeting
        greeting = self._get_greeting()
        # return the page
        return self.generate_template_response(
            request=request,
            template="index.html",
            links=links,
            greeting=greeting,
        )

    async def _error_page(self, request: Request, exception: HTTPException) -> Response:
        """Handle an HTTPException.

        If the error is a 404, redirect to the index page.

        Args:
            request (Request): HTTP request
            exception (HTTPException): HTTP exception

        Returns:
            Response
        """
        logger.warning("Handling HTTPException: %s", exception)

        is_api_request = request.url.path.startswith("/get")
        error_code = exception.status_code

        logger.info("Is API request: %s, Error code: %s", is_api_request, error_code)

        return self.generate_template_response(
            request=request,
            template="redirect.html",
        )

    async def _weather_api(self, request: Request) -> WeatherResponse:
        """Serve the weather api.

        Args:
            request (Request): HTTP request

        Returns:
            WeatherResponse: Weather response
        """
        logger.info("Serving weather api")
        self._is_local_request(request)
        w = await self._weather.get_weather()
        return w.to_response()

    async def _unsplash_api(self, request: Request) -> UnsplashResponse:
        """Serve the unsplash api.

        Args:
            request (Request): HTTP request

        Returns:
            UnsplashResponse: Unsplash response
        """
        logger.info("Serving unsplash api")
        self._is_local_request(request)
        u = await self._unsplash.get_random_photo()
        logger.info("Unsplash response: %s", u)
        return u.to_response()
