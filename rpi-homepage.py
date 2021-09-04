
import ujson
import logging
import requests

from datetime import datetime
from random import choice, randint
from flask import Flask, render_template, jsonify, request


app = Flask(__name__)


def loadSettings(path="static/src/settings.json"):
    """ simply loads settings """
    logging.info("Loading settings")
    with open(path, "r") as f:
        return ujson.load(f)


def loadLinks(base_ip, path="static/src/links.json"):
    """ loads and returns list of formatted links from file"""
    logging.info("Loading links")
    with open(path, "r") as f:
        links = ujson.load(f)

    return [{
            "href": f"http://{base_ip}:{link['port']}/{link.get('path', '')}",
            "name": link["display_name"],
            } for link in links]


def loadColors(path="static/src/colors.json"):
    """ simply loads colors """
    logging.info("Loading colors")
    with open(path, "r") as f:
        return ujson.load(f)


def getGradient():
    """ creates a css gradient with rotation """
    logging.info("getting a gradient")
    colors = loadColors()
    # pick two colors
    from_c, to_c = choice(colors)
    # set rotation
    angle = randint(0, 360)

    return f"linear-gradient({angle}deg, {from_c}, {to_c});"


def getWeather():
    """ loads weather from  OpenWeatherMap """
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
        "temperature": f"{temp}°C",
        "humidity": f"{hum}%",
        "description": description,
    }


@app.route("/")
@app.route("/homepage")
def index():
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

    links = loadLinks(base_ip)
    # get a gradient
    gradient = getGradient()
    # return all to main template
    return render_template("index.html", links=links, gradient=gradient)


@app.route("/get/weather/", methods=["GET"])
def get_weather():
    # load request ip
    ip = request.remote_addr
    logging.info(f"Serving weather to {ip}")
    # weather endpoint
    return jsonify(getWeather())


@app.route("/get/greetings/", methods=["GET"])
def get_greetings():
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
    return jsonify({
        "message": greeting,
    })


if __name__ == "__main__":
    logging.basicConfig(
        filename=__file__.replace(".py", ".log"),
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        filemode="w"
    )

    logging.info("Script started")

    settings = loadSettings()
    app.run(host=settings["Server"]["host"],
            port=settings["Server"]["port"],
            debug=settings["Server"]["debug"])
