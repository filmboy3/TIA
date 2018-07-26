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

# NEWS FUNCTIONS #


def news_source_parse(source):
    source = source.lower()
    news_sources_db = {
        "ap": "associated-press",
        "abc": "abc-news",
        "australian abc": "abc-news-au",
        "al jazeera": "al-jazeera-english",
        "ars technica": "ars-technica",
        "axios": "axios",
        "bbc": "bbc-news",
        "bbc sport": "bbc-sport",
        "br": "bleacher report",
        "bloomberg": "bloomberg",
        "business insider": "business-insider",
        "business insider uk": "business-insider-uk",
        "buzzfeed": "buzzfeed",
        "cbc": "cbc-news",
        "cbs": "cbs-news",
        "cnbc": "cnbc",
        "cnn": "cnn",
        "crypto": "crypto-coins-news",
        "daily mail": "daily-mail",
        "engadget": "engadget",
        "ew": "entertainment-weekly",
        "espn": "espn",
        "financial post": "financial-post",
        "ft": "financial times",
        "fortune": "fortune",
        "fox-sports": "fox-sports",
        "google news": "google-news",
        "google news uk": "google-news-uk",
        "ign": "ign",
        "the independent": "independent",
        "mashable": "mashable",
        "medical": "medical-news-today",
        "metro": "metro",
        "daily mirror": "mirror",
        "msnbc": "msnbc",
        "mtv": "mtv-news",
        "british mtv": "mtv-news-uk",
        "national-geographic": "national-geographic",
        "national-review": "national-review",
        "nbc": "nbc-news",
        "new scientist": "new-scientist",
        "news.com": "news-com-au",
        "newsweek": "newsweek",
        "nymag": "new york magazine",
        "next big future": "next-big-future",
        "nfl": "nfl-news",
        "nhl": "nhl-news",
        "politico": "politico",
        "polygon": "polygon",
        "recode": "recode",
        "reddit": "reddit-r-all",
        "reuters": "reuters",
        "techcrunch": "techcrunch",
        "techradar": "techradar",
        "economist": "the-economist",
        "Globe and Mail": "the-globe-and-mail",
        "the guardian": "the-guardian-uk",
        "the guardian australian": "the-guardian-au",
        "huffpost": "the-huffington-post",
        "irish times": "irish-times",
        "the lad bible": "the-lad-bible",
        "the next web": "the-next-web",
        "the sport bible": "the-sport-bible",
        "the telegraph": "the-telegraph",
        "the verge": "the-verge",
        "wall street journal": "the-wall-street-journal",
        "the washington post": "the-washington-post",
        "the washington times": "the-washington-times",
        "time": "time",
        "usa today": "usa-today",
        "vice": "vice-news",
        "wired": "wired"
    }
    try:
        return news_sources_db[source]
    except BaseException:
        return 'cnn'


def get_domain_for_hn(url):
    pat = r'((https?):\/\/)?(\w+\.)*(?P<domain>\w+)\.(\w+)(\/.*)?'
    m = re.match(pat, url)
    if m:
        domain = m.group('domain')
        return domain
    else:
        return False


def hacker_news_request():
    url = "https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty"
    json_data = requests.get(url).json()
    full_text = ""
    for i in range(0, 30):
        newUrl = "https://hacker-news.firebaseio.com/v0/item/" + \
            str(json_data[i]) + ".json?print=pretty"
        item_json_data = requests.get(newUrl).json()
        num_as_string = str(i + 1)
        domainStr = ""
        try:
            domainStr = str(get_domain_for_hn(str(item_json_data['url'])))
        except BaseException:
            print("Domain Str is not present")
        inner_combine = num_as_string + ": " + \
            str(item_json_data['title']) + "\n🔼 " + \
            str(item_json_data['score']) + " 🔼" + \
            domainStr + "\n\n"
        full_text += inner_combine
    return full_text


def nyt_request():
    url = "https://SHEETS.nytimes.com/svc/topstories/v2/home.json?api-key=" + SHEETS.NY_TIMES_API
    json_data = requests.get(url).json()
    print(json_data)
    print(type(json_data))
    full_text = ""
    for i in range(0, len(json_data['results']) - 1):
        phrase = ""
        section = str(json_data['results'][i]['section'])
        title = str(json_data['results'][i]['title'])
        abstract = str(json_data['results'][i]['abstract'])
        phrase = str("🗽 " + section + " 📰 '" + title + "' 📰\n" + abstract + " 🗽\n\n")
        if section != "Briefing":
            full_text += phrase
    return full_text


