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
  // set background
  background.style.backgroundImage = `url(${image.url})`;
  // blur background
  background.classList.add("blur");

  // set text color
  if (image.light_text) {
    page.classList.add("light-text");
    page.classList.remove("dark-text");
  } else {
    page.classList.add("dark-text");
    page.classList.remove("light-text");
  }

  // set background photographer credit
  const photographer = document.querySelector(".credits .photographer a");
  photographer.textContent = `photo by ${image.photographer} (via Unsplash)`;
  photographer.href = `${image.photographer_url}?utm_source=rpi-homepage&utm_medium=referral`;

  // set background location
  if (image.location) {
    const location = document.querySelector(".credits .location");
    location.textContent = image.location;
  }

  // set background description
  if (image.description) {
    const description = document.querySelector(".description");
    description.textContent = image.description;
  }
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

// toggles blur on background
const toggleBlur = (e) => {
  const background = document.querySelector(".background");
  const content = document.querySelectorAll(".content div");
  const blurred = background.classList.contains("blur");

  if (blurred) {
    // remove the blur
    background.classList.remove("blur");
    background.classList.add("unblur");
    // hide the page content
    content.forEach((div) => {
      div.classList.remove("show");
      div.classList.add("hide");
    });
    // change the button text
    e.target.textContent = "hide image";
  } else {
    // add the blur
    background.classList.remove("unblur");
    background.classList.add("blur");
    // show the page content
    content.forEach((div) => {
      div.classList.remove("hide");
      div.classList.add("show");
    });
    // change the button text
    e.target.textContent = "view image";
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

  // add event listener for view image
  document.querySelector(".view-image").addEventListener("click", toggleBlur);
};

document.addEventListener("DOMContentLoaded", () => {
  main();
});
