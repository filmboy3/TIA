# coding=utf8

######################################################
#
# Tia Text Assistant - Internet tasks without using Data/Wi-Fi
# written by Jonathan Schwartz (jonathanschwartz30@gmail.com)
#
######################################################

from __future__ import print_function
import httplib2
import os
from apiclient.discovery import build
import time
import base64
import re
import wikipedia
from apiclient import errors
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import datetime
import requests
import string
import numbers
import math
import random
import calendar
from textblob import TextBlob
from textblob import Word
from dateutil import parser
from faker import Faker
from oauth2client import file, client, tools
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import bs4
import html5lib
from pymongo import MongoClient
import ast
import json
from httplib2 import Http
import apiclient
from googleapiclient import errors
from googleapiclient import discovery
from googleapiclient.discovery import build
import numbers
from yelpapi import YelpAPI
from wit import Wit
# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.action_chains import ActionChains
import google_voice_hub as gv

# LINK UP GOOGLE SHEETS DATABASE

# Setup Google Sheets
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(
    'client_secret_sheet.json', scope)
client = gspread.authorize(creds)

# Open the Spreadsheets
user_info_sheet = client.open('SIA_USERS').sheet1
sms_request_sheet = client.open('SIA_USERS').get_worksheet(1)
api_keys_sheet = client.open('SIA_USERS').get_worksheet(2)

# Download spreadsheet data
tia_user_info = user_info_sheet.get_all_records()
sms_request_info = sms_request_sheet.get_all_records()
api_keys_info = api_keys_sheet.get_all_records()

# Convert spreadsheets to lists
users_converted_to_List = ast.literal_eval(str(tia_user_info))
sms_request_converted_to_List = ast.literal_eval(str(sms_request_info))

# Download API Keys from Database
HERE_APPID = api_keys_sheet.cell(2, 3).value
HERE_APPCODE = api_keys_sheet.cell(2, 4).value
OPEN_WEATHER_API = api_keys_sheet.cell(2, 5).value
NY_TIMES_API = api_keys_sheet.cell(2, 6).value
NEWS_API = api_keys_sheet.cell(2, 7).value
JOKES_URL = api_keys_sheet.cell(2, 8).value
WOLFRAM_API = api_keys_sheet.cell(2, 9).value
SECRET_MONGO_URI = str(api_keys_sheet.cell(2, 13).value)
SECRET_YELP_API = str(api_keys_sheet.cell(2, 14).value)
YELP_API = YelpAPI(SECRET_YELP_API)

# SET UP NLP w/ WIT.AI
WIT_CLIENT = Wit(str(api_keys_sheet.cell(2, 18).value))
print(WIT_CLIENT)
GV_EMAIL = str(api_keys_sheet.cell(2, 16).value)
GV_PASSWORD = str(api_keys_sheet.cell(2, 17).value)

BROWSER = gv.start_google_voice(GV_EMAIL, GV_PASSWORD)
print("Done sleeping after startup of Google Voice")

# WIT.AI NLP-BASED FUNCTIONS ############


def wit_parse_message(message, sender_info):
    print("In the parsing phase...")
    message = message.lower()
    message = re.sub(",", "", message)
    resp = WIT_CLIENT.message(message)
    nlp_extraction(resp, sender_info)


def language_code_convert(language):
    language = language.lower()
    lang_db = {
        "scots gaelic": "gd",
        "afrikaans": "af",
        "albanian": "sq",
        "amharic": "am",
        "arabic": "ar",
        "armenian": "hy",
        "azeerbaijani": "az",
        "basque": "eu",
        "belarusian": "be",
        "bengali": "bn",
        "bosnian": "bs",
        "bulgarian": "bg",
        "catalan": "ca",
        "cebuano": "ceb",
        "chinese": "zh-CN",
        "traditional chinese": "zh-TW",
        "corsican": "co",
        "croatian": "hr",
        "czech": "cs",
        "danish": "da",
        "dutch": "nl",
        "english": "en",
        "esperanto": "eo",
        "estonian": "et",
        "finnish": "fi",
        "french": "fr",
        "frisian": "fy",
        "galician": "gl",
        "georgian": "ka",
        "german": "de",
        "greek": "el",
        "gujarati": "gu",
        "haitian creole": "ht",
        "hausa": "ha",
        "hawaiian": "haw",
        "hebrew": "iw",
        "hindi": "hi",
        "hmong": "hmn",
        "hungarian": "hu",
        "icelandic": "is",
        "igbo": "ig",
        "indonesian": "id",
        "irish": "ga",
        "italian": "it",
        "japanese": "ja",
        "javanese": "jw",
        "kannada": "kn",
        "kazakh": "kk",
        "khmer": "km",
        "korean": "ko",
        "kurdish": "ku",
        "kyrgyz": "ky",
        "lao": "lo",
        "latin": "la",
        "latvian": "lv",
        "lithuanian": "lt",
        "luxembourgish": "lb",
        "macedonian": "mk",
        "malagasy": "mg",
        "malay": "ms",
        "malayalam": "ml",
        "maltese": "mt",
        "maori": "mi",
        "marathi": "mr",
        "mongolian": "mn",
        "myanmar": "my",
        "nepali": "ne",
        "norwegian": "no",
        "nyanja": "ny",
        "pashto": "ps",
        "persian": "fa",
        "polish": "pl",
        "portuguese": "pt",
        "punjabi": "pa",
        "romanian": "ro",
        "russian": "ru",
        "samoan": "sm",
        "serbian": "sr",
        "sesotho": "st",
        "shona": "sn",
        "sindhi": "sd",
        "sinhala": "si",
        "slovak": "sk",
        "slovenian": "sl",
        "somali": "so",
        "spanish": "es",
        "sundanese": "su",
        "swahili": "sw",
        "swedish": "sv",
        "tagalog": "tl",
        "tajik": "tg",
        "tamil": "ta",
        "telugu": "te",
        "thai": "th",
        "turkish": "tr",
        "ukrainian": "uk",
        "urdu": "ur",
        "uzbek": "uz",
        "vietnamese": "vi",
        "welsh": "cy",
        "xhosa": "xh",
        "yiddish": "yi",
        "yoruba": "yo",
        "zulu": "zu",
    }
    try:
        return lang_db[language]
    except BaseException:
        return 'en'


def trigger_newHome(resp, sender_info):
    print("New Home Triggered")
    location = resp['entities']['location'][0]['value']
    result = location
    print("New Home Location: " + location)
    print(resp)
    try:
        new_home_request(result, sender_info)
    except BaseException:
        send_full_text_message(
            send_error_text("new home"),
            sender_info,
            "💀 Error 💀")


