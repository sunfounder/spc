#!/usr/bin/env python3
from spc.spc import SPC
import time

spc = SPC()


def main():
    while True:
        # Read the data before clearing the screen，to retain the last data when an error occurs.
        data_buffer = spc.read_all()

        # print("\033[H\033[J", end='')  # clear terminal windows
        print("\033[H", end='')  # moves cursor to home position (0, 0)

        print(f"Board name:               {data_buffer['board_id']}")
        if ('battery'  in spc.device.peripherals):
            print(f"Battery voltage:          {data_buffer['battery_voltage']} mV")
            print(f"Battery current:          {data_buffer['battery_current']} mA")
            print(f"Battery capactiy:         {data_buffer['battery_capactiy']} mAh")
            print(f"Battery percentage:       {data_buffer['battery_percentage']} %")
        if ('usb_in'  in spc.device.peripherals):
            print(f"USB voltage:              {data_buffer['usb_voltage']} mV")
            print(f"USB current:              {data_buffer['usb_current']} mA")
        if ('output'  in spc.device.peripherals):
            print(f"Output voltage:           {data_buffer['output_voltage']} mV")
            print(f"Output current:           {data_buffer['output_current']} mA")
        if ('battery'  in spc.device.peripherals):
            print(f"Charging:                 {'Charging' if data_buffer['is_charging'] else 'Not charging'}")
            print(f"Power source:             {'Battery' if data_buffer['power_source'] == spc.BATTERY else 'USB'}")
            print(f"USB plugged in:           {'Plugged in' if data_buffer['is_usb_plugged_in'] else 'Unplugged'}")
        if ('fan'  in spc.device.peripherals):
            print(f"Fan speed:                {data_buffer['fan_speed']} %")

        time.sleep(1)

if __name__ == '__main__':
    try:
        print('\033[?25l', end='', flush=True) # cursor invisible
        print("\033[H\033[J", end='', flush=True)  # clear terminal windows
        main()
    finally:
        print('\033[?25h') # cursor visible
