from datetime import datetime


def is_timer_done(timer: datetime) -> bool:
    """Check if the timer is finished."""
    return datetime.now() > timer
