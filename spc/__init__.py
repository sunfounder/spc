from .version import __version__

def monitor(spc):
    import time
    print("\033c", end='')  # clear terminal windows
    time.sleep(.01) # Delay is necessary, otherwise the cursor cannot be hidden
    print('\033[?25l', end='', flush=True) # cursor invisible
    try:
        while True:
            print("\033[H", end='')  # moves cursor to home position (0, 0)
            print('\033[?25l', end='', flush=True) # cursor invisible
            print_all_data_once(spc)
            time.sleep(.5)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"\n{e}")  # clear terminal windows
    finally:
        print('\033[?25h') # cursor visible


def print_all_data_once(spc):
    # Read the data before clearing the screen，to retain the last data when an error occurs.
    data_buffer = spc.read_all()
    
    # print("\033c", end='')  # clear terminal windows

    print(f"Board name:               {data_buffer['board_name']:<20s}")

    if ('battery'  in spc.device.peripherals):
        print(f"Battery voltage:          {str(data_buffer['battery_voltage'])+' mV':<10s}")
        print(f"Battery current:          {str(data_buffer['battery_current'])+' mA':<10s}")
        print(f"Battery capacity:         {str(data_buffer['battery_capacity'])+' mAh':<10s}")
        print(f"Battery percentage:       {str(data_buffer['battery_percentage'])+' %':<10s}")
        print(f"Charging:                 {'Charging' if data_buffer['is_charging'] else 'Not charging':<15s}")
    if ('external_input'  in spc.device.peripherals):
        print(f"External input voltage:   {str(data_buffer['external_input_voltage'])+' mV':<10s}")
        print(f"External input current:   {str(data_buffer['external_input_current'])+' mA':<10s}")
        print(f"Plugged in:               {'Plugged in' if data_buffer['is_plugged_in'] else 'Unplugged':<15s}")
    if ('raspberry_pi_power'  in spc.device.peripherals):
        print(f"Raspberry Pi voltage:     {str(data_buffer['raspberry_pi_voltage'])+' mV':<10s}")
        print(f"Raspberry Pi current:     {str(data_buffer['raspberry_pi_current'])+' mA':<10s}")
    if ('power_source_sensor'  in spc.device.peripherals):
        print(f"Power source:             {'Battery' if data_buffer['power_source'] == spc.BATTERY else 'External':<15s}")
    if ('fan'  in spc.device.peripherals):
        print(f"Fan speed:                {str(data_buffer['fan_speed'])+' %':<10s}")
        print(f"CPU temperature:          {str(data_buffer['cpu_temperature'])+' °C':<{RIGHT_STR_MAX_LEN}s}")


def print_all_data_once_json(spc):
    import json
    data_buffer = spc.read_all()
    print(json.dumps(data_buffer))

def main():
    import argparse
    from .spc import SPC

    parser = argparse.ArgumentParser()

    parser.add_argument('-m', '--monitor', action='store_true', help='open a monitor')
    parser.add_argument('-a', '--all', action='store_true', help='print all the data of spc')
    parser.add_argument('-f', '--fan', nargs='?', const=-1, type=int, metavar="speed percentage", help='get/set the speed of fan')
    parser.add_argument('-F', '--fan-mode', nargs='?', const=-1, type=str, choices=['auto', 'quiet', 'normal', 'performance'], help='get/set the mode of fan')
    parser.add_argument('-b', '--battery', action='store_true', help='battery voltage, current, percentage')
    parser.add_argument('-e', '--external_input', action='store_true', help='external input')
    parser.add_argument('-o', '--raspberry_pi_power', action='store_true', help='raspberry pi voltage, current')
    parser.add_argument('-p', '--powered', action='store_true', help='power source')
    parser.add_argument('-c', '--charge', action='store_true', help='is charging')
    parser.add_argument('-j', '--json', action='store_true', help='output json format')
    parser.add_argument("-st", "--shutdown-strategy", nargs='?', const=-1, type=int, choices=range(10, 100), metavar="battery percentage",help="get/set battery percentage for Shutdown Strategy")

    args = parser.parse_args()

    spc = SPC()
    if args.monitor:
        monitor(spc)
    elif args.all:
        print("\033c", end='')  # clear terminal windows
        print_all_data_once(spc)
    elif args.json:
        print_all_data_once_json(spc)
    elif args.fan is not None:
        speed = args.fan
        if speed == -1:
            fan_speed = spc.read_fan_speed()
            print(f'fan_speed: {fan_speed}')
        else:
            if speed < 0:
                speed = 0
            elif speed > 100:
                speed = 100
            spc.set_fan_speed(speed)
            print(f'set fan speed to {speed}')
    elif args.fan_mode is not None:
        mode = args.fan_mode
        if mode == -1:
            fan_mode = spc.read_fan_mode()
            print(f'fan_mode: {fan_mode}')
        else:
            spc.set_fan_mode(mode)
            print(f'set fan mode to {mode}')
    elif args.battery:
        battery_voltage = spc.read_battery_voltage()
        battery_current = spc.read_battery_current()
        # battery_percentage = spc.read_battery_percentage()
        battery_percentage = round(
            min(max((battery_voltage - 6.2) / 2.2, 0) * 100, 100),
            2)
        battery_info = f'''\
battery_voltage: {battery_voltage/1000.0:2.3f} V
battery_current: {battery_current:-5d} mA
battery_percentage: {battery_percentage:-5d}
        '''
        print(battery_info)

    elif args.external_input:
        external_input_voltage = spc.read_external_input_voltage()
        print(f'external_input_voltage: {external_input_voltage/1000.0:2.3f} V')
    elif args.raspberry_pi_power:
        raspberry_pi_voltage = spc.read_raspberry_pi_voltage()
        raspberry_pi_current = spc.read_raspberry_pi_current()
        raspberry_pi_power = f'''\
raspberry_pi_voltage: {raspberry_pi_voltage/1000.0:2.3f} V
raspberry_pi_current: {raspberry_pi_current:-5d} mA            
        '''
        print(raspberry_pi_power)
    elif args.powered:
        power_source = spc.read_power_source()
        if power_source == 1:
            print('Power source: External')
        else:
            print('Power source: Battery')
    elif args.charge:
        is_charge = spc.read_is_charging()
        if is_charge == 1:
            print('Charging')
        else:
            print('No charge')
    elif args.shutdown_strategy is not None:
        pct =  args.shutdown_strategy
        if pct == -1:
            pct = spc.read_shutdown_battery_pct()
            print(f'shutdown strategy: {pct}')
        else:
            spc.set_shutdown_battery_pct(pct)
            print(f'set shutdown strategy to {pct}')        

    