def news_request(news):
    print("Inside the news_request")
    sourceInsert = news_source_parse(news)
    print("Source Insert: " + sourceInsert)
    url = "https://newsSHEETS.org/v2/top-headlines?sources=" + \
          sourceInsert + "&apiKey=" + SHEETS.NEWS_API
    print("News url: " + url)
    json_data = requests.get(url).json()
    articles = json_data['articles']
    full_text = "Top Headlines from " + articles[0]['source']['name'] + ":\n\n"
    for i in range(0, len(articles)):
        title = articles[i]['title']
        description = ""
        if str(articles[i]['description']) != "None":
            description = "\n" + articles[i]['description']
        inner_combine = "📰 " + title + \
            " 🌏 " + description + " 📰\n\n"
        full_text += inner_combine
    return full_text


def trigger_news_directory(resp, sender_info):
    news_directory_text = "Here are the available news sources you can use: \n\n📰 abc 📰" \
                          "ap 📰 abc 📰 abc au 📰 al jazeera 📰 ars technica 📰 axios 📰" \
                          " bbc 📰 bbc sport 📰 br 📰 bloomberg 📰 business " \
                          "insider 📰 business insider uk 📰 buzzfeed 📰 cbc 📰 cbs 📰 " \
                          "cnbc 📰 cnn 📰 crypto 📰 daily mail 📰 engadget 📰 ew 📰 espn 📰" \
                          " financial post 📰 ft 📰 fortune 📰 fox sports 📰 google 📰 google " \
                          "uk 📰 hn 📰 ign 📰\n📰 independent 📰 mashable 📰 medical 📰 metro 📰 " \
                          "mirror 📰 msnbc 📰 mtv 📰 mtv uk 📰 national geographic 📰 national " \
                          "review 📰 nbc 📰 new scientist 📰 com au 📰week 📰 nymag 📰 future 📰" \
                          " nfl 📰 nhl 📰 politico 📰 polygon 📰 recode 📰 reddit 📰 reuters 📰 " \
                          "techcrunch 📰 techradar 📰 economist 📰 globe and mail 📰 guardian 📰 " \
                          "guardian au 📰 huffpost 📰 the irish times 📰 lad bible 📰 nyt 📰 next " \
                          "web 📰 sport bible 📰 telegraph 📰 verge 📰 wsj 📰 washington post 📰 " \
                          "washington times 📰 time 📰 usa today 📰 vice 📰 wired 📰"
    try:
        header = "🌏 News Directory 🌏"
        print(header)
        send_full_text_message(news_directory_text, sender_info, header)
    except BaseException:
        send_full_text_message(
            send_error_text("news"),
            sender_info,
            "💀 Error 💀")

def trigger_nyt(resp, sender_info):
    print("NY Times Triggered")
    print(resp)
    try:
        send_full_text_message(nyt_request(), sender_info, "📰 NY Times 📰")
    except BaseException:
        send_full_text_message(
            send_error_text("ny times"),
            sender_info,
            "💀 Error 💀")


def trigger_hn(resp, sender_info):
    print("Hacker News Triggered")
    print(resp)
    try:
        send_full_text_message(
            hacker_news_request(),
            sender_info,
            "💻 Hacker News 💻")
    except BaseException:
        send_full_text_message(
            send_error_text("hacker news"),
            sender_info,
            "💀 Error 💀")


def trigger_news(resp, sender_info):
    print("News Triggered")
    print(resp)
    try:
        newsSource = resp['entities']['wit_news_source'][0]['value']
    except BaseException:
        newsSource = 'cnn'
    print("Wit.AI extracted news source: " + newsSource)

    try:
        header = "🌏 " + str(newsSource).upper() + " 🌏"
        print(header)
        send_full_text_message(news_request(newsSource), sender_info, header)
    except BaseException:
        send_full_text_message(
            send_error_text("news"),
            sender_info,
            "💀 Error 💀")