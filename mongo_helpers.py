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

MONGODB_URI = SHEETS.SECRET_MONGO_URI
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
                "name": existing_user['name'],
                "offset_time_zone": existing_user['offset_time_zone']
            }
            update_record(sender_info, shared_user_data, message_records)


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


def process_message(browser, sender_info):
    current_user = user_records.find_one({"phone": sender_info['from']})
    # If they haven't texted much with TIA (i.e., the count), she first sends
    # some intro messages
    if current_user['count'] < 1:
        print("Inside process message")
        msg_gen.process_first_message(browser, sender_info)
    elif current_user['count'] < 2:
        msg_gen.process_intro_messages(browser, sender_info)
    # Otherwise, she processes the users' messages
    else:
        wit.wit_parse_message(browser, sender_info['body'], sender_info)


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


def process_all_unsent(browser):
    for message in message_records.find({"status": "unsent"}):
        process_message(browser, message)


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
