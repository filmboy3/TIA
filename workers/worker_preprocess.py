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
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='pre_processing_queue', durable=True)
        channel.basic_publish(exchange='',
                              routing_key='pre_processing_queue',
                              body=str(message),
                              properties=pika.BasicProperties(
                              delivery_mode = 2, # make message persistent
                              ))
        print("\n\n[x] Sent Message To PRE-PROCESSING QUEUE %r" % str(message['body']))

def wit_loop():

    def inner():
        transfer_unprocessed_to_wit_queue()
        time.sleep(2)
    while True:
        inner()


wit_loop()
