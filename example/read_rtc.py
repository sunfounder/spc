#!/usr/bin/env python3
from spc import SPC
import time
from datetime import datetime

spc = SPC()

# current_time = datetime.now()
# time_list = [
#     current_time.year,
#     current_time.month,
#     current_time.day,
#     current_time.hour,
#     current_time.minute,
#     current_time.second,
#     current_time.microsecond,
# ]
# time_list.pop()
# # spc.set_rtc([2023, 10, 20, 17, 12, 30])
# print(f"time_list: {time_list}")
# spc.set_rtc(time_list)

print("\n")
# print("\n")
# print("\n")

while True:
    rtc = spc.read_rtc()
    print(f"\033[2A", end='')  # moves cursor up 3 lines

    # print(f"\033[3A", end='')  # moves cursor up 3 lines
    # print(f"\033[K RTC: {rtc}", end="\n", flush=True)
    year = rtc[0] + 2000
    month = rtc[1]
    day = rtc[2]
    hour = rtc[3]
    min = rtc[4]
    sec = rtc[5]
    ssec = rtc[6]
 
    print(f"\033[K RTC: {year}-{month:02d}-{day:02d} {hour:02d}:{min:02d}:{sec:02d}:{ssec:03d}", end="\n", flush=True)
    print(f"\033[K local: {datetime.now().isoformat(timespec='milliseconds')}")


    time.sleep(1)
