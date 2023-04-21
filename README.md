# rpi-homepage

A Flask-based dashboard for my RaspberryPi

## Background

Since I bought a RaspberryPi 4, I started installing a lot (and I mean a lot) of services, to the point it's hard to remember the IP for every web interface.

As many do, I quickly installed Plex, PiHole, Transmission, Jellyfin, ZeroTier... and things got messy.
I could never remember how to connect to each service configuration panel.

So this is how _rpi-homepage_ was born. It's a simple, quick, easy way to connect to some important service and why not, get local time and weather in a clean-looking, minimal, interface.
The webpage is completely scalable as I have tested it on many devices and screen resolutions.

## Code structure

This whole backend is coded in Python using Flask.

The front end works on vanilla JS.
Previously it used jQuery but I decided to get rid of it because it looks useless, nowadays.

The weather is fetched from [OpenWeatherMap.com](https://openweathermap.org/) since it's free, fairly correct and reliable.

## Translations

The code supports multi-language for weather forecasts.

The base code is in Italian. To set the interface into a foreign (well, for me at least) language, you have to change the parameter inside _settings.json_ file.

## Installation

In order to use this script, you have to:

1. Clone or download this repo on your computer
1. Navigate to `static/src` folder
1. Rename `settings.example.json` to `settings.json` and provide all necessary info.
1. Rename `links.example.json` to `links.json` and edit it until it fits all your needs.
1. Simply run `rpi-homepage.py` and connect through your browser.
1. Done!

## Screenshots

![screenshot-1](screenshots/screenshot_1.png)
![screenshot-2](screenshots/screenshot_2.png)

## License

This project is distributed under _Attribution 4.0 International (CC BY 4.0)_ license.
