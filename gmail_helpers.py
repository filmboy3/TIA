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

# GMAIL API FUNCTIONS / SETUP ###########

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

import auth
SCOPES = 'https://mail.google.com/'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'start'
authInst = auth.auth(SCOPES, CLIENT_SECRET_FILE, APPLICATION_NAME)
credentials = authInst.get_credentials()

http = credentials.authorize(httplib2.Http())
service = discovery.build('gmail', 'v1', http=http)

# Build the Gmail service from discovery
gmail_service = build('gmail', 'v1', http=http)


def messages_label_list(service, user_id, label_ids=[]):
    try:
        response = service.users().messages().list(
            userId=user_id, labelIds=label_ids).execute()
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])
        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(
                userId=user_id, labelIds=label_ids, pageToken=page_token).execute()
            if 'messages' in response:
                messages.extend(response['messages'])
        return messages
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


def get_message(service, user_id, msg_id):
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id).execute()
        print('Message snippet: %s' % message['snippet'])
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


def delete_message(service, user_id, msg_id):
    try:
        service.users().messages().delete(userId=user_id, id=msg_id).execute()
        print('Message with id: %s deleted successfully.' % msg_id)
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


def modify_message(service, user_id, msg_id, msg_labels):
    try:
        message = service.users().messages().modify(userId=user_id, id=msg_id,
                                                    body=msg_labels).execute()
        label_ids = message['labelIds']
        print('Message ID: %s - With Label IDs %s' % (msg_id, label_ids))
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


def create_message_labels():
    """Create object to update labels.

    Returns:
      A label update object.
    """
    return {'removeLabelIds': ['UNREAD'], 'addLabelIds': []}


def parse_num_from_GV(fromLabel):
    new_num = ["+1"]
    isolated_from = fromLabel[1:15]
    for i in range(0, len(isolated_from)):
        if isolated_from[i].isnumeric():
            new_num.append(isolated_from[i])
    mongo_num = "".join(new_num)
    return mongo_num


def parse_message_from_GV(message):
    mongo_message = re.search(
        r'Google Voice (.*?) YOUR ACCOUNT HELP CENTER HELP FORUM',
        str(message)).group(1)
    mongo_message = re.sub(
        r'To respond to this text message, reply to this email or visit Google Voice.',
        '', mongo_message)
    return mongo_message


def mark_as_read():
    a = messages_label_list(service, 'me', label_ids=['UNREAD'])[0]['id']
    modify_message(service, 'me', a, create_message_labels())
    print("Completed Removing of the Label for " + a + "?")