import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(
               'localhost'))

# Create normal 'Hello World' type channel.
channel = connection.channel()
channel.confirm_delivery()
channel.queue_declare(queue='hello', durable=True)

# We need to bind this channel to an exchange, that will be used to transfer 
# messages from our delay queue.
channel.queue_bind(exchange='amq.direct',
                   queue='hello')

# Create our delay channel.
delay_channel = connection.channel()
delay_channel.confirm_delivery()

# This is where we declare the delay, and routing for our delay channel.
delay_channel.queue_declare(queue='hello_delay', durable=True,  arguments={
  'x-message-ttl' : 5000, # Delay until the message is transferred in milliseconds.
  'x-dead-letter-exchange' : 'amq.direct', # Exchange used to transfer the message from A to B.
  'x-dead-letter-routing-key' : 'hello' # Name of the queue we want the message transferred to.
})

delay_channel.basic_publish(exchange='',
                      routing_key='hello_delay',
                      body="Message to be Delayed",
                      properties=pika.BasicProperties(delivery_mode=2))

print(" \n[x] Sent")