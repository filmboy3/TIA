#!/usr/bin/env python
import pika
import time
import mongo_helpers as mongo
import google_voice_hub as gv
import api_keys as SHEETS

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

browser = gv.start_google_voice(SHEETS.GV_EMAIL, SHEETS.GV_PASSWORD)

channel.queue_declare(queue='google_voice_queue', durable=True)
print('[*] Waiting for messages from GOOGLE-VOICE QUEUE ... To exit press CTRL+C')

def callback(ch, method, properties, body): 
    # print("Body: " + str(body))  
    body = str(mongo.convert_message_from_bytes(body))
    # print("Body after conversion: " + body)
    body = mongo.message_records.find_one({"sms_id": body})
    time.sleep(1)
    # print(body)
    
    print("[x] Received Message from GOOGLE-VOICE QUEUE with sms_id '" + body['sms_id'] + "' to be sent to '" + str(body['from']) + "'")
    ch.basic_ack(delivery_tag = method.delivery_tag)
    # print(body)
    gv.process_reply(body, browser)
    print(" [x] Message Sent")
    mongo.change_db_message_value(body, "status", "message sent")

channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback,
                      queue='google_voice_queue')

channel.start_consuming()