def trigger_jokes(resp, sender_info):
    print("Jokes Triggered")
    print(resp)
    jokes_date = "latest"
    # print(resp['entities']['wdatetime'][0]['values'][0]['from']['value'])
    try:
        if (resp['entities']['wdatetime'][0]['values'][0]['from']['value']):
            jokes_date = resp['entities']['wdatetime'][0]['values'][0]['from']['value']
            jokes_date = jokes_date[:10]
    except BaseException:
        pass

    try:
        if (resp['entities']['wit_random'][0]['value']):
            jokes_date = 'random'
    except BaseException:
        pass

    print(jokes_date)
    try:
        send_full_text_message(
            late_night_request(jokes_date),
            sender_info,
            "🌃 Late Night 🌃")
    except BaseException:
        send_full_text_message(
            send_error_text("late night jokes"),
            sender_info,
            "💀 Error 💀")


def use_backup_keywords(resp):
    wit_keyword_list = [
        "wikipedia_search_query",
        "phrase_to_translate",
        "location",
        "wolfram_search_query",
        "wit_news_source",
        "wit_biography_terms",
        "wit_yelp_category"]
    for i in range(0, len(wit_keyword_list)):
        try:
            return resp['entities'][wit_keyword_list[i]][0]['value']
        except BaseException:
            pass
    return resp['_text']


def trigger_translate(resp, sender_info):
    print("Translate Triggered")
    print(resp)

    language = 'english'

    try:
        language = resp['entities']['wit_language'][0]['value']
    except BaseException:
        language = resp['entities']['wit_yelp_category'][0]['value']

    try:
        translationPhrase = resp['entities']['phrase_to_translate'][0]['value']
    except BaseException:
        translationPhrase = use_backup_keywords(resp)

    blob = TextBlob(translationPhrase)
    langCode = language_code_convert(language)
    translation = (resp['_text'], blob.translate(to=langCode))
    result = "Original: '" + translationPhrase + "'\n\nTranslated into 🌏 " + \
        language.capitalize() + " 🌏 '" + str(translation[1]).capitalize() + "'"
    # print(result)
    print("Language Code: ", langCode)
    print("Translation Phrase: ", translationPhrase)

    try:
        send_full_text_message(result, sender_info, "📝 Translation 📝")
    except BaseException:
        send_full_text_message(
            send_error_text("Translation"),
            sender_info,
            "💀 Error 💀")


def trigger_nyt(resp, sender_info):
    print("NY Times Triggered")
    print(resp)
    try:
        send_full_text_message(nyt_request(), sender_info, "📰 NY Times 📰")
    except BaseException:
        send_full_text_message(
            send_error_text("ny times"),
            sender_info,
            "💀 Error 💀")


def trigger_hn(resp, sender_info):
    print("Hacker News Triggered")
    print(resp)
    try:
        send_full_text_message(
            hacker_news_request(),
            sender_info,
            "💻 Hacker News 💻")
    except BaseException:
        send_full_text_message(
            send_error_text("hacker news"),
            sender_info,
            "💀 Error 💀")


def trigger_news(resp, sender_info):
    print("News Triggered")
    print(resp)
    try:
        newsSource = resp['entities']['wit_news_source'][0]['value']
    except BaseException:
        newsSource = 'cnn'
    print("Wit.AI extracted news source: " + newsSource)

    try:
        header = "🌏 " + str(newsSource).upper() + " 🌏"
        print(header)
        send_full_text_message(news_request(newsSource), sender_info, header)
    except BaseException:
        send_full_text_message(
            send_error_text("news"),
            sender_info,
            "💀 Error 💀")


def trigger_help(resp, sender_info):
    print("Help Triggered")
    print(resp)
    command_help_messages(sender_info)


def trigger_wolfram(resp, sender_info):
    print("Wolfram Triggered")
    print(resp)
    try:
        send_full_text_message(
            wolfram_request(
                resp['_text']),
            sender_info,
            "🔭 Wolfram-Alpha 🔭")
    except BaseException:
        send_full_text_message(
            send_error_text("wolfram-alpha"),
            sender_info,
            "💀 Error 💀")


def trigger_wiki(resp, sender_info):
    print("Wikipedia Triggered")
    print(resp)
    wikiSearch = resp['_text']
    try:
        wikiSearch = resp['entities']['wikipedia_search_query'][0]['value']
    except BaseException:
        pass
    try:
        wikiSearch = resp['entities']['wolfram_search_query'][0]['value']
    except BaseException:
        pass

    print("Wit.AI Wikisearch term: " + wikiSearch)
    try:
        send_full_text_message(
            wikipedia_request(
                wikiSearch,
                sender_info),
            sender_info,
            "🔎 Wikipedia 🔎")
    except BaseException:
        send_full_text_message(
            send_error_text("wikipedia"),
            sender_info,
            "💀 Error 💀")

    print(resp)


def trigger_directions(resp, sender_info):
    print("Directions Triggered")
    print(resp)
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

    try:
        send_full_text_message(
            directions_request(
                directions_data,
                sender_info),
            sender_info,
            "🚗 Directions 🚗")
    except BaseException:
        send_full_text_message(
            send_error_text("directions"),
            sender_info,
            "💀 Error 💀")


def fallback_multi_address_parse(text):
    text = text.split(" ")
    fromIndex = text.index("from")
    addressSection = text[fromIndex + 1:]
    addressSection = " ".join(addressSection).split("to")
    origin = addressSection[0]
    destination = addressSection[1]
    result = (origin, destination)
    return result


def trigger_weather(resp, sender_info):
    print("Weather Triggered")
    location = 'home'
    try:
        location = resp['entities']['location'][0]['value']
    except BaseException:
        pass

    try:
        result = location
        print("Weather location: " + location)
        try:
            send_full_text_message(
                weather_request(
                    result,
                    sender_info),
                sender_info,
                "⛅ Weather ⛅")
        except BaseException:
            send_full_text_message(
                send_error_text("Weather"),
                sender_info,
                "💀 Error 💀")
    except BaseException:
        print("Location not found, so checking for Non-Weather keywords ...")
        checkKeywords(resp, sender_info)


def trigger_forecast(resp, sender_info):
    print("Forecast Triggered")
    location = 'home'
    try:
        location = resp['entities']['location'][0]['value']
    except BaseException:
        pass

    try:
        result = location
        print("Forecast location: " + location)
        try:
            send_full_text_message(
                forecast_request(
                    result,
                    sender_info),
                sender_info,
                "🌞 Forecast 🌞")
        except BaseException:
            send_full_text_message(
                send_error_text("forecast"),
                sender_info,
                "💀 Error 💀")
    except BaseException:
        print("Location not found, so checking for Non-Weather keywords ...")
        checkKeywords(resp, sender_info)


