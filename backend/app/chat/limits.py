from datetime import datetime, timedelta


def today_range():
    now = datetime.utcnow()
    start = datetime(now.year, now.month, now.day)
    end = start + timedelta(days=1)
    return start, end