from celery import Celery

app = Celery('tasks', broker='amqp://localhost//', backend='mongodb://test:testers1@ds235461.mlab.com:35461/tia')

@app.task
def reverse(string):
    return string[::-1]