def trigger_yelp(resp, sender_info):
    print("Yelp Triggered")
    print(resp)
    try:
        location = resp['entities']['location'][0]['value']
    except BaseException:
        try:
            location = resp['entities']['wit_home'][0]['value']
            location = sender_info['home']
        except BaseException:
            try:
                location = location = resp['entities']['wikipedia_search_query'][0]['value']
            except BaseException:
                location = ""
    try:
        category = resp['entities']['wit_yelp_category'][0]['value']
    except BaseException:
        category = use_backup_keywords(resp)

    print("Yelp Location: " + location)
    print("Yelp Category: " + category)
    result = (category, location)
    # Handling an early edge case in which AI confuses language names with
    # Yelp Ethnic foods, i.e., Chinese (language) vs Chinese (cuisine)
    if (location != ""):
        try:
            send_full_text_message(
                yelp_request(result), sender_info, "🍴 Yelp 🍴")
        except BaseException:
            send_full_text_message(
                send_error_text("Yelp"),
                sender_info,
                "💀 Error 💀")
    else:
        try:
            print("Switching Yelp to Translate Task")
            trigger_translate(resp, sender_info)
        except BaseException:
            pass

    return result


def trigger_jeopardy(resp, sender_info):
    print("Jeopardy Triggered")
    try:
        jeopardyTuple = jeopardy_request()
        jeopardyTogether = jeopardyTuple[0] + jeopardyTuple[1]
        send_full_text_message(jeopardyTogether, sender_info, "📺 Jeopardy 📺")
    except BaseException:
        send_full_text_message(
            send_error_text("jeopardy"),
            sender_info,
            "💀 Error 💀")


def nlp_extraction(resp, sender_info):
    intent_db = {
        "new_home_get": "trigger_newHome",
        "translate_get": "trigger_translate",
        "jokes_get": "trigger_jokes",
        "directions_get": "trigger_directions",
        "news_directory_get": "trigger_news_directory",
        "news_get": "trigger_news",
        "nyt_get": "trigger_nyt",
        "hn_get": "trigger_hn",
        "help_get": "trigger_help",
        "jeopardy_get": "trigger_jeopardy",
        "yelp_get": "trigger_yelp",
        "weather_get": "trigger_weather",
        "forecast_get": "trigger_forecast"
    }
    try:
        intent_result = str(resp['entities']['intent'][0]['value'])
        func_name = intent_db[intent_result] + "(resp, sender_info)"
        print("Function name: " + func_name)
        eval(func_name)
    except BaseException:
        print("Unable to determine intent ... continuing:")
        checkKeywords(resp, sender_info)


def checkKeywords(resp, sender_info):
    preventRepeatCounter = 0
    try:
        if (preventRepeatCounter == 0 and resp['entities']['wit_direction']):
            trigger_directions(resp, sender_info)
            preventRepeatCounter = 1
    except BaseException:
        pass
    try:
        if (preventRepeatCounter == 0 and resp['entities']['wit_jeopardy']):
            trigger_jeopardy(resp, sender_info)
            preventRepeatCounter = 1
    except BaseException:
        pass
    try:
        if (preventRepeatCounter == 0 and resp['entities']['wit_language']):
            trigger_translate(resp, sender_info)
            preventRepeatCounter = 1
    except BaseException:
        pass
    try:
        if (preventRepeatCounter == 0 and resp['entities']['wit_news_source']):
            trigger_news(resp, sender_info)
            preventRepeatCounter = 1
    except BaseException:
        pass
    try:
        if (preventRepeatCounter == 0 and resp['entities']['wit_provider']):
            print("Cruft, remove Intent from Wit.Ai")
            preventRepeatCounter = 1
    except BaseException:
        pass
    try:
        if (preventRepeatCounter ==
                0 and resp['entities']['wit_yelp_category']):
            trigger_yelp(resp, sender_info)
            preventRepeatCounter = 1
    except BaseException:
        pass
    try:
        if (preventRepeatCounter == 0 and resp['entities']['wit_transit']):
            trigger_directions(resp, sender_info)
            preventRepeatCounter = 1
    except BaseException:
        pass
    try:
        if (preventRepeatCounter ==
                0 and resp['entities']['intent'][0]['value'] == "wiki_get"):
            trigger_wiki(resp, sender_info)
            preventRepeatCounter = 1
    except BaseException:
        pass
    try:
        if (preventRepeatCounter ==
                0 and resp['entities']['wolfram_search_query']):
            trigger_wolfram(resp, sender_info)
            preventRepeatCounter = 1
    except BaseException:
        pass
    try:
        if (preventRepeatCounter ==
                0 and resp['entities']['intent'][0]['value'] == "wolfram_get"):
            trigger_wolfram(resp, sender_info)
            preventRepeatCounter = 1
    except BaseException:
        pass
    try:
        if (preventRepeatCounter ==
                0 and resp['entities']['wikipedia_search_query']):
            trigger_wiki(resp, sender_info)
            preventRepeatCounter = 1
    except BaseException:
        pass

# MONGO DB SETUP AND HELPER FUNCTIONS ###


MONGODB_URI = SECRET_MONGO_URI
client = MongoClient(MONGODB_URI, connectTimeoutMS=30000)
db = client.get_database("tia")
message_records = db.message_records
user_records = db.user_records


def get_record(user_id, collection):
    records = collection.find_one({"user_id": user_id})
    return records


def push_record(record, collection):
    collection.insert_one(record)


def update_record(record, updates, collection):
    collection.update_one({'_id': record['_id']}, {
        '$set': updates
    }, upsert=False)


def add_new_item_to_db(sender_info, key, value):
    current_user = user_records.find_one({"phone": sender_info['from']})
    updated_gateway = {
        key: value
    }
    update_record(sender_info, updated_gateway, message_records)
    update_record(current_user, updated_gateway, user_records)
    # Returning a copy of the newly updated message so it can be used
    # immediately back in caller functions
    return message_records.find_one({"sms_id": sender_info['sms_id']})


def update_user_data():
    for sender_info in message_records.find({"status": "unsent"}):
        if user_records.find_one({"phone": sender_info['from']}) is None:
            print("Yes, this is a first-time user")
            new_user_info = {
                "phone": sender_info['from'],
                "name": "NO NAME",
                "home": "NO ADDRESS GIVEN",
                "count": 0
            }
            push_record(new_user_info, user_records)
        else:
            print("Updating an existing record ...")
            existing_user = user_records.find_one(
                {"phone": sender_info['from']})

            # "This is an increment of the userCount..."
            incremented_user_count = {
                "count": (int(existing_user['count']) + 1)
            }
            update_record(existing_user, incremented_user_count, user_records)

            # "This is a transfer of existing user data back to the message"
            shared_user_data = {
                "home": existing_user['home'],
                "count": existing_user['count'],
                "name": existing_user['name']
            }
            update_record(sender_info, shared_user_data, message_records)

# GMAIL API FUNCTIONS / SETUP ###########


try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

import auth
SCOPES = 'https://mail.google.com/'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'start'
authInst = auth.auth(SCOPES, CLIENT_SECRET_FILE, APPLICATION_NAME)
credentials = authInst.get_credentials()

http = credentials.authorize(httplib2.Http())
service = discovery.build('gmail', 'v1', http=http)

