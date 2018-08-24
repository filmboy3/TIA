# coding=utf8

######################################################
#
# Tia Text Assistant - Internet tasks without using Data/Wi-Fi
# written by Jonathan Schwartz (jonathanschwartz30@gmail.com)
#
######################################################

from __future__ import print_function
import re
import requests
import math
import api_keys as SHEETS
import string
import general_message_helpers as msg_gen
import weather_helpers as wthr
import time
import mongo_helpers as mongo


def convert_distance_from_metric(text):
    num = re.findall('<span class="length">(.*?)</span>', text)
    for i in range(0, len(num)):
        distance_before_conversion = num[i].split(" ")
        new_num = ""
        if (distance_before_conversion[1] == 'm'):
            print("\nHey, I'm a metre:")
            print(distance_before_conversion)
            feet = int(round(int(distance_before_conversion[0]) * 3.28084, 0))
            feet = int(math.ceil(feet / 25.0)) * 25
            print(feet)
            new_num = str(feet) + " ft"
            print("Post converted meters: " + str(new_num))
        else:
            print("\nhey, I'm a km")
            miles = round(float(distance_before_conversion[0]) / 0.6213, 1)
            new_num = str(miles) + " miles"
            print("post converted km: " + str(new_num))
        text = text.replace(num[i], new_num)
    return text

def lat_long_single_location(location_str):
    # print("Inside lat_long_single_location")
    url = "https://geocoder.cit.api.here.com/6.2/geocode.json?app_id=" + \
        str(SHEETS.HERE_APPID) + "&app_code=" + str(SHEETS.HERE_APPCODE) + "&searchtext="
    for s in string.punctuation:
        location_str = location_str.replace(s, '')
    location_str = location_str.split(" ")
    location_str = "+".join(location_str)
    url = url + location_str
    json_data = requests.get(url).json()
    lat_long = []
    print("JSON_DATA: " + str(json_data))
    lat_long.append(json_data['Response']['View'][0]['Result'][0]['Location']['DisplayPosition']['Latitude'])
    lat_long.append(json_data['Response']['View'][0]['Result'][0]['Location']['DisplayPosition']['Longitude'])
    return lat_long


def clean_up_directions(text):
    text = convert_distance_from_metric(text)
    directions_scrub_dict = {
        'Airport': '✈️ Airport',
        'Arrive at': '🎯 Arrive at',
        '<span class="time">': "⌚ ",
        '<span class="cross_street">': "🛣️ ",
        '<span class="distance-description">': '',
        '<span class="stops">': '🚇 ',
        '<span class="station">': '🚉 ',
        '<span class="line">': '🚆 ',
        '<span class="heading">northwest': '↖️ ↖',
        '<span class="heading">north': '⬆️ ',
        '<span class="heading">south': '⬇️ ',
        '<span class="heading">northeast': '↗️ ↗',
        '<span class="heading">southwest': '↙️ ↙',
        '<span class="heading">southeast': '↘️ ↘',
        '<span class="next-street">': '',
        '<span class="direction">left': '⬅️ left',
        '<span class="direction">middle': '⬆️ middle',
        '<span class="street">': '🛣️ ',
        '<span class="length">': '',
        '<span class="transit">': '🚉 ',
        '<span class="toward_street">': '🛣️ ',
        '<span class="direction">right': 'right ➡️',
        '<span class="number">': '🛣️ ',
        '<span class="sign">': '🚧 ',
        '<span lang="en">': '',
        '<span class="exit">': '↪️',
        '<span class="destination">': '',
        '<span class="direction">slightly left': '↖️ left',
        '<span class="direction">slightly right': '↗️ right',
        '<span class="direction">sharp right': '🔪➡️ sharp right',
        '<span class="direction">sharp left': '🔪⬅️ sharp left',
        '</span>': '',
        'ftiles': 'miles'
    }
    for key, value in directions_scrub_dict.items():
        text = re.sub(key, value, text)
    return text


def format_directions(data, lat_long_list):
    data = data['response']['route'][0]
    transit = str(data["mode"]['transportModes'][0])

    # Retrieving human-readable destination/origin for display in header
    origin_location = "your start"
    destination_location = "your final destination"
    if(data['leg'][0]['start']['label'] != ""):
        origin_location = str(data['leg'][0]['start']['label'])
    if(data['leg'][0]['end']['label'] != ""):
        destination_location = str(data['leg'][0]['end']['label'])

    # Creating a Header
    if (transit == "pedestrian"):
        transit = '🚶 walking'
    elif (transit == "car"):
        transit = '🚗 driving'
    elif (transit == "publicTransport"):
        transit = '🚉 public transit'
    text = ("Here are your " +
            transit +
            " directions from " +
            origin_location +
            " to " +
            destination_location +
            ".\n\n" +
            str(data['summary']['text']) +
            "🏃 Let's Go! 🏃")

    for i in range(0, len(data['leg'][0]['maneuver'])):
        text += "\n\n" + str(data['leg'][0]['maneuver'][i]['instruction'])
    text = clean_up_directions(text)
    print(text)
    return text


