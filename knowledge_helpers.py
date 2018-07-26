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

# INFORMATION FUNCTIONS #######

def wikipedia_request(command_body, sender_info):
    return wiki_split(wikipedia.summary(command_body))

def wiki_split(text_input):
    text_input = re.sub('"', "\'", str(text_input))
    text_input = re.sub("'", "\'", str(text_input))
    text_input = re.sub('%', " percent", str(text_input))
    wiki = TextBlob(text_input)
    chunked = wiki.sentences
    
    total_string = []
    for i in range(0, len(chunked)):

        total_string.append(str(chunked[i]))

    total_string =  " 📖 \n\n 📖 ".join(total_string)
    return total_string

def wolfram_request(input):
    print("triggered wolf alert inside with: " + str(input))
    original_input = input
    input = re.sub(" ", "%20", str(input))
    url = "http://SHEETS.wolframalpha.com/v2/query?appid=" + \
        SHEETS.WOLFRAM_API + "&input=" + input + "&output=json"
    print(url)
    json_data = requests.get(url).json()
    result = "Question: '" + str(original_input) + "'\n\n📚 Answer: " + str(
        json_data['queryresult']['pods'][1]['subpods'][0]['plaintext'])
    return result


def wolfram_examples_request():
    return "You can compute 💻 expert-level answers using Wolfram's breakthrough algorithms," \
    " 💡 knowledgebase and AI 🤖 technology.\n\nGeneral query topics include ➗ Mathematics, " \
    "🔬 Science & Technology, 🎭 Society & Culture and 🍴 Everyday Life 🏀 📖\n\n✨ Examples ✨\n" \
    "\n📖 Mini Cooper Roadster 📖 📖 " \
    " total length of all roads in Spain 📖 📖 motorcycle traffic in Germany 📖 📖 " \
    "annual deaths from auto accients in the Czech Republic 📖 📖 price of gasoline in Dallas " \
    "📖 📖 length of USS Ronald Reagan 📖 📖 United States railway length" \
    " 📖 📖 Apollo 11 📖 📖 heart 📖 📖 nerve supply of gallbladder " \
    "📖 📖 musk rose 📖 📖 BAC 5 drinks, 2 hours, male, 180lb 📖 📖 " \
    "who invented the cell phone 📖 📖 inventions by Benjamin Franklin 📖" \
    " 📖 BMI 5'10\", 165lb 📖 📖 generate a 12 character password 📖 📖" \
    " Morse code 'Wolfram Alpha' 📖 📖 what is the french equivalent ring size " \
    "to ring size 2? 📖 📖 U.K. men's size 11 shoe in Japanese size 📖 📖 " \
    "vehicles with highway gas mileage > 42 mpg 📖 📖 calories in a serving of " \
    "pineapple 📖 📖 Birthdays of the discoverers of Neptune 📖 📖 Robert Pattinson" \
    " birthday moon phase 📖 📖 population of the US on Obama's birthday 📖 📖 " \
    "Notable people born in New Orleans metro area 📖 📖 famous people from Detroit 📖 📖" \
    " Who is Angelina Jolie's brother? 📖 📖 Claude Monet's death date 📖 📖" \
    " broccoli nutrition label 📖 📖 whopper vs baconator vs big mac 📖 📖 " \
    "2 slices of swiss cheese 📖 📖 how many people does a 20 pound turkey feed " \
    "📖 📖 unemployment rate North Dakota 📖 📖 construction cost of Lambeau Field" \
    " / population of Green Bay 📖 📖 head width of tennis racket 📖 📖 cost of living" \
    " index Boston 📖 📖 Easter 1910 📖 📖 How many days until Labor Day " \
    "📖 📖 weather Vancouver, San Diego, Buenos Aires 📖 📖 caffeine in 24 oz." \
    " coffee, 24 oz. soda 📖 📖 average lifespan of a horse, goat, and sheep 📖 📖 " \
    " define triangulate 📖 📖 synonyms granular 📖 📖 mortgage $150,000, 6.5%, " \
    "30 years 📖 📖 cost of living index Boulder vs Sacramento 📖 📖 _al__la__ 📖" \
    " 📖 who was King of England when WWI ended? 📖 📖 stars visible tonight " \
    "📖 📖 next eclipse 📖 📖 acroynym USSS 📖 📖 price of movie ticket " \
    "in Providence, Nashville, Boise 📖 📖 words that rhyme with demand 📖 📖 do" \
    " you know a dirty joke? 📖 📖 where in the world is carmen sandiego? 📖 📖 " \
    "what's a car's safe braking distance at 60 mph 📖 📖 9th Wedding anniversary 📖 📖" \
    " anagrams trace 📖 📖 population Madrid / population spain 📖 📖 marijuana " \
    "cases in NY courts 📖 📖 5 largest countries by area 📖 📖 Who wrote Stairway to Heaven?" \
    " 📖 📖 characters in a Midsummer Night's Dream 📖 📖 Mary Shelley's place of " \
    "birth 📖 📖 3 hours in the sun with SPF 15 in Kabul at noon 📖 📖 x+y=10, x-y=4 " \
    "📖 📖 convert 1/6 to percent 📖 📖 facts about Galileo 📖 📖 movies " \
    "starring Kevin Bacon and Tom Cruise 📖 📖 Greek for 'Pythagoras' 📖 📖 what" \
    " was the age of Leonardo when the Mona Lisa was painted? 📖 📖 Academy Awards won " \
    "by Meryl Streep 📖 📖 Michael Jordan points per game in 1996 postseason 📖 📖" \
    " How many medals has Michael Phelps won? 📖 📖 16th President of the United" \
    " States 📖 📖 Warren Buffett net worth 📖 📖 Wikipedia popularity of Betty" \
    " White 📖 📖 $29.95 - 15% 📖 📖 30 percent of 8 miles 📖 📖 Rachel " \
    "has 17 apples. She gives 9 to Sarah. How many apples does Rachel have now? 📖 📖 1/4" \
    " * (4 - 1/2) 📖 📖 How many baseballs fit in a Boeing 747? 📖 📖 pennis to cover" \
    " 2 square miles 📖 📖 How many grains of rice would it take to stretch around the moon? " \
    "📖 📖 tic-tac-toe game 📖 📖 5 dice 📖 📖 32 coin tosses 📖 📖 8:5" \
    " odds, bet 97 euros 📖 📖 chance 3 people share a birthday 📖 📖 probability 2 " \
    "people born in same month 📖"

def trigger_wolfram(resp, sender_info):
    print("Wolfram Triggered")
    print(resp)
    try:
        send_full_text_message(
            wolfram_request(
                resp['_text']),
            sender_info,
            "🔭 Wolfram-Alpha 🔭")
    except BaseException:
        send_full_text_message(
            send_error_text("wolfram-alpha"),
            sender_info,
            "💀 Error 💀")


def trigger_wiki(resp, sender_info):
    print("Wikipedia Triggered")
    print(resp)
    wikiSearch = resp['_text']
    try:
        wikiSearch = resp['entities']['wikipedia_search_query'][0]['value']
    except BaseException:
        pass
    try:
        wikiSearch = resp['entities']['wolfram_search_query'][0]['value']
    except BaseException:
        pass

    print("Wit.AI Wikisearch term: " + wikiSearch)
    try:
        send_full_text_message(
            wikipedia_request(
                wikiSearch,
                sender_info),
            sender_info,
            "🔎 Wikipedia 🔎")
    except BaseException:
        send_full_text_message(
            send_error_text("wikipedia"),
            sender_info,
            "💀 Error 💀")

    print(resp)