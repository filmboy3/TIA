import datetime
from dateutil import parser
import re
from datetime import datetime, timedelta
import time
import pandas as pd

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
  print(new_date)
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
  print("Averaging time range")
  print(ts_new)
  return ts_new

def convert_date_from_wit(resp):
    pst_counter = 0
    try:
        date = resp['entities']['datetime'][0]['value']
        print("\n1st date attempt: " + str(date))
        pst_counter = 1
    except BaseException:
        try:
            date = resp['entities']['datetime'][0]['values'][0]['to']['value']
            print("\n2nd date attempt: " + str(date))
            pst_counter = 1
            try:
                date2 = resp['entities']['wdatetime'][0]['values'][0]['from']['value']
                date = str(time_range_average(date, date2))
            except BaseException:
                pass
        except BaseException:
            try:
                date = resp['entities']['wdatetime'][0]['values'][0]['to']['value']
                print("\n3rd date attempt: " + str(date))
                try:
                    date2 = resp['entities']['wdatetime'][0]['values'][0]['from']['value']
                    date = str(time_range_average(date, date2))
                except BaseException:
                    pass
            except BaseException:
                try:
                    date = resp['entities']['wdatetime'][0]['value']
                    print("\n4th date attempt: " + str(date))
                except BaseException:
                    return 0
    return (date, pst_counter)


def parse_date_for_timed_messages(date_arr, sender_info):
    if (date_arr[1] == 1):
        local_date = parser.parse(date_arr[0]) + timedelta(hours=(sender_info['offset_time_zone']))
    else:
        local_date = parser.parse(date_arr[0])

    print("LOCAL TIME: " + str(local_date))
    local_readable_time = convert_local_to_readable(local_date)

    utc_offset = HOME_ZONE_TO_UTC[sender_info['offset_time_zone']]
    utc_date = local_date + timedelta(hours = utc_offset)
    print("UTC TIME: " + str(utc_date))

    utc_new_time = extract_time(utc_date)
    print(utc_new_time)
    return (utc_new_time, local_readable_time)

def reminder_date_check (resp, sender_info):
  date_arr = convert_date_from_wit(resp)
  result = parse_date_for_timed_messages(date_arr, sender_info)
  print(result)
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

trash_resp = {
  "_text": "Remind me to take out the trash tomorrow afternoon",
  "entities": {
    "wit_reminder_terms": [
      {
        "confidence": 0.97970484553614,
        "value": "reminder",
        "type": "value"
      }
    ],
    "reminder": [
      {
        "suggested": "true",
        "confidence": 0.9380825,
        "value": "take out the trash",
        "type": "value"
      }
    ],
    "wdatetime": [
      {
        "confidence": 0.99058118095999,
        "values": [
          {
            "to": {
              "value": "2018-08-13T19:00:00.000-07:00",
              "grain": "hour"
            },
            "from": {
              "value": "2018-08-13T12:00:00.000-07:00",
              "grain": "hour"
            },
            "type": "interval"
          }
        ],
        "to": {
          "value": "2018-08-13T19:00:00.000-07:00",
          "grain": "hour"
        },
        "from": {
          "value": "2018-08-13T12:00:00.000-07:00",
          "grain": "hour"
        },
        "type": "interval"
      }
    ],
    "intent": [
      {
        "confidence": 0.99999081248061,
        "value": "reminder_get"
      }
    ]
  },
  "msg_id": "0kkJV7B9yuMZjhbuk"
}

sender_name_info = {'recurring': 'YES', 'sms_id': '24YXY7QqS3bicAJL', 'body': 'I want mtv updates ', 'from': '+13473918206', 'status': 'unprocessed', 'result': '', 'count': 38, 'home': '50 spruce street cranford nj 07016', 'local_current_time': 'unknown local time', 'name': 'Timmy', 'offset_time_zone': 3, 'zone_name': 'America/New_York', 'timer-frequency': 'seconds=60', 'timer_marker': 'in place', 'chunk_len': 3, 'current_chunk': 1, 'launch_time': 'NOW', 'send_all_chunks': 'SINGLE_CHUNKS', 'current_sms_id': '24YXY7QqS3bicAJL'}

resp_name_info = {
  "_text": "I want cnn updates daily at 5 PM",
  "entities": {
    "wit_news_source": [
      {
        "confidence": 0.98373848004088,
        "value": "cnn",
        "type": "value"
      }
    ],
    "reminder": [
      {
        "suggested": "true",
        "confidence": 0.93559,
        "value": "updates",
        "type": "value"
      }
    ],
    "recur_frequency": [
      {
        "confidence": 0.92421368937412,
        "value": "daily",
        "type": "value"
      }
    ],
    "wdatetime": [
      {
        "confidence": 0.99240805404323,
        "values": [
          {
            "value": "2018-08-13T17:00:00.000-07:00",
            "grain": "hour",
            "type": "value"
          },
          {
            "value": "2018-08-14T17:00:00.000-07:00",
            "grain": "hour",
            "type": "value"
          },
          {
            "value": "2018-08-15T17:00:00.000-07:00",
            "grain": "hour",
            "type": "value"
          }
        ],
        "value": "2018-08-13T17:00:00.000-07:00",
        "grain": "hour",
        "type": "value"
      }
    ],
    "intent": [
      {
        "confidence": 0.99998353099171,
        "value": "news_get"
      }
    ]
  },
  "msg_id": "0g1bvmgB9kBW5dySS"
}
date = "2018-08-12T20:51:44.000-07:00"

def trigger_recurring(resp, sender_info):
    # message_copy = mongo.message_records.find_one({"sms_id": sender_info['sms_id']})
    time.sleep(1)
    print("Inside trigger_recurring")
    freq = resp['entities']['recur_frequency'][0]['value']
    date_arr = timing_date_check(resp, sender_info)

    freq_dict = {
        'daily': "'cron', " + date_arr[0],
        'weekly': "'cron', day_of_week=0, " + date_arr[0],
        'weekends': "'cron', day_of_week='sat-sun', " + date_arr[0],
        'weekdays': "'cron', day_of_week='mon-fri', " + date_arr[0],
        'hourly': "'cron', hour='*', ",
        'minutely': "'interval', seconds=60, "
    }
    str_scheduler = "scheduler.add_job(mongo.change_db_message_value_by_sms_id, " + freq_dict[freq] + "jitter=15, id=" + sender_info['sms_id'] + "'," + "kwargs={'sms_id': '" + sender_info['sms_id'] + "', 'key': 'status', 'value': 'unprocessed'})"
    reminder_text = resp['entities']["recur_frequency"][0]['value']
    message_result = "Your " + reminder_text + " messages are set for: " + date_arr[1]
    print(message_result)
    return str_scheduler

def trigger_reminder(resp, sender_info):
    # message_copy = "mongo.message_records.find_on"e({"sms_id": sender_info['sms_id']})
    time.sleep(1)
    print("Inside trigger_reminder")
    date_info_arr = reminder_date_check(resp, sender_info)
    str_scheduler = "scheduler.add_job(mongo.change_db_message_value_by_sms_id, 'date', run_date=" + date_info_arr[0][2] + ", id=" + sender_info['sms_id'] + "'," + "kwargs={'sms_id': '" + sender_info['sms_id'] + "', 'key': 'status', 'value': 'unprocessed'})"
    print(str_scheduler)
    reminder_text = resp['entities']['reminder'][0]['value']
    message_result = "Your '" + reminder_text + "' reminder is set for: " + date_info_arr[1]
    print(message_result)
    return str_scheduler

print(trigger_recurring(resp_name_info, sender_name_info))
print(trigger_reminder(trash_resp, sender_name_info))
