#!/usr/bin/env python
import pika
import time
import mongo_helpers as mongo

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='pre_processing_queue', durable=True)
print('[*] Waiting for new unprocessed messages from PRE-PROCESSING QUEUE ... To exit press CTRL+C')

def callback(ch, method, properties, body):   
    body = mongo.convert_message_from_bytes(body)
    print("[x] Received Message from PRE-PROCESSING QUEUE: '" + str(body['body']) + "' from '" + str(body['from']) + "'")
    ch.basic_ack(delivery_tag = method.delivery_tag)
    # print(body)
    mongo.process_message(body)
    print(" [x] Done")

channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback,
                      queue='pre_processing_queue')

channel.start_consuming()