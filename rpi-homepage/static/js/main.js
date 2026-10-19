// sparkline geometry, matching the svg viewBox (0 0 300 56)
const SPARK_WIDTH = 300;
const SPARK_TOP = 1;
const SPARK_BOTTOM = 55;
// temperature scale and thresholds, in °C
const TEMPERATURE_MIN = 20;
const TEMPERATURE_MAX = 90;
const TEMPERATURE_WARM = 70;
const TEMPERATURE_HOT = 80;
// fallback refresh interval, in seconds, used until the server provides one
const DEFAULT_REFRESH = 10;

// makes a request to an url
const makeRequest = async (url, method = "GET") => {
  const options = {
    method,
  };

  return fetch(url, options)
    .then((response) => (response.ok ? response.json() : null))
    .catch(() => null);
};

// sets the text of an element, only if it changed
const setText = (id, text) => {
  const element = document.getElementById(id);
  if (element && element.textContent != text) element.textContent = text;
};

// formats a number, with one decimal only for small values
const formatNumber = (value) => {
  if (value >= 10) return Math.round(value).toString();
  return (Math.round(value * 10) / 10).toString();
};

// picks the unit to display a size (in bytes) with
const sizeUnit = (bytes) => {
  const units = ["B", "KB", "MB", "GB", "TB"];
  let index = 0;
  while (bytes >= 1024 ** (index + 1) && index < units.length - 1) index++;
  return { name: units[index], divisor: 1024 ** index };
};

// formats a rate (in bytes per second) as [value, unit]
const formatRate = (bytes) => {
  const unit = sizeUnit(bytes);
  return [formatNumber(bytes / unit.divisor), `${unit.name}/s`];
};

// formats an uptime (in seconds)
const formatUptime = (seconds) => {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  if (days > 0) return `uptime ${days}d ${hours}h`;
  if (hours > 0) return `uptime ${hours}h ${minutes}m`;
  return `uptime ${minutes}m`;
};

// builds the line and area paths of a sparkline, scaling values in [min, max]
const sparkPaths = (values, min, max) => {
  if (values.length == 0) return { line: "", area: "" };
  // a single sample is drawn as a flat line
  if (values.length == 1) values = [values[0], values[0]];

  const span = max - min || 1;
  const step = SPARK_WIDTH / (values.length - 1);
  const points = values.map((value, i) => {
    const ratio = Math.min(Math.max((value - min) / span, 0), 1);
    const y = SPARK_BOTTOM - ratio * (SPARK_BOTTOM - SPARK_TOP);
    return `${(i * step).toFixed(1)} ${y.toFixed(1)}`;
  });

  const line = `M${points.join(" L")}`;
  const area = `${line} L${SPARK_WIDTH} 56 L0 56 Z`;
  return { line, area };
};

// draws a sparkline into the paths with the given id prefix
const drawSpark = (id, values, min, max, area = true) => {
  const paths = sparkPaths(values, min, max);
  document.getElementById(`${id}-line`).setAttribute("d", paths.line);
  if (area) document.getElementById(`${id}-area`).setAttribute("d", paths.area);
};

// sets the temperature status line, the matching icon is shown via css
const setTemperatureStatus = (temperature) => {
  let status;
  if (temperature == null) status = "unavailable";
  else if (temperature >= TEMPERATURE_HOT) status = "hot";
  else if (temperature >= TEMPERATURE_WARM) status = "warm";
  else status = "normal";

  document.getElementById("temperature-status").dataset.status = status;
  setText(
    "temperature-status-label",
    status == "unavailable" ? "sensor not available" : status,
  );
};

// renders the list of disks
const setDisks = (disks) => {
  const container = document.getElementById("disks");
  const rows = disks.map((disk) => {
    const unit = sizeUnit(disk.total);
    const used = formatNumber(disk.used / unit.divisor);
    const total = formatNumber(disk.total / unit.divisor);
    const percent = disk.total > 0 ? (disk.used / disk.total) * 100 : 0;

    const row = document.createElement("div");
    row.className = "disk";
    row.innerHTML =
      `<div class="mono disk-head"><span></span><span class="muted"></span></div>` +
      `<div class="track" role="img"><div class="fill"></div></div>`;
    row.querySelector(".disk-head span:first-child").textContent = disk.path;
    row.querySelector(".disk-head .muted").textContent =
      `${used} / ${total} ${unit.name}`;
    row
      .querySelector(".track")
      .setAttribute(
        "aria-label",
        `${disk.path}: ${used} of ${total} ${unit.name} used`,
      );
    row.querySelector(".fill").style.width = `${percent.toFixed(1)}%`;
    return row;
  });

  container.replaceChildren(...rows);
};

// sets a network rate, with its unit
const setRate = (id, bytes) => {
  const [value, unit] = formatRate(bytes);
  const element = document.getElementById(id);
  element.innerHTML = `${value} <span class="unit">${unit}</span>`;
};

// loads the system status from backend and sets it into containers
const setSystem = async () => {
  const system = await makeRequest("/get/system");
  if (!system) return DEFAULT_REFRESH;

  setText("uptime", formatUptime(system.uptime));

  // cpu
  setText("cpu", Math.round(system.cpu).toString());
  drawSpark("cpu", system.cpu_history, 0, 100);
  setText("load", `load ${system.load.map((l) => l.toFixed(2)).join(" · ")}`);

  // temperature
  setText(
    "temperature",
    system.temperature == null
      ? "-"
      : Math.round(system.temperature).toString(),
  );
  drawSpark(
    "temperature",
    system.temperature_history,
    TEMPERATURE_MIN,
    TEMPERATURE_MAX,
  );
  setTemperatureStatus(system.temperature);

  // ram, scaled to the total memory (the dashed line)
  const ram = sizeUnit(system.ram_total);
  setText("ram", formatNumber(system.ram_used / ram.divisor));
  setText(
    "ram-total",
    ` / ${formatNumber(system.ram_total / ram.divisor)} ${ram.name}`,
  );
  drawSpark("ram", system.ram_history, 0, system.ram_total);

  // disks
  setDisks(system.disks);

  // network, download and upload share the same scale
  const peak =
    Math.max(1024, ...system.download_history, ...system.upload_history) * 1.15;
  drawSpark("download", system.download_history, 0, peak);
  drawSpark("upload", system.upload_history, 0, peak, false);
  setRate("download", system.download);
  setRate("upload", system.upload);

  return system.sample_interval || DEFAULT_REFRESH;
};

// loads date into container
const setDate = () => {
  const now = new Date();
  // pad time
  const hours = now.getHours().toString().padStart(2, "0");
  const minutes = now.getMinutes().toString().padStart(2, "0");
  const seconds = now.getSeconds().toString().padStart(2, "0");
  setText("time", `${hours}:${minutes}:${seconds}`);

  // format date as "Tue 13 Oct 2026"
  const date = now
    .toLocaleDateString("en-GB", {
      weekday: "short",
      day: "numeric",
      month: "short",
      year: "numeric",
    })
    .replace(",", "");
  setText("date", date);
};

// refreshes the system status, following the sampling interval of the server
const refreshSystem = async () => {
  const interval = await setSystem();
  setTimeout(refreshSystem, interval * 1000);
};

document.addEventListener("DOMContentLoaded", () => {
  setDate();
  // update date every second
  setInterval(setDate, 1000);
  refreshSystem();
});
