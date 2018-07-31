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


def wit_parse_message(browser, message, sender_info):
    print("In the parsing phase...")
    message = message.lower()
    message = re.sub(",", "", message)
    resp = SHEETS.WIT_CLIENT.message(message)
    nlp_extraction(browser, resp, sender_info)


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


def nlp_extraction(browser, resp, sender_info):
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
        intent_result = str(resp['entities']['intent'][0]['value'])
        func_name = intent_db[intent_result] + "(browser, resp, sender_info)"
        print("Function name: " + func_name)
        eval(func_name)
    except BaseException:
        print("Unable to determine intent ... continuing:")
        check_keywords(browser, resp, sender_info)


def check_keywords(browser, resp, sender_info):
    preventRepeatCounter = 0
    try:
        if (preventRepeatCounter == 0 and resp['entities']['wit_direction']):
            geo.trigger_directions(browser, resp, sender_info)
            preventRepeatCounter = 1
    except BaseException:
        pass
    try:
        if (preventRepeatCounter == 0 and resp['entities']['wit_reminder_terms']):
            reminder.trigger_reminder(browser, resp, sender_info)
            preventRepeatCounter = 1
    except BaseException:
        pass
    try:
        if (preventRepeatCounter == 0 and resp['entities']['reminder']):
            reminder.trigger_reminder(browser, resp, sender_info)
            preventRepeatCounter = 1
    except BaseException:
        pass
    try:
        if (preventRepeatCounter == 0 and resp['entities']['wit_jeopardy']):
            jep.trigger_jeopardy(browser, resp, sender_info)
            preventRepeatCounter = 1
    except BaseException:
        pass
    try:
        if (preventRepeatCounter == 0 and resp['entities']['wit_language']):
            trans.trigger_translate(browser, resp, sender_info)
            preventRepeatCounter = 1
    except BaseException:
        pass
    try:
        if (preventRepeatCounter == 0 and resp['entities']['wit_news_source']):
            news.trigger_news(browser, resp, sender_info)
            preventRepeatCounter = 1
    except BaseException:
        pass
    try:
        if (preventRepeatCounter ==
                0 and resp['entities']['wit_yelp_category']):
            yelp.trigger_yelp(browser, resp, sender_info)
            preventRepeatCounter = 1
    except BaseException:
        pass
    try:
        if (preventRepeatCounter == 0 and resp['entities']['wit_transit']):
            geo.trigger_directions(browser, resp, sender_info)
            preventRepeatCounter = 1
    except BaseException:
        pass
    try:
        if (preventRepeatCounter ==
                0 and resp['entities']['intent'][0]['value'] == "wiki_get"):
            know.trigger_wiki(browser, resp, sender_info)
            preventRepeatCounter = 1
    except BaseException:
        pass
    try:
        if (preventRepeatCounter ==
                0 and resp['entities']['wolfram_search_query']):
            know.trigger_wolfram(browser, resp, sender_info)
            preventRepeatCounter = 1
    except BaseException:
        pass
    try:
        if (preventRepeatCounter ==
                0 and resp['entities']['intent'][0]['value'] == "wolfram_get"):
            know.trigger_wolfram(browser, resp, sender_info)
            preventRepeatCounter = 1
    except BaseException:
        pass
    try:
        if (preventRepeatCounter ==
                0 and resp['entities']['wikipedia_search_query']):
            know.trigger_wiki(browser, resp, sender_info)
            preventRepeatCounter = 1
    except BaseException:
        pass
