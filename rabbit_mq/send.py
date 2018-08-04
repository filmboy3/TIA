#!/usr/bin/env python
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
body = 'I\'m a meathead!'
channel.queue_declare(queue='hello')
channel.basic_publish(exchange='',
                      routing_key='hello',
                      body=body)
print("[x] Sent %r" %(body))
connection.close()

#  import pika
# url = 'amqp://kbrhdnvp:r2t8qKiJKgXAsFLviOX4Gt9itd3xgtDR@lion.rmq.cloudamqp.com/kbrhdnvp'
# params = pika.URLParameters(url)
# connection = pika.BlockingConnection(params)
# channel = connection.channel()
# channel.queue_declare(queue='hello')

# def callback(ch, method, properties, body):
#     print("[x] Received %r" %(body))

# channel.basic_consume(callback, queue='hello', no_ack=True)

# channel.start_consuming()

# import pika
# url = 'amqp://kbrhdnvp:r2t8qKiJKgXAsFLviOX4Gt9itd3xgtDR@lion.rmq.cloudamqp.com/kbrhdnvp'
# params = pika.URLParameters(url)
# connection = pika.BlockingConnection(params)
# channel = connection.channel()
# channel.basic_publish(exchange='', routing_key='hello', body='Hello Viewers a first time!')
# channel.basic_publish(exchange='', routing_key='hello', body='Hello Viewers a second time!')