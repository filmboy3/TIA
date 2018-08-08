from __future__ import absolute_import

from redis import Redis
from rq import Queue
from rq_scheduler import Scheduler
from datetime import datetime

scheduler = Scheduler(connection=Redis()) # Get a scheduler for the "default" queue

# You can also instantiate a Scheduler using an RQ Queue
queue = Queue('foo', connection=Redis())
scheduler = Scheduler(queue=queue)

# Puts a job into the scheduler. The API is similar to RQ except that it
# takes a datetime object as first argument. So for example to schedule a
# job to run on Jan 1st 2020 we do:
scheduler.enqueue_at(datetime(2020, 1, 1), func) # Date time should be in UTC

# Here's another example scheduling a job to run at a specific date and time (in UTC),
# complete with args and kwargs.
scheduler.enqueue_at(datetime(2020, 1, 1, 3, 4), func, foo, bar=baz)