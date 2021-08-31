# rpi-homepage
A flask based dashboard for my RaspberryPi

## Background
Since I bought a RaspberryPi 4, I started installing a lot of services, to the point it's hard to remember every web interface IP.

As many do, I quickly installed Plex, PiHole, Transmission, Jellyfin, ZeroTier... and things got messy. I could never remember how to connect to each service configuration panel.

I also wanted a way to quickly check some stats about my Raspberry, including (but not limiting to) internal temperaure, free hdd space, ram and cpu load...

So this is how *rpi-homepage* born. It's a simple, quick, easy way to check some stats about my Raspberry, connect to some important service and why not, get local time and weather in a clean looking, minimal, interface.

The webpage is completely scalable, I tested it on many devices and screen resolutions. Hover your mouse pointer on data to view what it represents!

## Code structure
This whole backend is coded in Python using Flask. The frontend works on JQuery and communicates with the backend via Ajax

## How it works
Each time the wepage is requested, the backend queries the Raspberry for some internal stats (internal temperature, cpu and ram load, free space on the external HDD, hostname, LAN IP and ZeroTier ip) and loads it in the browser. Sequentially it connects to [OpenWeatherMap](https://openweathermap.org/) to get local weather forecast and generates a background picking colors from a list.

Once loaded, the JQuery scripts calls an endpoint and triggers an internet speed test (provided by [speedtest](https://www.speedtest.net/)).

Every 30 seconds the internal infos are updated. Every 15 minutes a new background is generated, the weather forecast gets updated and a new speedtest is executed.

## Translations
The code support multi language translations for items descriptions and weather forecast.

The base code is in Italian. In order to set the interface into a foreign (well, for me at least) language, you have to change the parameter inside *settings.json* file. You will also have to provide the corrisponding *translations.json* file. As now, only english is available.

## Set Up
In order to use this script, you have to:
1. Clone or downlond this repo in your computer
2. Rename `settings.example.json` to `settings.json` and provide all necessary info.
3. Rename `links.example.json` to `links.json` and edit it until it fits all your needs.
4. Simply run `rpi-homepage.py` and connect through your browser.
5. Done!

# Screenshots
![screenshot](https://github.com/lorossi/rpi-homepage/blob/master/screenshots/screenshot_1.png)
![screenshot](https://github.com/lorossi/rpi-homepage/blob/master/screenshots/screenshot_2.png)

# License
This project is distributed under *Attribution 4.0 International (CC BY 4.0)* license.
