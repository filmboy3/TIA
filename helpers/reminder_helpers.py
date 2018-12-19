import datetime
from dateutil import parser
import re
from datetime import datetime, timedelta
import time
import pandas as pd
import general_message_helpers as msg_gen
import mongo_helpers as mongo
import wit_helpers as wit
import pika
import sys
import random
import string


def extract_time(date_arr):
    new_date = str(date_arr)[:-6]
    # print(new_date)
    time_split = str(date_arr).split(" ")[1]
    time_split = time_split.split(":")
    hours = int(time_split[0])
    minutes = int(time_split[1])

    return (hours, minutes, new_date)


def convert_local_to_readable(local):
    print("Inside convert_local_to_readable")
    new_local = extract_time(local)
    hours = new_local[0]
    mins = new_local[1]
    
    if hours > 12:
      hour_format = str(hours - 12)
      time_of_day = "PM"
    else:
      hour_format = str(hours)
      time_of_day = "AM"
    
    if mins < 10:
      mins = "0" + str(mins)
      
    full_local_time = hour_format + ":" + str(mins) + " " + time_of_day
    print("Full_local_time: " + str(full_local_time))
    return full_local_time


def time_range_average(first, second):
    ts1 = pd.Timestamp(parser.parse(first))
    ts2 = pd.Timestamp(parser.parse(second))
    ts_new = ts1+(ts2-ts1)/2
    # print("Averaging time range")
    # print(ts_new)
    return ts_new


def convert_date_from_wit(resp):
    print("Inside convert_date_from_wit")
    pst_counter = 0
    try:
        date = resp['entities']['datetime'][0]['value']
        print("\n1st date attempt: " + str(date))
        if "at" not in resp['_text']:
            pst_counter = 1
    except BaseException:
        try:
            date = resp['entities']['datetime'][0]['values'][0]['to']['value']
            print("\n2nd date attempt: " + str(date))
            if "at" not in resp['_text']:
                pst_counter = 1
            try:
                date2 = resp['entities']['wdatetime'][0]['values'][0]['from']['value']
                date = str(time_range_average(date, date2))
            except BaseException:
                pass
        except BaseException:
            try:
                date = resp['entities']['wdatetime'][0]['values'][0]['to']['value']
                # print("\n3rd date attempt: " + str(date))
                try:
                    date2 = resp['entities']['wdatetime'][0]['values'][0]['from']['value']
                    date = str(time_range_average(date, date2))
                except BaseException:
                    pass
            except BaseException:
                try:
                    date = resp['entities']['wdatetime'][0]['value']
                    if "in" in resp['_text']:
                        pst_counter = 1
                    print("\n4th date attempt: " + str(date))
                except BaseException:
                    return 0
    return (date, pst_counter)


def parse_date_for_timed_messages(date_arr, sender_info):
    current_user = mongo.user_records.find_one({"phone": sender_info['from']})

    if (date_arr[1] == 1):
        local_date = parser.parse(date_arr[0]) + timedelta(hours=(sender_info['offset_time_zone']))
    else:
        local_date = parser.parse(date_arr[0])

    print("LOCAL TIME: " + str(local_date))
    time.sleep(2)
    local_readable_time = convert_local_to_readable(local_date)
    print("LOCAL READABLE: " + str(local_readable_time))
    HOME_ZONE_TO_UTC = {
        '-4': '11',
        '-3': '10',
        '-2': '9',
        '-1': '8',
        '0': '7',
        '1': '6',
        '2': '5',
        '3': '4',
        '4': '3',
        '5': '2',
        '6': '1',
        '7': '0',
        '8': '-1',
        '9': '-2',
        '10': '-3',
        '11': '-4',
        '12': '-5',
        '13': '-6',
        '14': '-7',
        '15': '-8',
        '16': '-9',
        '17': '-10',
        '18': '-11',
        '19': '-12'
    }
    utc_offset = HOME_ZONE_TO_UTC[str(current_user['offset_time_zone'])]
    utc_date = local_date + timedelta(hours = int(utc_offset))
    print("UTC TIME: " + str(utc_date))

    utc_new_time = extract_time(utc_date)
    print(utc_new_time)
    return (utc_new_time, local_readable_time)


def reminder_date_check(resp, sender_info):
    date_arr = convert_date_from_wit(resp)
    result = parse_date_for_timed_messages(date_arr, sender_info)
    print(result)
    return result


def timing_date_check(resp, sender_info):
    print("Inside timing_date_check")
    result = [0, "."]
    if (convert_date_from_wit(resp) != 0):
        date_arr = convert_date_from_wit(resp)
        result = parse_date_for_timed_messages(date_arr, sender_info)
        hour = result[0][0]
        minute = result[0][1]
        partial_message = "hour=" + str(hour) + ", minute=" + str(minute) + ", "
    else:
        partial_message = "hour=13, minute=30, "
    return (partial_message, result[1])


