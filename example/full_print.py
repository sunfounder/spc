#!/usr/bin/env python3
from spc.spc import SPC
import time

spc = SPC()


def main():
    while True:
        # Read the data before clearing the screen，to retain the last data when an error occurs.
        data_buffer = spc.read_all()

        # print(data_buffer)
        
        # print("\033[H\033[J", end='')  # clear terminal windows
        print("\033[H", end='')  # moves cursor to home position (0, 0)
        print('\033[?25l', end='', flush=True) # cursor invisible

        
        print(f"Board name:               {data_buffer['board_id']:<20s}")
        print(f"Firmware Version:         {spc.read_firmware_version():<20s}")
        print(f"VCC voltage:              {str(spc._read_data('vcc_voltage'))+' mV':<10s}")

        if ('battery'  in spc.device.peripherals):
            print(f"Battery voltage:          {str(data_buffer['battery_voltage'])+' mV':<10s}")
            print(f"Battery current:          {str(data_buffer['battery_current'])+' mA':<10s}")
            print(f"Battery capactiy:         {str(data_buffer['battery_capactiy'])+' mAh':<10s}")
            print(f"Battery percentage:       {str(data_buffer['battery_percentage'])+' %':<10s}")
        if ('usb_in'  in spc.device.peripherals):
            print(f"USB voltage:              {str(data_buffer['usb_voltage'])+' mV':<10s}")
            print(f"USB current:              {str(data_buffer['usb_current'])+' mA':<10s}")
        if ('output'  in spc.device.peripherals):
            print(f"Output voltage:           {str(data_buffer['output_voltage'])+' mV':<10s}")
            print(f"Output current:           {str(data_buffer['output_current'])+' mA':<10s}")
        if ('battery'  in spc.device.peripherals):
            print(f"Charging:                 {'Charging' if data_buffer['is_charging'] else 'Not charging':<15s}")
            print(f"Power source:             {'Battery' if data_buffer['power_source'] == spc.BATTERY else 'USB':<15s}")
            print(f"USB plugged in:           {'Plugged in' if data_buffer['is_usb_plugged_in'] else 'Unplugged':<15s}")
        if ('fan'  in spc.device.peripherals):
            print(f"Fan speed:                {str(data_buffer['fan_speed'])+' %':<10s}")

        time.sleep(1)

if __name__ == '__main__':

    try:
        print("\033c", end='', flush=True)  # clear terminal windows
        time.sleep(.1) # Delay is necessary, otherwise the cursor cannot be hidden
        print('\033[?25l', end='', flush=True) # cursor invisible
        main()
    finally:
        print('\033[?25h') # cursor visible
