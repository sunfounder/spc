#!/usr/bin/env python3
from spc.spc import SPC
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
    int(128*current_time.microsecond/1000000),
]

print(f"Set RTC to: {current_time.year}-{current_time.month:02d}-{current_time.day:02d} {current_time.hour:02d}:{current_time.minute:02d}:{current_time.second:02d}")
spc.write_rtc(time_list)

year, month, day, hour, min, sec, ssec = spc.read_rtc()
year += 2000
print(f"Done setting RTC")
print(f"Current RTC: {year}-{month:02d}-{day:02d} {hour:02d}:{min:02d}:{sec:02d}:{ssec:03d}")