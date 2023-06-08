"""Module for the RPiServer class."""
from __future__ import annotations

import logging
import random
from datetime import datetime

import toml

from modules.gradients import Gradient
from modules.greetings import Greeting, GreetingResponse
from modules.links import Link
from modules.server import HTMLResponse, Request, Server
from modules.settings import ServerSettings
from modules.weather import WeatherResponse, WeatherService


class RPiServer(Server):
    """RPiServer class, used to represent the server."""

    _settings: ServerSettings
    _gradients: list[Gradient]
    _links: list[Link]
    _greetings: list[Greeting]

    _weather: WeatherService

    def __init__(self, settings_path: str = "settings/settings.toml") -> RPiServer:
        """Create a RPiServer object.

        Args:
            settings_path (str, optional): Path to the settings file.
            Defaults to "settings/settings.toml".

        Returns:
            RPiServer
        """
        logging.info("Initializing RPiServer")
        self.settings_path = settings_path

        self.loadSettings()
        self._loadAttributes()

        logging.info("Initializing RPiServer routes")
        self.addStaticRoute("/static", "static")
        self.addTemplateFolder("templates")
        self.addRoute("/", self._indexPage)
        self.addRoute("/get/weather", self._weatherApi)
        self.addRoute("/get/greetings", self._greetingApi)
        self.addHTTPExceptionRoute(self._indexPage)

        logging.info("Initializing weather")
        self._weather = WeatherService()

    def _loadAttributes(self) -> None:
        """Load the gradients and links from the settings file."""
        logging.info("Loading RPiServer attributes")

        logging.info("Loading gradients")
        with open(self._settings.gradients_path, "r") as f:
            gradients_list = toml.load(f)
        self._gradients = [
            Gradient.fromList(gradient) for gradient in gradients_list["Gradients"]
        ]

        logging.info("Loading links")
        with open(self._settings.links_path, "r") as f:
            links_dict = toml.load(f)
        self._links = [Link.fromDict(link) for link in links_dict["Links"]]

        logging.info("Loading greetings")
        with open(self._settings.greetings_path, "r") as f:
            greetings_list = toml.load(f)
        self._greetings = [
            Greeting.fromDict(greeting) for greeting in greetings_list["Greetings"]
        ]

    def _isLocalIp(self, ip: str) -> bool:
        """Check if the ip is local.

        Args:
            ip (str): IP address

        Returns:
            bool
        """
        return ip.startswith("192.168.1") or ip.startswith("127.0.0")

    def _getGradient(self) -> str:
        """Create a css gradient string.

        Returns:
            str
        """
        logging.info("Getting a gradient")
        gradient = random.choice(self._gradients)
        return gradient.getCSSString()

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
        # get a gradient
        gradient = self._getGradient()
        # return the page
        return self.generateTemplateResponse(
            request=request,
            template="index.html",
            links=links,
            gradient=gradient,
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

    async def _greetingApi(self, request: Request) -> GreetingResponse:
        """Serve the greeting api.

        Args:
            request (Request): HTTP request

        Returns:
            GreetingResponse: Greeting response
        """
        logging.info("Serving greeting api")
        ip = request.client.host
        local = self._isLocalIp(ip)
        logging.info(f"Client ip: {ip}. Local: {local}")
        g = self._getGreeting()
        return g.toResponse()
