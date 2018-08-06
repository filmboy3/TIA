#!/usr/bin/env python
import pika
import time
import mongo_helpers as mongo
from ast import literal_eval

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='gmail_queue', durable=True)
print(' [*] Waiting for new messages from GMAIL QUEUE. To exit press CTRL+C')

def callback(ch, method, properties, body):   
    body = body.decode("utf-8")
    result = literal_eval(body)
    print("\n[x] Received message from GMAIL QUEUE: '" + str(result[1]) + "' from '" + str(result[0]) + "'\n")
    record = mongo.database_new_item(result[0], result[1])
    mongo.update_user_data_for_message(record)
    print(" [x] Done")
    ch.basic_ack(delivery_tag = method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback,
                      queue='gmail_queue')

channel.start_consuming()