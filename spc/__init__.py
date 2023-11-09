from .version import __version__

def monitor(spc):
    import time
    print("\033[H\033[J", end='')  # clear terminal windows
    print('\033[?25l', end='', flush=True) # cursor invisible
    try:
        while True:
            print_all_data_once(spc, isclear=True)
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"\n{e}")  # clear terminal windows
    finally:
        print('\033[?25h') # cursor visible



def print_all_data_once(spc, isclear=False):
    data_buffer = spc.read_all()
    _clear_code = ''
    if isclear:
        _clear_code = '\033[K' # clear one line

    if isclear:
        print(f"\033[{len(data_buffer)}A", end='\r')  # moves cursor up x lines

    print(f"{_clear_code}Battery voltage:          {data_buffer['battery_voltage']} mV")
    print(f"{_clear_code}Battery current:          {data_buffer['battery_current']} mA")
    print(f"{_clear_code}Battery percentage:       {data_buffer['battery_percentage']} %")
    print(f"{_clear_code}USB voltage:              {data_buffer['usb_voltage']} mV")
    print(f"{_clear_code}USB current:              {data_buffer['usb_current']} mA")
    print(f"{_clear_code}Output voltage:           {data_buffer['output_voltage']} mV")
    print(f"{_clear_code}Output current:           {data_buffer['output_current']} mA")
    print(f"{_clear_code}Charging:                 {'Charging' if data_buffer['is_charging'] else 'Not charging'}")
    print(f"{_clear_code}Power source:             {'Battery' if data_buffer['power_source'] == spc.BATTERY else 'USB'}")
    print(f"{_clear_code}USB plugged in:           {'Plugged in' if data_buffer['is_usb_plugged_in'] else 'Unplugged'}")
    print(f"{_clear_code}Fan speed:                {data_buffer['fan_speed']} %")

    # if isclear:
    #     print(f"\033[{len(data_buffer)}A", end='\r')  # moves cursor up x lines


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
    parser.add_argument('-f', '--fan', nargs='?', const=-1, type=int, help='get/set the speed of fan')
    parser.add_argument('-F', '--fan-mode', nargs='?', const=-1, type=str, choices=['auto', 'quiet', 'normal', 'performance'], help='get/set the mode of fan')
    parser.add_argument('-b', '--battery', action='store_true', help='battery voltage, current, percentage')
    parser.add_argument('-u', '--usb', action='store_true', help='usb voltage')
    parser.add_argument('-o', '--output', action='store_true', help='output voltage, current')
    parser.add_argument('-p', '--powered', action='store_true', help='power source')
    parser.add_argument('-c', '--charge', action='store_true', help='is charging')
    parser.add_argument('-j', '--json', action='store_true', help='output json format')

    args = parser.parse_args()

    spc = SPC()
    if args.monitor:
        monitor(spc)
    elif args.all:
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

    elif args.usb:
        usb_voltage = spc.read_usb_voltage()
        print(f'usb_voltage: {usb_voltage/1000.0:2.3f} V')
    elif args.output:
        output_voltage = spc.read_output_voltage()
        output_current = spc.read_output_current()
        output_info = f'''\
output_voltage: {output_voltage/1000.0:2.3f} V
output_current: {output_current:-5d} mA            
        '''
        print(output_info)
    elif args.powered:
        power_source = spc.read_power_source()
        if power_source == 1:
            print('Power source: usb')
        else:
            print('Power source: battery')
    elif args.charge:
        is_charge = spc.read_is_charging()
        if is_charge == 1:
            print('Charging')
        else:
            print('No charge')
