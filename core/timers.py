import time
import re
from datetime import datetime, timedelta
import calendar

REGEX_TIME = r"([0-2])?[0-9]:[0-5][0-9]"


def start_timer(secs=0, mins=0, hrs=0):
    return datetime.now() + timedelta(seconds=secs) + timedelta(minutes=mins) + timedelta(hours=hrs)


def is_timer_done(timer):
    _time = datetime.fromtimestamp(time.time())
    return _time > timer


def remove_finished_timers(timers):
    for timer in timers:
        if is_timer_done(timer):
            timers.remove(timer)


def is_valid_time(time):
    matches = re.finditer(REGEX_TIME, time)
    for _, match in enumerate(matches, start=1):
        match = match.group()
        return match
    return '-1'


def get_time_difference(message_content):
    time_now = datetime.now()
    time = is_valid_time(message_content)
    if len(time) == 4:
        time = '0' + time
    print(time)
    if time == '-1':
        return -1
    time_reminder = datetime(time_now.year, time_now.month, time_now.day, 00, 00, 00, 00) + timedelta(hours=int(time[:-3]), minutes=int(time[3:])-5)
    time_difference = (time_reminder - time_now).total_seconds()
    return time_difference if time_difference >= 0 else -1


def convert_human_to_epoch_time(date: str) -> int:
    """ Input date formated as dd.mm.YYYY. Returns that
    date as epoch time.
    """
    date_time = f'{date}'
    pattern = '%d.%m.%Y'
    return int(time.mktime(time.strptime(date_time, pattern)))

def get_current_weekday() -> str:
    return datetime.today().strftime('%A')


def add_to_current_time(mins):
    return (datetime.now() + timedelta(minutes=mins)).strftime('%H:%M')


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
    print(add_to_current_time(5))
    print(get_time_difference('9:55'))

if __name__ == "__main__":
    test_module()
