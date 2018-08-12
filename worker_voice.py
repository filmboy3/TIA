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


print("[*] Checking for wit-processed 'SEND-NOW' messages from MongoDB ... To exit press CTRL+C")


def transfer_processed_to_voice_queue():

    for message in mongo.message_records.find({"status": "completed processing"}):
        # message = mongo.convert_message_from_bytes(message)
        message_id = message['sms_id']
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='google_voice_queue', durable=True)
        channel.basic_publish(exchange='',
                            routing_key='google_voice_queue',
                            body=str(message_id),
                            properties=pika.BasicProperties(
                            delivery_mode = 2, # make message persistent
                            ))
        print("\n\n[x] Sent Message To GOOGLE VOICE QUEUE with sms_id: %r" % message_id)
        mongo.change_db_message_value(message, "status", "sending in process")


def voice_loop():

    def inner():
        transfer_processed_to_voice_queue()

    while True:
        inner()


voice_loop()
