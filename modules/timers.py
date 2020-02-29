from datetime import datetime, timedelta, date
import time

def start_timer(secs=0, mins=0, hrs=0):
    return datetime.now() + timedelta(seconds=secs) + timedelta(minutes=mins) + timedelta(hours=hrs)  

def is_timer_done(timer):
    _time = datetime.fromtimestamp(time.time())  
    return _time > timer
    

def remove_finished_timers(timers):
  for timer in timers:
        if is_timer_done(timer):
            timers.remove(timer)

# === TEST === #
def test_module():
    timers = []
    timer = start_timer(secs = 1)
    timers.append(timer)
    print(timer)
    while not is_timer_done(timer):
        assert(len(timers) == 1)
        remove_finished_timers(timers)
    remove_finished_timers(timers)
    assert(len(timers) == 0)
    
#test_module()
