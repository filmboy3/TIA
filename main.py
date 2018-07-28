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
# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.action_chains import ActionChains
import google_voice_hub as gv
import google_sheets_api_storage as SHEETS
import mongo_helpers as mongo
import gmail_helpers as gmail
import news_helpers as news
import late_night_helpers as jokes
import knowledge_helpers as know
import jeopardy_helpers as jep
import directions_helpers as geo
import weather_helpers as weather
import wit_helpers as wit
import yelp_helpers as yelp
import general_message_helpers as msg_gen
import translation_helpers as trans


browser = gv.start_google_voice(SHEETS.GV_EMAIL, SHEETS.GV_PASSWORD)
print("Done sleeping after startup of Google Voice")

def run_sms_assist():
    # A 'latest_email_temp' global variable is initialized 
    # to compare whether newer 'unread' emails have arrived
    latest_email_temp = ''

    def inner():
        print('Starting...')
        latest_email = gmail.messages_label_list(gmail.service, 'me', label_ids=['UNREAD'])[0]['id']
        nonlocal latest_email_temp
        if latest_email != latest_email_temp:
            try:
                gmail_resp = gmail.get_message(gmail.service, 'me', latest_email)
                fromLabel = ""
                subject_label = ""
                # Parsing the 'From' and 'Subject's of the email
                for item in gmail_resp['payload']['headers']:
                    if item['name'] == 'From':
                        fromLabel = item['value']
                        mongo_num = gmail.parse_num_from_GV(fromLabel)

                    if item['name'] == 'Subject':
                        subject_label = item['value']
                        mongo_message = gmail.parse_message_from_GV(gmail_resp['snippet'])
                if "New text message from" in str(subject_label):
                    print("Received a new TIA-related message")
                    print(mongo_num)
                    print(mongo_message)
                    mongo.database_new_item(mongo_num, mongo_message)
                    # Run Full Script
                    time.sleep(2)
                    gmail.mark_as_read()
            except BaseException:
                print("No new messages ...")
        try:
            mongo.update_user_data()
            mongo.process_all_unsent(browser)
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
            print('Hit an error... trying to avoid a crash here')

            
run_sms_assist()