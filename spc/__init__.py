from .version import __version__
from .spc import SPC
import time

USAGE = '''\
Usage:
  spc <OPTION> <input>
  
Options:
  -h, help              help, show this usage
  -m, monitor           open a monitor
  -a, all               print all the data of spc
  -f, fan               <speed> get/set the speed of fan
                        ex:    spc -f
                               spc -f 30
  -b, battery           battery voltage, current, percentage
  -u, usb               usb voltage
  -o, output            output voltage, current
  -p, powered           power source
  -c, charge            is charging
'''

command_list = [
    '-h',
    'help',
    '-m',
    'monitor',
    '-a',
    'all',
    '-f',
    'fan',
    '-b',
    'battery',
    '-u',
    'usb',
    '-o',
    'output',
    '-p',
    'powered',
    '-c',
    'charge',
    '-j',
    'json',
]

DATA_ALIGN_POSITION = 25


def print_usage():
    print(USAGE)
    quit()


# Return CPU temperature as a character string
def getCPUtemperature():
    import subprocess
    cmd = 'cat /sys/class/thermal/thermal_zone0/temp'
    try:
        temp = int(subprocess.check_output(cmd, shell=True).decode())
        return round(temp / 1000, 2)
    except Exception as e:
        print('getCPUtemperature: %s' % e)
        return 0.0


def monitor(spc):
    while True:
        print("\033[H\033[J", end='')  # clear terminal windows
        data_buffer = spc.read_all()
        print(f"\033[{len(data_buffer)}A", end='\r')  # moves cursor up x lines
        for key, value in data_buffer.items():
            key_len = len(key)
            print(
                f"\033[K{key}{' '*(DATA_ALIGN_POSITION-key_len)}{value[0]}  {value[1]}"
            )
        time.sleep(0.5)


def print_all_data_once(spc):
    data_buffer = spc.read_all()
    for key, value in data_buffer.items():
        print(f"{key}: {value[0]}  {value[1]}")


def print_all_data_once_json(spc):
    import json
    data_buffer = spc.read_all()
    cpu_temp = getCPUtemperature()
    data_buffer['cpu_temp'] = [cpu_temp, '\'C']
    json_str = json.dumps(data_buffer)
    print(json_str)


def main():
    import sys
    argv_len = len(sys.argv)
    if argv_len > 1:
        for argv in sys.argv:
            if argv in command_list:
                spc = SPC()
                if '-h' in sys.argv or 'help' in sys.argv:
                    print_usage()
                elif "-m" in sys.argv or "monitor" in sys.argv:
                    monitor(spc)
                elif '-a' in sys.argv or 'all' in sys.argv:
                    print_all_data_once(spc)
                elif '-j' in sys.argv or 'json' in sys.argv:
                    print_all_data_once_json(spc)
                elif '-f' in sys.argv or 'fan' in sys.argv:
                    try:
                        index = sys.argv.index('-f')
                        speed = int(sys.argv[index + 1])
                        if speed < 0:
                            speed = 0
                        elif speed > 100:
                            speed = 100
                        spc.set_fan_speed(speed)
                        print(f'set fan speed to {speed}')
                    except:
                        fan_speed = spc.read_fan_speed()
                        print(f'fan_speed: {fan_speed}')
                elif '-b' in sys.argv or 'battery' in sys.argv:
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

                elif '-u' in sys.argv or 'usb' in sys.argv:
                    usb_voltage = spc.read_usb_voltage()
                    print(f'usb_voltage: {usb_voltage/1000.0:2.3f} V')
                elif '-o' in sys.argv or 'output' in sys.argv:
                    output_voltage = spc.read_output_voltage()
                    output_current = spc.read_output_current()
                    output_info = f'''\
output_voltage: {output_voltage/1000.0:2.3f} V
output_current: {output_current:-5d} mA            
                    '''
                    print(output_info)
                elif '-p' in sys.argv or 'powered' in sys.argv:
                    power_source = spc.read_power_source()
                    if power_source == 1:
                        print('Power source: usb')
                    else:
                        print('Power source: battery')
                elif '-c' in sys.argv or 'charge' in sys.argv:
                    is_charge = spc.read_is_charging()
                    if is_charge == 1:
                        print('Charging')
                    else:
                        print('No charge')
                break
        else:
            print('Invalid command. You run \"spc -h\" for usage.')
    else:
        print_usage()
