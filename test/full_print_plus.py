#!/usr/bin/env python3
from spc.spc import SPC
import time

spc = SPC()

LEFT_STR_MAX_LEN = 26
RIGHT_STR_MAX_LEN = 20

def main():
    while True:
        # Read the data before clearing the screen，to retain the last data when an error occurs.
        data_buffer = spc.read_all()

        # print("\033[H\033[J", end='')  # clear terminal windows
        print("\033[H", end='')  # moves cursor to home position (0, 0)
        print('\033[?25l', end='', flush=True) # cursor invisible

        print(f"Board name:               {str(data_buffer['board_id']):<{RIGHT_STR_MAX_LEN}s}")
        print(f"Firmware Version:         {spc.read_firmware_version():<{RIGHT_STR_MAX_LEN}s}")
        print(f"{' '*(26+RIGHT_STR_MAX_LEN)}")
        print(f"VCC voltage:              {str(spc._read_data('vcc_voltage'))+' mV':<{RIGHT_STR_MAX_LEN}s}")
        if ('battery'  in spc.device.peripherals):
            print(f"Battery voltage:          {str(data_buffer['battery_voltage'])+' mV':<{RIGHT_STR_MAX_LEN}s}")
            print(f"Battery current:          {str(data_buffer['battery_current'])+' mA':<{RIGHT_STR_MAX_LEN}s}")
            # print(f"Battery capactiy:         {str(data_buffer['battery_capactiy'])+' mAh':<{RIGHT_STR_MAX_LEN}s}")
            print(f"Battery percentage:       {str(data_buffer['battery_percentage'])+' %':<{RIGHT_STR_MAX_LEN}s}")
        if ('usb_in'  in spc.device.peripherals):
            print(f"USB voltage:              {str(data_buffer['usb_voltage'])+' mV':<{RIGHT_STR_MAX_LEN}s}")
            print(f"USB current:              {str(data_buffer['usb_current'])+' mA':<{RIGHT_STR_MAX_LEN}s}")
        if ('output'  in spc.device.peripherals):
            print(f"Output voltage:           {str(data_buffer['output_voltage'])+' mV':<{RIGHT_STR_MAX_LEN}s}")
            print(f"Output current:           {str(data_buffer['output_current'])+' mA':<{RIGHT_STR_MAX_LEN}s}")
        if ('battery'  in spc.device.peripherals):
            print(f"Charging:                 {'Charging' if data_buffer['is_charging'] else 'Not charging':<{RIGHT_STR_MAX_LEN}s}")
            print(f"Power source:             {'Battery' if data_buffer['power_source'] == spc.BATTERY else 'USB':<{RIGHT_STR_MAX_LEN}s}")
            print(f"USB plugged in:           {'Plugged in' if data_buffer['is_usb_plugged_in'] else 'Unplugged':<{RIGHT_STR_MAX_LEN}s}")
        if ('fan'  in spc.device.peripherals):
            print(f"Fan speed:                {str(data_buffer['fan_speed'])+' %':<{RIGHT_STR_MAX_LEN}s}")
        
        print(f"{' '*(26+RIGHT_STR_MAX_LEN)}")
        print(f"{'CPU temperature':<{LEFT_STR_MAX_LEN}s}{str(data_buffer['cpu_temperature'])+' C':<{RIGHT_STR_MAX_LEN}s}")
        print(f"{'Shutdown request':<{LEFT_STR_MAX_LEN}s}{str(data_buffer['shutdown_request']):<{RIGHT_STR_MAX_LEN}s}")
        print(f"{'Shutdown battery pct':<{LEFT_STR_MAX_LEN}s}{str(spc.read_shutdown_battery_pct()):<{RIGHT_STR_MAX_LEN}s}")
        
        rstflag = f'{spc.read_rstflag():08b}'
        print(f"{'RSTFLAG':<{LEFT_STR_MAX_LEN}s}{rstflag:<{RIGHT_STR_MAX_LEN}s}")
        
        time.sleep(1)

if __name__ == '__main__':

    try:
        print("\033c", end='', flush=True)  # clear terminal windows
        time.sleep(.1) # Delay is necessary, otherwise the cursor cannot be hidden
        print('\033[?25l', end='', flush=True) # cursor invisible
        main()
    finally:
        print('\033[?25h') # cursor visible
