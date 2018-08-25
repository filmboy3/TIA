
# coding=utf8
######################################################
# WIT.AI NLP-BASED FUNCTIONS
# Tia Text Assistant - Internet tasks without using Data/Wi-Fi
# written by Jonathan Schwartz (jonathanschwartz30@gmail.com)
#
######################################################

from __future__ import print_function
import re
import time
import api_keys as SHEETS
import knowledge_helpers as know
import directions_helpers as geo
import yelp_helpers as yelp
import news_helpers as news
import jeopardy_helpers as jep
import weather_helpers as weather
import translation_helpers as trans
import general_message_helpers as msg_gen
import reminder_helpers as reminder
import mongo_helpers as mongo
# import late_night_helpers as jokes
import datetime


def pre_wit_scrub(message):
    replacements = [
                        (',', ''),
                        ('\.', ''),
                    ]
    for old, new in replacements:
        message = re.sub(old, new, message)
    message = message.lower().strip()
    print("Wit Scrubbed Message: " + str(message))
    return message
    

def recurring_check(resp, sender_info):
    # reminder.trigger_recurring(resp, sender_info)
    try:
        _ = resp['entities']['recur_frequency'][0]['value']
        reminder.trigger_recurring(resp, sender_info)
    except:
        nlp_extraction(resp, sender_info)


def wit_parse_message(message, sender_info):
    # message = pre_wit_scrub(str(message))
    mongo.change_db_message_value(sender_info, 'body', message)
    resp = SHEETS.WIT_CLIENT.message(message)
    print(resp)
    recurring_check(resp, sender_info)


def use_backup_keywords(resp):
    wit_keyword_list = [
        "wikipedia_search_query",
        "phrase_to_translate",
        "location",
        "wolfram_search_query",
        "wit_news_source",
        "wit_biography_terms",
        "wit_yelp_category",
        "wit_reminder_terms"]
    for i in range(0, len(wit_keyword_list)):
        try:
            return resp['entities'][wit_keyword_list[i]][0]['value']
        except BaseException:
            pass
    return resp['_text']


def nlp_extraction(resp, sender_info):
    try:
        intent_result = resp['entities']['intent'][0]['value']
        print("Yes, we've got an intent_result")
        INTENT_DICT = {
            "new_home_get": "msg_gen.trigger_new_home",
            "translate_get": "trans.trigger_translate",
            "jokes_get": "jokes.trigger_jokes",
            "directions_get": "geo.trigger_directions",
            "news_directory_get": "news.trigger_news_directory",
            "news_get": "news.trigger_news",
            "nyt_get": "news.trigger_nyt",
            "hn_get": "news.trigger_hn",
            "help_get": "msg_gen.trigger_help",
            "jeopardy_get": "jep.trigger_jeopardy",
            "yelp_get": "yelp.trigger_yelp",
            "weather_get": "weather.trigger_weather",
            "forecast_get": "weather.trigger_forecast",
            "reminder_get": "reminder.trigger_reminder",
            "wiki_get": "know.trigger_wiki"
         }
        func_name = INTENT_DICT[intent_result] + "(resp, sender_info)" 
    except BaseException:
        print("Unable to determine intent ... moving on to keyword parsing.")
        func_name = check_keywords(resp, sender_info)

    try:
        sender_info = mongo.message_records.find_one({"sms_id": sender_info['sms_id']})
        time.sleep(1)
        eval(func_name)
    except BaseException:
        print("Final effort ")
        try:
            msg_gen.store_reply_in_mongo(
                                        know.wolfram_request(
                                            resp['_text']),
                                        sender_info,
                                        "🔭 Q & A 🔭")
        except BaseException:
            msg_gen.store_reply_in_mongo(
                
                msg_gen.send_error_text("text"),
                sender_info,
                "💀 Error 💀")

    
def check_keywords(resp, sender_info):
    keywords_db = {
        "01_wit_biography_terms": "know.trigger_wiki",
        "02_wit_direction": "geo.trigger_directions",
        "03_wit_reminder_terms": "reminder.trigger_reminder",
        "04_reminder": "reminder.trigger_reminder",
        "05_news_directory_get": "news.trigger_news_directory",
        "06_wit_jeopardy": "jep.trigger_jeopardy",
        "07_wit_language": "news.trigger_nyt",
        "08_wit_news_source": "news.trigger_news",
        "09_wit_yelp_category": "yelp.trigger_yelp",
        "10_wit_transit": "geo.trigger_directions",
        "12_wikipedia_search_query": "know.trigger_wiki",
        "13_wolfram_search_query": "know.trigger_wolfram"
    }
    sorted_keys = sorted(keywords_db.keys())

    for i in range(0, len(sorted_keys)):
        formatted_key = sorted_keys[i][3:]
        try:
          if (resp['entities'][formatted_key]):
              func_name = keywords_db[sorted_keys[i]] + "(resp, sender_info)"
              return func_name
        except BaseException:
          pass
    
    return "know.trigger_wolfram(resp, sender_info)"
