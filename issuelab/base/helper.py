import re
import datetime

def get_iso_timestamp(timestamp: float):
    return datetime.datetime.utcfromtimestamp(timestamp / 1000).isoformat()

def minutes_to_human_readable(minutes):
        minutes = int(minutes)
        if minutes > 60:
            time = float(minutes) / 60.0
            time_hours = int(time)
            time_minutes = int((time - time_hours) * 60)
            return f"{time_hours}h{time_minutes}m"
        else:
            return f"{minutes}m"
