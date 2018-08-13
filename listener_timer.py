#!/usr/bin/env python
import pika
import time
import mongo_helpers as mongo
from apscheduler.schedulers.background import BackgroundScheduler
import general_message_helpers as msg_gen
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

def send_recurring_receipt(body):
    result = "Your ⌛ recurring ⌛ message is all set! To cancel these messages at any ⌚, text CANCEL."
    record = {
        "from": body['from'],
        "body": body['body'],
        "result": [result],
        "launch_time": "NOW",
        "send_all_chunks": "ALL_CHUNKS",
        "current_chunk": 0,
        "chunk_len": 1,
        "status": "completed processing"
    }
    return mongo.database_new_populated_item(record)

def callback(ch, method, properties, body):   
    body = mongo.convert_message_from_bytes(body)
    print("[x] Received Message from TIMER QUEUE with sms_id '" + body['sms_id'] + "' to be sent to '" + str(body['from']) + "'")

    ch.basic_ack(delivery_tag = method.delivery_tag)
    print(body)
    str_scheduler = "scheduler.add_job(mongo.change_db_message_value_by_sms_id, 'interval', " + body['timer-frequency'] + ", jitter=15, id='" + body['sms_id'] + "'," + "kwargs={'sms_id': '" + body['sms_id'] + "', 'key': 'status', 'value': 'unprocessed'})"
    print(str_scheduler)
    timed_record = mongo.timed_records.find_one({"sms_id": body['sms_id']})
    mongo.update_record(timed_record, {"str_scheduler": str_scheduler}, mongo.timed_records)
    eval(str_scheduler)
    mongo.change_db_message_value(body, "status", "timer-post-setting")
    send_recurring_receipt(body)

    print(" [x] Added Job to Scheduler")

channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback,
                      queue='timer_queue')

channel.start_consuming()