import send_email

# Build the Gmail service from discovery
gmail_service = build('gmail', 'v1', http=http)


def messages_label_list(service, user_id, label_ids=[]):
    try:
        response = service.users().messages().list(
            userId=user_id, labelIds=label_ids).execute()
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])
        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(
                userId=user_id, labelIds=label_ids, pageToken=page_token).execute()
            if 'messages' in response:
                messages.extend(response['messages'])
        return messages
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


def get_message(service, user_id, msg_id):
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id).execute()
        print('Message snippet: %s' % message['snippet'])
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)

#   lower and camel case


def delete_message(service, user_id, msg_id):
    try:
        service.users().messages().delete(userId=user_id, id=msg_id).execute()
        print('Message with id: %s deleted successfully.' % msg_id)
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


def modify_message(service, user_id, msg_id, msg_labels):
    try:
        message = service.users().messages().modify(userId=user_id, id=msg_id,
                                                    body=msg_labels).execute()
        label_ids = message['labelIds']
        print('Message ID: %s - With Label IDs %s' % (msg_id, label_ids))
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


def create_message_labels():
    """Create object to update labels.

    Returns:
      A label update object.
    """
    return {'removeLabelIds': ['UNREAD'], 'addLabelIds': []}


def send_message(gv_number, gv_message, sender_info):
    print("Triggered Sending Message on GV")
    gv.send_reply(gv_number, gv_message, BROWSER)
    mark_as_sent(sender_info)


def mark_as_sent(sender_info):
    updated_status = {
        "status": "sent"
    }
    update_record(sender_info, updated_status, message_records)
    print("Successfully marked message as sent")


def mark_as_error(sender_info):
    updated_status = {
        "status": "error"
    }
    update_record(sender_info, updated_status, message_records)
    print("Marked message as error")

# LOCATION-BASED FUNCTIONS (WEATHER/


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
    url = "https://geocoder.cit.api.here.com/6.2/geocode.json?app_id=" + \
        str(HERE_APPID) + "&app_code=" + str(HERE_APPCODE) + "&searchtext="
    for s in string.punctuation:
        location_str = location_str.replace(s, '')
    location_str = location_str.split(" ")
    location_str = "+".join(location_str)
    url = url + location_str
    print(url)
    json_data = requests.get(url).json()
    return json_data


def get_lat_long(str):
    json_data = lookup_single_location(str)
    lat_long = []
    lat_long.append(json_data['Response']['View'][0]['Result']
                    [0]['Location']['DisplayPosition']['Latitude'])
    lat_long.append(json_data['Response']['View'][0]['Result']
                    [0]['Location']['DisplayPosition']['Longitude'])
    return lat_long


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
        zip = home.split(" ")
        zip = str(zip[len(zip) - 1])
        url = "http://api.openweathermap.org/data/2.5/weather?appid=" + \
            str(OPEN_WEATHER_API) + "&zip=" + zip
        subject_label = "🏠"
    else:
        api_address = "http://api.openweathermap.org/data/2.5/weather?appid=" + \
            str(OPEN_WEATHER_API) + "&zip="
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
        "Today in " +
        subject_label.upper() +
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
    outer = "Your 5-Day Forecast for " + subject_label.upper() + "\n"
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
        zip = home.split(" ")
        zip = str(zip[len(zip) - 1])
        url = "http://api.openweathermap.org/data/2.5/forecast?appid=" + \
            str(OPEN_WEATHER_API) + "&zip=" + zip
        subject_label = "🏠"
    # Or input zipcode
    else:
        api_address = "http://api.openweathermap.org/data/2.5/forecast?appid=" + \
            str(OPEN_WEATHER_API) + "&zip="
        url = api_address + get_zip(subject_label)
    json_data = requests.get(url).json()
    result = readable_forecast(json_data['list'], subject_label)
    return result


def remove_subject_command(subject_label):
    subject_label = subject_label.split(" ")
    print(subject_label)
    subject_label.pop(0)
    subject_label = " ".join(subject_label)
    return subject_label


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
        HERE_APPID + "&app_code=" + HERE_APPCODE + "&waypoint0=geo!" + \
        str(lat_long_list[0][0]) + "," + str(lat_long_list[0][1]) + "&waypoint1=geo!" + str(lat_long_list[1][0]) + "," + \
        str(lat_long_list[1][1]) + "&mode=fastest;" + transit_mode + ";traffic:enabled"
    print(url)
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
    print(home)

    lat_long_origin = []
    # If either start or final destination are the home, then change it to
    # saved home address.
    if (subject_label[0] == 'home'):
        if str(home) == "NO ADDRESS GIVEN":
            return "😟 Sorry, but I don't have your 🏠 address on file ... "
        lat_long_origin.append(get_lat_long(home))
    else:
        lat_long_origin.append(get_lat_long(subject_label[0]))
    if (subject_label[1] == 'home'):
        if str(home) == "NO ADDRESS GIVEN":
            return "😟 Sorry, but I don't have your 🏠 address on file ... "
        lat_long_origin.append(get_lat_long(home))
    else:
        lat_long_origin.append(get_lat_long(subject_label[1]))
    return lat_long_origin

# YELP FUNCTIONS #


def yelp_request(query):
    limit = 3
    return full_results_yelp_search(query[0], query[1], limit)


def full_results_yelp_search(categories, location, limit):
    search_results = YELP_API.search_query(
        term=categories, location=location, limit=limit)
    yelp_fully_formatted = format_yelp_search(search_results, limit)
    return yelp_fully_formatted


def format_yelp_search(search_results, limit):
    result = [""]
    for i in range(limit):
        result.append(format_single_yelp_biz(search_results['businesses'][i]))
    return "\n\n☕☕☕☕☕☕☕☕☕\n\n".join(result)


def format_single_yelp_biz(listing):
    reviews_formatted = format_yelp_reviews(listing['id'])
    more_details = fetch_more_yelp_details(listing['id'])
    name = ""
    try:
        name = "😋 " + listing['name'].upper() + " 😋\n"
    except BaseException:
        name = ""
    try:
        review_count = "\n🍲 " + str(listing['review_count']) + " reviews 🍲"
    except BaseException:
        review_count = ""
    try:
        rating = "\n🌟 " + str(listing['rating']) + ' stars 🌟'
    except BaseException:
        rating = ""
    categories = []
    try:
        for j in range(0, len(listing['categories'])):
            categories.append(" " + str(listing['categories'][j]['title']))
    except BaseException:
        categories = ""
    try:
        price = "\n💵 " + listing['price'] + " 💵"
    except BaseException:
        price = ""
    try:
        display_address = "\n🏠 " + \
            " ".join(listing['location']['display_address']) + " 🏠"
    except BaseException:
        display_address = ""
    try:
        display_phone = "\n☎ " + listing['display_phone'] + " ☎\n\nReviews:"
    except BaseException:
        display_phone = ""
    result = [name,
              review_count,
              rating,
              "\n🍳 " + str(" |".join(categories)) + " 🍳",
              price,
              str(more_details['is_open_now']),
              str(more_details['hours']),
              display_address,
              str(more_details['cross_streets']),
              display_phone,
              reviews_formatted]
    return "".join(result)


