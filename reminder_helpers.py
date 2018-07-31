# coding=utf8

######################################################
#
# Tia Text Assistant - Internet tasks without using Data/Wi-Fi
# written by Jonathan Schwartz (jonathanschwartz30@gmail.com)
#
######################################################

from __future__ import print_function
import time
import re
from dateutil import parser
import datetime 
import general_message_helpers as msg_gen

def reminder_request(input, date):
    result = "Okay, I've set a reminder for " + parser.parse(str(date)) + ": ⏱️ " + str(input) + " ⏱️"
    return result

def trigger_reminder(browser, resp, sender_info):
    print("Reminder Triggered")
    print(resp)
    try:
        reminder = resp['entities']['reminder'][0]['value']
    except BaseException:
        try:
            reminder = resp['entities']['phrase_to_translate'][0]['value']
        except BaseException:
            reminder = resp['_text']
    print("\nReminder: " + str(reminder))
    try:
        date = resp['entities']['datetime'][0]['value']
        print("\n1st Try date: " + str(date))
    except BaseException:
        try:
            date = resp['entities']['datetime'][0]['values'][0]['to']['value']
            print("\n2nd Try date: " + str(date))
        except BaseException:
            try:
                date = resp['entities']['wdatetime'][0]['values'][0]['to']['value']
                print("\n3rd Try date: " + str(date))
            except BaseException:
                try:
                    date = resp['entities']['wdatetime'][0]['value']
                    print("\n3rd Try date: " + str(date))
                except BaseException:
                    today = datetime.date.today()
                    date = today + datetime.timedelta(days = 1) 
                    date = str(date) + "T00:00:00.000-07:00"
                    print("\nExcept date: " + str(date))
    print("Date: " + str(date))
    try:
        msg_gen.send_full_text_message(browser,
                                       reminder_request(
                                           reminder, date),
                                       sender_info,
                                       "⏱️ Reminder Setup ⏱️")
    except BaseException:
        msg_gen.send_full_text_message(
            browser,
            msg_gen.send_error_text("reminder"),
            sender_info,
            "💀 Error 💀")
