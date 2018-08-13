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


print("[*] Checking for new timed messages from MongoDB ... To exit press CTRL+C")


def transfer_preset_timers_to_timer_queue():

    for message in mongo.timed_records.find({"scheduled": "NO"}):
        # message = mongo.convert_message_from_bytes(message)

        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='timer_queue', durable=True)
        channel.basic_publish(exchange='',
                              routing_key='timer_queue',
                              body=str(message['sms_id']),
                              properties=pika.BasicProperties(
                              delivery_mode = 2, # make message persistent
                              ))
        print("Worker Timer Body: " + str(message))
        mongo.update_record(message, {"scheduled": "IN PROCESS"}, mongo.timed_records)

        mongo.change_db_message_value(message, "status", "timer-processing-setting")
        print("\n\n[x] Sent Message To TIMED MESSAGES QUEUE %r" % str(message['body']))


def timer_loop():

    def inner():
        transfer_preset_timers_to_timer_queue()

    while True:
        inner()


timer_loop()