def format_yelp_reviews(id):
    reviews_results = YELP_API.reviews_query(id)
    total = "\n"
    for i in range(0, len(reviews_results)):
        text_review = str(reviews_results['reviews'][i]['text'])
        text_review = text_review.replace('\n', ' ')
        star_singular = " stars 🌟"
        if reviews_results['reviews'][i]['rating'] == 1:
            star_singular = " star 🌟"
        rating = "\n🌟 " + \
            str(reviews_results['reviews'][i]['rating']) + star_singular
        user = reviews_results['reviews'][i]['user']['name']
        date = str(reviews_results['reviews'][i]['time_created'].split(" ")[0])
        total = total + "\n" + rating + "\n🍽️" + " '" + \
            str(text_review) + "'\n--" + str(user) + \
            " on " + date_reformat(date) + " 🍽️"
    return total


def fetch_more_yelp_details(id):
    details = YELP_API.business_query(id=id)
    more_details = {}
    try:
        if details['location']['cross_streets'] != "":
            more_details['cross_streets'] = "\n🛣️ X-Streets: " + \
                details['location']['cross_streets'] + " 🛣️"
        else:
            more_details['cross_streets'] = ""
    except BaseException:
        more_details['cross_streets'] = ""
    try:
        hours_formatted = ""
        today_hours = "\nToday's ⌚: " + time_reformat(
            details['hours'][0]['open'][0]['start']) + " - " + time_reformat(
            details['hours'][0]['open'][0]['start'])
        tomorrow_hours = "\nTomorrow's ⌚: " + time_reformat(
            details['hours'][0]['open'][1]['start']) + "-" + time_reformat(
            details['hours'][0]['open'][1]['start'])
        hours_formatted = today_hours + tomorrow_hours
        more_details['hours'] = hours_formatted
    except BaseException:
        more_details['hours'] = ""
    try:
        more_details['is_open_now'] = details['hours'][0]['is_open_now']
        if more_details['is_open_now']:
            more_details['is_open_now'] = "\n🔓 Open Now 🔓"
        else:
            more_details['is_open_now'] = "\n🔒 Closed Now 🔒"
    except BaseException:
        more_details['is_open_now'] = ""
    return more_details


def date_reformat(date):
    split_date = date.split("-")
    new_date = []
    if split_date[1][0] == str(0):
        new_date.append(split_date[1][1])
    else:
        new_date.append(split_date[0])
    if split_date[2][0] == str(0):
        new_date.append(split_date[2][1])
    else:
        new_date.append(split_date[2])
    new_date.append(split_date[0][2:])
    return "/".join(new_date)


def time_reformat(time_string):
    hours = int(time_string[:2])
    min = time_string[2:]
    period = "AM"
    if hours > 12:
        hours = hours - 12
        period = "PM"
    return str(hours) + ":" + min + " " + period

# NEWS FUNCTIONS #


def news_source_parse(source):
    source = source.lower()
    news_sources_db = {
        "ap": "associated-press",
        "abc": "abc-news",
        "australian abc": "abc-news-au",
        "al jazeera": "al-jazeera-english",
        "ars technica": "ars-technica",
        "axios": "axios",
        "bbc": "bbc-news",
        "bbc sport": "bbc-sport",
        "br": "bleacher report",
        "bloomberg": "bloomberg",
        "business insider": "business-insider",
        "business insider uk": "business-insider-uk",
        "buzzfeed": "buzzfeed",
        "cbc": "cbc-news",
        "cbs": "cbs-news",
        "cnbc": "cnbc",
        "cnn": "cnn",
        "crypto": "crypto-coins-news",
        "daily mail": "daily-mail",
        "engadget": "engadget",
        "ew": "entertainment-weekly",
        "espn": "espn",
        "financial post": "financial-post",
        "ft": "financial times",
        "fortune": "fortune",
        "fox-sports": "fox-sports",
        "google news": "google-news",
        "google news uk": "google-news-uk",
        "ign": "ign",
        "the independent": "independent",
        "mashable": "mashable",
        "medical": "medical-news-today",
        "metro": "metro",
        "daily mirror": "mirror",
        "msnbc": "msnbc",
        "mtv": "mtv-news",
        "british mtv": "mtv-news-uk",
        "national-geographic": "national-geographic",
        "national-review": "national-review",
        "nbc": "nbc-news",
        "new scientist": "new-scientist",
        "news.com": "news-com-au",
        "newsweek": "newsweek",
        "nymag": "new york magazine",
        "next big future": "next-big-future",
        "nfl": "nfl-news",
        "nhl": "nhl-news",
        "politico": "politico",
        "polygon": "polygon",
        "recode": "recode",
        "reddit": "reddit-r-all",
        "reuters": "reuters",
        "techcrunch": "techcrunch",
        "techradar": "techradar",
        "economist": "the-economist",
        "Globe and Mail": "the-globe-and-mail",
        "the guardian": "the-guardian-uk",
        "the guardian australian": "the-guardian-au",
        "huffpost": "the-huffington-post",
        "irish times": "irish-times",
        "the lad bible": "the-lad-bible",
        "the next web": "the-next-web",
        "the sport bible": "the-sport-bible",
        "the telegraph": "the-telegraph",
        "the verge": "the-verge",
        "wall street journal": "the-wall-street-journal",
        "the washington post": "the-washington-post",
        "the washington times": "the-washington-times",
        "time": "time",
        "usa today": "usa-today",
        "vice": "vice-news",
        "wired": "wired"
    }
    try:
        return news_sources_db[source]
    except BaseException:
        return 'cnn'


def get_domain_for_hn(url):
    pat = r'((https?):\/\/)?(\w+\.)*(?P<domain>\w+)\.(\w+)(\/.*)?'
    m = re.match(pat, url)
    if m:
        domain = m.group('domain')
        return domain
    else:
        return False


def hacker_news_request():
    url = "https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty"
    json_data = requests.get(url).json()
    full_text = ""
    for i in range(0, 30):
        newUrl = "https://hacker-news.firebaseio.com/v0/item/" + \
            str(json_data[i]) + ".json?print=pretty"
        item_json_data = requests.get(newUrl).json()
        num_as_string = str(i + 1)
        domainStr = ""
        try:
            domainStr = str(get_domain_for_hn(str(item_json_data['url'])))
        except BaseException:
            print("Domain Str is not present")
        inner_combine = num_as_string + ": " + \
            str(item_json_data['title']) + "\n🔼 " + \
            str(item_json_data['score']) + " 🔼" + \
            domainStr + "\n\n"
        full_text += inner_combine
    return full_text


