# coding=utf8

######################################################
#
# Tia Text Assistant - Internet tasks without using Data/Wi-Fi
# written by Jonathan Schwartz (jonathanschwartz30@gmail.com)
#
######################################################

from __future__ import print_function
import requests
import random

import general_message_helpers as msg_gen


def jeopardy_request():
    url = "http://jservice.io/api/random?count=1"
    json_data = requests.get(url).json()
    category_id = json_data[0]["category"]["id"]

    url = "http://jservice.io/api/category?id=" + str(category_id)
    json_data = requests.get(url).json()

    total_clues = json_data['clues_count']
    clues_in_category = 5
    multiple = (total_clues / 5) - 1
    starting_index = round(random.random() * multiple) * clues_in_category

    category = str(json_data["title"].upper())
    total_string = ""
    air_year = str(json_data['clues'][starting_index]["airdate"].split("-")[0])
    total_string = category + " (" + air_year + ")\n\n"

    answer_key = "\n🚧 🚧 🚧 🚧 🚧 🚧 \n⬇️" \
                 " SPOILERS ⬇️\n🚧 🚧 🚧 🚧 🚧 🚧 \n\n"
    answer_key = answer_key + total_string

    for i in range(starting_index, starting_index + 5):
        if (str(json_data['clues'][i]["invalid_count"]) == 1):
            return jeopardy_request()
        response = str(json_data['clues'][i]["question"])
        value = "💰 $" + str(json_data['clues'][i]["value"]) + "💰"
        if (str(json_data['clues'][i]["value"]) == "None"):
            return jeopardy_request()
        total_string = total_string + value + " " + response + "\n\n"
        answer_question = str(json_data['clues'][i]["answer"])
        answer_key = answer_key + response + \
            " 🎯 " + answer_question + " 🎯 " + "\n\n"
    answer_key = answer_key.replace('<i>', '')
    answer_key = answer_key.replace('</i>', '')
    return (total_string, answer_key)


def trigger_jeopardy(resp, sender_info):
    print("Jeopardy Triggered")
    jeopardyTuple = jeopardy_request()
    jeopardyTogether = jeopardyTuple[0] + jeopardyTuple[1]
    msg_gen.store_reply_in_mongo(
            jeopardyTogether, sender_info, "📺 Jeopardy 📺")

