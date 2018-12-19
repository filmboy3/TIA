# coding=utf8

######################################################
#
# Tia Text Assistant - Internet tasks without using Data/Wi-Fi
# written by Jonathan Schwartz (jonathanschwartz30@gmail.com)
#
######################################################

from __future__ import print_function
import time
import mongo_helpers as mongo
import gmail_helpers as gmail
import pika
import sys

print("[*] Checking for Gmail Messages ... To exit press CTRL+C")

def gmail_loop():
    # A 'latest_email_temp' global variable is initialized
    # to compare whether newer 'unread' emails have arrived
    latest_email_temp = ''

    def inner():
        latest_email = gmail.messages_label_list(
            gmail.service, 'me', label_ids=['UNREAD'])[0]['id']
        nonlocal latest_email_temp
        if latest_email != latest_email_temp:
            try:
                gmail_resp = gmail.get_message(
                    gmail.service, 'me', latest_email)
                fromLabel = ""
                subject_label = ""
                # Parsing the 'From' and 'Subject's of the email
                for item in gmail_resp['payload']['headers']:
                    if item['name'] == 'From':
                        fromLabel = item['value']
                        mongo_num = gmail.parse_num_from_GV(fromLabel)

                    if item['name'] == 'Subject':
                        subject_label = item['value']
                        mongo_message = gmail.parse_message_from_GV(
                            gmail_resp['snippet'])
                if "New text message from" in str(subject_label):
                    result = [mongo_num, mongo_message]
                    str_result = str(result)
                    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
                    channel = connection.channel()
                    channel.queue_declare(queue='gmail_queue', durable=True)

                    channel.basic_publish(exchange='',
                                          routing_key='gmail_queue',
                                          body=str_result,
                                          properties=pika.BasicProperties(
                                            delivery_mode = 2, # make message persistent
                                          ))
                    print("\n\n[x] Sent message to GMAIL QUEUE: '" + str(result[1]) + "' from '" + str(result[0]))
                    gmail.mark_as_read()
            except BaseException:
                pass

        latest_email_temp = latest_email
        time.sleep(1)
    while True:
        inner()



gmail_loop()
