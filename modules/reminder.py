import bot_utility as utility
import consts
import re
from datetime import datetime, timedelta, date
import asyncio

REGEX_TIME = r"[0-2][0-9]:[0-5][0-9]"

def is_valid_time(time):
    matches = re.finditer(REGEX_TIME, time)
    for _, match in enumerate(matches, start=1):
        match = match.group()
        return match
    return '-1'


def get_time_difference(message):   
    time_now = datetime.now()
    time = is_valid_time(message.content)
    if time == '-1':
        return -1
    time_reminder = datetime(time_now.year, time_now.month, time_now.day, 00, 00, 00, 00) + timedelta(hours=int(time[:-3]), minutes= int(time[3:])-5)
    time_difference= (time_reminder-time_now).total_seconds()
    return time_difference if time_difference >= 0 else -1