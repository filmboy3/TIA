# coding=utf8

######################################################
#
# Tia Text Assistant - Internet tasks without using Data/Wi-Fi
# written by Jonathan Schwartz (jonathanschwartz30@gmail.com)
#
######################################################

from __future__ import print_function
import requests
import string
import calendar
import api_keys as SHEETS
import time
import mongo_helpers as mongo
import general_message_helpers as msg_gen
import wit_helpers as wit

# LOCATION-BASED FUNCTIONS (WEATHER)


def convert_weather_to_emoji(icon_name):
    emoji_dict = {
        "01d": "☀️",
        "01n": "🌃",
        "02d": "🌤",
        "02n": "🌤",
        "03d": "☁️",
        "03n": "☁️",
        "04d": "⛅️",
        "04n": "⛅️",
        "09d": "🌧",
        "09n": "🌧",
        "10d": "☔️",
        "10n": "☔️",
        "11d": "🌩",
        "11n": "🌩",
        "13d": "🌨",
        "13n": "🌨",
        "50d": "🌁",
        "50n": "🌁"
    }
    return emoji_dict[icon_name]


def convert_kelvin_to_fahrenheit(tempK):
    return (9 / 5) * (tempK - 273) + 32


def parse_weather(str):
    location = lookup_single_location(str)
    zip = get_zip(location)
    print(zip)

    return zip


def lookup_single_location(location_str):
    print("Inside lookup_single_location")
    url = "https://geocoder.cit.api.here.com/6.2/geocode.json?app_id=" + \
        str(SHEETS.HERE_APPID) + "&app_code=" + str(SHEETS.HERE_APPCODE) + "&searchtext="
    for s in string.punctuation:
        location_str = location_str.replace(s, '')
    location_str = location_str.split(" ")
    location_str = "+".join(location_str)
    url = url + location_str
    print("Url inside lookup_single_location: " + str(url))
    json_data = requests.get(url).json()
    print("JSON response inside lookup_single_location: " + str(json_data))
    return json_data


def get_zip(str):
    json_data = lookup_single_location(str)
    zip = json_data['Response']['View'][0]['Result'][0]['Location']['Address']['PostalCode']
    print(zip)
    return zip


def weather_request(subject_label, sender_info):
    home = str(sender_info['home'])
    print(home)
    if subject_label.lower() == "home":
        if str(home) == "NO ADDRESS GIVEN":
            return "😟 Sorry, but I don't have your 🏠 address on file ... " \
                   "please text 📲 me something like: My home address is 'address'"
        zip = get_zip(home)
        # zip = str(zip[len(zip) - 1])
        url = "http://api.openweathermap.org/data/2.5/weather?appid=" + \
            str(SHEETS.OPEN_WEATHER_API) + "&zip=" + zip
        print("Home with URL and zip: " + str(url))
        subject_label = "🏠"
    else:
        api_address = "http://api.openweathermap.org/data/2.5/weather?appid=" + \
            str(SHEETS.OPEN_WEATHER_API) + "&zip="
        url = api_address + get_zip(subject_label)
        print("url: " + str(url))
    json_data = requests.get(url).json()
    print(json_data)
    current_temp = str(
        int(round(convert_kelvin_to_fahrenheit(json_data['main']['temp']), 0)))
    print(current_temp)
    high_temp = str(
        int(round(convert_kelvin_to_fahrenheit(json_data['main']['temp_max']), 0)))
    print(high_temp)
    low_temp = str(
        int(round(convert_kelvin_to_fahrenheit(json_data['main']['temp_min']), 0)))
    print(low_temp)
    description = str(json_data['weather'][0]['description'])
    print(description)
    humidity = str(json_data['main']['humidity'])
    print(humidity)
    weather_icon = convert_weather_to_emoji(
        str(json_data['weather'][0]['icon']))
    result = (
        "\nToday near " +
        subject_label.capitalize() +
        " expect " +
        description +
        ", " +
        weather_icon +
        ", with a current 🌡 of " +
        current_temp +
        "°F, high of " +
        high_temp +
        "°F, low of " +
        low_temp +
        "°F, and humidity at " +
        humidity +
        "%. Have a great day!")
    return result


