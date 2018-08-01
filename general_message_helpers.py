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
import google_sheets_api_storage as SHEETS
import directions_helpers as geo
from dateutil import parser
import requests

def send_full_text_message(browser, result, sender_info, topic):
    tia_sign_off = "\n\n--😘,\n✨ Tia ✨\nText" \
        " 📲 me another request, " + str(
            sender_info['name']) + ", or text HELP"
    result = "I've got some " + str(topic) + " info for you, " + str(
        sender_info['name']) + "!\n\n" + result + tia_sign_off
    print(result)
    try:
        gv.send_new_message(browser, sender_info['from'], result, sender_info)
        print("Responded to request successfully: " + str(topic))
    except BaseException:
        print("Error, was unable to respond to request")
        mongo.mark_as_error(sender_info)
        result = "I'm so sorry, " + str(sender_info['name']) + ", " \
            "but I'm having a tough time with your " + str(
            topic) + " request. Please try again." + tia_sign_off
        gv.send_new_message(browser, sender_info['from'], result, sender_info)
    time.sleep(1)


def send_error_text(text):
    return "\n😟 I hate to be the bearer of bad 🗞️, but right now, your " + \
        text + " request didn't work ... 🙏 try again!"


# OPENING GREETING FUNCTIONS FOR NEW USER

# Help Message


def command_help_messages(browser, sender_info):
    message = "\nHey, " + str(sender_info['name']) + "! Here's a 🗒️ " \
        "of tasks I can 📲: \n\n🚇 Turn-by-turn directions 🚇\n🚗 by car, transit, " \
        "or foot 🚗\n\n📲 Examples: 'I want to drive from home to \"221 79th Street, " \
        "Bay Ridge, Brooklyn\"' 📲 'Let's walk from \"403 Main Street, Oakland, " \
        "California\", to \"1807 Thompson Ave, Oakland, CA 94612\"'\n\n☀️ Current weather ☀️ " \
        "and 5-day forecast ☔\n\n📲 Examples: 'What's it like outside in Houston?' " \
        "📲 'What\'s the weather forecast near me? \n\n🇺🇸 " \
        "Language Translation 🇺🇸\n📲 Example: How would an Italian say, 'I don't like pasta'?" \
        "\n\n🍲 Yelp Searches 🍲\n📲 Example: 'Please find me some asian fusion " \
        "near my house'\n\n🔎 Wikipedia summaries 🔎\n📲 Example: 'Tell me about Barack Obama'" \
        "\n\n💡 Jeopardy Questions 💡 \n📲 Example: 'This is Jeopardy!'" \
        "\n\nLate Night 🌃 Monologue jokes\n🤣(most recent, random, or specific date 2009-Present)🤣 📲" \
        " Example: 'What are the latest jokes? " \
        "'\n\n🔭 General Knowledge Q&A 🔭\n📲 Examples: 'How many baseballs " \
        "fit into a boeing 747?' 📲 'How many calories in a sweet potato? 📲 " \
        "Where can I find the North Star?\n\nGet NY Times 📰, Hacker News 💻, " \
        "and 75 other headlines from around the 🌏, including abc, cnn, espn, bloomberg, " \
        "techcrunch, etc. 🌏\n📲 Examples: What's happening at buzzfeed? 📲 " \
        "What are the headlines from wired?\n(For the full list of available sources, ask for the 'news directory')\n\nNow 🙏 give me a task!"
    gv.send_new_message(browser, sender_info['from'], message, sender_info)


def trigger_help(browser, resp, sender_info):
    print("Help Triggered")
    print(resp)
    command_help_messages(browser, sender_info)

def convert_coords_to_time_zone(lat, long):
    url = "http://api.timezonedb.com/v2/get-time-zone?key=" + \
          SHEETS.ZONE_API_KEY + "&format=json&by=position&lat=" + str(lat) + "&lng=" + str(long)
    json_data = requests.get(url).json()
    return json_data['zoneName']

def convert_wit_zone_to_home(home_zone):
  dt = parser.parse("2018-07-31T23:05:00.000-07:00")
  unixTime = int(time.mktime(dt.timetuple()))
  url = "http://api.timezonedb.com/v2/convert-time-zone?key=" + \
        SHEETS.ZONE_API_KEY + "&format=json&from=America/Los_Angeles&to=" + str(home_zone) + "&time=" + str(unixTime)
  json_data = requests.get(url).json()
  distance_from_pst = int(json_data['offset'])
  result = distance_from_pst/3600
  print("Offset: " + str(distance_from_pst/3600))
  # print("Now_time east:" + str(time.time()))
  return int(result)

