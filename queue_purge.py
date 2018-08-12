import pika
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_purge(queue='timer_queue')
channel.close()
connection.close()