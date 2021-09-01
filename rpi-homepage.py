
import ujson
import requests

from random import choice, randint
from flask import Flask, render_template, jsonify, request


app = Flask(__name__)


def loadSettings(path="static/src/settings.json"):
    """ simply loads settings """
    with open(path, "r") as f:
        return ujson.load(f)


def loadLinks(base_ip, path="static/src/links.json"):
    """ loads and returns list of formatted links from file"""
    with open(path, "r") as f:
        links = ujson.load(f)

    return [{
            "href": f"http://{base_ip}:{link['port']}/{link.get('path', '')}",
            "name": link["display_name"],
            } for link in links]


def loadColors(path="static/src/colors.json"):
    """ simply loads colors """
    with open(path, "r") as f:
        return ujson.load(f)


def getGradient():
    """ creates a css gradient with rotation """
    colors = loadColors()
    # pick two colors
    from_c, to_c = choice(colors)
    # set rotation
    angle = randint(0, 360)

    return f"linear-gradient({angle}deg, {from_c}, {to_c});"


def getWeather():
    """ loads weather from  OpenWeatherMap """
    # load parameters from file
    settings = loadSettings()
    api_key = settings["OpenWeatherMap"]["api_key"]
    city = settings["OpenWeatherMap"]["city"]
    lang = settings["OpenWeatherMap"]["lang"]
    # pack the url
    request_url = (
        f"http://api.openweathermap.org/data/2.5/weather?"
        f"q={city}&appid={api_key}"
        f"&units=metric&lang={lang}"
    )
    # make the request
    json_respose = requests.get(request_url).json()

    if json_respose["cod"] != 200:
        # negative response, just return the error code
        return {
            "cod": json_respose["cod"],
        }

    # otherwise return an hefty dict
    temp = json_respose["main"]["temp"]
    hum = json_respose["main"]["humidity"]
    description = json_respose["weather"][0]["description"]
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
    settings = loadSettings()
    # load request ip
    ip = request.remote_addr
    # format links according to request
    # (either local, from lan or from zerotier)
    if ip[:3] == "127":
        base_ip = "127.0.0.1"
    elif ip[:3] == "192":
        base_ip = settings["Server"].get("lan_ip")
    else:
        base_ip = settings["Server"].get("lan_ip")

    links = loadLinks(base_ip)
    # get a gradient
    gradient = getGradient()
    # return all to main template
    return render_template("index.html", links=links, gradient=gradient)


@app.route("/get/weather/", methods=["GET"])
def get_weather():
    # weather endpoint
    return jsonify(getWeather())


if __name__ == "__main__":
    settings = loadSettings()
    app.run(host=settings["Server"]["host"],
            port=settings["Server"]["port"],
            debug=settings["Server"]["debug"])
