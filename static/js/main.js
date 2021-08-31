// loads date into container
const setDate = () => {
  const now = new Date();
  // pad time and date
  const hours = now.getHours().toString().padStart(2, '0');
  const minutes = now.getMinutes().toString().padStart(2, '0');
  const year = now.getFullYear().toString().padStart(2, '0');
  const month = (now.getMonth() + 1).toString().padStart(2, '0');
  const day = now.getDate().toString().padStart(2, '0');

  // format hour and update if different
  const time_text = `${hours}:${minutes}`;
  const time_obj = document.querySelector("#time");
  if (time_text != time_obj.textContent)
    time_obj.textContent = time_text;

  // format date and update if different
  const date_text = `${day}/${month}/${year}`;
  const date_obj = document.querySelector("#date");
  if (date_text != date_obj.textContent)
    date_obj.textContent = date_text;
};

// loads weather from backend and sets it into containers
function setWeather(weather_obj) {
  $.ajax({
    type: 'POST',
    url: '/getweather/',
    complete: function (data) {
      if (data.responseJSON.cod == 200) {
        $(weather_obj + " #city").text(data.responseJSON.city);
        $(weather_obj + " #temperature").text(data.responseJSON.temperature);
        $(weather_obj + " #humidity").text(data.responseJSON.humidity);
        $(weather_obj + " #description").text(data.responseJSON.description);
      }
    }
  });
}


// loads data 
function getData(data_obj) {
  /*
  $.ajax({
    type: 'POST',
    url: '/getdata/',
    complete: function (data) {
      for (let i = 0; i < data.responseJSON.length; i++) {
        let obj = data.responseJSON[i];
        $(data_obj).find(`[data="${obj.name}"`).text(obj.string);
      }
    }
  });
  */
}


document.addEventListener('DOMContentLoaded', () => {
  setDate();
  //setWeather(weather_obj);

  /*
  const stat_container = document.querySelector(".stat, .weather");
  stat_container.onmouseover(e => {
    // TODO TOGGLE VISIBILITY ON ENTER/EXIT
  });
  */

  setInterval(setDate, 2000); // 2 seconds
});
