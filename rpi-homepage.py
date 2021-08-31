
import ujson
from flask import Flask, render_template, jsonify, request


app = Flask(__name__)


def loadSettings(path="static/src/settings.json"):
    with open(path, "r") as f:
        return ujson.load(f)


def loadLinks(base_ip, path="static/src/links.json"):
    with open(path, "r") as f:
        links = ujson.load(f)

    return [{
            "href": f"http://{base_ip}:{link['port']}/{link.get('path', '')}",
            "name": link["display_name"],
            } for link in links]


def getWeather():
    return None


@app.route('/')
@app.route('/homepage')
def index():
    settings = loadSettings()

    ip = request.remote_addr

    if ip[:3] == "127":
        base_ip = "127.0.0.1"
    elif ip[:3] == "192":
        base_ip = settings["Server"]["lan_ip"]
    else:
        base_ip = settings["Server"]["zerotier_ip"]

    links = loadLinks(base_ip)

    return render_template("index.html", links=links)


@app.route("/getweather/", methods=['POST'])
def get_weather():
    settings = loadSettings()
    weather = getWeather(settings)
    return jsonify(weather)


if __name__ == '__main__':
    settings = loadSettings()
    app.run(host=settings["Server"]["host"],
            port=settings["Server"]["port"],
            debug=settings["Server"]["debug"])
