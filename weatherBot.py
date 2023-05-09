import tokens
import table
import showWeather
import citytranslate
import heatIndex
import requests
import pyowm
import telebot
import json
from telebot import types
from datetime import datetime
from pyowm.utils.config import get_default_config
from pyowm.utils import timestamps
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
import urllib.request
from io import BytesIO

#tokens
bot = telebot.TeleBot(tokens.telegramToken)

api = tokens.owmToken
config_dict = get_default_config()
config_dict['language'] = 'ua'
owm = pyowm.OWM(api, config_dict)

api_accu = tokens.accuToken
api_weather = tokens.weatherApiToken

# Виклик функції створення таблиці
table.createTable()

#buttons
choicekeyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
todaybtn = types.KeyboardButton("На сьогодні")
tomorrowbtn = types.KeyboardButton("На завтра")
geo = types.KeyboardButton("Місцезнаходження", request_location=True)
fc = types.KeyboardButton("Прогноз погоди кожні 3 години")
choicekeyboard.add(todaybtn, tomorrowbtn, geo, fc)

# Today
def get_todayWeather(message):
    print("***Today***")
    if message.text == None: 
        lat = message.location.latitude
        lon = message.location.longitude
        geolocator = Nominatim(user_agent="Test")
        coordinates = lat, lon
        location = geolocator.reverse(coordinates)
        address = location.raw['address']
        city = address.get('city', '')
        message.text = city
    place = message.text
    ide = message.chat.id
    now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    day = int(now.timestamp())

    try:
        # Перевірка, чи є дані для міста в базі даних
        table.cur.execute("SELECT * FROM weather WHERE city=? AND day=?", (place, day))
        result = table.cur.fetchone()

        if result is not None:
            # Якщо дані є, надіслати їх
            print("Sending weather data from the database:")
            print(result)
        else:
            city = citytranslate.translation_city(place)
            # Якщо даних немає, виконати запит до API та записати їх у базу даних
            # OpenWeatherMap
            mgr = owm.weather_manager()
            dataOwm = mgr.weather_at_place(city).weather

            # AccuWeather
            url = f"http://dataservice.accuweather.com/locations/v1/cities/search?apikey={api_accu}&q={city}"
            response = requests.get(url)
            data = response.json()
            first_result = data[0]
            location_key = first_result['Key']
            url = f"http://dataservice.accuweather.com/currentconditions/v1/{location_key}?apikey={api_accu}&details=True"
            response = requests.get(url)
            dataAccu = response.json()

            #WeatherApi
            url = f'http://api.weatherapi.com/v1/forecast.json?key={api_weather}&q={city}&days=7'
            response = requests.get(url)
            dataWApi = response.json()

            feels_likeAvg = round(((dataAccu[0]["RealFeelTemperature"]["Metric"]["Value"] + 
                             dataOwm.temperature('celsius')['feels_like'] + 
                             dataWApi['current']['feelslike_c']) / 3), 2)
            tempAvg = round(((dataAccu[0]['Temperature']['Metric']['Value'] + 
                       dataOwm.temperature('celsius')['temp'] + 
                       dataWApi['current']['temp_c']) / 3), 2)
            humAvg = round(((dataAccu[0]['RelativeHumidity'] + 
                      dataOwm.humidity + 
                      dataWApi['current']['humidity']) / 3), 2)
            windAvg = round(((dataAccu[0]['Wind']['Speed']['Metric']['Value'] + 
                       dataOwm.wind()['speed'] + 
                       dataWApi['current']['wind_kph']) / 3), 2)
            presAvg = round(((dataAccu[0]['Pressure']['Metric']['Value'] + 
                       dataOwm.pressure['press'] + 
                       dataWApi['current']['pressure_mb']) / 3), 2)
            temp_minAvg = round(((dataAccu[0]['TemperatureSummary']['Past24HourRange']['Minimum']['Metric']['Value'] + 
                                  dataOwm.temperature('celsius')['temp_min'] + 
                                  dataWApi["forecast"]["forecastday"][0]["day"]["mintemp_c"]) / 3), 2)
            temp_maxAvg = round(((dataAccu[0]['TemperatureSummary']['Past24HourRange']['Maximum']['Metric']['Value'] + 
                           dataOwm.temperature('celsius')['temp_max'] + 
                           dataWApi["forecast"]["forecastday"][0]["day"]["maxtemp_c"]) / 3), 2)
            
            icon = dataWApi["forecast"]["forecastday"][0]["day"]['condition']['icon']

            table.cur.execute("""
                INSERT INTO weather (city, temperature, description, date, minT, maxT, feel, pres, hum, wind, icon, day)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (place, tempAvg, dataOwm.detailed_status, dataOwm.ref_time,
                temp_minAvg, temp_maxAvg, feels_likeAvg,
                presAvg, humAvg, windAvg, icon, day))
            table.conn.commit()

            # Надіслання нових даних
            table.cur.execute("SELECT * FROM weather WHERE city=? AND day=?", (place,day,))
            result = table.cur.fetchone()

        ide, answer = showWeather.print_weather(result, ide, place)
        icon_big = result[11].replace('64x64', '128x128')
        bot.send_photo(ide, photo=f'http:{icon_big}', caption=answer)
    except:
        bot.send_message(ide, 'Я незнаю такого міста 😠:(\nДавай подивимся погоду в іншому місті?')
 
# Choice today
def choice1(message):
    try:
        msg = bot.reply_to(message, 'Прогноз погоди на сьогодні в місті?')
        bot.register_next_step_handler(msg, get_todayWeather)
    except Exception as e:
        bot.reply_to(message, 'oooops')

# Tommorow
def get_tomorrowWeather(message):
    print("***Tomorrow***")
    if message.text == None: 
        lat = message.location.latitude
        lon = message.location.longitude
        geolocator = Nominatim(user_agent="Test")
        coordinates = lat, lon
        location = geolocator.reverse(coordinates)
        address = location.raw['address']
        city = address.get('city', '')
        message.text = city
    place = message.text
    ide = message.chat.id
    now = datetime.now()
    tomorrow = now.date() + timedelta(days=1)
    day = int(datetime(tomorrow.year, tomorrow.month, tomorrow.day).timestamp())

    try:
        # Перевірка, чи є дані для міста в базі даних
        table.cur.execute("SELECT * FROM weather WHERE city=? AND day=?", (place,day))
        result = table.cur.fetchone()

        if result is not None:
            # Якщо дані є, надіслати їх
            print("Sending weather data from the database:")
            print(result)
        else:
            city = citytranslate.translation_city(place)
            # Якщо даних немає, виконати запит до API та записати їх у базу даних
            # OpenWeatherMap
            mgr = owm.weather_manager()
            daily_forecast = mgr.forecast_at_place(city, "3h")
            tomorrow = timestamps.tomorrow(14, 0)
            owm_data = daily_forecast.get_weather_at(tomorrow)

            # AccuWeather
            location_api_url = f"http://dataservice.accuweather.com/locations/v1/search?q={city}&apikey={api_accu}"
            location_response = requests.get(location_api_url).json()
            city_key = location_response[0]['Key']
            accu_url = f"http://dataservice.accuweather.com/forecasts/v1/daily/1day/{city_key}?apikey={api_accu}&metric=true"
            weather_response = requests.get(accu_url).json()
            accu_data = weather_response['DailyForecasts'][0]

            # WeatherApi
            url = f'http://api.weatherapi.com/v1/forecast.json?key={api_weather}&q={city}&days=2'
            response = requests.get(url).json()
            wapi_data = response['forecast']['forecastday'][1]['day']

            avg_temp = round(((owm_data.temperature('celsius')['temp'] + 
                               wapi_data['avgtemp_c']) / 2), 2)
            avg_min_temp = round(((accu_data['Temperature']['Minimum']['Value'] + 
                            owm_data.temperature('celsius')['temp_min'] + 
                            wapi_data['mintemp_c']) / 3), 2)
            avg_max_temp = round(((accu_data['Temperature']['Maximum']['Value'] + 
                            owm_data.temperature('celsius')['temp_max'] + 
                            wapi_data['maxtemp_c']) / 3), 2)
            avg_wind = round(((owm_data.wind()['speed'] + 
                               wapi_data['maxwind_mph']) / 2), 2)
            avg_hum = round(((owm_data.humidity + 
                              wapi_data['avghumidity']) / 2), 2)
            avg_pres = owm_data.pressure['press']
            avg_feellike = round(((owm_data.temperature('celsius')['feels_like'] + 
                                   heatIndex.heat_index(avg_temp, 
                                                        avg_hum)) / 2), 2)
            
            icon = wapi_data['condition']['icon']
            
            # Запис даних в базу даних
            table.cur.execute("""
                INSERT INTO weather (city, temperature, description, date, minT, maxT, feel, pres, hum, wind, icon, day)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (place, avg_temp, owm_data.detailed_status, 
                  owm_data.ref_time, avg_min_temp, 
                  avg_max_temp, avg_feellike,
                  avg_pres, avg_hum, avg_wind, icon, day))
            table.conn.commit()

            # Надіслання нових даних
            table.cur.execute("SELECT * FROM weather WHERE city=? AND day=?", (place,day,))
            result = table.cur.fetchone()

        ide, answer = showWeather.print_weather(result, ide, place)
        icon_big = result[11].replace('64x64', '128x128')
        bot.send_photo(ide, photo=f'http:{icon_big}', caption=answer)
    except:
        bot.send_message(ide, 'Я незнаю такого міста 😠:(\nДавай подивимся погоду в іншому місті?')
