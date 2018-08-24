# coding=utf8

######################################################
#
# Tia Text Assistant - Internet tasks without using Data/Wi-Fi
# written by Jonathan Schwartz (jonathanschwartz30@gmail.com)
#
######################################################

from __future__ import print_function
import time
import re
import mongo_helpers as mongo
import google_voice_hub as gv
import api_keys as SHEETS
import directions_helpers as geo
import wit_helpers as wit
from dateutil import parser
import weather_helpers as weather
import requests


def extract_quoted_text(text):
    text = re.sub('"', "'", text)
    try:
        text = re.search(r'\'(.*?)\'', str(text)).group(1)
    except:
        pass
    return text


def store_reply_in_mongo_no_header(result, sender_info, send_all_chunks="ALL_CHUNKS", launch_time="NOW"):
    message_copy = mongo.message_records.find_one({"sms_id": sender_info['sms_id']})
    time.sleep(1)
    
    result = gv.sizing_sms_chunks(result, send_all_chunks)
    chunk_len = result[0]
    chunk_reply = result[1]

    db_changes = {
        "result": chunk_reply,
        "status": "completed processing",
        "launch_time": launch_time,
        "send_all_chunks": send_all_chunks,
        "current_chunk": 0,
        "chunk_len": chunk_len
    }

    mongo.update_record(message_copy, db_changes, mongo.message_records)



def store_reply_in_mongo(result, sender_info, topic, send_all_chunks="SINGLE_CHUNKS", launch_time="NOW"):
    message_copy = mongo.message_records.find_one({"sms_id": sender_info['sms_id']})
    time.sleep(1)
    tia_sign_off = "\n\n--😘,\n✨ Tia ✨ Text" \
        " 📲 me another request, " + str(
            message_copy['name']) + ", or text HELP"
    result = str(topic) + " for " + str(
        message_copy['name']) + "!\n\n" + result + tia_sign_off

    result = gv.sizing_sms_chunks(result, send_all_chunks)
    chunk_len = result[0]
    chunk_reply = result[1]

    db_changes = {
        "result": chunk_reply,
        "status": "completed processing",
        "launch_time": launch_time,
        "send_all_chunks": send_all_chunks,
        "current_chunk": 0,
        "chunk_len": chunk_len
    }

    mongo.update_record(message_copy, db_changes, mongo.message_records)

    # print(sender_info)



def send_error_text(text):
    return "\n😟 I hate to be the bearer of bad 🗞️, but right now, your " + \
        text + " request didn't work ... 🙏 try again!"


# OPENING GREETING FUNCTIONS FOR NEW USER


def trigger_help(sender_info):
    name = mongo.fetch_name_from_db(sender_info)

    message = "\nHey, " + name + "! Here's a 🗒️ " \
    "of tasks I can 📲: \n\n🚇 Directions 🚇\n by 🚗, 🚉, " \
    "or 🚶\n\nI want to drive from home to '221 79th Street, " \
    "Bay Ridge, Brooklyn' 📲 Let's walk from '403 Main Street, Oakland, " \
    "California', to '1807 Thompson Ave, Oakland, CA 94612'\n\n☀️ Weather ☀️ " \
    "\nWhat's it like outside in Houston? " \
    "📲 What's the forecast near me? \n\n⏲️ Reminders ⏲️\n" \
    "Remind me to pick up my sister in an hour\n\n🇺🇸 " \
    "Translation 🇺🇸\nHow would an Italian say, 'I don't like pasta'?" \
    "\n\n🍲 Yelp 🍲\nPlease find me some asian fusion " \
    "near my house\n\n🔎 Wikipedia 🔎\nI want a bio of Barack Obama" \
    "\n\n💡 Jeopardy Trivia 💡 \n📲 Let's play jeopardy" \
    "\n\n🤣 Late Night Jokes 🤣\n" \
    "What are the latest jokes? " \
    "\n\n🔭 Knowledge Q&A 🔭\nHow many baseballs " \
    "fit into a boeing 747?\n📲 How many calories in a sweet potato?\n📲 " \
    "Where can I find the North Star?\n\n📰 News Briefs 📰\nGet NY 🗽 Times, Hacker 💻 News, " \
    "and 75 other headlines from around the 🌏, including abc, cnn, espn, bloomberg, " \
    "techcrunch, etc.\n\n📲 What's happening at buzzfeed? 📲 " \
    "What are the headlines from wired?\n\n(For a full list of 🌏 sources, text NEWS)\n\nI can also send" \
    " your ✨ faves ✨ on a regular basis ⏲️ hourly, daily, or weekly!\n\n" \
    "📲 I want daily new york times at 9 AM\n📲 Give me Jeopardy questions every hour" \
    "\n\nNow 🙏 give me a task!"

    store_reply_in_mongo_no_header(message, sender_info)


