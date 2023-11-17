#!/usr/bin/env python3
from spc import SPC
import time
from datetime import datetime

spc = SPC()

current_time = datetime.now()
time_list = [
    current_time.year,
    current_time.month,
    current_time.day,
    current_time.hour,
    current_time.minute,
    current_time.second,
    # current_time.microsecond,
    int(128*current_time.microsecond/1000000),
]
# time_list.pop()

print(current_time.microsecond)
print(f"time_list: {time_list}")
spc.set_rtc(time_list)
print(f"\033[K set RTC: {current_time.year}-{current_time.month:02d}-{current_time.day:02d} {current_time.hour:02d}:{current_time.minute:02d}:{current_time.second:02d}")