def nyt_request():
    url = "https://api.nytimes.com/svc/topstories/v2/home.json?api-key=" + NY_TIMES_API
    json_data = requests.get(url).json()
    print(json_data)
    print(type(json_data))
    full_text = ""
    for i in range(0, len(json_data['results']) - 1):
        phrase = ""
        section = str(json_data['results'][i]['section'])
        title = str(json_data['results'][i]['title'])
        abstract = str(json_data['results'][i]['abstract'])
        phrase = str("🗽 " + section + " 📰 '" + title + "' 📰\n" + abstract + " 🗽\n\n")
        if section != "Briefing":
            full_text += phrase
    return full_text


def news_request(news):
    print("Inside the news_request")
    sourceInsert = news_source_parse(news)
    print("Source Insert: " + sourceInsert)
    url = "https://newsapi.org/v2/top-headlines?sources=" + \
          sourceInsert + "&apiKey=" + NEWS_API
    print("News url: " + url)
    json_data = requests.get(url).json()
    articles = json_data['articles']
    full_text = "Top Headlines from " + articles[0]['source']['name'] + ":\n\n"
    for i in range(0, len(articles)):
        title = articles[i]['title']
        description = ""
        if str(articles[i]['description']) != "None":
            description = "\n" + articles[i]['description']
        inner_combine = "📰 " + title + \
            " 🌏 " + description + " 📰\n\n"
        full_text += inner_combine
    return full_text


def trigger_news_directory(resp, sender_info):
    news_directory_text = "Here are the available news sources you can use: \n\n📰 abc 📰" \
                          "ap 📰 abc 📰 abc au 📰 al jazeera 📰 ars technica 📰 axios 📰" \
                          " bbc 📰 bbc sport 📰 br 📰 bloomberg 📰 business " \
                          "insider 📰 business insider uk 📰 buzzfeed 📰 cbc 📰 cbs 📰 " \
                          "cnbc 📰 cnn 📰 crypto 📰 daily mail 📰 engadget 📰 ew 📰 espn 📰" \
                          " financial post 📰 ft 📰 fortune 📰 fox sports 📰 google 📰 google " \
                          "uk 📰 hn 📰 ign 📰\n📰 independent 📰 mashable 📰 medical 📰 metro 📰 " \
                          "mirror 📰 msnbc 📰 mtv 📰 mtv uk 📰 national geographic 📰 national " \
                          "review 📰 nbc 📰 new scientist 📰 com au 📰week 📰 nymag 📰 future 📰" \
                          " nfl 📰 nhl 📰 politico 📰 polygon 📰 recode 📰 reddit 📰 reuters 📰 " \
                          "techcrunch 📰 techradar 📰 economist 📰 globe and mail 📰 guardian 📰 " \
                          "guardian au 📰 huffpost 📰 the irish times 📰 lad bible 📰 nyt 📰 next " \
                          "web 📰 sport bible 📰 telegraph 📰 verge 📰 wsj 📰 washington post 📰 " \
                          "washington times 📰 time 📰 usa today 📰 vice 📰 wired 📰"
    try:
        header = "🌏 News Directory 🌏"
        print(header)
        send_full_text_message(news_directory_text, sender_info, header)
    except BaseException:
        send_full_text_message(
            send_error_text("news"),
            sender_info,
            "💀 Error 💀")

# JUST-FOR-FUN FUNCTIONS #


def jeopardy_request():
    url = "http://jservice.io/api/random?count=1"
    json_data = requests.get(url).json()
    category_id = json_data[0]["category"]["id"]

    url = "http://jservice.io/api/category?id=" + str(category_id)
    json_data = requests.get(url).json()

    total_clues = json_data['clues_count']
    clues_in_category = 5
    multiple = (total_clues / 5) - 1
    starting_index = round(random.random() * multiple) * clues_in_category

    category = str(json_data["title"].upper())
    total_string = ""
    air_year = str(json_data['clues'][starting_index]["airdate"].split("-")[0])
    total_string = category + " (" + air_year + ")\n\n"

    answer_key = "\n🚧 🚧 🚧 🚧 🚧 🚧 \n⬇️" \
                 " SPOILERS ⬇️\n🚧 🚧 🚧 🚧 🚧 🚧 \n\n"
    answer_key = answer_key + total_string

    for i in range(starting_index, starting_index + 5):
        if (str(json_data['clues'][i]["invalid_count"]) == 1):
            return jeopardy_request()
        response = str(json_data['clues'][i]["question"])
        value = "💰 $" + str(json_data['clues'][i]["value"]) + "💰"
        if (str(json_data['clues'][i]["value"]) == "None"):
            return jeopardy_request()
        total_string = total_string + value + " " + response + "\n\n"
        answer_question = str(json_data['clues'][i]["answer"])
        answer_key = answer_key + response + \
            " 🎯 " + answer_question + " 🎯 " + "\n\n"
    answer_key = answer_key.replace('<i>', '')
    answer_key = answer_key.replace('</i>', '')
    return (total_string, answer_key)


def late_night_request(response):
    url = JOKES_URL
    json_data = requests.get(url).json()
    json_data = json_data['feed']['entry']
    if response == "latest":
        query_date = str(datetime.datetime.now())
        query_date = str(query_date.split(" ")[0]) + " 00:00:00"
        query_date = parser.parse(query_date)
    elif response == "random":
        fake = Faker()
        start_date = datetime.date(2009, 12, 3)
        query_date = fake.date_between(start_date=start_date, end_date='today')
        query_date = parser.parse(str(query_date))
        print("Random Query Date: " + str(query_date))
    else:
        query_date = parser.parse(response)
        print(query_date)

    date_counter = 50
    total_jokes = ""

    for i in range(0, len(json_data)):
        date = json_data[i]['gsx$date']['$t']
        current_date = parser.parse(date)

        distance = abs(int(str(query_date - current_date).split(" ")[0]))

        if distance > 1:
            if distance < date_counter:
                date_counter = distance
                jokes = str(json_data[i]['content']['$t'])
                jokes = re.sub("jokes:.", "😂 ", jokes)
                jokes = re.sub(", joke\S+.", " 😂\n\n😂 ", jokes)
                total_jokes = "🌃 " + \
                    str(date).split(" ")[0] + " 🌃\n\n" + str(jokes) + "\n\n"
        elif distance == 1:
            date_counter = distance
            next_day = json_data[i + 1]['gsx$date']['$t']
            print("Trigger Elif")
            jokes = str(json_data[i + 1]['content']['$t'])
            jokes = re.sub("jokes:.", "😂 ", jokes)
            jokes = re.sub(", joke\S+.", " 😂\n\n😂 ", jokes)
            total_jokes = "🌃 " + \
                str(next_day).split(" ")[0] + "🌃\n\n" + str(jokes) + "\n\n"
            break

    return total_jokes

# INFORMATION FUNCTIONS #######