def convert_coords_to_time_zone(lat, long):
    url = "http://api.timezonedb.com/v2/get-time-zone?key=" + \
          SHEETS.ZONE_API_KEY + "&format=json&by=position&lat=" + str(lat) + "&lng=" + str(long)
    print(url)
    # json_data = requests.get(url).json()
    json_data = requests.get(url).json()
    result = []
    result.append(json_data['zoneName'])
    result.append(json_data['formatted'])
    return result


def update_local_time(zone):
    url = "http://api.timezonedb.com/v2/get-time-zone?key=" + \
          SHEETS.ZONE_API_KEY + "&format=json&by=zone&zone=" + zone
    json_data = requests.get(url).json()
    return json_data['formatted']


def convert_wit_zone_to_home(home_zone):
  dt = parser.parse("2018-07-31T23:05:00.000-07:00")
  unixTime = int(time.mktime(dt.timetuple()))
  url = "http://api.timezonedb.com/v2/convert-time-zone?key=" + \
        SHEETS.ZONE_API_KEY + "&format=json&from=America/Los_Angeles&to=" + str(home_zone) + "&time=" + str(unixTime)
  json_data = requests.get(url).json()
  distance_from_pst = int(json_data['offset'])
  result = distance_from_pst/3600
#   print("Offset: " + str(distance_from_pst/3600))
  # print("Now_time east:" + str(time.time()))
  return int(result)


def add_geo_data_to_db(command, sender_info):
    try:
        home_str = sender_info['home']
        if home_str == "NO ADDRESS GIVEN":
            home_str = sender_info['body']
    except:
        home_str = sender_info['body']
    
    print("Home_str: " + str(home_str))
    
    home_lat_long = geo.lat_long_single_location(command)
    print("home_lat_long: " + str(home_lat_long))
    time_zone_list = convert_coords_to_time_zone(str(home_lat_long[0]), str(home_lat_long[1]))
    zone_name = time_zone_list[0]
    local_current_time = time_zone_list[1]

    home_zip = weather.get_zip(home_str)

    time_zone_change = convert_wit_zone_to_home(zone_name)
    print("time_zone_change: " + str(time_zone_change))

    message_copy = mongo.message_records.find_one({"sms_id": sender_info['sms_id']})
    db_changes = {
        "offset_time_zone": time_zone_change,
        "local_current_time": local_current_time,
        "zone_name": zone_name,
        "home_lat_long": home_lat_long,
        "home_zip": home_zip
    }
    mongo.update_record(message_copy, db_changes, mongo.message_records)
    user_data = mongo.user_records.find_one({'phone': sender_info['from']})
    mongo.update_record(user_data, db_changes, mongo.user_records)
    return time_zone_change


