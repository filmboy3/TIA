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
import message_boilerplates as msg_boiler
import general_message_helpers as msg_gen
import google_sheets_api_storage as SHEETS


def late_night_request(response):
    url = SHEETS.JOKES_URL
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


def trigger_jokes(resp, sender_info):
    print("Jokes Triggered")
    print(resp)
    jokes_date = "latest"
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
        msg_gen.send_full_text_message(
            late_night_request(jokes_date),
            sender_info,
            "🌃 Late Night 🌃")
    except BaseException:
        msg_gen.send_full_text_message(
            msg_boiler.send_error_text("late night jokes"),
            sender_info,
            "💀 Error 💀")
