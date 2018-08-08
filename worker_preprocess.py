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
import pika
import sys


print("[*] Checking for new unprocessed messages from MongoDB ... To exit press CTRL+C")


def transfer_unprocessed_to_wit_queue():

    for message in mongo.message_records.find({"status": "unprocessed"}):
        # message = mongo.convert_message_from_bytes(message)

        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='pre_processing_queue_2', durable=True)
        channel.basic_publish(exchange='',
                              routing_key='pre_processing_queue_2',
                              body=str(message),
                              properties=pika.BasicProperties(
                              delivery_mode = 2, # make message persistent
                              ))
        print("\n\n[x] Sent Message To PRE-PROCESSING QUEUE %r" % str(message['body']))
        mongo.change_db_message_value(message, "status", "currently processing")


def wit_loop():

    def inner():
        transfer_unprocessed_to_wit_queue()

    while True:
        try:
            inner()
            time.sleep(1)
        except BaseException:
            time.sleep(1)
            print('Hit an error... trying to avoid a crash here')

wit_loop()
