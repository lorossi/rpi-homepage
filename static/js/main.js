// load background from backend and set it into body
const setBackground = async () => {
  // get background from server
  const image = await makeRequest("/get/image");

  // place into page
  if (!image) return;
  const page = document.querySelector(".page");
  const background = document.querySelector(".background");

  // set background as solid color
  background.style.backgroundColor = image.color;
  // blur background
  background.classList.add("blur");
  // set background
  background.style.backgroundImage = `url(${image.url})`;

  // set text color
  if (image.light_text) {
    page.classList.add("light-text");
    page.classList.remove("dark-text");
  } else {
    page.classList.add("dark-text");
    page.classList.remove("light-text");
  }

  // set background credits
  const photographer = document.querySelector(".credits .photographer a");
  const location = document.querySelector(".credits .location");

  photographer.textContent = image.photographer;
  photographer.href = image.photographer_url;
  location.textContent = image.location;

  // set background description
  // TODO
};

// loads date into container
const setDate = () => {
  const now = new Date();
  // pad time and date
  const hours = now.getHours().toString().padStart(2, "0");
  const minutes = now.getMinutes().toString().padStart(2, "0");
  const seconds = now.getSeconds().toString().padStart(2, "0");
  const years = now.getFullYear().toString().padStart(2, "0");
  const months = (now.getMonth() + 1).toString().padStart(2, "0");
  const days = now.getDate().toString().padStart(2, "0");

  // format hour and update if different
  const time_text = `${hours}:${minutes}:${seconds}`;
  const time_obj = document.querySelector("#time");
  if (time_text != time_obj.textContent) time_obj.textContent = time_text;

  // format date and update if different
  const date_text = `${days}/${months}/${years}`;
  const date_obj = document.querySelector("#date");
  if (date_text != date_obj.textContent) date_obj.textContent = date_text;
};

// loads weather from backend and sets it into containers
const setWeather = async () => {
  // get weather from server
  const weather = await makeRequest("/get/weather");
  // place into page
  if (weather && weather.cod == 200) {
    document.querySelector("#city").textContent = weather.city;
    document.querySelector(
      "#temperature-humidity"
    ).textContent = `${weather.temperature} - ${weather.humidity}`;
    document.querySelector("#description").textContent = weather.description;
  }
};

// makes a request to an url
const makeRequest = async (url, method = "GET") => {
  const options = {
    method,
  };

  return fetch(url, options)
    .then((response) => response.json())
    .catch(() => null);
};

const main = () => {
  // set date, weather and background
  setDate();
  setWeather();
  setBackground();
  // update date every second
  setInterval(setDate, 1000);
  // update weather every 5 minutes
  setInterval(setWeather, 300000);
};

document.addEventListener("DOMContentLoaded", () => {
  main();
});