def add_time_zone_offset_from_pst(command, sender_info):
    home_lat_long = geo.lat_long_single_location(command)
    print("home_lat_long: " + str(home_lat_long))
    time_zone_change = convert_wit_zone_to_home(convert_coords_to_time_zone(str(home_lat_long[0]), str(home_lat_long[1])))
    print("time_zone_change: " + str(time_zone_change))
    # Comment Out the Following Line when Unit Testing
    sender_info = mongo.add_new_item_to_db(sender_info, "offset_time_zone", time_zone_change)
    return time_zone_change

def new_home_request(browser, command, sender_info):
    if command.lower() == "no":
        message = "\nI totally understand, "
    else:
        command = re.sub("new home", "", command.lower())
        add_time_zone_offset_from_pst(command, sender_info)
        sender_info = mongo.add_new_item_to_db(sender_info, "home", command)
        message = "\nThere's no place like 🏠, "
    message = message + str(sender_info['name']) + "!\n\nText me 'new home'" \
             " with your address to change 🏠 at any time\n\n🙋 Want some tips on what I can do? 📲 Reply help"
    gv.send_new_message(browser, sender_info['from'], message, sender_info)


def trigger_new_home(browser, resp, sender_info):
    print("New Home Triggered")
    try:
        location = resp['entities']['location'][0]['value']
    except BaseException:
        location = resp['_text']
    result = location
    print("New Home Location: " + location)
    print(resp)
    try:
        new_home_request(browser, result, sender_info)
    except BaseException:
        send_full_text_message(browser,
                               send_error_text("new home"),
                               sender_info,
                               "💀 Error 💀")


def process_first_message(browser, sender_info):
    print("Inside process_first_message")
    time.sleep(1)
    print("sleeping...")
    print("New message: " + str(sender_info))
    # Boilerplate first message
    message = "\n👋 Hi! I'm TIA 🤗, your Texting 📲 Internet Assistant! I do 💻 tasks via text message, " \
              " so no need for 📶 or Wi-Fi!\n\nI can text you:\n🚗 Directions 🚗\n☔ Weather Forecasts ☔\n🍲 " \
              "Yelp 🍲\n✍️ Language Translation ✍️\n📚 Knowledge Questions 📚 \n🔎 Wikipedia 🔎\n🌏 News from " \
              "around the 🌏\n📺 Late Night Jokes 📺\n💡 Jeopardy Trivia 💡 and more!\n\n🙋‍ " \
              "What's your first name?"
    gv.send_new_message(browser, sender_info['from'], message, sender_info)


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
    # print(new_name_list)
    result = " ".join(new_address_list)
    print(result)
    return result


def process_intro_messages(browser, sender_info):
    current_user = mongo.user_records.find_one({"phone": sender_info['from']})
    # SECOND MESSAGE, ASKING FOR FIRST NAME
    if current_user['count'] == 1:
        name = parse_name(sender_info['body'])
        sender_info = mongo.add_new_item_to_db(sender_info, "name", name)
        print("Hi, " + sender_info['name'] + "!")
        message = "\nIt's a pleasure to 🤗 meet you, " + name + \
            "!\n\nIf you'd like me to set up a 🏠 address for quicker 🚗" \
            " directions and 🌧️ weather, please reply with your full address or NO\n"
        # Sending Message
        gv.send_new_message(browser, sender_info['from'], message, sender_info)
    # FINAL INTRO MESSAGE, ASKING FOR ADDRESS
    # elif current_user['count'] == 2:
    #     if (sender_info['body'].lower() == 'no'):
    #         print('they said no')
    #         message = "\nI totally understand, "
    #     else:
    #         print('they said yes to the address!')
    #         address = parse_address(sender_info['body'])
    #         add_time_zone_offset_from_pst(address, sender_info)
    #         sender_info = mongo.add_new_item_to_db(
    #             sender_info, "home", address)
    #         message = "\nThere's no place like 🏠, "
    #     # Put together a response whether they gave an address or not
    #     message = message + \
    #         str(sender_info['name']) + "! \n\n🙋 Want some tips on what I can do? 📲 Reply help"
    #     gv.send_new_message(browser, sender_info['from'], message, sender_info)