def new_home_request(command, sender_info):
    command = str(command).lower()
    print(command)
    if command == "no":
        message = "\nI totally understand, "
    else:
        command = re.sub("new home", "", command)
        command = extract_quoted_text(command)
        print(command)
        add_geo_data_to_db(command, sender_info)
        sender_info = mongo.add_new_item_to_db(sender_info, "home", command)
        message = "\nThere's no place like 🏠, "
    message = message + str(sender_info['name']) + "!\n\nText me NEW HOME" \
             " followed by your address to change 🏠 at any time.\n\n🙋 Wanna see what I can do? 📲 Text INFO"

    store_reply_in_mongo_no_header(message, sender_info)
    # gv.send_new_message(sender_info['from'], message, sender_info)
    # print(sender_info)


def trigger_new_home(resp, sender_info):
    print("New Home Triggered")
    try:
        location = resp['entities']['location'][0]['value']
    except BaseException:
        location = extract_quoted_text(resp['_text'])
    result = location
    print("New Home Location: " + location)
    store_reply_in_mongo(
                        new_home_request(result, sender_info),
                        sender_info,
                        "🏠 New Home 🏠")


def process_first_message(sender_info):
    print("Inside process_first_message")
    print("New message: " + str(sender_info))
    # Boilerplate first message
    message = "\n👋 Hi! I'm TIA 🤗, your Texting 📲 Internet Assistant! I do 💻 tasks via texts, " \
              " so no need for 📶 or Wi-Fi!\n\nI can text you:\n🚗 Directions 🚗\n☔ Weather ☔\n🍲 " \
              "Yelp 🍲\n⏲️ Reminders ⏲️\n✍️ Translation ✍️\n📚 Q & A 📚 \n🔎 Wikipedia 🔎\n🌏 News " \
              "🌏\n📺 Late Night Jokes 📺\n💡 Jeopardy Trivia 💡 and more...\n\n🙋‍ " \
              "What's your first name?"
    store_reply_in_mongo_no_header(message, sender_info)


def parse_name(name_string):
    name_scrub = {
        "scrubs": [
            'my',
            'name',
            'you',
            'ahead',
            'should',
            'and',
            'can',
            'call',
            'me',
            'is',
            'by',
            'I',
            'go',
            'answer',
            'to',
            'please',
            'let\'s',
            'go',
            'with',
            'first']}
    name_string = re.sub(r'[^\w\s]', ' ', name_string).lower()
    name_string = name_string.split(" ")
    print(name_string)
    new_name_list = []

    for i in range(0, len(name_string)):
        if name_string[i] not in name_scrub['scrubs']:
            new_name_list.append(name_string[i].capitalize())
    result = " ".join(new_name_list)
    return result


def parse_address(address_string):
    address_scrub = {
        "scrubs": [
            'my',
            'home',
            'house',
            'local',
            'set',
            'default',
            'homebase',
            'over',
            'is',
            'at',
            'find',
            'you',
            'go',
            'let\'s',
            'set',
            'please',
            'want',
            'wanna',
            'put',
            'address',
            'as'
        ]
    }
    address_string = address_string.lower()
    address_string = address_string.split(" ")
    print(address_string)
    new_address_list = []

    for i in range(0, len(address_string)):
        if address_string[i] not in address_scrub['scrubs']:
            new_address_list.append(address_string[i].capitalize())
    result = " ".join(new_address_list)
    print(result)
    return result


def process_name_prompt(sender_info):
    current_user = mongo.user_records.find_one({"phone": sender_info['from']})
    # SECOND MESSAGE, ASKING FOR FIRST NAME
    if current_user['count'] == 1:
        name = parse_name(sender_info['body'])
        name = name.strip()
        sender_info = mongo.add_new_item_to_db(sender_info, "name", name)
        print("Hi, " + name + "!")
        message = "\nIt's a pleasure to 🤗 meet you, " + name + \
            "!\n\nIf you'd like me to set up a 🏠 address for quicker 🚗" \
            " directions and 🌧️ weather, please reply with your full address or NO\n"
        store_reply_in_mongo_no_header(message, sender_info)

