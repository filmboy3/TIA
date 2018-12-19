# coding=utf8

######################################################
#
# Tia Text Assistant - Internet tasks without using Data/Wi-Fi
# written by Jonathan Schwartz (jonathanschwartz30@gmail.com)
#
######################################################

from __future__ import print_function
import re
import datetime
import requests
from dateutil import parser
from faker import Faker
from datetime import datetime
import re
import time
import general_message_helpers as msg_gen
import api_keys as SHEETS
import pytz
from datetime import datetime, timedelta
from datetime import *


def random_joke():
    import mongo_helpers as mongo
    joke_raw = mongo.jokes_records.aggregate(
        [ { "$sample": {'size': 1} } ] 
    )
    joke_full = list(joke_raw)
    return joke_full[0]

def record_jokes_in_db(date, joke):
    import mongo_helpers as mongo
    new_joke = {
        "date": date,
        "joke": joke
    }
    if mongo.jokes_records.find_one({"date": date}) is None:
       mongo.push_record(new_joke, mongo.jokes_records)
       print("Pushed new joke")
    else:
        old_data = mongo.jokes_records.find_one({"date": date})
        print("Old joke: old_data")


def late_night_request(response):
    import mongo_helpers as mongo
    joke_text = ""

    if response == "random":
        return random_joke()
    else:
        if response == "latest":
            today = str(date.today())
            query_date = parser.parse(today)
        else:
            query_date = parser.parse(response)

        date_new_low = 50
        temp_message = ""

        for message in mongo.jokes_records.find():
            date_check = parser.parse(message['date'])
            date_diff = query_date - date_check
            if date_diff.days == 0:
                joke_text = message['joke']
                return joke_text
            elif abs(date_diff.days) < date_new_low:
                temp_message = message['joke']
                date_new_low = date_diff.days

        return temp_message

    return joke_text

def trigger_jokes(resp, sender_info):
    print("Jokes Triggered")
    print(resp)
    jokes_date = "latest"
    try:
        jokes_date = resp['entities']['wdatetime'][0]['values'][0]['from']['value']
        jokes_date = jokes_date[:10]
    except BaseException:
        try:
            jokes_date = resp['entities']['datetime'][0]['value']
            jokes_date = jokes_date[:10]
        except BaseException:
            pass

    try:
        if (resp['entities']['wit_random'][0]['value']):
            jokes_date = 'random'
    except BaseException:
        pass

    print(jokes_date)
    msg_gen.store_jokes_in_mongo(
                                       late_night_request(jokes_date),
                                       sender_info,
                                       "🌃 Late Night 🌃"
                                       )