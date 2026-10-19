# RPi Homepage

A *(formerly Flask-based)* FastAPI-based dashboard for my Raspberry Pi.

## Background

Ever since I bought a Raspberry Pi 4, I have been installing a lot *(and I mean a lot)* of services, to the point that I had to move some of them to another embedded device *(an Odroid, this time)*.
As of now, the following services are running across the two devices:

- Plex
- Jellyfin
- Radarr, Sonarr, Prowlarr and Bazarr
- Transmission
- Aria2
- File Browser
- Pi-hole
- probably a few more that I can't even remember right now

Given these premises, you can imagine how I could never remember the port and URL path of each service, let alone its IP address.

That's how the RPi homepage was born: a simple, quick way to reach my services and, why not, keep an eye on how the Pi is doing, all in a clean, minimal interface.
The page scales to any screen size: I have tested it on many devices and resolutions.

## Code structure

The whole backend is written in Python using the FastAPI framework.
I moved from Flask to FastAPI because the GitHub dependency bot kept complaining about security issues in Flask, and because I could never find a clean way to structure a Flask app in an OOP style.

The backend is split into a few small modules:

- `rpiserver` creates the FastAPI app, its routes and the scheduled jobs
- `settings` loads the whole configuration from a single TOML file
- `system` periodically samples the host resources through [psutil](https://github.com/giampaolo/psutil) and keeps a short history of them
- `icons` downloads the icons of the services and caches them on disk
- `logs` routes every log *(uvicorn and apscheduler included)* through [loguru](https://github.com/Delgan/loguru)

The front end is written in vanilla JS, without any build step.
I used to write it all in jQuery but, let's be honest, nowadays it's useless: JavaScript has evolved enough to include CSS selectors for DOM elements (can you imagine!), promises (unbelievable!) and HTTP requests (no more Ajax!).
On top of that, CSS now supports transitions and animations natively, making jQuery even more pointless.

### Homepage

My goal was to make a simple, clean, minimal page that displays the most important information at a glance.
To accomplish this, I divided the page into three sections:

1. the top section, displaying the date and time
2. the services section, displaying the links to the services, grouped by category
3. the system section, displaying the status of the host

Behind the clock, a few coloured blobs slowly float around.
They are drawn by a tiny WebGL shader, rendered at a fraction of the screen resolution *(they are blurry anyway)* and capped at 30 fps, so the page doesn't keep the CPU busy.
They replace the random Unsplash background of the previous version: no more API keys, and no more images that make the text unreadable.

Each service gets an icon from the [Lucide](https://lucide.dev/icons) set.
Icons are downloaded once and then served from a local cache, so the page keeps working even without an internet connection.

The links point to the LAN address of the service when the page is opened from the local network, and to the VPN address otherwise.
The local networks are customisable in the settings file.

### System status

The system section shows:

- CPU usage and load average
- CPU temperature, with a warning when it gets too hot
- RAM usage
- disk usage of the configured mount points
- download and upload speed

The resources are sampled in the background at a fixed interval, and each one gets a small chart of its recent history.
The page fetches the data from the `/get/system` endpoint and refreshes at the same interval.

### Deployment

Thanks to FastAPI, the code can be deployed in many ways.
I am currently using the Uvicorn server alone: a more reliable and robust web server such as Nginx could be put in front of it, but I don't think it's necessary for this project.
Uvicorn is more than enough to handle the very few requests this project will ever receive.

If you do put the homepage behind a reverse proxy, add the proxy's address to `forwarded_allow_ips` in the settings, so that the real client IP *(and therefore the LAN/VPN choice)* is still detected correctly.

## Installation

First of all:

1. Clone or download this repo
1. Navigate to the `rpi-homepage/settings/` folder
1. Rename `settings.example.toml` to `settings.toml` and fill it in
   - add a `[[Links]]` table for each service you want to display

Then you can run it either in a container or directly on the host.

### Docker

1. Go back to the main folder
1. Build and start the container with `docker compose up -d --build`
1. Open your browser and navigate to `http://localhost:1234` *(or whatever port you set in the settings file)*
1. Done!

The container uses host networking, so the app can see the real IP of each client and measure the network speed of the host.
The settings folder is mounted read-only, and the icons are cached in a named volume so they survive rebuilds.
Remember to change the `TZ` variable in `compose.yaml` to your timezone.

### Without Docker

1. Go back to the main folder
1. Install the dependencies with `uv sync` *(requires [uv](https://docs.astral.sh/uv/))*
1. Navigate to the `rpi-homepage/` folder
1. Run the script with `uv run rpi-homepage.py`
1. Open your browser and navigate to `http://localhost:1234` *(or whatever port you set in the settings file)*
1. Done!

## Screenshots

![screenshot-1](screenshots/screenshot-1.png)

![screenshot-2](screenshots/screenshot-2.png)

## License

This project is distributed under the MIT license. See [LICENSE.md](LICENSE.md) for more information.
