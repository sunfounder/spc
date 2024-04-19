#!/usr/bin/env python3
from spc.spc import SPC
import time

spc = SPC()

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
            print(f"Power source: {data_buffer['power_source']} - {'Battery' if data_buffer['power_source'] == spc.BATTERY else 'External'}")
        if ('is_input_plugged_in'  in data_buffer):
            print(f"Input plugged in: {data_buffer['is_input_plugged_in']}")
        if ('is_battery_plugged_in'  in data_buffer):
            print(f"Battery plugged in: {data_buffer['is_battery_plugged_in']}")
        if ('is_charging' in data_buffer):
            print(f"Charging: {data_buffer['is_charging']}")
        if ('fan_power' in data_buffer):
            print(f"Fan power: {data_buffer['fan_power']} %")
        print('')
        print(f"Internal data:")
        print(f'Board id: {spc.read_board_id()}')
        if ('shutdown_request' in data_buffer):
            shutdown_request_str = 'None'
            if data_buffer['shutdown_request'] == spc.SHUTDOWN_REQUEST_NONE:
                shutdown_request_str = 'None'
            elif data_buffer['shutdown_request'] == spc.SHUTDOWN_REQUEST_LOW_BATTERY:
                shutdown_request_str = 'Low battery'
            elif data_buffer['shutdown_request'] == spc.SHUTDOWN_REQUEST_BUTTON:
                shutdown_request_str = 'Button'
            else:
                shutdown_request_str = 'Unknown'
            print(f"Shutdown request: {data_buffer['shutdown_request']} - {shutdown_request_str}")
        if ('always_on' in spc.device.peripherals):
            print(f"Always on: {spc.read_always_on()}")
        if ('power_source_voltage' in spc.device.peripherals):
            print(f"Power source voltage: {spc.read_power_source_voltage()} mV")
        if ('shutdown_percentage' in spc.device.peripherals):
            print(f"Shutdown percentage: {spc.read_shutdown_percentage()} %")
        if ('power_off_percentage' in spc.device.peripherals):
            print(f"Power off percentage: {spc.read_power_off_percentage()} %")

        print('')
        print('')
        time.sleep(1)

if __name__ == '__main__':
    main()
