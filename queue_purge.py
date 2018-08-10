import pika
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_purge(queue='google_voice_queue')
channel.close()
connection.close()