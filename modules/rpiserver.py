"""Module for the RPiServer class."""
from __future__ import annotations

import logging
from datetime import datetime

import toml

from modules.greetings import Greeting
from modules.links import Link
from modules.server import HTMLResponse, HTTPException, Request, Server
from modules.settings import ServerSettings
from modules.unsplash import UnsplashResponse, UnsplashService
from modules.weather import WeatherResponse, WeatherService


class APIException(HTTPException):
    message: str


class RPiServer(Server):
    """RPiServer class, used to represent the server."""

    _settings: ServerSettings
    _links: list[Link]
    _greetings: list[Greeting]

    _weather: WeatherService
    _unsplash: UnsplashService

    def __init__(self, settings_path: str = "settings/settings.toml") -> RPiServer:
        """Create a RPiServer object.

        Args:
            settings_path (str, optional): Path to the settings file.
            Defaults to "settings/settings.toml".

        Returns:
            RPiServer
        """
        logging.info("Initializing RPiServer")
        self._settings_path = settings_path

        self._settings = self.loadSettings()
        self._links, self._greetings = self.loadAttributes()

        logging.info("Initializing RPiServer routes")
        self.addStaticRoute("/static", "static")
        self.addTemplateFolder("templates")
        self.addRoute("/", self._indexPage)
        self.addRoute("/get/weather", self._weatherApi)
        self.addRoute("/get/image", self._unsplashApi)
        self.addHTTPExceptionRoute(self._errorPage)

        logging.info("Initializing weather")
        self._weather = WeatherService()
        logging.info("Initializing unsplash")
        self._unsplash = UnsplashService()

    def loadAttributes(self) -> tuple[list[Link], list[Greeting]]:
        """Load the gradients and links from the settings file."""
        logging.info("Loading RPiServer attributes")

        logging.info("Loading links")
        with open(self._settings.links_path, "r") as f:
            links_dict = toml.load(f)

        links = sorted(
            [Link.fromDict(link) for link in links_dict["Links"]],
            key=lambda link: len(link.display_name),
            reverse=True,
        )

        logging.info("Loading greetings")
        with open(self._settings.greetings_path, "r") as f:
            greetings_list = toml.load(f)

        greetings = [
            Greeting.fromDict(greeting) for greeting in greetings_list["Greetings"]
        ]

        return links, greetings

    def _isLocalIp(self, ip: str) -> bool:
        """Check if the ip is local.

        Args:
            ip (str): IP address

        Returns:
            bool
        """
        return ip.startswith("192.168.1") or ip.startswith("127.0.0")

    def _getGreeting(self) -> Greeting:
        """Get a greeting.

        Returns:
            Greeting
        """
        logging.info("Getting a greeting")
        hour = datetime.now().hour
        for greeting in self._greetings:
            if greeting.isInTime(hour):
                return greeting

    async def _indexPage(self, request: Request) -> HTMLResponse:
        """Serve the index page.

        Args:
            request (Request): HTTP request

        Returns:
            HTMLResponse
        """
        logging.info("Serving index page")
        ip = request.client.host
        local = self._isLocalIp(ip)
        logging.info(f"Client ip: {ip}. Local: {local}")

        # format the links according to the request
        # (either local or remote)
        links = [link.getPropertiesDict(local) for link in self._links]
        # get a greeting
        greeting = self._getGreeting()
        # return the page
        return self.generateTemplateResponse(
            request=request,
            template="index.html",
            links=links,
            greeting=greeting,
        )

    async def _errorPage(
        self, request: Request, exception: HTTPException
    ) -> HTMLResponse:
        """Handle an HTTPException.

        If the error is a 404, redirect to the index page.

        Args:
            request (Request): HTTP request
            exception (HTTPException): HTTP exception

        Returns:
            HTMLResponse
        """
        logging.warning(f"Handling HTTPException: {exception}")

        is_api_request = request.url.path.startswith("/get")
        error_code = exception.status_code

        logging.info(f"Is API request: {is_api_request}, Error code: {error_code}")

        return self.generateTemplateResponse(
            request=request,
            template="redirect.html",
        )

    async def _weatherApi(self, request: Request) -> WeatherResponse:
        """Serve the weather api.

        Args:
            request (Request): HTTP request

        Returns:
            WeatherResponse: Weather response
        """
        logging.info("Serving weather api")
        ip = request.client.host
        local = self._isLocalIp(ip)
        logging.info(f"Client ip: {ip}. Local: {local}")
        w = await self._weather.getWeather()
        return w.toResponse()

    async def _unsplashApi(self, request: Request) -> UnsplashResponse:
        """Serve the unsplash api.

        Args:
            request (Request): HTTP request

        Returns:
            UnsplashResponse: Unsplash response
        """
        logging.info("Serving unsplash api")
        ip = request.client.host
        local = self._isLocalIp(ip)
        logging.info(f"Client ip: {ip}. Local: {local}")
        u = await self._unsplash.getRandomPhoto()
        logging.info(f"Unsplash response: {u}")
        return u.toResponse()
