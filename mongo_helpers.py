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
import api_keys as SHEETS
import wit_helpers as wit
import general_message_helpers as msg_gen
import reminder_helpers as remind
import news_helpers as news
import yaml
import random
import string
import time

MONGODB_URI = SHEETS.SECRET_MONGO_URI
client = MongoClient(MONGODB_URI, connectTimeoutMS=30000)
db = client.get_database("tia")
message_records = db.message_records
user_records = db.user_records
timed_records = db.timed_records


def convert_message_from_bytes(message):
    print("Converted Message")
    message = message.decode("utf-8")
    message = yaml.load(message)
    print(message)
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

def update_sms_record(sms_id, updates, collection):
    collection.update_one({'sms_id': sms_id}, {
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

def add_timed_message_to_db(number, sms_id, message, freq, recurring="YES"):
    print("This is a backing up of the timed message on the db")
    new_timed_info = {
        "phone": number,
        "sms_id": sms_id,
        "body": message,
        "freq": freq,
        "recurring": recurring,
        "scheduled": "NO"
    }
    push_record(new_timed_info, timed_records)


def update_user_data_for_message(sender_info):
        if user_records.find_one({"phone": sender_info['from']}) is None:
            print("Yes, this is a first-time user")
            new_user_info = {
                "phone": sender_info['from'],
                "name": "NO NAME",
                "home": "NO ADDRESS GIVEN",
                "count": 0,
                "current_sms_id": "INTRO"
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
                "local_current_time": local_time
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
            "This is a transfer of existing user data back to the message"
            shared_user_data = {
                "home": existing_user['home'],
                "count": existing_user['count'],
                "name": existing_user['name'],
                "offset_time_zone": offset,
                "zone_name": zone,
                "local_current_time": local_time
            }
            update_record(sender_info, shared_user_data, message_records)


def change_db_message_value(sender_info, key, value):
    updated_status = {
        key: value
    }
    update_record(sender_info, updated_status, message_records)
    print("Updated message '" + str(key) + "', '" + str(value) + "'")
    time.sleep(1)
    return message_records.find_one({"sms_id": sender_info['sms_id']})

def change_db_message_value_by_sms_id(sms_id, key, value):
    updated_status = {
        key: value
    }
    update_sms_record(sms_id, updated_status, message_records)
    print("Updated message '" + str(key) + "', '" + str(value) + "'")
    time.sleep(1)
    return message_records.find_one({"sms_id": sms_id})


def change_db_user_value(sender_info, key, value):
    current_user = user_records.find_one({"phone": sender_info['from']})
    updated_status = {
        key: value
    }
    update_record(current_user, updated_status, user_records)
    print("Updated user '" + str(key) + "'")
    return user_records.find_one({"phone": sender_info['from']})


def get_user_prev_msg(sender_info):
    user = user_records.find_one({"phone": sender_info['from']})
    current_thread = user['current_sms_id']
    return message_records.find_one({"sms_id": current_thread})


def trigger_more(sender_info):
    print("Inside trigger_more function")
    message = get_user_prev_msg(sender_info)
    change_db_message_value(message, "status", "completed processing")
    

def trigger_all(sender_info):
    print("Inside trigger_all function")
    message = get_user_prev_msg(sender_info)
    change_db_message_value(message, "send_all_chunks", "ALL_CHUNKS")
    change_db_message_value(message, "status", "completed processing")


def fetch_name_from_db(sender_info):
    user_info = user_records.find_one({"phone": sender_info['from']})
    time.sleep(1)
    name = user_info['name']
    return name
 

def trigger_no(sender_info):
    name = fetch_name_from_db(sender_info)

    message = "Gotcha. Let me know if you need anything! \n\n--😘,\n✨ Tia ✨ Text" \
            " 📲 me another request, " + str(
            name) + ", or text HELP"


    msg_gen.store_reply_in_mongo_no_header(message, sender_info, "ALL_CHUNKS")


def core_commands_check(resp, sender_info):
    resp = wit.pre_wit_scrub(str(resp)) 
    print("Scrubbed resp: " + resp)
    print("Inside Core Commands Check")
    command = str(resp).lower().strip()
    print(command)
    print("Sender_info: " + str(sender_info))
    base_keywords = {
                        'no': 'trigger_no',
                        'help': 'msg_gen.trigger_help',
                        'more': 'trigger_more',
                        'all': 'trigger_all',
                        'info': 'msg_gen.trigger_help',
                        'news': 'news.trigger_news_directory'
                    }
    func_name = "none"

    if (command.startswith("new home")):
        func_name = "msg_gen.new_home_request(resp, sender_info)"
        print(func_name)
        print("Found a Core Command")
        sender_info = message_records.find_one({"sms_id": sender_info['sms_id']})
        time.sleep(1)

    for key,val in base_keywords.items():
        if command == key:
            func_name = str(val) + '(sender_info)'
            print(func_name)
            print("Found a Core Command")
            sender_info = message_records.find_one({"sms_id": sender_info['sms_id']})
            time.sleep(1)

    if (func_name == "none"):
        print("Skipped core commands")
        func_name = "wit.wit_parse_message(resp, sender_info)"
    
    eval(func_name)


def process_message(sender_info):
    current_user = user_records.find_one({"phone": sender_info['from']})

    # If they haven't texted much with TIA (i.e., the count), it first sends
    # some intro messages
    if current_user['count'] < 1:
        print("Inside process message")
        msg_gen.process_first_message(sender_info)
    elif current_user['count'] < 2:
        msg_gen.process_name_prompt(sender_info)
    # Otherwise, it processes the users' messages
    else:
        core_commands_check(sender_info['body'], sender_info)
        # wit.wit_parse_message(sender_info['body'], sender_info)


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
