#!/usr/bin/env python3
from spc import SPC
import time

spc = SPC()

while True:
    print('----------------------------------------------')
    data_buffer = spc.read_all()
    print(f"Battery voltage:    {data_buffer['battery_voltage']} mV")
    print(f"Battery current:    {data_buffer['battery_current']} mA")
    print(f"Battery percentage: {data_buffer['battery_percentage']} %")
    print(f"USB voltage:        {data_buffer['usb_voltage']} mV")
    print(f"USB current:        {data_buffer['usb_current']} mA")
    print(f"Output voltage:     {data_buffer['output_voltage']} mV")
    print(f"Output current:     {data_buffer['output_current']} mA")
    print(f"Charging:           {'Charging' if data_buffer['is_charging'] else 'Not charging'}")
    print(f"Power source:       {'Battery' if data_buffer['power_source'] == spc.BATTERY else 'USB'}")
    print(f"USB plugged in:     {'Plugged in' if data_buffer['is_usb_plugged_in'] else 'Unplugged'}")
    print(f"Fan speed:          {data_buffer['fan_speed']} %")

    time.sleep(1)
