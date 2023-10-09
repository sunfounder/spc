#!/usr/bin/env python3
from smbus import SMBus
import struct
import time
from configparser import ConfigParser
import os


#
# =================================================================
def run_command(cmd):
    import subprocess
    p = subprocess.Popen(cmd,
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    result = p.stdout.read().decode()
    status = p.poll()
    return status, result


#
# =================================================================
config_file = '/opt/spc/config'
fan_switch = False
fan_speed = 0
fan_mode = 'auto'  # auto, quiet, normal, performance

config = ConfigParser()
# check config_file
if not os.path.exists(config_file):
    print('Configuration file does not exist, recreating ...')
    # create config_file
    status, result = run_command(cmd=f'sudo touch {config_file}' +
                                 f' && sudo chmod 774 {config_file}')
    if status != 0:
        print('create config_file failed:\n%s' % result)
        raise Exception(result)

# read config_file
try:
    config.read(config_file)
    fan_switch = bool(config['all']['fan_switch'])
    fan_speed = int(config['all']['fan_speed'])
    fan_mode = str(config['all']['fan_mode'])
except Exception as e:
    print(f"read config error: {e}")
    config['all'] = {
        'fan_switch': fan_switch,
        'fan_speed': fan_speed,
        'fan_mode': fan_mode,
    }
    with open(config_file, 'w') as f:
        config.write(f)

# ups case hat
# =================================================================
ups_case_board_id = 0x00

ups_case_data_mapping = {
    'board_id': (0, 1, 'B'),  # data start index, data length, format
    'ref_voltage': (1, 2, '>H'),
    'usb_voltage': (3, 2, '>H'),
    'usb_current': (5, 2, '>h'),
    'output_voltage': (7, 2, '>H'),
    'output_current': (9, 2, '>h'),
    'battery_voltage': (11, 2, '>H'),
    'battery_current': (13, 2, '>h'),
    'battery_percentage': (15, 1, 'B'),
    'battery_capactiy': (16, 2, '>H'),
    #
    'power_source': (12, 1),
    'is_usb_plugged_in': (13, 1),
    'is_charging': (14, 1),
    'fan_speed': (15, 1),
    'shutdown_request': (18, 1),
}

ups_case_data_buffer = {
    'battery_voltage': [0, 'mV'],  # value, unit
    'battery_current': [0, 'mA'],
    'usb_voltage': [0, 'mV'],
    'output_voltage': [0, 'mV'],
    'output_current': [0, 'mA'],
    'ref_voltage': [0, 'mV'],
    'power_source': [0, ''],
    'is_usb_plugged_in': [0, ''],
    'is_charging': [0, ''],
    'fan_speed': [0, ''],
    'battery_percentage': [0, ''],
    'board_id': [0, ''],
    'shutdown_request': [0, ''],
    'pid_out': [0, ''],
    'dac_vol': [0, ''],
    'test': [0, ''],
}

# pironman hat
# =================================================================
pironman_board_id = 0x01


# class SPC()
# =================================================================
class SPC():

    I2C_ADDRESS = 0x5A

    data_format = '>HhHHHHBBBBBBBhHH'
    total_length = 25
    data_map = {
        'battery_voltage': (0, 2),  # data start index, data length
        'battery_current': (2, 2),
        'usb_voltage': (4, 2),
        'output_voltage': (6, 2),
        'output_current': (8, 2),
        'ref_voltage': (10, 2),
        'power_source': (12, 1),
        'is_usb_plugged_in': (13, 1),
        'is_charging': (14, 1),
        'fan_speed': (15, 1),
        'battery_percentage': (16, 1),
        'board_id': (17, 1),
        'shutdown_request': (18, 1),
        'pid_out': (19, 2),
        'dac_vol': (21, 2),
        'test': (23, 2),
    }
    data_buffer = {
        'battery_voltage': [0, 'mV'],  # value, unit
        'battery_current': [0, 'mA'],
        'usb_voltage': [0, 'mV'],
        'output_voltage': [0, 'mV'],
        'output_current': [0, 'mA'],
        'ref_voltage': [0, 'mV'],
        'power_source': [0, ''],
        'is_usb_plugged_in': [0, ''],
        'is_charging': [0, ''],
        'fan_speed': [0, ''],
        'battery_percentage': [0, ''],
        'board_id': [0, ''],
        'shutdown_request': [0, ''],
        'pid_out': [0, ''],
        'dac_vol': [0, ''],
        'test': [0, ''],
    }

    control_map = {
        'fan_speed': (0, 1),
    }

    def __init__(self, address=I2C_ADDRESS):
        self.addr = address
        try:
            self.i2c_dev = SMBus(1)
            self.i2c_dev.read_byte_data(self.addr, 0x00)  # try to read a byte
        except Exception as e:
            raise IOError(f'UPS Case init error:\b\t{e}')

    def _read_data(self, name: str, format: str):
        _start, _len = self.data_map[name]
        result = self.i2c_dev.read_i2c_block_data(self.addr, _start, _len)
        # print(result)
        result = struct.unpack(format, bytes(result))
        return result[0]

    def read_battery_voltage(self) -> int:
        result = self._read_data('battery_voltage', '>H')
        self.data_buffer['battery_voltage'] = int(result)
        return int(result)

    def read_battery_current(self) -> int:
        result = self._read_data('battery_current', '>h')
        self.data_buffer['battery_current'] = int(result)
        return int(result)

    def read_usb_voltage(self) -> int:
        result = self._read_data('usb_voltage', '>H')
        self.data_buffer['usb_voltage'] = int(result)
        return int(result)

    def read_output_voltage(self) -> int:
        result = self._read_data('output_voltage', '>H')
        self.data_buffer['output_voltage'] = int(result)
        return int(result)

    def read_output_current(self) -> int:
        result = self._read_data('output_current', '>H')
        self.data_buffer['output_current'] = int(result)
        return int(result)

    def read_ref_voltage(self) -> int:
        result = self._read_data('ref_voltage', '>H')
        self.data_buffer['ref_voltage'] = int(result)
        return int(result)

    def read_power_source(self) -> int:
        result = self._read_data('power_source', 'B')
        self.data_buffer['power_source'] = int(result)
        return int(result)

    def read_is_usb_plugged_in(self) -> int:
        result = self._read_data('is_usb_plugged_in', 'B')
        self.data_buffer['is_usb_plugged_in'] = int(result)
        return int(result)

    def read_is_charging(self) -> int:
        result = self._read_data('is_charging', 'B')
        self.data_buffer['is_charging'] = int(result)
        return int(result)

    def read_battery_percentage(self) -> int:
        result = self._read_data('battery_percentage', 'B')
        self.data_buffer['battery_percentage'] = int(result)
        return int(result)

    def read_fan_speed(self) -> int:
        result = self._read_data('fan_speed', 'B')
        self.data_buffer['fan_speed'] = int(result)
        return int(result)

    def read_board_id(self) -> int:
        result = self._read_data('board_id', 'B')
        self.data_buffer['board_id'] = int(result)
        return int(result)

    def read_shutdown_request(self) -> int:
        result = self._read_data('shutdown_request', 'B')
        self.data_buffer['shutdown_request'] = int(result)
        return int(result)

    def read_all(self) -> dict:
        result = self.i2c_dev.read_i2c_block_data(self.addr, 0,
                                                  self.total_length)
        # print(result)
        result = struct.unpack(self.data_format, bytes(result))
        # print(result)
        index = 0
        for key in self.data_buffer:
            self.data_buffer[key][0] = result[index]
            index += 1
            # print(key)
        return self.data_buffer

    def _write_data(self, name: str, value: list):
        # self.i2c_dev.write_i2c_block_data(self.addr, self.control_map[name][0], value)
        self.i2c_dev.write_i2c_block_data(self.addr, 0, value)

    def set_fan_speed(self, speed):
        global fan_speed

        if speed <= 0:
            speed = 0
            self._write_data('fan_speed', [0])
            return
        elif speed > 100:
            speed = 100

        fan_speed = speed
        config['all']['fan_speed'] = str(fan_speed)
        with open(config_file, 'w') as f:
            config.write(f)
        self._write_data('fan_speed', [speed])

    def set_fan_state(self, switch: bool):
        if switch:
            print(config['all']['fan_speed'])
            speed = int(config['all']['fan_speed'])
            self.set_fan_speed(speed)
        else:
            self.set_fan_speed(0)

    def set_fan_mode(self, mode: str):
        speed = fan_speed
        if mode == 'quiet':
            speed = 35
        elif mode == 'normal':
            speed = 65
        elif mode == 'performance':
            speed = 100
        else:
            mode = 'auto'
            speed = 0

        fan_mode = mode
        config['all']['fan_mode'] = str(fan_mode)
        with open(config_file, 'w') as f:
            config.write(f)

        self.set_fan_speed(speed)