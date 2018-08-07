# coding=utf8

######################################################
# MONGO DB SETUP AND HELPER FUNCTIONS
# Tia Text Assistant - Internet tasks without using Data/Wi-Fi
# written by Jonathan Schwartz (jonathanschwartz30@gmail.com)
#
######################################################

from __future__ import print_function
import re
import datetime
from pymongo import MongoClient
import google_sheets_api_storage as SHEETS
import wit_helpers as wit
import general_message_helpers as msg_gen
import reminder_helpers as remind
import yaml
import random
import string

MONGODB_URI = SHEETS.SECRET_MONGO_URI
client = MongoClient(MONGODB_URI, connectTimeoutMS=30000)
db = client.get_database("tia")
message_records = db.message_records
user_records = db.user_records


def convert_message_from_bytes(message):
    print("Converted Message")
    message = message.decode("utf-8")
    message = yaml.load(message)
    return message

def get_record(user_id, collection):
    records = collection.find_one({"user_id": user_id})
    return records


def push_record(record, collection):
    collection.insert_one(record)


def update_record(record, updates, collection):
    collection.update_one({'_id': record['_id']}, {
        '$set': updates
    }, upsert=False)


def process_reminders():
    for message in message_records.find({"reminder_trigger": "activated"}):
        remind.check_reminder(message)


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


def update_user_data_for_message(sender_info):
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
            # print("\nUpdating message with existing records")
            existing_user = user_records.find_one(
                {"phone": sender_info['from']})
            
            # "This is an increment of the userCount..."
            incremented_user_count = {
                "count": (int(existing_user['count']) + 1)
            }
            update_record(existing_user, incremented_user_count, user_records)
            sender_info = message_records.find_one({"sms_id": sender_info['sms_id']})
            # print("New Sender Info: " + str(sender_info))
            try:
                msg_gen.add_time_zone_data(existing_user['home'], sender_info)
            except:
                print("No address")
            try:
                offset = existing_user['offset_time_zone']
            except:
                offset = "unknown offset"
            try:
                zone = existing_user['zone_name']
            except:
                zone = "unknown zone"
            try:
                local_time = msg_gen.update_local_time(existing_user['zone_name'])
            except:
                local_time = "unknown local time"
            # "This is a transfer of existing user data back to the message"
            shared_user_data = {
                "home": existing_user['home'],
                "count": existing_user['count'],
                "name": existing_user['name'],
                "offset_time_zone": offset,
                "zone_name": zone,
                "current_local_time": local_time
            }
            update_record(sender_info, shared_user_data, message_records)
            return shared_user_data


def update_user_data():
    for sender_info in message_records.find({"status": "unprocessed"}):
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
            print("\nUpdating existing record ...")
            existing_user = user_records.find_one(
                {"phone": sender_info['from']})

            # "This is an increment of the userCount..."
            incremented_user_count = {
                "count": (int(existing_user['count']) + 1)
            }
            update_record(existing_user, incremented_user_count, user_records)

            try:
                offset = existing_user['offset_time_zone']
            except:
                offset = "unknown offset"
            try:
                zone = existing_user['zone_name']
            except:
                zone = "unknown zone"
            try:
                local_time = msg_gen.update_local_time(existing_user['zone_name'])
            except:
                local_time = "unknown local time"
            # "This is a transfer of existing user data back to the message"
            shared_user_data = {
                "home": existing_user['home'],
                "count": existing_user['count'],
                "name": existing_user['name'],
                "offset_time_zone": offset,
                "zone_name": zone,
                "current_local_time": local_time
            }
            update_record(sender_info, shared_user_data, message_records)


def change_db_value(sender_info, key, value):
    updated_status = {
        key: value
    }
    update_record(sender_info, updated_status, message_records)
    print("Updated " + str(key) + " to " + str(value))
    return message_records.find_one({"sms_id": sender_info['sms_id']})


def process_message(sender_info):
    current_user = user_records.find_one({"phone": sender_info['from']})
    # If they haven't texted much with TIA (i.e., the count), she first sends
    # some intro messages
    if current_user['count'] < 1:
        print("Inside process message")
        msg_gen.process_first_message(sender_info)
    elif current_user['count'] < 2:
        msg_gen.process_intro_messages(sender_info)
    # Otherwise, she processes the users' messages
    else:
        wit.wit_parse_message(sender_info['body'], sender_info)


def scrub_html_from_message(message):
    # print("Attempting to Scrub message here")
    scrub_dict = {
        "&nbsp;": " ",
        "&amp;": "&",
        "&quot;": '"',
        "&ndash;": "--",
        "&#39;": "'",
    }
    for key, value in scrub_dict.items():
        message = re.sub(key, value, message)
    # print("New Message: " + str(message))
    return str(message)


def database_new_item(phone, message):
    # print("Yes, This is a new item ...")
    # print(message)
    record = {
        "sms_id": ''.join([random.choice(string.ascii_letters + string.digits) for n in range(0, 16)]),
        "body": scrub_html_from_message(message),
        "from": phone,
        "status": "unprocessed",
        "result": "tba"
    }
    # print(record)
    push_record(record, message_records)
    return record
