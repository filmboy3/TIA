# coding=utf8

######################################################
# YELP FUNCTIONS
# Tia Text Assistant - Internet tasks without using Data/Wi-Fi
# written by Jonathan Schwartz (jonathanschwartz30@gmail.com)
#
######################################################

from __future__ import print_function
import wit_helpers as wit
import translation_helpers as trans

import general_message_helpers as msg_gen
import google_sheets_api_storage as SHEETS


def yelp_request(query):
    limit = 3
    return full_results_yelp_search(query[0], query[1], limit)


def full_results_yelp_search(categories, location, limit):
    search_results = SHEETS.YELP_API.search_query(
        term=categories, location=location, limit=limit)
    yelp_fully_formatted = format_yelp_search(search_results, limit)
    return yelp_fully_formatted


def format_yelp_search(search_results, limit):
    result = [""]
    for i in range(limit):
        result.append(format_single_yelp_biz(search_results['businesses'][i]))
    return "\n\n☕☕☕☕☕☕☕☕☕\n\n".join(result)


def format_single_yelp_biz(listing):
    reviews_formatted = format_yelp_reviews(listing['id'])
    more_details = fetch_more_yelp_details(listing['id'])
    name = ""
    try:
        name = "😋 " + listing['name'].upper() + " 😋\n"
    except BaseException:
        name = ""
    try:
        review_count = "\n🍲 " + str(listing['review_count']) + " reviews 🍲"
    except BaseException:
        review_count = ""
    try:
        rating = "\n🌟 " + str(listing['rating']) + ' stars 🌟'
    except BaseException:
        rating = ""
    categories = []
    try:
        for j in range(0, len(listing['categories'])):
            categories.append(" " + str(listing['categories'][j]['title']))
    except BaseException:
        categories = ""
    try:
        price = "\n💵 " + listing['price'] + " 💵"
    except BaseException:
        price = ""
    try:
        display_address = "\n🏠 " + \
            " ".join(listing['location']['display_address']) + " 🏠"
    except BaseException:
        display_address = ""
    try:
        display_phone = "\n☎ " + listing['display_phone'] + " ☎\n\nReviews:"
    except BaseException:
        display_phone = ""
    result = [name,
              review_count,
              rating,
              "\n🍳 " + str(" |".join(categories)) + " 🍳",
              price,
              str(more_details['is_open_now']),
              str(more_details['hours']),
              display_address,
              str(more_details['cross_streets']),
              display_phone,
              reviews_formatted]
    return "".join(result)


def format_yelp_reviews(id):
    reviews_results = SHEETS.YELP_API.reviews_query(id)
    total = "\n"
    for i in range(0, len(reviews_results)):
        text_review = str(reviews_results['reviews'][i]['text'])
        text_review = text_review.replace('\n', ' ')
        star_singular = " stars 🌟"
        if reviews_results['reviews'][i]['rating'] == 1:
            star_singular = " star 🌟"
        rating = "\n🌟 " + \
            str(reviews_results['reviews'][i]['rating']) + star_singular
        user = reviews_results['reviews'][i]['user']['name']
        date = str(reviews_results['reviews'][i]['time_created'].split(" ")[0])
        total = total + "\n" + rating + "\n🍽️" + " '" + \
            str(text_review) + "'\n--" + str(user) + \
            " on " + date_reformat(date) + " 🍽️"
    return total


def fetch_more_yelp_details(id):
    details = SHEETS.YELP_API.business_query(id=id)
    more_details = {}
    try:
        if details['location']['cross_streets'] != "":
            more_details['cross_streets'] = "\n🛣️ X-Streets: " + \
                details['location']['cross_streets'] + " 🛣️"
        else:
            more_details['cross_streets'] = ""
    except BaseException:
        more_details['cross_streets'] = ""
    try:
        hours_formatted = ""
        today_hours = "\nToday's ⌚: " + time_reformat(
            details['hours'][0]['open'][0]['start']) + " - " + time_reformat(
            details['hours'][0]['open'][0]['start'])
        tomorrow_hours = "\nTomorrow's ⌚: " + time_reformat(
            details['hours'][0]['open'][1]['start']) + "-" + time_reformat(
            details['hours'][0]['open'][1]['start'])
        hours_formatted = today_hours + tomorrow_hours
        more_details['hours'] = hours_formatted
    except BaseException:
        more_details['hours'] = ""
    try:
        more_details['is_open_now'] = details['hours'][0]['is_open_now']
        if more_details['is_open_now']:
            more_details['is_open_now'] = "\n🔓 Open Now 🔓"
        else:
            more_details['is_open_now'] = "\n🔒 Closed Now 🔒"
    except BaseException:
        more_details['is_open_now'] = ""
    return more_details


def date_reformat(date):
    split_date = date.split("-")
    new_date = []
    if split_date[1][0] == str(0):
        new_date.append(split_date[1][1])
    else:
        new_date.append(split_date[0])
    if split_date[2][0] == str(0):
        new_date.append(split_date[2][1])
    else:
        new_date.append(split_date[2])
    new_date.append(split_date[0][2:])
    return "/".join(new_date)


def time_reformat(time_string):
    hours = int(time_string[:2])
    min = time_string[2:]
    period = "AM"
    if hours > 12:
        hours = hours - 12
        period = "PM"
    return str(hours) + ":" + min + " " + period


def trigger_yelp(resp, sender_info):
    print("Yelp Triggered")
    print(resp)
    try:
        location = resp['entities']['location'][0]['value']
    except BaseException:
        try:
            location = resp['entities']['wit_home'][0]['value']
            location = sender_info['home']
        except BaseException:
            try:
                location = location = resp['entities']['wikipedia_search_query'][0]['value']
            except BaseException:
                location = ""
    try:
        category = resp['entities']['wit_yelp_category'][0]['value']
    except BaseException:
        category = wit.use_backup_keywords(resp)

    print("Yelp Location: " + location)
    print("Yelp Category: " + category)
    result = (category, location)
    # Handling an early edge case in which AI confuses language names with
    # Yelp Ethnic foods, i.e., Chinese (language) vs Chinese (cuisine)
    if (location != ""):
        try:
            msg_gen.send_full_text_message(
                yelp_request(result), sender_info, "🍴 Yelp 🍴")
        except BaseException:
            msg_gen.send_full_text_message(
                msg_gen.send_error_text("Yelp"),
                sender_info,
                "💀 Error 💀")
    else:
        try:
            print("Switching Yelp to Translate Task")
            trans.trigger_translate(resp, sender_info)
        except BaseException:
            pass

    return result
