# -*- coding: UTF-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import math
from dateutil import parser
import string
import datetime
import random
import string
import time
import re
import api_keys as SHEETS

# def import_other_modules():
#     import api_keys as SHEETS
#     import jokes_crawler as crawler
#     import general_message_helpers as msg_gen
#     import mongo_helpers as mongo
#     import google_voice_hub as gv

# import_other_modules()


chromedriver = SHEETS.CHROME_PATH

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument("--incognito")
# options.add_argument('window-size=1200x600')  # optional

browser = webdriver.Chrome(
    executable_path=chromedriver,
    chrome_options=options)
print("Browser: " + str(browser))


def random_joke():
    import mongo_helpers as mongo
    joke_raw = mongo.jokes_records.aggregate(
         [ { "$sample": {'size': 1} } ] 
    )
    joke_full = list(joke_raw)
    return joke_full[0]


def record_jokes_in_db(date, joke):
    import mongo_helpers as mongo
    new_joke = {
        "date": date,
        "joke": joke
    }
    if mongo.jokes_records.find_one({"date": date}) is None:
       mongo.push_record(new_joke, mongo.jokes_records)
        print("Pushed new joke")
    else:
        old_data = mongo.jokes_records.find_one({"date": date})

def fetch_jokes(num=""):
    jokes_url = "https://www.newsmax.com/jokes/" + str(num)
    browser.get(jokes_url)
    # time.sleep(2)
    date_element = browser.find_element_by_css_selector('div.jokesDate')
    date_text = date_element.get_attribute("textContent")
    date_parsed = str(parser.parse(date_text))
    print(date_parsed)

    # print("We did something")
    jokes_all = []
    jokes_concat = "🌃  " + str(date_text) + " 🌃\n\n" 
    jokes_all = browser.find_elements_by_xpath(
        """//p""")
    for i in range(0, len(jokes_all)):
        joke = str(jokes_all[i].get_attribute("textContent"))
        if ("This site uses cookies" in joke):
            pass
        elif (joke == "RECOMMENDED"):
            break
        elif (joke == "" or "rerun" in joke.lower()):
            pass
        else:
            jokes_concat = jokes_concat + " 😂  " + joke.rstrip() + " 😂\n\n"
    print(jokes_concat)
    import google_voice_hub as gv
    jokes_chunk = gv.sizing_sms_chunks(jokes_concat, send_all_chunks="ALL_CHUNKS")
    record_jokes_in_db(date_parsed, jokes_chunk)
    return jokes_chunk

fetch_jokes()

# 2000 -> 0 has been done to fill the database. Use to backfill missing dates later on.  

# while (num > 2000):
#     try:
#         print("Trying num: " + str(num))
#         fetch_jokes(num)
#     except:
#         pass
#     num = num - 1
    
   