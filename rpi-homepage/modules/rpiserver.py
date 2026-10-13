"""Module for the homepage web app."""

import ipaddress
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

import toml
import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from loguru import logger
from starlette.exceptions import HTTPException

from modules.icons import IconService
from modules.settings import ServerSettings
from modules.system import SystemResponse, SystemService

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Iterable

IPNetwork = ipaddress.IPv4Network | ipaddress.IPv6Network


def load_settings(path: str) -> ServerSettings:
    """Load the settings from the `RPiServer` table of a toml file.

    Args:
        path (str): Path to the settings file.

    Returns:
        ServerSettings
    """
    logger.info("Loading settings from {}", path)
    try:
        settings = ServerSettings.from_toml(path, "RPiServer")
    except FileNotFoundError, toml.TomlDecodeError:
        logger.exception("Could not load settings from {}", path)
        raise

    logger.info("Loaded {} links", len(settings.links))
    return settings


def is_local_ip(ip: str, networks: Iterable[IPNetwork]) -> bool:
    """Check if the ip belongs to one of the local networks.

    Args:
        ip (str): IP address
        networks (Iterable[IPNetwork]): Local networks

    Returns:
        bool: False if the ip is not valid
    """
    try:
        address = ipaddress.ip_address(ip)
    except ValueError:
        return False
    return any(address in net for net in networks)


def create_app(settings: ServerSettings) -> FastAPI:
    """Create the homepage app.

    Args:
        settings (ServerSettings): The server settings.

    Returns:
        FastAPI
    """
    local_networks = tuple(ipaddress.ip_network(n) for n in settings.local_networks)
    logger.info("Local networks: {}", local_networks)
    system = SystemService(settings.system)
    icons = IconService(
        settings.icons,
        (link.icon for link in settings.links if link.icon),
    )
    templates = Jinja2Templates(directory="templates")
    scheduler = AsyncIOScheduler()

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
        # awaited before the server starts serving requests
        await icons.prefetch()
        scheduler.add_job(system.sample, "interval", seconds=system.sample_interval)
        # retry the icons that could not be downloaded (no-op once all loaded)
        scheduler.add_job(icons.prefetch, "interval", seconds=icons.retry_interval)
        scheduler.start()
        yield
        scheduler.shutdown()

    app = FastAPI(lifespan=lifespan)
    app.mount("/static", StaticFiles(directory="static"), name="static")

    def is_local_request(request: Request) -> bool:
        """Check if the request comes from the local network, logging its ip."""
        ip = request.client.host if request.client is not None else ""
        local = is_local_ip(ip, local_networks)
        logger.info("Client ip: {}. Local: {}", ip, local)
        return local

    @app.get("/")
    async def index_page(request: Request) -> Response:
        """Serve the index page."""
        logger.info("Serving index page")
        local = is_local_request(request)

        # format the links according to the request (either local or remote)
        groups = {
            category: [
                link.get_properties_dict(lan=local, icon_markup=icons.get(link.icon))
                for link in links
            ]
            for category, links in settings.grouped_links().items()
        }
        return templates.TemplateResponse(request, "index.html", {"groups": groups})

    @app.get("/get/system")
    async def system_api(request: Request) -> SystemResponse:
        """Serve the system api."""
        logger.debug("Serving system api")
        is_local_request(request)
        return system.get_status()

    @app.exception_handler(HTTPException)
    async def error_page(request: Request, exception: HTTPException) -> Response:
        """Handle an HTTPException.

        API requests get a JSON error, every other request is redirected
        to the index page.
        """
        logger.warning("Handling HTTPException: {}", exception)

        is_api_request = request.url.path.startswith("/get")
        error_code = exception.status_code

        logger.info("Is API request: {}, Error code: {}", is_api_request, error_code)

        if is_api_request:
            return JSONResponse(
                status_code=error_code,
                content={"detail": exception.detail},
            )

        return RedirectResponse("/")

    return app


async def serve(settings_path: str = "settings/settings.toml") -> None:
    """Load the settings and serve the homepage until stopped.

    Args:
        settings_path (str, optional): Path to the settings file.
            Defaults to "settings/settings.toml".
    """
    settings = load_settings(settings_path)
    config = uvicorn.Config(
        create_app(settings),
        host="0.0.0.0",  # noqa: S104 - the homepage is served to the whole LAN
        port=settings.port,
        loop="asyncio",
        # logs are routed to loguru, see modules.logs
        log_config=None,
        # the client ip is taken from X-Forwarded-For only if the request
        # comes from a trusted proxy
        proxy_headers=bool(settings.forwarded_allow_ips),
        forwarded_allow_ips=settings.forwarded_allow_ips,
    )
    logger.info("Starting server on port {}", settings.port)
    await uvicorn.Server(config).serve()
    logger.info("Server stopped")
