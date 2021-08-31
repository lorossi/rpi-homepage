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
  if (time_text != time_obj.textContent)
    time_obj.textContent = time_text;

  // format date and update if different
  const date_text = `${days}/${months}/${years}`;
  const date_obj = document.querySelector("#date");
  if (date_text != date_obj.textContent)
    date_obj.textContent = date_text;
};

// loads weather from backend and sets it into containers
const setWeather = async () => {
  const weather = await makeRequest("/get/weather");
  console.log(weather)

  if (weather) {
    document.querySelector("#city").textContent = weather.city;
    document.querySelector("#temperature-humidity").textContent = `${weather.temperature} - ${weather.humidity}`;
    document.querySelector("#description").textContent = weather.description;
  }
};

const makeRequest = (url, method = "GET") => {
  const options = {
    method,
  };

  return fetch(url, options).then(response => response.json()).catch(() => null);
};


// loads data 
function getData(data_obj) {
  /*
  $.ajax({
    type: "POST",
    url: "/getdata/",
    complete: function (data) {
      for (let i = 0; i < data.responseJSON.length; i++) {
        let obj = data.responseJSON[i];
        $(data_obj).find(`[data="${obj.name}"`).text(obj.string);
      }
    }
  });
  */
}


document.addEventListener("DOMContentLoaded", () => {
  setDate();
  setWeather();

  /*
  const stat_container = document.querySelector(".stat, .weather");
  stat_container.onmouseover(e => {
    // TODO TOGGLE VISIBILITY ON ENTER/EXIT
  });
  */

  setInterval(setDate, 1000); // 1 second
});
