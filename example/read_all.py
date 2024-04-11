#!/usr/bin/env python3
from spc.spc import SPC
import time

spc = SPC()

RIGHT_STR_MAX_LEN = 20

def main():
    print(f"Board name: {spc.device.name}")
    print(f"Firmware Version: {spc.read_firmware_version()}")
    time.sleep(2)

    while True:
        # Read the data before clearing the screen，to retain the last data when an error occurs.
        data_buffer = spc.read_all()

        if ('input_voltage' in data_buffer):
            print(f"Input voltage: {data_buffer['input_voltage']} mV")
        if ('input_current' in data_buffer):
            print(f"Input current: {data_buffer['input_current']} mA")
        if ('output_voltage' in data_buffer):
            print(f"Raspberry Pi voltage: {data_buffer['output_voltage']} mV")
        if ('output_current' in data_buffer):
            print(f"Raspberry Pi current: {data_buffer['output_current']} mA")
        if ('battery_voltage' in data_buffer):
            print(f"Battery voltage: {data_buffer['battery_voltage']} mV")
        if ('battery_current' in data_buffer):
            print(f"Battery current: {data_buffer['battery_current']} mA")
        if ('battery_capacity' in data_buffer):
            print(f"Battery capacity: {data_buffer['battery_capacity']} mAh")
        if ('battery_percentage' in data_buffer):
            print(f"Battery percentage: {data_buffer['battery_percentage']} %")
        if ('power_source'  in data_buffer):
            print(f"Power source: {data_buffer['power_source']} ({'Battery' if data_buffer['power_source'] == spc.BATTERY else 'External'})")
        if ('is_input_plugged_in'  in data_buffer):
            print(f"Input plugged in: {data_buffer['is_input_plugged_in']}")
        if ('is_battery_plugged_in'  in data_buffer):
            print(f"Battery plugged in: {data_buffer['is_battery_plugged_in']}")
        if ('is_charging' in data_buffer):
            print(f"Charging: {data_buffer['is_charging']}")
        if ('fan_power' in data_buffer):
            print(f"Fan power: {data_buffer['fan_power']} %")
        if ('shutdown_battery_pct' in data_buffer):
            print(f"Shutdown battery percentage: {data_buffer['shutdown_battery_pct']}")

        print('')
        print(f"Internal data:")
        print(f"Shutdown request: {data_buffer['shutdown_request']}")
        print(f'Board id: {spc.read_board_id()}')
        if ('always_on' in spc.device.peripherals):
            print(f"Always on: {spc.read_always_on()}")
        if ('power_source_voltage' in spc.device.peripherals):
            print(f"Power source voltage: {spc.read_power_source_voltage()} mV")

        print('')
        print('')
        time.sleep(1)

if __name__ == '__main__':
    main()
