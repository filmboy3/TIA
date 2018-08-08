
# coding=utf8
######################################################
# WIT.AI NLP-BASED FUNCTIONS
# Tia Text Assistant - Internet tasks without using Data/Wi-Fi
# written by Jonathan Schwartz (jonathanschwartz30@gmail.com)
#
######################################################

from __future__ import print_function
import re
import google_sheets_api_storage as SHEETS
import knowledge_helpers as know
import directions_helpers as geo
import yelp_helpers as yelp
import news_helpers as news
import jeopardy_helpers as jep
import weather_helpers as weather
import late_night_helpers as jokes
import translation_helpers as trans
import general_message_helpers as msg_gen
import reminder_helpers as reminder
import mongo_helpers as mongo

def pre_wit_scrub(message):
    replacements = [
                        (',', ''),
                        ('\.', ''),
                    ]
    for old, new in replacements:
        message = re.sub(old, new, message)
    message = message.lower()
    print("Wit Scrubbed Message: " + str(message))
    return message

def wit_parse_message(message, sender_info):
    message = pre_wit_scrub(str(message))
    mongo.change_db_message_value(sender_info, 'body', message)
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
        "wit_yelp_category",
        "wit_reminder_terms"]
    for i in range(0, len(wit_keyword_list)):
        try:
            return resp['entities'][wit_keyword_list[i]][0]['value']
        except BaseException:
            pass
    return resp['_text']


def nlp_extraction(resp, sender_info):
    intent_db = {
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
        "reminder_get": "reminder.trigger_reminder"

    }
    try:
        if (resp['_text'].lower() == 'no' or resp['_text'].lower().startswith("new home")):
            func_name = "msg_gen.trigger_new_home(resp, sender_info)"    
        else:
            intent_result = str(resp['entities']['intent'][0]['value'])
            func_name = intent_db[intent_result] + "(resp, sender_info)" 
    except BaseException:
        print("Unable to determine intent ... moving on to keyword parsing.")
        func_name = check_keywords(resp, sender_info)

    eval(func_name)

def check_keywords(resp, sender_info):
    preventRepeatCounter = 0
    try:
        if (resp['entities']['wit_direction']):
            return "geo.trigger_directions(resp, sender_info)"
            
    except BaseException:
        pass
    try:
        if (resp['entities']['wit_reminder_terms']):
            return "reminder.trigger_reminder(resp, sender_info)"
            
    except BaseException:
        pass
    try:
        if (resp['entities']['reminder']):
            return "reminder.trigger_reminder(resp, sender_info)"
            
    except BaseException:
        pass
    try:
        if (resp['entities']['wit_jeopardy']):
            return "jep.trigger_jeopardy(resp, sender_info)"
            
    except BaseException:
        pass
    try:
        if (resp['entities']['wit_language']):
            return "trans.trigger_translate(resp, sender_info)"
            
    except BaseException:
        pass
    try:
        if (resp['entities']['wit_news_source']):
            return "news.trigger_news(resp, sender_info)"
            
    except BaseException:
        pass
    try:
        if (preventRepeatCounter ==
                0 and resp['entities']['wit_yelp_category']):
            return "yelp.trigger_yelp(resp, sender_info)"
            
    except BaseException:
        pass
    try:
        if (resp['entities']['wit_transit']):
            return "geo.trigger_directions(resp, sender_info)"
            
    except BaseException:
        pass
    try:
        if (resp['entities']['intent'][0]['value'] == "wiki_get"):
            return "know.trigger_wiki(resp, sender_info)"
            
    except BaseException:
        pass
    try:
        if (resp['entities']['wolfram_search_query']):
            return "know.trigger_wolfram(resp, sender_info)"
            
    except BaseException:
        pass
    try:
        if (resp['entities']['intent'][0]['value'] == "wolfram_get"):
            return "know.trigger_wolfram(resp, sender_info)"
            
    except BaseException:
        pass
    try:
        if (preventRepeatCounter ==
                0 and resp['entities']['wikipedia_search_query']):
            return "know.trigger_wiki(resp, sender_info)"
            
    except BaseException:
        pass
