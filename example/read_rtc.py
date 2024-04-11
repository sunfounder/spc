#!/usr/bin/env python3
from spc.spc import SPC
from datetime import datetime

spc = SPC()

year, month, day, hour, min, sec, ssec = spc.read_rtc()
year += 2000

print(f"RTC: {year}-{month:02d}-{day:02d} {hour:02d}:{min:02d}:{sec:02d}:{ssec:03d}")
print(f"local: {datetime.now().isoformat(timespec='milliseconds')}")

