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

  setTimeout(setDate, 1000); // 1 second
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

  setTimeout(setWeather, 1000 * 60 * 5); // 5 minutes
};

// loads greeting into container
const setGreeting = async () => {
  // get greeting from server
  const greeting = await makeRequest("/get/greetings");
  // place into page
  if (greeting && greeting.message) {
    document.querySelector("#greeting").textContent = greeting.message;
  }

  setTimeout(setGreeting, 1000 * 60 * 5); // 5 minutes
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

document.addEventListener("DOMContentLoaded", () => {
  setDate();
  setWeather();
  setGreeting();
});
