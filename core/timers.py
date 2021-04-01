from datetime import datetime, timedelta


def start_timer(secs=0, mins=0, hrs=0):
    return datetime.now() + timedelta(seconds=secs, minutes=mins, hours=hrs)


def is_timer_done(timer):
    return datetime.now() > timer