def make_directions_request(lat_long_list, transit_mode):
    url = "https://route.cit.api.here.com/routing/7.2/calculateroute.json?app_id=" + \
        SHEETS.HERE_APPID + "&app_code=" + SHEETS.HERE_APPCODE + "&waypoint0=geo!" + \
        str(lat_long_list[0][0]) + "," + str(lat_long_list[0][1]) + "&waypoint1=geo!" + str(lat_long_list[1][0]) + "," + \
        str(lat_long_list[1][1]) + "&mode=fastest;" + transit_mode + ";traffic:enabled"
    return format_directions(requests.get(url).json(), lat_long_list)
    

def car_directions(subject_label, sender_info):
    lat_long_list = get_two_lat_long(subject_label, sender_info)
    print("Car Trip: " + str(lat_long_list))
    return make_directions_request(lat_long_list, "car")


def public_transit_directions(subject_label, sender_info):
    lat_long_list = get_two_lat_long(subject_label, sender_info)
    print("Public Transit Trip: " + str(lat_long_list))
    return make_directions_request(lat_long_list, "publicTransport")


def walking_directions(subject_label, sender_info):
    lat_long_list = get_two_lat_long(subject_label, sender_info)
    print("Walking Trip: " + str(lat_long_list))
    return make_directions_request(lat_long_list, "pedestrian")


def directions_request(directions_data, sender_info):
    if (directions_data[2] == "drive"):
        return car_directions(directions_data, sender_info)
    elif (directions_data[2] == "public transit"):
        return public_transit_directions(directions_data, sender_info)
    elif (directions_data[2] == "walk" or directions_data[2] == "Walking"):
        return walking_directions(directions_data, sender_info)


def get_two_lat_long(subject_label, sender_info):
    home = str(sender_info['home'])
    print("Home in two_lat_long:" + str(home))
    print("Subject_label/data input: " + str(subject_label))
    lat_long_origin = []
    print("lat_long_origin: " + str(lat_long_origin))
    # If either start or final destination are the home, then change it to
    # saved home address.
    if (subject_label[0] == 'home'):
        if str(home) == "NO ADDRESS GIVEN":
            return "😟 Sorry, but I don't have your 🏠 address on file ... "
        print("Yes, this is home...")
        subject_label[0] = home
        # lat_long_origin.append(lat_long_single_location(subject_label[0]))
        lat_long_origin.append(sender_info['home_lat_long'])
        print("lat_long_origin.append 1: " + str(lat_long_origin))
    else:
        lat_long_origin.append(lat_long_single_location(subject_label[0]))
        print("lat_long_origin.append 2: " + str(lat_long_origin))
    if (subject_label[1] == 'home'):
        if str(home) == "NO ADDRESS GIVEN":
            print("No, this is not home")
            return "😟 Sorry, but I don't have your 🏠 address on file ... "
        print("Yes this is a destination home")
        subject_label[1] == home
        # lat_long_origin.append(lat_long_single_location(subject_label[1]))
        lat_long_origin.append(lat_long_single_location(sender_info['home_lat_long']))
        print("lat_long_origin.append 3: " + str(lat_long_origin))
    else:
        lat_long_origin.append(lat_long_single_location(subject_label[1]))
        print("lat_long_origin.append 4: " + str(lat_long_origin))
    
    print("lat_long_origin.append 5: " + str(lat_long_origin))
    return lat_long_origin


def trigger_directions(resp, sender_info):
    sender_info = mongo.message_records.find_one({"sms_id": sender_info['sms_id']})
    time.sleep(1)
    print("Directions Triggered")
    # print(resp)
    start_location = ""
    end_location = ""

    try:
        transit_method = resp['entities']['wit_transit'][0]['value']
    except BaseException:
        transit_method = "drive"

    home_status = ""

    try:
        home_status = resp['entities']['wit_fromHome'][0]['value']
        print(home_status)
    except BaseException:
        home_status = ""

    if (home_status != ""):
        if (home_status == "from home"):
            start_location = "home"
            try:
                end_location = resp['entities']['location'][0]['value']
            except BaseException:
                pass
        else:
            try:
                start_location = resp['entities']['location'][0]['value']
            except BaseException:
                pass
            end_location = "home"
    else:
        try:
            start_location = resp['entities']['location'][0]['value']
        except BaseException:
            pass
        try:
            end_location = resp['entities']['location'][1]['value']
        except BaseException:
            pass

    backupAddresses = fallback_multi_address_parse(resp['_text'])
    if (start_location == "" and end_location == ""):
        start_location = backupAddresses[0]
        end_location = backupAddresses[1]
    elif (end_location == ""):
        end_location = backupAddresses[1]
    elif (start_location == ""):
        start_location = backupAddresses[1]

    directions_data = [start_location, end_location, transit_method]
    print(
        "Origin: " +
        start_location +
        "\nDestination: " +
        end_location +
        "\nTransit: " +
        transit_method)


    msg_gen.store_reply_in_mongo(
                                       directions_request(
                                           directions_data,
                                           sender_info),
                                       sender_info,
                                       "🚗 Directions 🚗",
                                       "ALL_CHUNKS")



def fallback_multi_address_parse(text):
    text = text.split(" ")
    fromIndex = text.index("from")
    addressSection = text[fromIndex + 1:]
    addressSection = " ".join(addressSection).split("to")
    origin = addressSection[0]
    destination = addressSection[1]
    result = (origin, destination)
    return result