def wikipedia_request(command_body, sender_info):
    return wiki_split(wikipedia.summary(command_body))

def wiki_split(text_input):
    text_input = re.sub('"', "\'", str(text_input))
    text_input = re.sub("'", "\'", str(text_input))
    text_input = re.sub('%', " percent", str(text_input))
    wiki = TextBlob(text_input)
    chunked = wiki.sentences
    
    total_string = []
    for i in range(0, len(chunked)):

        total_string.append(str(chunked[i]))

    total_string =  " 📖 \n\n 📖 ".join(total_string)
    return total_string

def wolfram_request(input):
    print("triggered wolf alert inside with: " + str(input))
    original_input = input
    input = re.sub(" ", "%20", str(input))
    url = "http://api.wolframalpha.com/v2/query?appid=" + \
        WOLFRAM_API + "&input=" + input + "&output=json"
    print(url)
    json_data = requests.get(url).json()
    result = "Question: '" + str(original_input) + "'\n\n📚 Answer: " + str(
        json_data['queryresult']['pods'][1]['subpods'][0]['plaintext'])
    return result


def wolfram_examples_request():
    return "You can compute 💻 expert-level answers using Wolfram's breakthrough algorithms," \
    " 💡 knowledgebase and AI 🤖 technology.\n\nGeneral query topics include ➗ Mathematics, " \
    "🔬 Science & Technology, 🎭 Society & Culture and 🍴 Everyday Life 🏀 📖\n\n✨ Examples ✨\n" \
    "\n📖 Mini Cooper Roadster 📖 📖 " \
    " total length of all roads in Spain 📖 📖 motorcycle traffic in Germany 📖 📖 " \
    "annual deaths from auto accients in the Czech Republic 📖 📖 price of gasoline in Dallas " \
    "📖 📖 length of USS Ronald Reagan 📖 📖 United States railway length" \
    " 📖 📖 Apollo 11 📖 📖 heart 📖 📖 nerve supply of gallbladder " \
    "📖 📖 musk rose 📖 📖 BAC 5 drinks, 2 hours, male, 180lb 📖 📖 " \
    "who invented the cell phone 📖 📖 inventions by Benjamin Franklin 📖" \
    " 📖 BMI 5'10\", 165lb 📖 📖 generate a 12 character password 📖 📖" \
    " Morse code 'Wolfram Alpha' 📖 📖 what is the french equivalent ring size " \
    "to ring size 2? 📖 📖 U.K. men's size 11 shoe in Japanese size 📖 📖 " \
    "vehicles with highway gas mileage > 42 mpg 📖 📖 calories in a serving of " \
    "pineapple 📖 📖 Birthdays of the discoverers of Neptune 📖 📖 Robert Pattinson" \
    " birthday moon phase 📖 📖 population of the US on Obama's birthday 📖 📖 " \
    "Notable people born in New Orleans metro area 📖 📖 famous people from Detroit 📖 📖" \
    " Who is Angelina Jolie's brother? 📖 📖 Claude Monet's death date 📖 📖" \
    " broccoli nutrition label 📖 📖 whopper vs baconator vs big mac 📖 📖 " \
    "2 slices of swiss cheese 📖 📖 how many people does a 20 pound turkey feed " \
    "📖 📖 unemployment rate North Dakota 📖 📖 construction cost of Lambeau Field" \
    " / population of Green Bay 📖 📖 head width of tennis racket 📖 📖 cost of living" \
    " index Boston 📖 📖 Easter 1910 📖 📖 How many days until Labor Day " \
    "📖 📖 weather Vancouver, San Diego, Buenos Aires 📖 📖 caffeine in 24 oz." \
    " coffee, 24 oz. soda 📖 📖 average lifespan of a horse, goat, and sheep 📖 📖 " \
    " define triangulate 📖 📖 synonyms granular 📖 📖 mortgage $150,000, 6.5%, " \
    "30 years 📖 📖 cost of living index Boulder vs Sacramento 📖 📖 _al__la__ 📖" \
    " 📖 who was King of England when WWI ended? 📖 📖 stars visible tonight " \
    "📖 📖 next eclipse 📖 📖 acroynym USSS 📖 📖 price of movie ticket " \
    "in Providence, Nashville, Boise 📖 📖 words that rhyme with demand 📖 📖 do" \
    " you know a dirty joke? 📖 📖 where in the world is carmen sandiego? 📖 📖 " \
    "what's a car's safe braking distance at 60 mph 📖 📖 9th Wedding anniversary 📖 📖" \
    " anagrams trace 📖 📖 population Madrid / population spain 📖 📖 marijuana " \
    "cases in NY courts 📖 📖 5 largest countries by area 📖 📖 Who wrote Stairway to Heaven?" \
    " 📖 📖 characters in a Midsummer Night's Dream 📖 📖 Mary Shelley's place of " \
    "birth 📖 📖 3 hours in the sun with SPF 15 in Kabul at noon 📖 📖 x+y=10, x-y=4 " \
    "📖 📖 convert 1/6 to percent 📖 📖 facts about Galileo 📖 📖 movies " \
    "starring Kevin Bacon and Tom Cruise 📖 📖 Greek for 'Pythagoras' 📖 📖 what" \
    " was the age of Leonardo when the Mona Lisa was painted? 📖 📖 Academy Awards won " \
    "by Meryl Streep 📖 📖 Michael Jordan points per game in 1996 postseason 📖 📖" \
    " How many medals has Michael Phelps won? 📖 📖 16th President of the United" \
    " States 📖 📖 Warren Buffett net worth 📖 📖 Wikipedia popularity of Betty" \
    " White 📖 📖 $29.95 - 15% 📖 📖 30 percent of 8 miles 📖 📖 Rachel " \
    "has 17 apples. She gives 9 to Sarah. How many apples does Rachel have now? 📖 📖 1/4" \
    " * (4 - 1/2) 📖 📖 How many baseballs fit in a Boeing 747? 📖 📖 pennis to cover" \
    " 2 square miles 📖 📖 How many grains of rice would it take to stretch around the moon? " \
    "📖 📖 tic-tac-toe game 📖 📖 5 dice 📖 📖 32 coin tosses 📖 📖 8:5" \
    " odds, bet 97 euros 📖 📖 chance 3 people share a birthday 📖 📖 probability 2 " \
    "people born in same month 📖"


def send_full_text_message(result, sender_info, topic):
    tia_sign_off = "\n\n--😘,\n✨ Tia ✨\nText" \
            " 📲 me another request, " + str(
            sender_info['name']) + ", or text HELP"
    result = "I've got some " + str(topic) + " info for you, " + str(
        sender_info['name']) + "!\n\n" + result + tia_sign_off
    try:
        send_message(sender_info['from'], result, sender_info)
        print("Responded to request successfully: " + str(topic))
    except BaseException:
        print("Error, was unable to respond to request")
        mark_as_error(sender_info)
        result = "I'm so sorry, " + str(sender_info['name']) + ", " \
            "but I'm having a tough time with your " + str(
            topic) + " request. Please try again." + tia_sign_off
        send_message(sender_info['from'], result, sender_info)
    time.sleep(1)