def send_timing_receipt(body):
    record = {
        "from": body['from'],
        "body": "",
        "result": [body['result']],
        "launch_time": "NOW",
        "send_all_chunks": "ALL_CHUNKS",
        "current_chunk": 0,
        "chunk_len": 1,
        "status": "completed processing"
    }
    return mongo.database_new_populated_item(record)


def trigger_recurring(resp, sender_info):
    sender_info = mongo.message_records.find_one({"sms_id": sender_info['sms_id']})
    time.sleep(2)
    current_user = mongo.user_records.find_one({"phone": sender_info['from']})
    time.sleep(2)
    print("Inside trigger_recurring")
    print(current_user)
    freq = resp['entities']['recur_frequency'][0]['value']
    date_arr = timing_date_check(resp, sender_info)
    print("Got a date_arr: " + str(date_arr))

    freq_dict = {
        'daily': "'cron', " + date_arr[0],
        'weekly': "'cron', day_of_week=0, " + date_arr[0],
        'weekend': "'cron', day_of_week='sat-sun', " + date_arr[0],
        'weekday': "'cron', day_of_week='mon-fri', " + date_arr[0],
        'hourly': "'cron', hour='*', ",
        'minute-by-minute': "'interval', seconds=60, "
    }

    try:
        topic = " " + resp['entities']['wit_news_source'][0]['value'].upper() + " "
        topic_full = "News " + topic
    except BaseException:
        try:
            pre_topic = str(resp['entities']['intent'][0]['value'])
            print(pre_topic)
            topic = pre_topic[:-4]
            topic = " " + pre_topic[:-4] + " "
            print(topic)
            topic_full = topic
        except BaseException:
            topic = ""
        topic = topic.title()
        topic = re.sub('Nyt', 'NY Times', topic)

    new_sms_id = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(0, 16)])
    str_scheduler = "scheduler.add_job(mongo.change_db_message_value_by_sms_id, " + freq_dict[freq] + "jitter=15, id='" + new_sms_id + "'," + " kwargs={'sms_id': '" + new_sms_id + "', 'key': 'status', 'value': 'unprocessed'})"
    reminder_text = resp['entities']["recur_frequency"][0]['value']
    print("\n\nOriginal Command: " + str(resp['_text']))
    time_text = str(date_arr[1])
    if time_text != ".":
        time_text = " for: " + time_text + "."
    message_result = "👋 Hey, " + current_user['name'] + "! Your " + reminder_text + " ⏰ " + topic + "messages are all set" + time_text + " To 🛑 recurring messages at any ⌚, text 📲 CANCEL\n\n--😘,\n✨ Tia ✨"
    print(message_result)
    print("SMS_id: " + str(new_sms_id))
    print("body: " + str(topic_full))
    print("Current User: " + str(current_user))
    print("Current Sender Info: " + str(sender_info))
    print("from: " + str(sender_info['from']))
    print("home: " + str(current_user['home']))
    print("offset_time_zone: " + str(current_user['offset_time_zone']))
    print("created_at: " + str(pd.Timestamp.now()))

    fresh_message_record = {
        "sms_id": new_sms_id,
        "body": topic_full,
        "name": current_user['name'],
        "from": sender_info['from'],
        "status": "waiting for trigger",
        "result": "tba",
        "home": current_user['home'],
        "offset_time_zone": current_user['offset_time_zone'],
        "zone_name": current_user['zone_name'],
        "created_at": str(pd.Timestamp.now())
    }

    mongo.push_record(fresh_message_record, mongo.message_records)
    time.sleep(1)
    new_timed_records = {
        "from": sender_info['from'],
        "sms_id": new_sms_id,
        "body": message_result,
        "result": message_result,
        "orig_request": resp['_text'], 
        "topic": topic_full,
        "freq": freq,
        "deactivate": "NO",
        "status": "timer-preset",
        "recurring": 'recurring',
        "scheduled": "NO",
        "str_scheduler": str_scheduler,
        "created_at": pd.Timestamp.now()
    }
    mongo.push_record(new_timed_records, mongo.timed_records)

    print("Did we reach after the pushed records?")
    
    return str_scheduler

def send_cancel_receipt(sender_info, result):
    record = {
        "from": sender_info['from'],
        "body": sender_info['body'],
        "result": [result],
        "launch_time": "NOW",
        "send_all_chunks": "ALL_CHUNKS",
        "current_chunk": 0,
        "chunk_len": 1,
        "status": "completed processing"
    }
    return mongo.database_new_populated_item(record)


