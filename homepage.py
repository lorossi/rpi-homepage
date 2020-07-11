import requests
import json
import subprocess
import psutil
import shutil
import speedtest
from random import sample, randint, seed, shuffle
from flask import Flask, render_template, request, jsonify, url_for


# returns the best color combination to make a nice gradient
def getGradient(settings):
    colors = settings["Interface"]["colors"]

    colors_copy = [c for c in colors]
    shuffle(colors_copy)

    selected = [0, 0]
    selected[0] = colors_copy.pop(0)

    hue = calculateHue(selected[0])
    found = False
    while not found:
        attempt = colors_copy.pop(0)
        attempt_hue = calculateHue(attempt)
        angle_between = abs(attempt_hue - hue)
        if  angle_between < 90 and angle_between > 20:
            selected[1] = attempt
            found = True
        else:
            if len(colors_copy) == 0:
                colors_copy = [c for c in colors]
                shuffle(colors_copy)


    angle = randint(0, 360)
    average, brightness = averageColor(selected)

    gradient = {
        "from": selected[0],
        "to": selected[1],
        "angle": angle,
        "string": f"linear-gradient({angle}deg, {selected[0]}, {selected[1]})",
        "brightness": brightness,
        "average_color": average
    }

    return gradient

# calculates average between two colors and its brightness
def averageColor(colors):
    r = [int(c[1:3], 16) for c in colors]
    g = [int(c[3:5], 16) for c in colors]
    b = [int(c[5:7], 16) for c in colors]

    average = []
    average.append((r[0] + r[1]) / 2)
    average.append((g[0] + g[1]) / 2)
    average.append((b[0] + b[1]) / 2)
    brightness = (0.2126 * average[0] + 0.7152 * average[1] + 0.0722 * average[2])

    r_hex = []
    for a in average:
        r_hex.append(format(int(a), 'x'))

    average_color = "#" + "".join(r_hex).upper()
    return average_color, brightness

# calculates the hue (angle) of a color
def calculateHue(color):
    r = int(color[1:3], 16) / 255
    g = int(color[3:5], 16) / 255
    b = int(color[5:7], 16) / 255

    minval = min(r, g, b)
    maxval = max(r, g, b)
    if (r > g and r > b):
        # red is max
        hue = (g - b) / (maxval - minval)
    elif (g > r and g > b):
        # green is max
        hue = 2 + (b - r) / (maxval - minval)
    elif (b > r and b > g):
        # blue is max
        hue = 4 + (r - g) / (maxval - minval)
    else:
        hue = 0

    hue *= 60;
    if (hue < 0): hue += 360

    return hue

# selects text color and background_color according to the chosen color palette
def returnColor(brightness, settings):
    threshold_brightness = settings["Interface"]["threshold_brightness"]

    color = {}
    if brightness > threshold_brightness:
        color["text_color"] = "#000000"
    else:
        color["text_color"] = "#FFFFFF"

    return color

# load ips and hostnames from Raspberry web interface
def loadIps():
    # load all ips
    ips = {}

    p = subprocess.Popen("hostname -I".split(" "), stdout=subprocess.PIPE).stdout.read()
    rasp_ip = p.decode("utf-8").rstrip().split(" ")
    ips["lanip"] = rasp_ip[0]

    # load all networks and extract ip of the first one
    p = subprocess.Popen("sudo zerotier-cli listnetworks".split(), stdout=subprocess.PIPE).stdout.read()
    zerotier_ip = p.decode("utf-8").rstrip().split(" ")[-1].split("/")[-2]
    ips["zerotierip"] = zerotier_ip

    # load hostname
    p = subprocess.Popen(["hostname"], stdout=subprocess.PIPE).stdout.read()
    hostname = p.decode("utf-8").rstrip()
    ips["hostname"] = hostname

    return ips

# loads links from file
def loadLinks(request_ip, path="src/links.json"):
    with open(path) as json_file:
        links = json.load(json_file)

    ips = loadIps()

    if request_ip[:9] == "192.168.1":
        for l in links:
            l["ip"] = ips["lanip"] # lan
    else:
        for l in links:
            l["ip"] = ips["zerotierip"] # zerotier
    return links

def loadSettings(path="src/settings.json"):
    with open(path) as json_file:
        settings = json.load(json_file)
    return settings

def loadTranslations(lang, path="src/translations.json"):
    with open(path) as json_file:
        translations = json.load(json_file)
    return translations[lang]

