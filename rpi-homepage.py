"""This module contains the logic to handle the homepage."""
from __future__ import annotations

import logging
from datetime import datetime
from random import choice, randint

import requests
import ujson

from flask import Flask, jsonify, render_template, request
from flask_classful import FlaskView, route


from modules.links import Link
from modules.gradients import Gradient

app = Flask(__name__)


class Server(FlaskView):
    """This class contains the logic to handle the homepage."""

    def __init__(
        self,
        settings_path: str = "static/src/settings.json",
        links_path="static/src/links.json",
        colors_path="static/src/colors.json",
    ):
        """Initialize the server.

        Args:
            settings_path (str, optional): Path to settings file. \
                Defaults to "static/src/settings.json".
            links_path (str, optional): Path to links file. \
                Defaults to "static/src/links.json".
            colors_path (str, optional): Path to colors file. \
                Defaults to "static/src/colors.json".
        """
        self._settings_path = settings_path
        self._links_path = links_path
        self._colors_path = colors_path

        self._settings = self._loadSettings()
        self._links = self._loadLinks()
        self._colors = self._loadColors()

    def _loadSettings(self) -> dict:
        with open(self._settings_path, "r") as f:
            return ujson.load(f)

    def _loadLinks(self) -> list[dict[str, str]]:
        with open(self._links_path, "r") as f:
            links_dict = ujson.load(f)

        return [Link.fromJSON(link) for link in links_dict]

    def _loadColors(self) -> dict:
        with open(self._colors_path, "r") as f:
            gradients_list = ujson.load(f)

        return [Gradient.fromList(gradient) for gradient in gradients_list]

    def _getGradient(self) -> str:
        """Create a css gradient string.

        Returns:
            str
        """
        logging.info("Getting a gradient")
        # pick two colors
        color = choice(self._colors)
        # set rotation
        angle = randint(0, 360)
        return color.getCss(angle)

    def _getWeather(self) -> str:
        """Load weather from OpenWeatherMap.

        Returns:
            str
        """
        logging.info("Getting weather")
        # load parameters from file
        api_key = self._settings["OpenWeatherMap"]["api_key"]
        city = self._settings["OpenWeatherMap"]["city"]
        language = self._settings["OpenWeatherMap"].get("language", "en")
        # pack the url
        request_url = (
            f"http://api.openweathermap.org/data/2.5/weather?"
            f"q={city}&appid={api_key}"
            f"&units=metric&lang={language}"
        )
        # make the request
        json_response = requests.get(request_url).json()

        if json_response["cod"] != 200:
            # negative response, just return the error code
            return {
                "cod": json_response["cod"],
            }

        # otherwise return an hefty dict
        temp = json_response["main"]["temp"]
        hum = json_response["main"]["humidity"]
        description = json_response["weather"][0]["description"]
        return {
            "cod": 200,
            "city": city.lower(),
            "temperature": f"{round(temp, 1)}°C",
            "humidity": f"{hum}%",
            "description": description,
        }

    def _isLocalIp(self, ip: str) -> bool:
        """Check if an ip is local.

        Args:
            ip (str): Ip to check.

        Returns:
            bool
        """
        return ip.startswith("192.168.") or ip.startswith("127.")

    def _isZerotierIp(self, ip: str) -> bool:
        """Check if an ip is local.

        Args:
            ip (str): Ip to check.

        Returns:
            bool
        """
        return not self._isLocalIp(ip)

    @route("/")
    def index(self) -> render_template:
        """Render homepage.

        Returns:
            render_template
        """
        # load request ip
        ip = request.remote_addr
        logging.info(f"Serving homepage to {ip}")

        # format links according to request
        # (either local, from lan or from zerotier)
        links = [link.getPropertiesDict(self._isZerotierIp(ip)) for link in self._links]
        # get a gradient
        gradient = self._getGradient()
        # return all to main template
        return render_template("index.html", links=links, gradient=gradient)

    @route("/get/weather/")
    def get_weather(self) -> str:
        """Weather endpoint.

        Returns:
            str
        """
        # load request ip
        ip = request.remote_addr
        logging.info(f"Serving weather to {ip}")
        # weather endpoint
        return jsonify(self._getWeather())

    @route("/get/greetings/")
    def get_greetings(self) -> str:
        """Greetings endpoint.

        Returns:
            str
        """
        # load request ip
        ip = request.remote_addr
        logging.info(f"Serving greetings to {ip}")

        hour = datetime.now().hour

        if hour < 6:
            greeting = self._settings["Greetings"]["night"]
        elif hour < 12:
            greeting = self._settings["Greetings"]["morning"]
        elif hour < 18:
            greeting = self._settings["Greetings"]["afternoon"]
        else:
            greeting = self._settings["Greetings"]["evening"]

        # weather endpoint
        return jsonify(
            {
                "message": greeting,
            }
        )

    @property
    def host(self) -> str:
        """Get the host from settings."""
        return self._settings["Server"]["host"]

    @property
    def port(self) -> int:
        """Get the port from settings."""
        return self._settings["Server"]["port"]

    @property
    def debug(self) -> bool:
        """Get the debug flag from settings."""
        return self._settings["Server"]["debug"]


Server.register(app, route_base="/")


def main():
    """Program entry point, starting the server."""
    logging.basicConfig(
        filename=__file__.replace(".py", ".log"),
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filemode="w",
    )

    logging.info("Starting server")
    s = Server()
    app.run(host=s.host, port=s.port, debug=s.debug)


if __name__ == "__main__":
    main()
