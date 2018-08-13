#!/usr/bin/env python
import pika
import time
import mongo_helpers as mongo
from apscheduler.schedulers.background import BackgroundScheduler
import general_message_helpers as msg_gen
import reminder_helpers as remind
import datetime
import time
from pytz import utc


def reschedule_old_items_on_restart():
    for message in mongo.timed_records.find():
        eval(message['str_scheduler'])
        print("Added previously timed message")


scheduler = BackgroundScheduler(timezone=utc)
scheduler.start()

# IF THE SERVER IS (RE)STARTING, CHECK ALL PREVIOUS
# Items in the  them back into new scheduler instance
reschedule_old_items_on_restart()


connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='timer_queue', durable=True)
print('[*] Waiting for new unprocessed messages from TIMER QUEUE ... To exit press CTRL+C')


def callback(ch, method, properties, body):   
    body = mongo.convert_message_from_bytes(body)
    print("[x] Received Message from TIMER QUEUE with sms_id " + str(body))

    ch.basic_ack(delivery_tag = method.delivery_tag)
    print(body)
    timed_record = mongo.timed_records.find_one({"sms_id": body})
    str_scheduler = timed_record['str_scheduler']
    print(str_scheduler)
    eval(str_scheduler)
    mongo.change_db_message_value(timed_record, "status", "timer-post-setting")
    mongo.update_record(timed_record, {"scheduled": "YES"}, mongo.timed_records)

    remind.send_timing_receipt(timed_record)
    # send_recurring_receipt(body)

    print(" [x] Added Job to Scheduler")

channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback,
                      queue='timer_queue')

channel.start_consuming()