def trigger_cancel(sender_info):
    message_array = []
    name = mongo.fetch_name_from_db(sender_info)
    for message in mongo.timed_records.find({"from": sender_info['from']}):
        message_array.append(message)
    
    most_recent = message_array[0]
    for i in range(0, len(message_array)):
        if most_recent['created_at'] < message_array[i]['created_at']:
            most_recent = message_array[i]
    result = "👌 Sure thing, " + name + '!' + " I've 🛑 your most recently scheduled ⌚ message, '" + str(most_recent['orig_request']).capitalize() + "'. To 🚫 all notifications, text 📲 CANCEL ALL. \n\n--😘,\n✨ Tia ✨"
    # print(result)
    db_changes = {
            "deactivate": "YES",
            "scheduled": "NO"
        }
    mongo.update_record(most_recent, db_changes, mongo.timed_records)
    send_cancel_receipt(sender_info, result)


def trigger_cancel_all(sender_info):
    name = mongo.fetch_name_from_db(sender_info)
    for message in mongo.timed_records.find({"from": sender_info['from']}):
        db_changes = {
            "deactivate": "YES",
            "scheduled": "NO"
        }
        mongo.update_record(message, db_changes, mongo.timed_records)
    result ="👌 Sure thing, " + name + "! 🛑 I've cancelled all of your scheduled ⌚ notifications! \n\n--😘,\n✨ Tia ✨"
    send_cancel_receipt(sender_info, result)
    # print(result)    


def trigger_reminder(resp, sender_info):
    sender_info = mongo.message_records.find_one({"sms_id": sender_info['sms_id']})
    time.sleep(2)
    current_user = mongo.user_records.find_one({"phone": sender_info['from']})
    time.sleep(2)
    print("Inside trigger_reminder")
    date_info_arr = reminder_date_check(resp, sender_info)
    new_sms_id = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(0, 16)])
    str_scheduler = "scheduler.add_job(mongo.change_db_message_value_by_sms_id, 'date', run_date='" + date_info_arr[0][2] + "', id='" + new_sms_id + "'," + " kwargs={'sms_id': '" + new_sms_id + "', 'key': 'status', 'value': 'completed processing'})"
    print(str_scheduler)
    
    try:
        reminder_text = resp['entities']['reminder'][0]['value']
        print("Found a reminder_text")
    except BaseException:
        print("Did not connect with a reminder_text via reminder value")
        try:
            reminder_text = ""
            for i in range(0, len(resp['entities']['phrase_to_translate'])):
              reminder_text = reminder_text + resp['entities']['phrase_to_translate'][i]['value'] + " " 
            reminder_text = reminder_text.rstrip()
        except BaseException:
            reminder_text = resp['_text']
            print("last resort reminder text: " + str(reminder_text))
        reminder_text = reminder_text.title()
        reminder_text = re.sub('Pm', 'PM', reminder_text)
        reminder_text = re.sub('Am', 'AM', reminder_text)
    print("Here is the ultimate reminder_text: " + str(reminder_text))

    print("\n\nOriginal Command: " + str(resp['_text']))
    # print(sender_info)
    message_prep = "Hey, " + current_user['name'] + "! Your '" + reminder_text + "' reminder ⌚ is set for: " + date_info_arr[1] + ". To 🚫 reminders at any ⌚, text 📲 CANCEL\n\n--😘,\n✨ Tia ✨"
    # print(message_prep)
    message_final = "📣 Hey, " + current_user['name'] + "! 📣 Here's your reminder: " + " '" + reminder_text.capitalize() + "'! ⌚\n\n--😘,\n✨ Tia ✨"
    # print(message_final)
    fresh_message_record = {
        "sms_id": new_sms_id,
        "body": message_prep,
        "name": current_user['name'],
        "from": sender_info['from'],
        "result": [message_final],
        "home": current_user['home'],
        "offset_time_zone": current_user['offset_time_zone'],
        "zone_name": current_user['zone_name'],
        "send_all_chunks": "ALL_CHUNKS",
        "current_chunk": 0,
        "single-timer": "YES",
        "chunk_len": 1,
        "launch_time": "NOW",
        "status": "waiting to be triggered",
        "created_at": pd.Timestamp.now()
    }

    mongo.push_record(fresh_message_record, mongo.message_records)
    time.sleep(1)
    new_timed_records = {
        "from": sender_info['from'],
        "sms_id": new_sms_id,
        "body": message_prep,
        "result": [message_prep],
        "deactivate": "NO",
        "eventual_message": message_final,
        "orig_request": resp['_text'], 
        "status": "timer-preset",
        "recurring": 'one-time',
        "scheduled": "NO",
        "str_scheduler": str_scheduler,
        "created_at": pd.Timestamp.now()
    }
    mongo.push_record(new_timed_records, mongo.timed_records)

    return str_scheduler
