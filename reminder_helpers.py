
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
from dateutil import parser
import datetime 
import general_message_helpers as msg_gen
import mongo_helpers as mongo
from datetime import datetime
import wit_helpers as wit
import pika
import sys


def check_reminder(message):
    trigger_local_time = message['local_trigger_time']
    local_current_time = msg_gen.update_local_time(message['zone_name'])

    current_local_strip = datetime.strptime(local_current_time, '%Y-%m-%d %I:%M:%S')
    trigger_local_strip = datetime.strptime(str(trigger_local_time), '%Y-%m-%d %I:%M:%S')

    bool_trigger = bool(current_local_strip >= trigger_local_strip)

    if (bool_trigger is True):
        print("It's time to remind user about: " + str(message['reminder_text']))
        trigger_reminder_alert( message)


def trigger_reminder_alert(message):
    result = "Don't forget! " + " '" + message['reminder_text'].capitalize() + "'!"

    msg_gen.store_reply_in_mongo(
                                    result,
                                    message,
                                    "⏱️ Reminder ⏱️")
    mongo.add_new_item_to_db(message, 'reminder_trigger', 'off')

def trigger_recurring(resp, sender_info):
    message_copy = mongo.message_records.find_one({"sms_id": sender_info['sms_id']})
    time.sleep(1)
    print("Inside trigger_recurring")
    freq_dict = {
        "minutely": "seconds=60",
        "hourly": "minutes=60",
        "daily": "day=1",
        "weekly": "week=1",
    }
    freq = resp['entities']['recur_frequency'][0]['value']
    new_freq = freq_dict[freq]
    body = sender_info['body']
    replacements = [
                        ('daily', ''),
                        ('hourly', ''),
                        ('weekly', ''),
                        ('hourly', ''),
                        ('hourly', ''),
                        ('hourly', ''),
                        ('at the top of the hour', ''),
                        ('every 60 minutes', ''),
                        ('every hour', ''),
                        ('on the hour', ''),
                        ('each minute', ''),
                        ('every minute', ''),
                        ('on the minute', ''),
                        ('each day', ''),
                        ('every day', ''),
                        ('each and every day', ''),
                        ('once a day', ''),
                        ('once an hour', ''),
                        ('once a week', ''),
                        ('one time every day', ''),
                        ('once a minute', ''),
                        ('every single hour', ''),
                    ]
    for old, new in replacements:
        body = re.sub(old, new, body)
    mongo.add_timed_message_to_db(sender_info['from'], sender_info['sms_id'], body, new_freq, recurring="YES")
    mongo.add_new_item_to_db(message_copy, 'body', body)
    mongo.add_new_item_to_db(message_copy, 'timer_marker', "in place")
    mongo.add_new_item_to_db(message_copy, 'timer-frequency', new_freq)
    mongo.add_new_item_to_db(message_copy, 'status', 'timer-preset')


def reminder_request(sender_info, input, date):
    hour_to_trigger_pst = str(date[11:13])
    date = re.sub("T", ".", date)
    date = date.split(".")
    print("Date: " + str(date))
    time_pre_change = date[1].split(":")
    print(time_pre_change[1])

    offset_time_zone = sender_info['offset_time_zone']
    hour_in_home_zone = int(hour_to_trigger_pst) + offset_time_zone

    if (hour_in_home_zone > 10):
            hour_in_home_zone = str(hour_in_home_zone)
    else:
            hour_in_home_zone = "0" + str(hour_in_home_zone)

    time_post_change = hour_in_home_zone + ":" + str(time_pre_change[1]) + ":" + str(time_pre_change[2])
    print(time_post_change)

    new_date = str(date[0]) + " " + time_post_change
    parsed_date = parser.parse(new_date)
    print(parsed_date)
    # parsed_date = parser.parse(str(date[0]) + " " + str(date[1]))
    reminder = {
                'local_trigger_time': parsed_date,
                'reminder_trigger': 'activated',
                'reminder_text': input 
                }
    for key, value in reminder.items():
        sender_info = mongo.add_new_item_to_db(sender_info, key, value)

    day_full = str(parsed_date).split(" ")[0]
    day_without_year = day_full.split("-")[1:]
    day_str_without_year = "/".join(day_without_year)
    time = str(parsed_date).split(" ")[1]
    time_split = time.split(":")
    hours = time_split[0]
    minutes = time_split[1]
    time_of_day_str = "AM"
    
    if (int(hours) > 12):
      hours = int(hours) - 12
      time_of_day_str = "PM"
  
    formatted_time = str(hours) + ":" + str(minutes) + " " + time_of_day_str

    result = "I've set a reminder for " + day_str_without_year + " @ " + formatted_time + ": ⏱️ " + str(input) + " ⏱️"
    return result

def trigger_reminder(resp, sender_info):
    print("Reminder Triggered")
    time_zone = sender_info['offset_time_zone']
    print("Time_zone offset is: " + str(time_zone))
    print("Sender Info: " + str(sender_info))
    # print(resp)
    try:
        reminder = resp['entities']['reminder'][0]['value']
    except BaseException:
        try:
            reminder = resp['entities']['phrase_to_translate'][0]['value']
        except BaseException:
            reminder = resp['_text']
    print("\nReminder: " + str(reminder))
    try:
        date = resp['entities']['datetime'][0]['value']
        print("\n1st Try date: " + str(date))
    except BaseException:
        try:
            date = resp['entities']['datetime'][0]['values'][0]['to']['value']
            print("\n2nd Try date: " + str(date))
        except BaseException:
            try:
                date = resp['entities']['wdatetime'][0]['values'][0]['to']['value']
                print("\n3rd Try date: " + str(date))
            except BaseException:
                try:
                    date = resp['entities']['wdatetime'][0]['value']
                    print("\n4rd Try date: " + str(date))
                except BaseException:
                    today = datetime.date.today()
                    date = today + datetime.timedelta(days = 1) 
                    date = str(date) + "T00:00:00.000-07:00"
                    print("\nExcept date: " + str(date))
    print("Date: " + str(date))
    msg_gen.store_reply_in_mongo(
                                       reminder_request(sender_info, str(reminder), str(date)),
                                       sender_info,
                                       "⏱️ Reminder Setup ⏱️")