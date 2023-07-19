from datetime import datetime, timedelta


def start_timer(secs: int = 0, mins: int = 0, hrs: int = 0) -> datetime:
    """Give a `datetime` object for the current time plus the extra time given by the parameters."""
    return datetime.now() + timedelta(seconds=secs, minutes=mins, hours=hrs)


def is_timer_done(timer: datetime) -> bool:
    """Check if the timer is finished."""
    return datetime.now() > timer
