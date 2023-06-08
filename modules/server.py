"""Module for the Server class."""
from __future__ import annotations

import asyncio
import logging
from typing import Callable

import uvicorn
from apscheduler.job import Job
from apscheduler.schedulers.asyncio import AsyncIOScheduler as Scheduler
from fastapi import APIRouter, FastAPI
from fastapi import Request as FastAPIRequest
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

from modules.settings import ServerSettings


class Request(FastAPIRequest):
    """Mask for FastAPIRequest class."""


class HTTPException(StarletteHTTPException):
    """Mask for StarletteHTTPException class."""


class HTMLResponse(HTMLResponse):
    """Mask for HTMLResponse class."""


class Server:
    """The Server class.

    This class is not meant to be instantiated; it is meant to be inherited from.
    """

    _fastapi_app: FastAPI
    _router: APIRouter
    _scheduler: Scheduler
    _templates: Jinja2Templates
    _settings: ServerSettings
    settings_path: str
    _schedules: dict[Callable, Job]

    def __init__(self) -> Server:
        """Instantiate a new Server object.

        Throws an error if instantiated directly.
        """
        raise NotImplementedError("Server is an abstract class")

    def __init_subclass__(cls) -> None:
        """Initialize the subclass.

        Args:
            cls (Server): The subclass.
        """
        logging.info(f"Initializing subclass {cls.__name__}")
        cls._fastapi_app = FastAPI()
        cls._router = APIRouter()
        cls._scheduler = Scheduler()
        cls._schedules = {}
        cls.settings_path = "settings.toml"

    def loadSettings(self) -> None:
        """Load the settings."""
        logging.info("Loading settings")
        self._settings = ServerSettings.fromToml(
            self.settings_path,
            self.__class__.__name__,
        )
        logging.info("Loaded settings")

    def _setupGuvicorn(self, port: int) -> uvicorn.Server:
        config = uvicorn.Config(
            self.app,
            host="0.0.0.0",
            port=port,
            loop="asyncio",
        )
        return uvicorn.Server(config=config)

    def addScheduleInterval(self, interval: float, method: Callable) -> None:
        """Add a schedule interval.

        Args:
            interval (float): The interval in seconds.
            method (Callable): The method to call.
        """
        logging.info(f"Adding schedule interval {interval} {method}")
        self._schedules[method] = self._scheduler.add_job(
            method,
            "interval",
            seconds=interval,
        )
        logging.info("Added schedule interval")

    def removeSchedule(self, method: Callable) -> None:
        """Remove a schedule.

        Args:
            method (Callable): The method to remove.
        """
        logging.info(f"Removing schedule {method}")
        self._schedules[method].remove()
        del self._schedules[method]
        logging.info("Removed schedule")

    def addRoute(
        self, path: str, f: Callable, methods: list[str] | None = None
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

        logging.info(f"Adding route {path} {f} {methods}")

        self._router.add_api_route(
            path=path,
            endpoint=f,
            methods=methods,
        )
        logging.info("Added route")

    def addStaticRoute(self, path: str, directory: str, html: bool = False) -> None:
        """Add a static route to the server.

        Args:
            path (str): The path of the route.
            directory (str): The directory of the static files.
            html (bool, optional): Whether or not the static files are html files.
                Defaults to False.
        """
        logging.info(f"Adding static route {path} {directory}")
        self._fastapi_app.mount(
            path, StaticFiles(directory=directory, html=html), name="static"
        )
        logging.info("Added static route")

    def addHTTPExceptionRoute(self, f: Callable) -> None:
        """Add an error route to the server.

        Args:
            f (function): The function to execute.
        """
        logging.info(f"Adding error route {f}")
        self._fastapi_app.add_exception_handler(StarletteHTTPException, f)
        logging.info("Added error route")

    def addTemplateFolder(self, directory: str) -> None:
        """Add a template folder to the server.

        Args:
            directory (str): The directory of the template folder.
        """
        logging.info(f"Adding template folder {directory}")
        self._templates = Jinja2Templates(directory=directory)
        logging.info("Added template folder")

    def generateTemplateResponse(
        self, request: Request, template: str, **kwargs
    ) -> HTMLResponse:
        """Generate a template.

        Args:
            request (Request): The request.
            template (str): The template name.
            **kwargs: The template arguments.

        Returns:
            HTMLResponse: The generated template.
        """
        logging.info(f"Generating template {template} {kwargs}")
        return self._templates.TemplateResponse(
            template,
            {
                "request": request,
                **kwargs,
            },
        )

    async def startAsync(self) -> None:
        """Start the server.

        Returns:
            Server: The instance of the running server

        """
        if not hasattr(self, "_settings"):
            logging.warning("Settings not loaded, loading now")
            self.loadSettings()

        port = self._settings.port
        logging.info(f"Starting server on port {port}")
        server = self._setupGuvicorn(port)

        self._scheduler.start()
        await server.serve()
        logging.info("Server stopped")

    def start(
        self,
    ) -> None:
        """Start the server synchronously."""
        asyncio.run(self.startAsync())

    @property
    def app(self) -> FastAPI:
        """Get the FastAPI app.

        Needed to start the uvicorn server.
        """
        a = self._fastapi_app
        a.include_router(self._router)
        return a
