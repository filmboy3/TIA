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

HOME_ZONE_TO_UTC = {
        -4: 11,
        -3: 10,
        -2: 9,
        -1: 8,
        0: 7,
        1: 6,
        2: 5,
        3: 4,
        4: 3,
        5: 2,
        6: 1,
        7: 0,
        8: -1,
        9: -2,
        10: -3,
        11: -4,
        12: -5,
        13: -6,
        14: -7,
        15: -8,
        16: -9,
        17: -10,
        18: -11,
        19: -12
    }

def extract_time(date_arr):
    new_date = str(date_arr)[:-6]
    # print(new_date)
    time_split = str(date_arr).split(" ")[1]
    time_split = time_split.split(":")
    hours = int(time_split[0])
    minutes = int(time_split[1])

    return (hours, minutes, new_date)


def convert_local_to_readable(local):
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
    return full_local_time


def time_range_average(first, second):
    ts1 = pd.Timestamp(parser.parse(first))
    ts2 = pd.Timestamp(parser.parse(second))
    ts_new = ts1+(ts2-ts1)/2
    # print("Averaging time range")
    # print(ts_new)
    return ts_new


def convert_date_from_wit(resp):
    pst_counter = 0
    try:
        date = resp['entities']['datetime'][0]['value']
        # print("\n1st date attempt: " + str(date))
        if "at" not in resp['_text']:
            pst_counter = 1
    except BaseException:
        try:
            date = resp['entities']['datetime'][0]['values'][0]['to']['value']
            # print("\n2nd date attempt: " + str(date))
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
                    # print("\n4th date attempt: " + str(date))
                except BaseException:
                    return 0
    return (date, pst_counter)


def parse_date_for_timed_messages(date_arr, sender_info):
    if (date_arr[1] == 1):
        local_date = parser.parse(date_arr[0]) + timedelta(hours=(sender_info['offset_time_zone']))
    else:
        local_date = parser.parse(date_arr[0])

    # print("LOCAL TIME: " + str(local_date))
    local_readable_time = convert_local_to_readable(local_date)

    utc_offset = HOME_ZONE_TO_UTC[sender_info['offset_time_zone']]
    utc_date = local_date + timedelta(hours = utc_offset)
    # print("UTC TIME: " + str(utc_date))

    utc_new_time = extract_time(utc_date)
    # print(utc_new_time)
    return (utc_new_time, local_readable_time)


def reminder_date_check (resp, sender_info):
    date_arr = convert_date_from_wit(resp)
    result = parse_date_for_timed_messages(date_arr, sender_info)
    # print(result)
    return result


def timing_date_check(resp, sender_info):
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
        "body": body['body'],
        "result": body['result'],
        "launch_time": "NOW",
        "send_all_chunks": "ALL_CHUNKS",
        "current_chunk": 0,
        "chunk_len": 1,
        "status": "completed processing"
    }
    return mongo.database_new_populated_item(record)


def trigger_recurring(resp, sender_info):
    sender_info = mongo.message_records.find_one({"sms_id": sender_info['sms_id']})
    time.sleep(1)
    # print("Inside trigger_recurring")
    freq = resp['entities']['recur_frequency'][0]['value']
    date_arr = timing_date_check(resp, sender_info)

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
    except BaseException:
        try:
            pre_topic = resp['entities']['intent'][0]['value']
            topic = pre_topic[:-4]
            topic = " " + pre_topic[:-4] + " "
        except BaseException:
            topic = ""
        topic = topic.title()
        topic = re.sub('Nyt', 'NY Times', topic)

    str_scheduler = "scheduler.add_job(mongo.change_db_message_value_by_sms_id, " + freq_dict[freq] + "jitter=15, id=" + sender_info['sms_id'] + "'," + " kwargs={'sms_id': '" + sender_info['sms_id'] + "', 'key': 'status', 'value': 'unprocessed'})"
    reminder_text = resp['entities']["recur_frequency"][0]['value']
    print("\n\nOriginal Command: " + str(resp['_text']))
    message_result = "Your " + reminder_text + topic + "messages ⌚ are set for: " + date_arr[1] + ". To cancel recurring messages at any time, text CANCEL\n\n--😘,\n✨ Tia ✨"
    print(message_result)
    
    new_timed_records = {
        "phone": sender_info['from'],
        "sms_id": sender_info['sms_id'],
        "body": message_result,
        "orig_request": resp['_text'], 
        "topic": topic,
        "freq": freq,
        "recurring": 'recurring',
        "scheduled": "NO",
        "str_scheduler": str_scheduler
    }
    mongo.push_record(new_timed_records, mongo.timed_records)
    mongo.update_record(sender_info, new_timed_records, mongo.timed_records)
    
    return str_scheduler


def trigger_reminder(resp, sender_info):
    # message_copy = "mongo.message_records.find_on"e({"sms_id": sender_info['sms_id']})
    time.sleep(1)
    # print("Inside trigger_reminder")
    date_info_arr = reminder_date_check(resp, sender_info)
    str_scheduler = "scheduler.add_job(mongo.change_db_message_value_by_sms_id, 'date', run_date='" + date_info_arr[0][2] + "', id=" + sender_info['sms_id'] + "'," + " kwargs={'sms_id': '" + sender_info['sms_id'] + "', 'key': 'status', 'value': 'unprocessed'})"
    print(str_scheduler)
    
    try:
        reminder_text = resp['entities']['reminder'][0]['value']
    except BaseException:
        try:
            reminder_text = ""
            for i in range(0, len(resp['entities']['phrase_to_translate'])):
              reminder_text = reminder_text + resp['entities']['phrase_to_translate'][i]['value'] + " " 
            reminder_text = reminder_text.rstrip()
        except BaseException:
            reminder_text = resp['_text']
        reminder_text = reminder_text.title()
        reminder_text = re.sub('Pm', 'PM', reminder_text)
        reminder_text = re.sub('Am', 'AM', reminder_text)

    print("\n\nOriginal Command: " + str(resp['_text']))
    message_result = "Your '" + reminder_text + "' reminder ⌚ is set for: " + date_info_arr[1] + ". To cancel reminders at any time, 📲 text CANCEL\n\n--😘,\n✨ Tia ✨"
    print(message_result)
    return str_scheduler
