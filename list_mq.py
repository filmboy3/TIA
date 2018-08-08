import pika

def callback(ch, method, properties, body):
    print(body)

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='google_voice_queue', passive=True)
channel.basic_consume(callback, queue='google_voice_queue', no_ack=False)
connection.close()