# Choice tomorrow
def choice2(message):
	try:
		msg = bot.reply_to(message, 'Прогноз погоди на завтра в місті?')
		bot.register_next_step_handler(msg, get_tomorrowWeather)
	except Exception as e:
		bot.reply_to(message, 'oooops')

# By location
def get_locationPlace(message):
    try:
        lat = message.location.latitude
        lon = message.location.longitude
        geolocator = Nominatim(user_agent="Test")
        coordinates = lat, lon
        location = geolocator.reverse(coordinates)
        address = location.raw['address']
        city = address.get('city', '')
        message.text = city
        get_todayWeather(message)
    except:
        bot.send_message(message.chat.id, 'Я незнаю такого міста 😠:(\n\
			Давай подивимся погоду в іншому місті?')

# Choice location
def choice3(message):
	try:
		get_locationPlace(message)
	except Exception as e:
		bot.reply_to(message, 'oooops')

# Forecast
def print_forecast_today(location):
    try:
        forecast = []
        answer = ''
        city = citytranslate.translation_city(location.text)
        lang = 'ua'
        url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api}&units=metric&lang={lang}'
        response = requests.get(url)
        data = response.json()
        now = datetime.now()
        start_of_day = datetime(now.year, now.month, now.day)
        end_of_day = start_of_day + timedelta(days=1)

        for item in data['list']:
            forecast_time = datetime.fromtimestamp(item['dt'])
            
            # Якщо час прогнозу на сьогодні і його часова мітка кратна 3 годинам
            if start_of_day <= forecast_time < end_of_day and forecast_time.hour % 3 == 0:
                forecast.append({
                    'time': forecast_time.strftime('%Y-%m-%d %H:%M'),
                    'temperature': item['main']['temp'],
                    'description': item['weather'][0]['description']
                })

        answer += 'Погода у місті ' + location.text + ', ' + '\n'
        for item in forecast:
            answer += f"{item['time']}: 🌡 {item['temperature']}°C, {item['description']}" + '\n'
        bot.send_message(location.chat.id, answer)
    except:
        bot.send_message(location.chat.id, 'Я незнаю такого міста 😠:(\nДавай подивимся погоду в іншому місті?')
# Choice forecast
def choice4(message):
	try:
		msg = bot.reply_to(message, 'Прогноз погоди в місті?')
		bot.register_next_step_handler(msg, print_forecast_today)
	except Exception as e:
		bot.reply_to(message, 'oooops')

# start
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, \
        "Привіт, {0.first_name}!\nЯ - <b>{1.first_name}</b>\n"\
        "Напишіть /weather, щоб взнати прогноз погоди".format(message.from_user, bot.get_me()),\
        parse_mode='html')

# weather
@bot.message_handler(commands=['weather'])
def weather_message(message):
    bot.send_message(message.chat.id, "Виберіть на коли вам треба знати погоду.", reply_markup=choicekeyboard)

@bot.message_handler(content_types=["location"])
def location_message(message):
	if message.location is not None:
		choice3(message)

# day
@bot.message_handler(content_types=['text'])
def day_message(message):
    if message.text == "На сьогодні":
        choice1(message)
    elif message.text == "На завтра":
        choice2(message)
    elif message.text == "Прогноз погоди кожні 3 години":
        choice4(message)

bot.polling(none_stop=True)