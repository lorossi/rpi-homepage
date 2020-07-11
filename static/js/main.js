function setDate(time_obj, date_obj) {
  let now = new Date();

  let hours = now.getHours();
  let minutes = now.getMinutes();
  let year = now.getFullYear();
  let month = now.getMonth() + 1;
  let day = now.getDate();

  if (hours < 10) {
    hours = '0' + hours;
  }

  if (minutes < 10) {
    minutes = '0' + minutes;
  }

  if (month < 10) {
    month = '0' + month;
  }

  if (day < 10)  {
    day = '0' + day;
  }

  let time_text = `${hours}:${minutes}`
  if (time_text != $(time_obj).text()) {
    $(time_obj).text(time_text);
  }

  let date_text = `${day}/${month}/${year}`
  if (date_text != $(date_obj).text()) {
    $(date_obj).text(date_text);
  }
}

function setWeather(weather_obj) {
  $.ajax({
    type : 'POST',
    url : '/getweather/',
    complete : function(data) {
      if (data.responseJSON["cod"] == 200) {
        $(weather_obj + " #city").text(data.responseJSON["city"]);
        $(weather_obj + " #temperature").text(data.responseJSON["temperature"]);
        $(weather_obj + " #humidity").text(data.responseJSON["humidity"]);
        $(weather_obj + " #description").text(data.responseJSON["description"]);
      }
    }
  })
}

function getImage() {
  $.ajax({
    type : 'POST',
    url : '/getimage/',
    complete : function(data) {
      $("body").css({"background": data.responseJSON["gradient"]["string"], "color": data.responseJSON["color"]["text_color"]});
    }
  })
}

function setSpeed(speed_obj) {
  $.ajax({
    type : 'POST',
    url : '/getspeed/',
    complete : function(data) {
      $(speed_obj).append(data.responseJSON["string"]);
    }
  })
}

function getData(data_obj) {
  $.ajax({
    type : 'POST',
    url : '/getdata/',
    complete : function(data) {
      for (let i = 0; i < data.responseJSON.length; i++){
        let obj = data.responseJSON[i];
        $(data_obj).find(`[data="${obj['name']}"`).text(obj['string']);
      }
    }
  })
}


$(document).ready(function() {
  let time_obj = "#time";
  let date_obj = "#date";
  let weather_obj = ".weather";
  let data_obj = ".stats";
  let speed_obj = "#speedtest .value"

  setDate(time_obj, date_obj);
  setWeather(weather_obj);
  setSpeed(speed_obj);


  $(".stat, .weather").mouseenter(function() {
    $(this).find(".hidden").css({"display": "inline-block"});
  })

  $(".stat, .weather").mouseleave(function() {
    $(this).find(".hidden").css({"display": "none"});
  })

  setInterval(setDate, 2000, time_obj, date_obj); // 2 seconds
  setInterval(getImage, 15 * 60 * 1000); // 15 minutes
  setInterval(setWeather, 15 * 60 * 1000, weather_obj); // 15 minutes
  setInterval(setSpeed, 15 * 60 * 1000, speed_obj); // 15 minutes
  setInterval(getData, 30 * 1000, data_obj) // 30 seconds
})
