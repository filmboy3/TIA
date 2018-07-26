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

# WIT.AI NLP-BASED FUNCTIONS ############

def wit_parse_message(message, sender_info):
    print("In the parsing phase...")
    message = message.lower()
    message = re.sub(",", "", message)
    resp = SHEETS.WIT_CLIENT.message(message)
    nlp_extraction(resp, sender_info)

def use_backup_keywords(resp):
    wit_keyword_list = [
        "wikipedia_search_query",
        "phrase_to_translate",
        "location",
        "wolfram_search_query",
        "wit_news_source",
        "wit_biography_terms",
        "wit_yelp_category"]
    for i in range(0, len(wit_keyword_list)):
        try:
            return resp['entities'][wit_keyword_list[i]][0]['value']
        except BaseException:
            pass
    return resp['_text']

def nlp_extraction(resp, sender_info):
    intent_db = {
        "new_home_get": "trigger_newHome",
        "translate_get": "trigger_translate",
        "jokes_get": "trigger_jokes",
        "directions_get": "trigger_directions",
        "news_directory_get": "trigger_news_directory",
        "news_get": "trigger_news",
        "nyt_get": "trigger_nyt",
        "hn_get": "trigger_hn",
        "help_get": "trigger_help",
        "jeopardy_get": "trigger_jeopardy",
        "yelp_get": "trigger_yelp",
        "weather_get": "trigger_weather",
        "forecast_get": "trigger_forecast"
    }
    try:
        intent_result = str(resp['entities']['intent'][0]['value'])
        func_name = intent_db[intent_result] + "(resp, sender_info)"
        print("Function name: " + func_name)
        eval(func_name)
    except BaseException:
        print("Unable to determine intent ... continuing:")
        checkKeywords(resp, sender_info)


def checkKeywords(resp, sender_info):
    preventRepeatCounter = 0
    try:
        if (preventRepeatCounter == 0 and resp['entities']['wit_direction']):
            trigger_directions(resp, sender_info)
            preventRepeatCounter = 1
    except BaseException:
        pass
    try:
        if (preventRepeatCounter == 0 and resp['entities']['wit_jeopardy']):
            trigger_jeopardy(resp, sender_info)
            preventRepeatCounter = 1
    except BaseException:
        pass
    try:
        if (preventRepeatCounter == 0 and resp['entities']['wit_language']):
            trigger_translate(resp, sender_info)
            preventRepeatCounter = 1
    except BaseException:
        pass
    try:
        if (preventRepeatCounter == 0 and resp['entities']['wit_news_source']):
            trigger_news(resp, sender_info)
            preventRepeatCounter = 1
    except BaseException:
        pass
    try:
        if (preventRepeatCounter == 0 and resp['entities']['wit_provider']):
            print("Cruft, remove Intent from Wit.Ai")
            preventRepeatCounter = 1
    except BaseException:
        pass
    try:
        if (preventRepeatCounter ==
                0 and resp['entities']['wit_yelp_category']):
            trigger_yelp(resp, sender_info)
            preventRepeatCounter = 1
    except BaseException:
        pass
    try:
        if (preventRepeatCounter == 0 and resp['entities']['wit_transit']):
            trigger_directions(resp, sender_info)
            preventRepeatCounter = 1
    except BaseException:
        pass
    try:
        if (preventRepeatCounter ==
                0 and resp['entities']['intent'][0]['value'] == "wiki_get"):
            trigger_wiki(resp, sender_info)
            preventRepeatCounter = 1
    except BaseException:
        pass
    try:
        if (preventRepeatCounter ==
                0 and resp['entities']['wolfram_search_query']):
            trigger_wolfram(resp, sender_info)
            preventRepeatCounter = 1
    except BaseException:
        pass
    try:
        if (preventRepeatCounter ==
                0 and resp['entities']['intent'][0]['value'] == "wolfram_get"):
            trigger_wolfram(resp, sender_info)
            preventRepeatCounter = 1
    except BaseException:
        pass
    try:
        if (preventRepeatCounter ==
                0 and resp['entities']['wikipedia_search_query']):
            trigger_wiki(resp, sender_info)
            preventRepeatCounter = 1
    except BaseException:
        pass