#!/usr/bin/env python3
from spc.spc import SPC
import time

spc = SPC()

def main():
    print(f"Board name: {spc.device.name}")
    print(f"Firmware Version: {spc.read_firmware_version()}")
    time.sleep(2)

    while True:
        if ('input_voltage' in spc.device.peripherals):
            print(f"Input voltage: {spc.read_input_voltage()} mV")
        if ('input_current' in spc.device.peripherals):
            print(f"Input current: {spc.read_input_current()} mA")
        if ('output_voltage' in spc.device.peripherals):
            print(f"Raspberry Pi voltage: {spc.read_output_voltage()} mV")
        if ('output_current' in spc.device.peripherals):
            print(f"Raspberry Pi current: {spc.read_output_current()} mA")
        if ('battery_voltage' in spc.device.peripherals):
            print(f"Battery voltage: {spc.read_battery_voltage()} mV")
        if ('battery_current' in spc.device.peripherals):
            print(f"Battery current: {spc.read_battery_current()} mA")
        if ('battery_capacity' in spc.device.peripherals):
            print(f"Battery capacity: {spc.read_battery_capacity()} mAh")
        if ('battery_percentage' in spc.device.peripherals):
            print(f"Battery percentage: {spc.read_battery_percentage()} %")
        if ('power_source'  in spc.device.peripherals):
            power_source = spc.read_power_source()
            print(f"Power source: {power_source} - {'Battery' if power_source == spc.BATTERY else 'External'}")
        if ('is_input_plugged_in'  in spc.device.peripherals):
            print(f"Input plugged in: {spc.read_is_input_plugged_in()}")
        if ('is_battery_plugged_in'  in spc.device.peripherals):
            print(f"Battery plugged in: {spc.read_is_battery_plugged_in()}")
        if ('is_charging' in spc.device.peripherals):
            print(f"Charging: {spc.read_is_charging()}")
        if ('fan_power' in spc.device.peripherals):
            print(f"Fan power: {spc.read_fan_power()} %")

        print('')
        print(f"Others:")
        shutdown_request = spc.read_shutdown_request()
        shutdown_request_str = 'None'
        if shutdown_request == spc.SHUTDOWN_REQUEST_NONE:
            shutdown_request_str = 'None'
        elif shutdown_request == spc.SHUTDOWN_REQUEST_LOW_BATTERY:
            shutdown_request_str = 'Low battery'
        elif shutdown_request == spc.SHUTDOWN_REQUEST_BUTTON:
            shutdown_request_str = 'Button'
        else:
            shutdown_request_str = 'Unknown'
        print(f"Shutdown request: {shutdown_request} - {shutdown_request_str}")
        print(f'Board id: {spc.read_board_id()}')
        if ('always_on' in spc.device.peripherals):
            print(f"Always on: {spc.read_always_on()}")
        if ('power_source_voltage' in spc.device.peripherals):
            print(f"Power source voltage: {spc.read_power_source_voltage()} mV")
        if ('shutdown_percentage' in spc.device.peripherals):
            print(f"Shutdown percentage: {spc.read_shutdown_percentage()} %")
        if ('power_off_percentage' in spc.device.peripherals):
            print(f"Power off percentage: {spc.read_power_off_percentage()} %")

        print('')
        time.sleep(1)

if __name__ == '__main__':
    main()
