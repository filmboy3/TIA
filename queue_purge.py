import pika
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_purge(queue='pre_processing_queue')
channel.close()
connection.close()