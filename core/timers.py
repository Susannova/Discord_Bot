from datetime import datetime, timedelta
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
    timer = start_timer(secs=1)
    timers.append(timer)
    print(timer)
    while not is_timer_done(timer):
        assert(len(timers) == 1)
        remove_finished_timers(timers)
    remove_finished_timers(timers)
    assert(len(timers) == 0)

if __name__ == "__main__":
    test_module()


def convert_human_to_epoch_time(date: str) -> int:
    """ Input date formated as dd.mm.YYYY. Returns that
    date as epoch time.
    """
    date_time = f'{date}'
    pattern = '%d.%m.%Y'
    return int(time.mktime(time.strptime(date_time, pattern)))