def send_error_text(text):
    return "\n😟 I hate to be the bearer of bad 🗞️, but right now, your " + \
        text + " request didn't work ... 🙏 try again!"


def process_message(sender_info):
    current_user = user_records.find_one({"phone": sender_info['from']})
    # If they haven't texted much with TIA (i.e., the count), she first sends
    # some intro messages
    if current_user['count'] < 1:
        print("Inside process message")
        process_first_message(sender_info)
    elif current_user['count'] < 3:
        process_intro_messages(sender_info)
    # Otherwise, she processes the users' messages
    else:
        wit_parse_message(sender_info['body'], sender_info)


def scrub_html_from_message(message):
    print("Attempting to Scrub message here")
    scrub_dict = {
        "&nbsp;": " ",
        "&amp;": "&",
        "&quot;": '"',
        "&ndash;": "--",
        "&#39;": "'",
    }
    for key, value in scrub_dict.items():
        message = re.sub(key, value, message)
    print("New Message: " + str(message))
    return str(message)


# OPENING GREETING FUNCTIONS FOR NEW USER

# Help Message

def command_help_messages(sender_info):
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
    send_message(sender_info['from'], message, sender_info)


def new_home_request(command, sender_info):
    sender_info = add_new_item_to_db(sender_info, "home", command)
    message = "\nNice digs, " + \
        str(sender_info['name']) + "!\n\nText me 'new home' with your address to change 🏠 at any time"
    send_message(sender_info['from'], message, sender_info)


def process_first_message(sender_info):
    print("Inside process_first_message")
    time.sleep(1)
    print("sleeping...")
    print("New message: " + str(sender_info))
    # Boilerplate first message
    message = "\n👋 Hi! I'm TIA 🤗, your Texting 📲 Internet Assistant!\n\nI do 💻 tasks via text messages, " \
              " so no need for 📶 or Wi-Fi!\n\nI can text you:\n🚗 Directions 🚗\n☔ Weather Forecasts ☔\n🍲 " \
              "Yelp 🍲\n✍️ Language Translation ✍️\n📚 Knowledge Questions 📚 \n🔎 Wikipedia 🔎\n🌏 News 📰 from " \
              "around the 🌏\n📺 Late Night Jokes 📺\n💡 Jeopardy Trivia 💡\nand more!\n\n🙋‍ " \
              "What would you like me to 💬 call you?"
    send_message(sender_info['from'], message, sender_info)


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


def process_intro_messages(sender_info):
    current_user = user_records.find_one({"phone": sender_info['from']})
    # SECOND MESSAGE, ASKING FOR FIRST NAME
    if current_user['count'] == 1:
        name = parse_name(sender_info['body'])
        sender_info = add_new_item_to_db(sender_info, "name", name)
        print("Hi, " + sender_info['name'] + "!")
        message = "\nIt's a pleasure to 🤗 meet you, " + name + \
            "!\n\nIf you'd like me to set up a 🏠 address for quicker 🚗" \
            " directions and 🌧️ weather, please reply with your full address or NO\n"
        # Sending Message
        send_message(sender_info['from'], message, sender_info)
    # FINAL INTRO MESSAGE, ASKING FOR ADDRESS
    elif current_user['count'] == 2:
        if (sender_info['body'].lower() == 'no'):
            print('they said no')
            message = "\nI totally understand, "
        else:
            print('they said yes to the address!')
            address = parse_address(sender_info['body'])
            sender_info = add_new_item_to_db(sender_info, "home", address)
            print(
                "\nNice digs, " +
                sender_info['name'] +
                "! Is your address really ... " +
                sender_info['home'] +
                "?")
            message = "\nNice digs, "
        # Put together a response whether they gave an address or not
        message = message + str(sender_info['name']) + "! \n\n🙋 Want to learn how I can help you? 📲 Reply help"
        send_message(sender_info['from'], message, sender_info)


def process_all_unsent():
    for message in message_records.find({"status": "unsent"}):
        process_message(message)


def database_new_item(phone, message):
    print("Yes, This is a new item ...")
    print(message)
    record = {
        "sms_id": datetime.datetime.now(),
        "body": scrub_html_from_message(message),
        "from": phone,
        "status": "unsent",
        "result": "tba"
    }
    print(record)
    push_record(record, message_records)

############################################ LOOPING TIA #################


def parse_num_from_GV(fromLabel):
    new_num = ["+1"]
    isolated_from = fromLabel[1:15]
    for i in range(0, len(isolated_from)):
        if isolated_from[i].isnumeric():
            new_num.append(isolated_from[i])
    mongo_num = "".join(new_num)
    return mongo_num


def parse_message_from_GV(message):
    mongo_message = re.search(
        r'Google Voice (.*?) YOUR ACCOUNT HELP CENTER HELP FORUM',
        str(message)).group(1)
    mongo_message = re.sub(
        r'To respond to this text message, reply to this email or visit Google Voice.',
        '', mongo_message)
    return mongo_message


def mark_as_read():
    a = messages_label_list(service, 'me', label_ids=['UNREAD'])[0]['id']
    modify_message(service, 'me', a, create_message_labels())
    print("Completed Removing of the Label for " + a + "?")


def run_sms_assist():
    # A 'temp' global variable is initialized since
    # we need to be able to keep track of the most
    # recent 'unread' email for deleting/marking-as-read purposes
    temp = ''

    def inner():
        print('Starting...')
        a = messages_label_list(service, 'me', label_ids=['UNREAD'])[0]['id']
        nonlocal temp
        if a != temp:
            try:
                b = get_message(service, 'me', a)
                fromLabel = ""
                subject_label = ""
                # Parsing the 'From' and 'Subject's of the email
                for item in b['payload']['headers']:
                    if item['name'] == 'From':
                        fromLabel = item['value']
                        mongo_num = parse_num_from_GV(fromLabel)

                    if item['name'] == 'Subject':
                        subject_label = item['value']
                        mongo_message = parse_message_from_GV(b['snippet'])
                if "New text message from" in str(subject_label):
                    print("Received a new TIA-related message")
                    print(mongo_num)
                    print(mongo_message)
                    database_new_item(mongo_num, mongo_message)
                    # Run Full Script
                    time.sleep(2)
                    mark_as_read()
            except BaseException:
                print("No new messages ...")
        try:
            update_user_data()
            process_all_unsent()
        except BaseException:
            print("Moving on to next loop ...")
        temp = a
        time.sleep(10)
    while True:
        try:
            inner()
            time.sleep(10)
        except BaseException:
            time.sleep(10)
            print('Hit an error... trying to avoid a crash here')

            
run_sms_assist()