# get weather from OpenWeatherMap
def getWeather(settings):
    open_weather_api_key = settings["OpenWeatherMap"]["api_key"]
    city = settings["OpenWeatherMap"]["city"]
    lang = settings["OpenWeatherMap"]["lang"]

    request_url = (
                    f"http://api.openweathermap.org/data/2.5/weather?"
                    f"q={city}&appid={open_weather_api_key}"
                    f"&units=metric&lang={lang}"
                )

    response = requests.get(request_url)
    json_respose = response.json()

    if json_respose["cod"] != 200:
        weather = {
            "cod" : json_respose["cod"]
        }

    else:
        temp = json_respose["main"]["temp"]
        hum = json_respose["main"]["humidity"]
        description = json_respose["weather"][0]["description"]
        weather = {
          "cod": 200,
          "city": city.lower(),
          "temperature": f"{temp}°C",
          "humidity": f"{hum}%",
          "description": description
        }

    return weather

# load all relevant data from the Raspberry
def loadData(settings):
    folder = settings["Interface"]["folder"]
    ips = loadIps()

    raw_temperature = round(psutil.sensors_temperatures()['cpu-thermal'][0][1], 1)
    raw_cpu = psutil.cpu_percent()
    raw_ram = psutil.virtual_memory()[2]

    data = [
        {
            "name": "temperature",
            "string": f"{raw_temperature}°C",
            "hidden": "temperatura"
        },
        {
            "name": "cpuram",
            "string": f"{raw_cpu}% {raw_ram}%",
            "hidden": "cpu ram"
        },
        {
            "name": "hostname",
            "string": ips["hostname"],
            "hidden": "hostname"
        },
        {
            "name": "ip",
            "string": ips["lanip"],
            "hidden": "ip lan"
        },
        {
            "name": "speedtest",
            "string": "",
            "hidden": "dowload upload ping"
        }
    ]

    # if the user specified a particular folder
    if folder:
        raw_free_space = int(shutil.disk_usage(folder)[2] / (2**30))
        data.insert(-3, {
            "name": "free_space",
            "string": f"{raw_free_space}GB",
            "hidden": "spazio libero"
            }
        )


    # if we found a zerotier ip, we want to add it to second last position
    if ips["zerotierip"]:
        data.insert(-1,
            {
                "name": "ip",
                "string": ips["zerotierip"],
                "hidden": "ip zerotier"
            }
        )

    if settings["Interface"]["lang"] != "it":
        translations = loadTranslations(settings["Interface"]["lang"])
        for d in data:
            for t in translations:
                if d["hidden"] == t:
                    d["hidden"] = translations[t]

    return data


# get internet connection speed from speedtest
def getSpeed():
    s = speedtest.Speedtest()
    s.get_best_server()

    s.upload(threads=4)
    s.download(threads=4)

    res = s.results.dict()

    upload = int(res['upload'] / (1024 * 1024))
    download = int(res['download'] / (1024 * 1024))
    ping = int(res['ping'])
    string = f"{download}Mb/s {upload}Mb/s {ping}ms"


    speed = {
            "download": download,
            "upload": upload,
            "ping": ping,
            "string": string
        }

    return speed


app = Flask(__name__)
@app.route('/')
@app.route('/homepage')
def index():
    settings = loadSettings()

    gradient = getGradient(settings)
    color = returnColor(gradient["brightness"], settings)
    request_ip = request.remote_addr
    links = loadLinks(request_ip)
    data = loadData(settings)
    return render_template('index.html', gradient=gradient,
                            color=color, links=links, data=data)


@app.route("/getweather/", methods=['POST'])
def get_weather():
    settings = loadSettings()

    weather = getWeather(settings)
    return jsonify(weather)


@app.route("/getimage/", methods=['POST'])
def get_image():
    settings = loadSettings()

    gradient = getGradient(settings)
    color = returnColor(gradient["brightness"], settings)
    response = {"gradient": gradient, "color": color}
    return jsonify(response)


@app.route("/getspeed/", methods=['POST'])
def get_speed():
    speedtest = getSpeed()
    return jsonify(speedtest)


@app.route("/getdata/", methods=['POST'])
def get_data():
    settings = loadSettings()

    data = loadData(settings)
    data = [d for d in data if not d["name"] == "speedtest"]
    return jsonify(data)


if __name__ == '__main__':
    settings = loadSettings()
    app.run(host=settings["Server"]["host"],
            port=settings["Server"]["port"],
            debug=settings["Server"]["debug"])

    psutil.cpu_percent() # needed because the first measurment is always wrong
    seed() # random seeding
