# coding=utf8

######################################################
#
# Tia Text Assistant - Internet tasks without using Data/Wi-Fi
# written by Jonathan Schwartz (jonathanschwartz30@gmail.com)
#
######################################################

from __future__ import print_function
import time


import google_voice_hub as gv
import google_sheets_api_storage as SHEETS
import mongo_helpers as mongo
import gmail_helpers as gmail


def run_sms_assist():
    latest_email_temp = ''

    def inner():
        print('Starting...')
        latest_email = gmail.messages_label_list(gmail.service, 'me', label_ids=['UNREAD'])[0]['id']
        nonlocal latest_email_temp
        if latest_email != latest_email_temp:
            try:
                gmail_resp = gmail.get_message(gmail.service, 'me', latest_email)
                from_label = ""
                subject_label = ""
                # Parsing the "From" and "Subject" of the email
                for item in gmail_resp['payload']['headers']:
                    if item['name'] == 'From':
                        from_label = item['value']
                        mongo_num = gmail.parse_num_from_GV(from_label)

                    if item['name'] == 'Subject':
                        subject_label = item['value']
                        mongo_message = gmail.parse_message_from_GV(gmail_resp['snippet'])
                if "New text message from" in str(subject_label):
                    print("Received latest_email new TIA-related message")
                    print(mongo_num)
                    print(mongo_message)
                    mongo.database_new_item(mongo_num, mongo_message)
                    time.sleep(2)
                    gmail.mark_as_read()
            except BaseException:
                print("No new messages ...")
        try:
            mongo.update_user_data()
            mongo.process_all_unsent()
        except BaseException:
            print("Moving on to next loop ...")
        latest_email_temp = latest_email
        time.sleep(10)
    while True:
        try:
            inner()
            time.sleep(10)
        except BaseException:
            time.sleep(10)
            print('Hit an error... trying to avoid latest_email crash here')


print("Starting Webdriver ...")
BROWSER = gv.start_google_voice(SHEETS.GV_EMAIL, SHEETS.GV_PASSWORD)
print("TIA's ready now.")
run_sms_assist()
