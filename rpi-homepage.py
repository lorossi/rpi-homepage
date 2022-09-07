import ujson
import logging
import requests

from datetime import datetime
from random import choice, randint
from flask import Flask, render_template, jsonify, request


app = Flask(__name__)


def loadSettings(path: str = "static/src/settings.json") -> dict:
    """Load settings from file.

    Args:
        path (str, optional): Settings file path. \
            Defaults to "static/src/settings.json".

    Returns:
        dict: Settings dictionary
    """
    logging.info("Loading settings")
    with open(path, "r") as f:
        return ujson.load(f)


def loadLinks(
    base_ip: str = "192.168.1.1", path: str = "static/src/links.json"
) -> dict:
    """Loads links from settings file.

    Args:
        base_ip (str): Base ip (either local or zerotier ip)
        path (str, optional): Path of links file. \
            Defaults to "static/src/links.json".

    Returns:
        dict: [description]
    """
    logging.info("Loading links")
    with open(path, "r") as f:
        links = ujson.load(f)

    return [
        {
            "href": f"http://{base_ip}:{link['port']}/{link.get('path', '')}",
            "name": link["display_name"],
        }
        for link in links
    ]


def loadColors(path: str = "static/src/colors.json") -> dict:
    """Loads colors from file.

    Args:
        path (str, optional): Colors file path. \
            Defaults to "static/src/colors.json".

    Returns:
        dict
    """
    logging.info("Loading colors")
    with open(path, "r") as f:
        return ujson.load(f)


def getGradient() -> str:
    """Creates a css gradient string

    Returns:
        str
    """
    logging.info("Getting a gradient")
    colors = loadColors()
    # pick two colors
    from_c, to_c = choice(colors)
    # set rotation
    angle = randint(0, 360)

    return f"linear-gradient({angle}deg, {from_c}, {to_c});"


def getWeather() -> str:
    """Loads weather from OpenWeatherMap

    Returns:
        str
    """
    logging.info("Getting weather")
    # load parameters from file
    settings = loadSettings()
    api_key = settings["OpenWeatherMap"]["api_key"]
    city = settings["OpenWeatherMap"]["city"]
    language = settings["OpenWeatherMap"].get("language", "it")
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


@app.route("/")
@app.route("/homepage")
def index() -> render_template:
    """Renders homepage

    Returns:
        render_template
    """
    # load request ip
    ip = request.remote_addr
    logging.info(f"Serving homepage to {ip}")
    settings = loadSettings()
    # format links according to request
    # (either local, from lan or from zerotier)
    if ip[:3] == "127":
        base_ip = "127.0.0.1"
    elif ip[:3] == "192":
        base_ip = settings["Server"].get("lan-ip")
    else:
        base_ip = settings["Server"].get("zerotier-ip")

    links = loadLinks(base_ip=base_ip)
    # get a gradient
    gradient = getGradient()
    # return all to main template
    return render_template("index.html", links=links, gradient=gradient)


@app.route("/get/weather/", methods=["GET"])
def get_weather() -> str:
    """Weather endpoint

    Returns:
        str
    """
    # load request ip
    ip = request.remote_addr
    logging.info(f"Serving weather to {ip}")
    # weather endpoint
    return jsonify(getWeather())


@app.route("/get/greetings/", methods=["GET"])
def get_greetings() -> str:
    """Greetings endpoint

    Returns:
        str
    """
    ip = request.remote_addr
    logging.info(f"Serving greetings to {ip}")

    settings = loadSettings()
    hour = datetime.now().hour

    if hour <= 4:
        greeting = settings["Server"]["greetings"]["night"]
    elif hour <= 12:
        greeting = settings["Server"]["greetings"]["morning"]
    elif hour <= 18:
        greeting = settings["Server"]["greetings"]["afternoon"]
    else:
        greeting = settings["Server"]["greetings"]["evening"]

    # weather endpoint
    return jsonify(
        {
            "message": greeting,
        }
    )


def main():
    logging.basicConfig(
        filename=__file__.replace(".py", ".log"),
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        filemode="w",
    )

    logging.info("Script started")

    settings = loadSettings()
    app.run(
        host=settings["Server"]["host"],
        port=settings["Server"]["port"],
        debug=settings["Server"]["debug"],
    )


if __name__ == "__main__":
    main()
