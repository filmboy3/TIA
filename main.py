# coding=utf8

######################################################
#
# Tia Text Assistant - Internet tasks without using Data/Wi-Fi
# written by Jonathan Schwartz (jonathanschwartz30@gmail.com)
#
######################################################

from __future__ import print_function
import httplib2
import os
from apiclient.discovery import build
import time
import base64
import re
import wikipedia
from apiclient import errors
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import datetime
import requests
import string
import numbers
import math
import random
import calendar
from textblob import TextBlob
from textblob import Word
from dateutil import parser
from faker import Faker
from oauth2client import file, client, tools
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import bs4
import html5lib
from pymongo import MongoClient
import ast
import json
from httplib2 import Http
import apiclient
from googleapiclient import errors
from googleapiclient import discovery
from googleapiclient.discovery import build
import numbers
from yelpapi import YelpAPI
from wit import Wit


import google_voice_hub as gv
import google_sheets_api_storage as SHEETS

def run_sms_assist():
    # A 'temp' global variable is initialized since
    # we need to be able to keep track of the most
    # recent 'unread' email for deleting/marking-as-read purposes
    temp = ''

    def inner():
        print('Starting...')
        a = messages_label_list(service, 'me', label_ids=['UNREAD'])[0]['id']
        nonlocal temp
        if a != temp:
            try:
                b = get_message(service, 'me', a)
                fromLabel = ""
                subject_label = ""
                # Parsing the 'From' and 'Subject's of the email
                for item in b['payload']['headers']:
                    if item['name'] == 'From':
                        fromLabel = item['value']
                        mongo_num = parse_num_from_GV(fromLabel)

                    if item['name'] == 'Subject':
                        subject_label = item['value']
                        mongo_message = parse_message_from_GV(b['snippet'])
                if "New text message from" in str(subject_label):
                    print("Received a new TIA-related message")
                    print(mongo_num)
                    print(mongo_message)
                    database_new_item(mongo_num, mongo_message)
                    # Run Full Script
                    time.sleep(2)
                    mark_as_read()
            except BaseException:
                print("No new messages ...")
        try:
            update_user_data()
            process_all_unsent()
        except BaseException:
            print("Moving on to next loop ...")
        temp = a
        time.sleep(10)
    while True:
        try:
            inner()
            time.sleep(10)
        except BaseException:
            time.sleep(10)
            print('Hit an error... trying to avoid a crash here')


print("Starting Webdriver ...")
BROWSER = gv.start_google_voice(SHEETS.GV_EMAIL, SHEETS.GV_PASSWORD)
print("TIA's ready now.")    

run_sms_assist()
