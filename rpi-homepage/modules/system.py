"""System module, used to monitor the resources of the host."""

import os
import time
from collections import deque

import psutil
from loguru import logger
from pydantic import BaseModel

from modules.settings import SystemSettings

# preferred temperature sensors, in order (Raspberry Pi, Intel, AMD)
TEMPERATURE_SENSORS = ("cpu_thermal", "coretemp", "k10temp")


class DiskResponse(BaseModel):
    """DiskResponse class, used to represent the usage of a disk."""

    path: str
    used: int
    total: int


class SystemResponse(BaseModel):
    """SystemResponse class, used to represent the status of the system.

    Sizes are expressed in bytes, rates in bytes per second, the uptime in
    seconds and temperatures in degrees Celsius.
    Histories are sorted from the oldest to the newest sample.
    """

    uptime: float
    sample_interval: int
    history_length: int
    cpu: float
    cpu_history: list[float]
    load: tuple[float, float, float]
    temperature: float | None
    temperature_history: list[float]
    ram_used: int
    ram_total: int
    ram_history: list[int]
    disks: list[DiskResponse]
    download: float
    upload: float
    download_history: list[float]
    upload_history: list[float]


class SystemService:
    """SystemService class, used to periodically sample the system resources."""

    _settings: SystemSettings

    def __init__(self, settings: SystemSettings | None = None) -> None:
        """Create a SystemService object.

        Args:
            settings (SystemSettings, optional): The system settings.
                Defaults to None (default settings).
        """
        logger.info("Initializing SystemService")
        self._settings = settings if settings is not None else SystemSettings()

        length = self._settings.history_length
        self._cpu_history: deque[float] = deque(maxlen=length)
        self._temperature_history: deque[float] = deque(maxlen=length)
        self._ram_history: deque[int] = deque(maxlen=length)
        self._download_history: deque[float] = deque(maxlen=length)
        self._upload_history: deque[float] = deque(maxlen=length)

        # prime the cpu and network counters, so that the first sample is meaningful
        psutil.cpu_percent(interval=None)
        self._last_net = psutil.net_io_counters()
        self._last_net_time = time.monotonic()

    @property
    def sample_interval(self) -> int:
        """Get the interval between two samples, in seconds."""
        return self._settings.sample_interval

    def _read_temperature(self) -> float | None:
        """Read the cpu temperature, if a sensor is available."""
        # sensors_temperatures is not available on every platform
        sensors_temperatures = getattr(psutil, "sensors_temperatures", None)
        if sensors_temperatures is None:
            return None

        sensors = sensors_temperatures()
        if not sensors:
            return None

        name = next((s for s in TEMPERATURE_SENSORS if s in sensors), None)
        readings = sensors[name] if name is not None else next(iter(sensors.values()))
        if not readings:
            return None

        return sum(r.current for r in readings) / len(readings)

    def sample(self) -> None:
        """Sample the system resources and store them in the histories."""
        self._cpu_history.append(psutil.cpu_percent(interval=None))
        self._ram_history.append(psutil.virtual_memory().used)

        temperature = self._read_temperature()
        if temperature is not None:
            self._temperature_history.append(temperature)

        net = psutil.net_io_counters()
        now = time.monotonic()
        elapsed = now - self._last_net_time
        if elapsed > 0:
            download = (net.bytes_recv - self._last_net.bytes_recv) / elapsed
            upload = (net.bytes_sent - self._last_net.bytes_sent) / elapsed
            # counters can wrap or reset, never report negative rates
            self._download_history.append(max(download, 0))
            self._upload_history.append(max(upload, 0))
        self._last_net = net
        self._last_net_time = now

    def _read_disks(self) -> list[DiskResponse]:
        """Read the usage of the configured disks, skipping the missing ones."""
        disks = []
        for path in self._settings.disks:
            try:
                usage = psutil.disk_usage(path)
            except OSError:
                logger.warning("Could not read disk usage of {}", path)
                continue
            disks.append(DiskResponse(path=path, used=usage.used, total=usage.total))

        return disks

    def get_status(self) -> SystemResponse:
        """Get the current status of the system.

        Returns:
            SystemResponse
        """
        if not self._cpu_history:
            self.sample()

        return SystemResponse(
            uptime=time.time() - psutil.boot_time(),
            sample_interval=self._settings.sample_interval,
            history_length=self._settings.history_length,
            cpu=self._cpu_history[-1],
            cpu_history=list(self._cpu_history),
            load=os.getloadavg(),
            temperature=(
                self._temperature_history[-1] if self._temperature_history else None
            ),
            temperature_history=list(self._temperature_history),
            ram_used=self._ram_history[-1],
            ram_total=psutil.virtual_memory().total,
            ram_history=list(self._ram_history),
            disks=self._read_disks(),
            download=self._download_history[-1] if self._download_history else 0,
            upload=self._upload_history[-1] if self._upload_history else 0,
            download_history=list(self._download_history),
            upload_history=list(self._upload_history),
        )
