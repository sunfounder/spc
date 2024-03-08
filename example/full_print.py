#!/usr/bin/env python3
from spc.spc import SPC
import time

spc = SPC()

RIGHT_STR_MAX_LEN = 20

def main():
    while True:
        # Read the data before clearing the screen，to retain the last data when an error occurs.
        data_buffer = spc.read_all()


        if ('battery'  in spc.device.peripherals):
            print(f"Battery voltage: {data_buffer['battery_voltage']} mV")
            print(f"Battery current: {data_buffer['battery_current']} mA")
            print(f"Battery capacity: {data_buffer['battery_capacity']} mAh")
            print(f"Battery percentage: {data_buffer['battery_percentage']} %")
            print(f"Charging: {data_buffer['is_charging']}")
            print(f"Shutdown battery percentage: {data_buffer['shutdown_battery_pct']}")
        if ('external_input'  in spc.device.peripherals):
            print(f"External input voltage: {data_buffer['external_input_voltage']} mV")
            print(f"External input current: {data_buffer['external_input_current']} mA")
            print(f"Plugged in: {data_buffer['is_plugged_in']}")
        if ('raspberry_pi_power'  in spc.device.peripherals):
            print(f"Raspberry Pi voltage: {data_buffer['raspberry_pi_voltage']} mV")
            print(f"Raspberry Pi current: {data_buffer['raspberry_pi_current']} mA")
        if ('power_source_sensor'  in spc.device.peripherals):
            print(f"Power source: {data_buffer['power_source']} ({'Battery' if data_buffer['power_source'] == spc.BATTERY else 'External'})")
        if ('fan'  in spc.device.peripherals):
            print(f"Fan power: {data_buffer['fan_power']} %")

        print('')
        print(f"Internal data:")
        print(f"Board name: {data_buffer['board_name']}")
        print(f"Board id: {data_buffer['board_id']}")
        print(f"Firmware Version: {spc.read_firmware_version()}")
        print(f"VCC voltage: {spc._read_data('vcc_voltage')} mV")
        print(f"Shutdown request: {data_buffer['shutdown_request']}")
        print(f"RSTFLAG: {spc.read_rstflag():08b}")

        print('')
        print('')
        time.sleep(1)

if __name__ == '__main__':
    main()
