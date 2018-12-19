import pika
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_purge(queue='pre_processing_queue')
channel.queue_purge(queue='gmail_queue')
channel.queue_purge(queue='google_voice_queue')
channel.queue_purge(queue='timer_queue')
channel.close()
connection.close()