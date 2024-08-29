import os
from datetime import datetime
import pytz
from investpy import economic_calendar
import numpy as np
import pandas as np


def convert_timezone_to_gmt_offset(timezone_str: str) -> str:
    # Get the timezone object
    timezone = pytz.timezone(timezone_str)
    
    # Get the current time in the specified timezone
    now = datetime.now(timezone)
    
    # Calculate the UTC offset
    utc_offset = now.utcoffset()
    
    # Format the offset in +/-HH:MM format
    offset_hours = int(utc_offset.total_seconds() // 3600)
    offset_minutes = int((utc_offset.total_seconds() % 3600) // 60)
    
    # Handle the sign and format it as GMT+HH:MM or GMT-HH:MM
    offset_str = f"GMT{' +' if offset_hours >= 0 else '-'}{abs(offset_hours):02}:{abs(offset_minutes):02}"
    
    return offset_str



def get_all_events():
    timezone = "Europe/Amsterdam"
    print(convert_timezone_to_gmt_offset(timezone))



get_all_events()

