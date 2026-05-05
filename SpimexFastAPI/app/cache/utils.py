from datetime import datetime, time, timedelta


def get_ttl_until_14_11():
    now = datetime.now()
    target = datetime.combine(now.date(), time(14, 11))

    if now >= target:
        target += timedelta(days=1)
    return int((target - now).total_seconds())
