"""Module for the Server class."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

import toml
import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler as Scheduler
from fastapi import APIRouter, FastAPI
from fastapi import Request as FastAPIRequest
from fastapi.responses import HTMLResponse
from fastapi.responses import Response as FastAPIResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

from modules.settings import ServerSettings

if TYPE_CHECKING:
    from collections.abc import Callable

    from apscheduler.job import Job

logger = logging.getLogger(__name__)


class Request(FastAPIRequest):
    """Mask for FastAPIRequest class."""


class HTTPException(StarletteHTTPException):
    """Mask for StarletteHTTPException class."""


class HTMLResponse(HTMLResponse):
    """Mask for HTMLResponse class."""


# alias (not a mask) so that template responses are still instances of it
Response = FastAPIResponse


class Server:
    """The Server class.

    This class is not meant to be instantiated; it is meant to be inherited from.
    """

    _fastapi_app: FastAPI
    _router: APIRouter
    _scheduler: Scheduler
    _templates: Jinja2Templates
    _settings: ServerSettings
    _settings_path: str
    _schedules: dict[Callable, Job]

    def __init__(self) -> None:
        """Instantiate a new Server object.

        Throws an error if instantiated directly.
        """
        msg = "Server is an abstract class"
        raise NotImplementedError(msg)

    def __init_subclass__(cls) -> None:
        """Initialize the subclass.

        Args:
            cls (Server): The subclass.
        """
        logger.info("Initializing subclass %s", cls.__name__)
        cls._fastapi_app = FastAPI()
        cls._router = APIRouter()
        cls._scheduler = Scheduler()
        cls._schedules = {}

    def load_settings(self) -> ServerSettings:
        """Load the settings."""
        logger.info("Loading settings")
        try:
            settings = ServerSettings.from_toml(
                self._settings_path,
                self.__class__.__name__,
            )
        except FileNotFoundError, toml.TomlDecodeError:
            logger.exception("Could not load settings from %s", self._settings_path)
            raise

        logger.info("Loaded settings")
        return settings

    def _setup_uvicorn(self, port: int, logging_config: str) -> uvicorn.Server:
        config = uvicorn.Config(
            self.app,
            host="0.0.0.0",  # noqa: S104 - the homepage is served to the whole LAN
            port=port,
            loop="asyncio",
            log_config=logging_config,
        )
        return uvicorn.Server(config=config)

    def add_schedule_interval(self, interval: float, method: Callable) -> None:
        """Add a schedule interval.

        Args:
            interval (float): The interval in seconds.
            method (Callable): The method to call.
        """
        logger.info("Adding schedule interval %s %s", interval, method)
        self._schedules[method] = self._scheduler.add_job(
            method,
            "interval",
            seconds=interval,
        )
        logger.info("Added schedule interval")

    def remove_schedule(self, method: Callable) -> None:
        """Remove a schedule.

        Args:
            method (Callable): The method to remove.
        """
        logger.info("Removing schedule %s", method)
        self._schedules[method].remove()
        del self._schedules[method]
        logger.info("Removed schedule")

    def add_route(
        self,
        path: str,
        f: Callable,
        methods: list[str] | None = None,
    ) -> None:
        """Add a route to the server.

        Args:
            path (str): The path of the route.
            f (function): The function to execute.
            methods (list[str], optional): The methods of the route.
                Defaults to ["GET"].
                possible values: ["GET", "POST", "PUT", "DELETE"].
        """
        if methods is None:
            methods = ["GET"]

        logger.info("Adding route %s %s %s", path, f, methods)

        self._router.add_api_route(
            path=path,
            endpoint=f,
            methods=methods,
        )
        logger.info("Added route")

    def add_static_route(
        self, path: str, directory: str, *, html: bool = False
    ) -> None:
        """Add a static route to the server.

        Args:
            path (str): The path of the route.
            directory (str): The directory of the static files.
            html (bool, optional): Whether or not the static files are html files.
                Defaults to False.
        """
        logger.info("Adding static route %s %s", path, directory)
        self._fastapi_app.mount(
            path,
            StaticFiles(directory=directory, html=html),
            name="static",
        )
        logger.info("Added static route")

    def add_http_exception_route(self, f: Callable) -> None:
        """Add an error route to the server.

        Args:
            f (function): The function to execute.
        """
        logger.info("Adding error route %s", f)
        self._fastapi_app.add_exception_handler(StarletteHTTPException, f)
        logger.info("Added error route")

    def add_template_folder(self, directory: str) -> None:
        """Add a template folder to the server.

        Args:
            directory (str): The directory of the template folder.
        """
        logger.info("Adding template folder %s", directory)
        self._templates = Jinja2Templates(directory=directory)
        logger.info("Added template folder")

    def generate_template_response(
        self,
        request: Request,
        template: str,
        **kwargs: object,
    ) -> Response:
        """Generate a template.

        Args:
            request (Request): The request.
            template (str): The template name.
            **kwargs: The template arguments.

        Returns:
            Response: The generated template.
        """
        logger.info("Generating template %s %s", template, kwargs)
        return self._templates.TemplateResponse(request, template, kwargs)

    async def start_async(self) -> None:
        """Start the server."""
        if not hasattr(self, "_settings"):
            logger.warning("Settings not loaded, loading now")
            self._settings = self.load_settings()

        port = self._settings.port
        logger.info("Starting server on port %s", port)
        server = self._setup_uvicorn(
            port=port,
            logging_config=self._settings.logging_config,
        )

        self._scheduler.start()
        await server.serve()
        logger.info("Server stopped")

    def start(self) -> None:
        """Start the server synchronously."""
        asyncio.run(self.start_async())

    @property
    def app(self) -> FastAPI:
        """Get the FastAPI app.

        Needed to start the uvicorn server.
        """
        a = self._fastapi_app
        a.include_router(self._router)
        return a
