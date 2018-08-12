import worker_scheduler as schedule

def second_command():
    print("This is a separate command")

schedule.scheduler.add_job(second_command, 'interval', seconds=10, jitter=15)