def readable_forecast(data, subject_label):
    outer = "\nYour 5-Day Forecast for " + subject_label.capitalize() + "\n"
    for i in range(0, len(data) - 1):
        date_check = data[i]["dt_txt"].split(" ")[0]
        day_of_week = str(calendar.weekday(int(date_check.split(
            "-")[0]), int(date_check.split("-")[1]), int(date_check.split("-")[2])))
        day_of_week_dict = {
            "0": "Mon @ ",
            "1": "Tue @ ",
            "2": "Wed @ ",
            "3": "Thu @ ",
            "4": "Fri @ ",
            "5": "Sat @ ",
            "6": "Sun @ "
        }
        str_of_day = day_of_week_dict[day_of_week]
        time_of_day = data[i]["dt_txt"].split(" ")[1]
        updated_time = int(time_of_day.split(":")[0])
        if (updated_time > 12):
            updated_time = updated_time - 12
            final_time = str(updated_time) + " pm"
        elif (updated_time == 12):
            final_time = "noon"
        elif (updated_time == 0):
            final_time = "12am"
        else:
            final_time = str(updated_time) + " am"
        mini_phrase = str_of_day + final_time + " 🌡 " + str(
            int(
                round(
                    convert_kelvin_to_fahrenheit(
                        (data[i]['main']['temp']))))) + "° " + convert_weather_to_emoji(
            data[i]['weather'][0]['icon']) + " " + data[i]['weather'][0]['description'] + "\n"
        outer += mini_phrase
    return outer


def forecast_request(subject_label, sender_info):
    home = str(sender_info['home'])
    print(home)

    if subject_label == "home":
        if str(home) == "NO ADDRESS GIVEN":
            return "😟 Sorry, but I don't have your 🏠 address on file ... " \
                   "please text 📲 me something like: My home address is 'address'"
        zip = get_zip(home)
        # zip = str(zip[len(zip) - 1])
        url = "http://api.openweathermap.org/data/2.5/forecast?appid=" + \
            str(SHEETS.OPEN_WEATHER_API) + "&zip=" + zip
        subject_label = "home"
    # Or input zipcode
    else:
        api_address = "http://api.openweathermap.org/data/2.5/forecast?appid=" + \
            str(SHEETS.OPEN_WEATHER_API) + "&zip="
        url = api_address + get_zip(subject_label)
    json_data = requests.get(url).json()
    result = readable_forecast(json_data['list'], subject_label)
    return result


def trigger_weather(resp, sender_info):
    print("Weather Triggered")
    sender_info = mongo.message_records.find_one({"sms_id": sender_info['sms_id']})
    time.sleep(1)
    try:
        location = resp['entities']['location'][0]['value']
    except BaseException:
        location = 'home'

    try:
        result = location
        print("Weather location: " + location)

        msg_gen.store_reply_in_mongo(
                                           weather_request(
                                               result,
                                               sender_info),
                                           sender_info,
                                           "⛅ Weather ⛅")

    except BaseException:
        print("Location not found, so checking for Non-Weather keywords ...")
        wit.check_keywords(resp, sender_info)


def trigger_forecast(resp, sender_info):
    sender_info = mongo.message_records.find_one({"sms_id": sender_info['sms_id']})
    time.sleep(1)
    print("Forecast Triggered")
    try:
        location = resp['entities']['location'][0]['value']
    except BaseException:
        location = 'home'

    try:
        result = location
        print("Forecast location: " + location)

        msg_gen.store_reply_in_mongo(
                                           forecast_request(
                                               result,
                                               sender_info),
                                           sender_info,
                                           "🌞 Forecast 🌞")

    except BaseException:
        print("Location not found, so checking for Non-Weather keywords ...")
        wit.check_keywords(resp, sender_info)
